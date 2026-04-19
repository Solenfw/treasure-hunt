"""Focused logic tests for map rules, AI pathfinding, and skills."""

import random
import tempfile
import unittest
from pathlib import Path

try:
    import pygame  # noqa: F401
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("pygame is required for gameplay logic tests") from exc

from src.audio_manager import AudioManager
from src.bot_ai import BotAI
from src.game import Game
from src.game_mode import GameMode
from src.game_mode import Difficulty
from src.map import Map, Tile
from src.player import Player


class GameplayLogicTests(unittest.TestCase):
    def setUp(self):
        random.seed(7)

    def test_treasure_requires_all_hints(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player = Player(0, 0)

        player.col, player.row = game_map.treasure_pos
        self.assertEqual(game_map.try_dig(player), 'locked')
        self.assertFalse(player.found_treasure)
        self.assertFalse(game_map.get_tile(*game_map.treasure_pos).revealed)

        for level in range(game_map.HINT_CHAIN_LENGTH):
            player.col, player.row = game_map.hint_positions[level]
            self.assertEqual(game_map.try_dig(player), 'hint_correct')

        player.col, player.row = game_map.treasure_pos
        self.assertEqual(game_map.try_dig(player), 'treasure')
        self.assertTrue(player.found_treasure)

    def test_walls_block_player_and_astar(self):
        game_map = Map(spawn_positions=[(0, 0)])
        wall_pos = (1, 0)
        wall_tile = game_map.get_tile(*wall_pos)
        wall_tile.type = 'wall'
        wall_tile.state = Tile.VISIBLE

        player = Player(0, 0)
        self.assertFalse(player.move('right', game_map))
        self.assertEqual((player.col, player.row), (0, 0))

        bot = BotAI(2, 0, 0, difficulty=Difficulty.HARD)
        goal = game_map.hint_positions[0]
        path = bot._find_path(game_map, goal)
        self.assertIsNotNone(path)
        self.assertNotIn(wall_pos, path)
        self.assertTrue(all(game_map.is_walkable(col, row) for col, row in path))

    def test_skills_apply_real_effects(self):
        game_map = Map(spawn_positions=[(0, 0)])
        caster = Player(0, 0)
        target = Player(0, 0, player_id=2)

        self.assertTrue(caster.use_skill('freeze', own_map=game_map, target=target))
        self.assertTrue(target.is_frozen)
        self.assertIsNotNone(target.skill_feedback)
        self.assertEqual(target.skill_feedback['skill'], 'freeze')
        self.assertFalse(target.move('right', game_map))

        target.update(3.0, game_map)
        self.assertFalse(target.is_frozen)

        caster.current_hint_level = 0
        next_hint = game_map.hint_positions[1]
        self.assertFalse(game_map.get_tile(*next_hint).visible)
        self.assertTrue(caster.use_skill('extra_hint', own_map=game_map, target=target))
        self.assertTrue(game_map.get_tile(*next_hint).visible)
        self.assertEqual(game_map.skill_markers[-1]['position'], next_hint)

    def test_human_keydown_moves_only_one_tile_per_press(self):
        game_map = Map(spawn_positions=[(0, 0)])
        game_map.get_tile(1, 0).type = 'dirt'
        player = Player(0, 0)
        game = object.__new__(Game)
        event = type(
            'KeyEvent',
            (),
            {'key': pygame.K_d, 'scancode': 7, 'unicode': 'd'},
        )()

        game._handle_player_input(event, player, game_map)
        player.update(1 / 60, game_map)

        self.assertEqual((player.col, player.row), (1, 0))

    def test_repeated_keydown_moves_player_multiple_tiles(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player = Player(0, 0)
        game = object.__new__(Game)

        first_event = type('KeyEvent', (), {'key': pygame.K_d, 'scancode': 7, 'unicode': 'd'})()
        second_event = type('KeyEvent', (), {'key': pygame.K_d, 'scancode': 7, 'unicode': 'd'})()

        game._handle_player_input(first_event, player, game_map)
        first_position = (player.col, player.row)
        self.assertNotEqual(first_position, (0, 0))

        player.update(0.2, game_map)
        game._handle_player_input(second_event, player, game_map)
        self.assertGreater(player.col, first_position[0])

    def test_blind_limits_bot_intent_without_breaking_walls(self):
        game_map = Map(spawn_positions=[(0, 0)])
        caster = Player(0, 0)
        bot = BotAI(2, 0, 0, difficulty=Difficulty.HARD)

        self.assertTrue(caster.use_skill('blind', own_map=game_map, target=bot))
        self.assertTrue(bot.is_blinded)

        for _ in range(10):
            bot.update(0.3, game_map, opponent=caster, opponent_map=game_map)
            self.assertTrue(game_map.is_walkable(bot.col, bot.row))

    def test_unicode_skill_fallback_can_target_bot(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player = Player(0, 0, player_id=1)
        bot = BotAI(2, 0, 0, difficulty=Difficulty.NORMAL)
        game = object.__new__(Game)
        game._is_human = lambda actor: isinstance(actor, Player)
        game._play_actor_audio = lambda actor: None
        event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 0, 'unicode': 'q'})()

        game._handle_player_input(event, player, game_map, bot, game_map)
        self.assertTrue(bot.is_frozen)

        bot.update(3.0, game_map, opponent=player, opponent_map=game_map)
        blind_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 0, 'unicode': 'e'})()
        game._handle_player_input(blind_event, player, game_map, bot, game_map)
        self.assertTrue(bot.is_blinded)

    def test_pvp_player1_scancode_fallback_moves_and_skills(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player1 = Player(0, 0, player_id=1)
        player2 = Player(0, 0, player_id=2)
        game = object.__new__(Game)
        game._is_human = lambda actor: isinstance(actor, Player)
        game._play_actor_audio = lambda actor: None
        game._matches_control = Game._matches_control.__get__(game, Game)
        game._binding_text_matches = Game._binding_text_matches.__get__(game, Game)
        game._matches_input_binding = Game._matches_input_binding.__get__(game, Game)
        game._matches_direction_input = Game._matches_direction_input.__get__(game, Game)
        game.game_state = type('State', (), {'game_mode': GameMode.PVP})()

        move_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 7, 'unicode': ''})()
        game._handle_player_input(move_event, player1, game_map, player2, game_map)
        self.assertEqual((player1.col, player1.row), (1, 0))

        skill_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 20, 'unicode': ''})()
        game._handle_player_input(skill_event, player1, game_map, player2, game_map)
        self.assertTrue(player2.is_frozen)

        alt_move_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 32, 'unicode': ''})()
        game._handle_player_input(alt_move_event, player1, game_map, player2, game_map)
        self.assertGreaterEqual(player1.col, 1)

    def test_pvp_player2_scancode_fallback_skills(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player1 = Player(0, 0, player_id=1)
        player2 = Player(0, 0, player_id=2)
        game = object.__new__(Game)
        game._is_human = lambda actor: isinstance(actor, Player)
        game._play_actor_audio = lambda actor: None
        game._matches_control = Game._matches_control.__get__(game, Game)
        game._binding_text_matches = Game._binding_text_matches.__get__(game, Game)
        game._matches_input_binding = Game._matches_input_binding.__get__(game, Game)
        game._matches_direction_input = Game._matches_direction_input.__get__(game, Game)
        game.game_state = type('State', (), {'game_mode': GameMode.PVP})()

        freeze_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 12, 'unicode': ''})()
        game._handle_player_input(freeze_event, player2, game_map, player1, game_map)
        self.assertTrue(player1.is_frozen)

        player1.update(3.0, game_map)
        blind_event = type('KeyEvent', (), {'key': pygame.K_UNKNOWN, 'scancode': 18, 'unicode': ''})()
        game._handle_player_input(blind_event, player2, game_map, player1, game_map)
        self.assertTrue(player1.is_blinded)

    def test_pvp_player1_polled_wasd_movement_fallback(self):
        game_map = Map(spawn_positions=[(0, 0)])
        player1 = Player(0, 0, player_id=1)
        player2 = Player(0, 0, player_id=2)
        game = object.__new__(Game)
        game._is_human = lambda actor: isinstance(actor, Player)
        game._poll_pvp_player1_movement = Game._poll_pvp_player1_movement.__get__(game, Game)
        game._update_actor = Game._update_actor.__get__(game, Game)
        game.game_state = type('State', (), {'game_mode': GameMode.PVP})()

        class PressedState:
            def __getitem__(self, key):
                return 1 if key == pygame.K_d else 0

        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: PressedState()
        try:
            game._update_actor(player1, game_map, player2, game_map, 0.1)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertEqual((player1.col, player1.row), (1, 0))

    def test_generated_layouts_stay_fair_and_connected_across_seeds(self):
        spawn = (7, 5)

        for seed in range(20):
            with self.subTest(seed=seed):
                random.seed(seed)
                template_map = Map(spawn_positions=[spawn])
                layout = template_map.export_layout()
                map1 = Map(layout=layout)
                map2 = Map(layout=layout)

                self.assertEqual(map1.export_layout(), map2.export_layout())
                self.assertTrue(map1._routes_are_valid(spawn_positions=[spawn]))
                self.assertTrue(map2._routes_are_valid(spawn_positions=[spawn]))
                self.assertTrue(map1.get_tile(*map1.hint_positions[0]).visible)
                self.assertNotIn(map1.treasure_pos, map1.wall_positions)
                self.assertTrue(all(position not in map1.wall_positions for position in map1.hint_positions.values()))

    def test_audio_manager_accepts_mp3_music_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            menu_mp3 = temp_path / 'menu.mp3'
            menu_mp3.write_bytes(b'placeholder')

            audio = object.__new__(AudioManager)
            audio.MUSIC_TRACKS = {
                'menu': (
                    temp_path / 'menu.ogg',
                    menu_mp3,
                ),
            }
            audio.MUSIC_FALLBACKS = {}
            audio._missing_music = set()

            resolved_key, resolved_path = audio._resolve_music_path('menu')

            self.assertEqual(resolved_key, 'menu')
            self.assertEqual(resolved_path, menu_mp3)

    def test_game_over_requests_no_gameplay_music(self):
        game = object.__new__(Game)
        game.game_state = type('State', (), {
            'is_playing': lambda self: False,
            'is_paused': lambda self: False,
            'is_settings': lambda self: False,
            'is_game_over': lambda self: True,
        })()
        game.settings_return_state = None

        self.assertIsNone(game._desired_music_key())


if __name__ == '__main__':
    unittest.main()
