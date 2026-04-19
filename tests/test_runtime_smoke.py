"""Headless runtime smoke tests for menu-to-match gameplay flows."""

import os
import unittest

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame

from src.bot_ai import BotAI
from src.game import Game
from src.game_mode import Difficulty, GameMode
from src.player import Player
from src.settings import HUD_HEIGHT, TILE_SIZE


class RuntimeSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        pygame.event.clear()
        self.game = Game()

    def tearDown(self):
        self.game.running = False
        pygame.event.clear()

    def _start_mode(self, mode):
        self.game.game_state.set_game_mode(mode)
        self.game._start_game()
        self.assertTrue(self.game.game_state.is_playing())

    def _step_game(self, frames=1, dt=1 / 30):
        for _ in range(frames):
            self.game.handle_events()
            self.game.update(dt)
            self.game.render()

    def _post_key(self, key, unicode=''):
        pygame.event.post(
            pygame.event.Event(
                pygame.KEYDOWN,
                key=key,
                unicode=unicode,
                mod=0,
                scancode=0,
            )
        )
        self.game.handle_events()
        pygame.event.post(
            pygame.event.Event(
                pygame.KEYUP,
                key=key,
                mod=0,
                scancode=0,
            )
        )
        self.game.handle_events()

    def _first_walkable_direction(self, actor, game_map):
        candidates = [
            ('up', pygame.K_w),
            ('down', pygame.K_s),
            ('left', pygame.K_a),
            ('right', pygame.K_d),
        ]
        deltas = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0),
        }
        for direction, default_key in candidates:
            dx, dy = deltas[direction]
            next_col = actor.col + dx
            next_row = actor.row + dy
            if not game_map.is_walkable(next_col, next_row):
                continue

            key_binding = actor.controls[direction]
            if isinstance(key_binding, (tuple, list)):
                return direction, key_binding[0]
            return direction, key_binding if key_binding else default_key

        self.fail('No walkable direction from spawn.')

    def test_pvp_humans_move_independently_and_skills_apply(self):
        self._start_mode(GameMode.PVP)

        player1_start = (self.game.player1.col, self.game.player1.row)
        player2_start = (self.game.player2.col, self.game.player2.row)

        _, p1_key = self._first_walkable_direction(self.game.player1, self.game.map1)
        self._post_key(p1_key, 'd')
        self.assertNotEqual((self.game.player1.col, self.game.player1.row), player1_start)
        self.assertEqual((self.game.player2.col, self.game.player2.row), player2_start)

        _, p2_key = self._first_walkable_direction(self.game.player2, self.game.map2)
        self._post_key(p2_key)
        self.assertNotEqual((self.game.player2.col, self.game.player2.row), player2_start)

        self.game.player1.current_hint_level = 0
        next_hint = self.game.map1.get_next_objective_position(self.game.player1)
        self.assertFalse(self.game.map1.get_tile(*next_hint).visible)
        self._post_key(pygame.K_f, 'f')
        self.assertTrue(self.game.map1.get_tile(*next_hint).visible)

        self._post_key(pygame.K_q, 'q')
        self.assertTrue(self.game.player2.is_frozen)

        self.game.player2.update(3.0, self.game.map2)
        self.assertFalse(self.game.player2.is_frozen)

        self._post_key(pygame.K_o, 'o')
        self.assertTrue(self.game.player1.is_blinded)
        self.game.render()

    def test_menu_route_flow_reaches_selected_match(self):
        self.assertTrue(self.game.game_state.is_menu())

        self._post_key(pygame.K_RETURN, '\r')
        self.assertTrue(self.game.game_state.is_mode_select())

        self._post_key(pygame.K_2, '2')
        self.assertTrue(self.game.game_state.is_difficulty_select())
        self.assertEqual(self.game.selected_mode_family, 'pve')

        self._post_key(pygame.K_3, '3')
        self.assertTrue(self.game.game_state.is_playing())
        self.assertEqual(self.game.game_state.game_mode, GameMode.PVE_HARD)
        self.assertEqual(self.game.player2.difficulty, Difficulty.HARD)

    def test_settings_route_can_toggle_and_return(self):
        self.game.render()
        self.assertIn('settings', self.game.ui_actions)

        self.game._activate_ui_action('settings')
        self.assertTrue(self.game.game_state.is_settings())

        self.game._activate_ui_action('toggle_hints')
        self.assertFalse(self.game.settings_values['hints'])
        self.game._activate_ui_action('cycle_language')
        self.assertEqual(self.game.settings_values['language'], 'vi')
        self.game.render()
        self.assertIn('settings_manual', self.game.ui_actions)
        self.game._activate_ui_action('settings_manual')
        self.assertTrue(self.game.game_state.is_manual())
        self.game.render()
        self.assertIn('manual_back', self.game.ui_actions)
        self.game._activate_ui_action('manual_back')
        self.assertTrue(self.game.game_state.is_settings())
        self.game._activate_ui_action('settings_save')
        self.assertTrue(self.game.game_state.is_menu())

        self._start_mode(GameMode.PVE_NORMAL)
        self.game.render()
        self.game._activate_ui_action('settings')
        self.assertTrue(self.game.game_state.is_settings())
        self.game._activate_ui_action('settings_back')
        self.assertTrue(self.game.game_state.is_playing())
        self.assertEqual(
            self.game._get_clue_text_for_actor(self.game.player1, self.game.map1),
            self.game.ui.translate(self.game.settings_values['language'], 'clue_disabled'),
        )

    def test_audio_backend_tolerates_missing_assets(self):
        self.assertIn(self.game.audio.play_music('menu'), (True, False))
        self.assertIn(self.game.audio.play_sfx('ui_click'), (True, False))

        self.game._activate_ui_action('settings')
        self.game._activate_ui_action('toggle_music')
        self.game._activate_ui_action('toggle_sfx')
        self.game.render()

        self.assertTrue(self.game.game_state.is_settings())
        self.assertFalse(self.game.settings_values['music'])
        self.assertFalse(self.game.settings_values['sfx'])

    def test_fullscreen_toggle_and_escape_exit_fullscreen(self):
        self.game.render()
        self.assertFalse(self.game.fullscreen)

        self._post_key(pygame.K_F11)
        self.assertTrue(self.game.fullscreen)
        self.assertGreater(self.game.viewport_rect.width, 0)
        self.assertGreater(self.game.viewport_rect.height, 0)

        self._post_key(pygame.K_ESCAPE)
        self.assertFalse(self.game.fullscreen)

    def test_match_render_keeps_players_visible_on_playfield(self):
        self._start_mode(GameMode.PVP)
        self.game.render()

        p1_center = (
            self.game.player1.col * TILE_SIZE + TILE_SIZE // 2,
            HUD_HEIGHT + self.game.player1.row * TILE_SIZE + TILE_SIZE // 2,
        )
        p2_center = (
            (self.game.screen.get_width() // 2) + self.game.player2.col * TILE_SIZE + TILE_SIZE // 2,
            HUD_HEIGHT + self.game.player2.row * TILE_SIZE + TILE_SIZE // 2,
        )

        self.assertEqual(self.game.screen.get_at(p1_center)[:3], self.game.player1.color)
        self.assertEqual(self.game.screen.get_at(p2_center)[:3], self.game.player2.color)

    def test_pve_modes_boot_and_bot_stays_walkable(self):
        expectations = [
            (GameMode.PVE_EASY, Difficulty.EASY),
            (GameMode.PVE_NORMAL, Difficulty.NORMAL),
            (GameMode.PVE_HARD, Difficulty.HARD),
        ]

        for mode, difficulty in expectations:
            with self.subTest(mode=mode):
                self._start_mode(mode)
                self.assertIsInstance(self.game.player1, Player)
                self.assertIsInstance(self.game.player2, BotAI)
                self.assertEqual(self.game.player2.difficulty, difficulty)

                self._post_key(pygame.K_f, 'f')
                self._post_key(pygame.K_q, 'q')
                self.assertTrue(self.game.player2.is_frozen)

                self.game.player2.update(3.0, self.game.map2, opponent=self.game.player1, opponent_map=self.game.map1)
                self.assertFalse(self.game.player2.is_frozen)

                self._post_key(pygame.K_e, 'e')
                self.assertTrue(self.game.player2.is_blinded)

                self.game.player2.skill_decision_cooldown = 0.0
                self.game.player2.skill_aggression = 1.0
                self._step_game(frames=90, dt=0.1)

                self.assertTrue(self.game.map2.is_walkable(self.game.player2.col, self.game.player2.row))
                self.assertIn(self.game.game_state.current_state, (self.game.game_state.PLAYING, self.game.game_state.GAME_OVER))

    def test_eve_runs_without_crashing_and_bots_use_skills(self):
        self._start_mode(GameMode.EVE)

        self.assertIsInstance(self.game.player1, BotAI)
        self.assertIsInstance(self.game.player2, BotAI)

        self.game.player1.skill_decision_cooldown = 0.0
        self.game.player2.skill_decision_cooldown = 0.0
        self.game.player1.skill_aggression = 1.0
        self.game.player2.skill_aggression = 1.0

        self._step_game(frames=150, dt=0.1)

        self.assertTrue(self.game.map1.is_walkable(self.game.player1.col, self.game.player1.row))
        self.assertTrue(self.game.map2.is_walkable(self.game.player2.col, self.game.player2.row))
        self.assertTrue(self.game.player1.last_skill_result or self.game.player2.last_skill_result)
        self.assertIn(self.game.game_state.current_state, (self.game.game_state.PLAYING, self.game.game_state.GAME_OVER))

    def test_gameplay_and_end_screen_text_localize_with_language(self):
        self.game.settings_values['language'] = 'vi'
        self._start_mode(GameMode.EVE)

        clue_text = self.game._get_clue_text_for_actor(self.game.player1, self.game.map1)
        self.assertTrue(clue_text.startswith('Gợi ý 1 ở'))

        self.game._end_game('AI 2 Wins!', 'Secured the treasure after collecting all 3 keys.')
        self.assertEqual(self.game._localized_winner_text(self.game.game_state.winner), 'Máy 2 Thắng!')
        self.assertEqual(
            self.game._localized_reason_text(self.game.game_state.message),
            'Đã lấy được kho báu sau khi thu thập đủ 3 chìa.',
        )
        self.assertEqual(self.game._localized_mode_label(), 'EvE Thường')

    def test_restart_shortcut_keeps_current_mode_and_resets_round(self):
        self._start_mode(GameMode.PVE_HARD)

        self.game.player1.col += 1
        self.game.game_state.round_time_remaining = 17.0

        self._post_key(pygame.K_r, 'r')

        self.assertTrue(self.game.game_state.is_playing())
        self.assertEqual(self.game.game_state.game_mode, GameMode.PVE_HARD)
        self.assertEqual((self.game.player1.col, self.game.player1.row), (self.game.SPAWN_COL, self.game.SPAWN_ROW))
        self.assertEqual((self.game.player2.col, self.game.player2.row), (self.game.SPAWN_COL, self.game.SPAWN_ROW))
        self.assertAlmostEqual(self.game.game_state.round_time_remaining, self.game.game_state.round_time)
        self.assertEqual(self.game.player2.difficulty, Difficulty.HARD)

    def test_game_over_rematch_and_mode_select_shortcuts(self):
        self._start_mode(GameMode.PVP)
        self.game._end_game('Player 1 Wins!', 'Secured the treasure after collecting all 3 keys.')

        self._post_key(pygame.K_r, 'r')
        self.assertTrue(self.game.game_state.is_playing())
        self.assertEqual(self.game.game_state.game_mode, GameMode.PVP)

        self.game._end_game('Draw', 'Timer expired before anyone won.')
        self._post_key(pygame.K_RETURN, '\r')
        self.assertTrue(self.game.game_state.is_mode_select())


if __name__ == '__main__':
    unittest.main()
