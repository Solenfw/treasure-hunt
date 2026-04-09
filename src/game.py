"""Main game loop and state management."""

import pygame

from src.bot_ai import BotAI
from src.game_mode import Difficulty, GameMode
from src.game_state import GameState
from src.map import Map
from src.player import Player
from src.settings import BLACK, CLUE_BOX_HEIGHT, FPS, GRID_COLS, GRID_ROWS, HUD_HEIGHT, MAP_HEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from src.ui_manager import UIManager


class Game:
    """Main game class handling the game loop and state."""

    MODE_OPTIONS = [
        GameMode.PVP,
        GameMode.PVE_EASY,
        GameMode.PVE_NORMAL,
        GameMode.PVE_HARD,
        GameMode.EVE,
    ]
    SPAWN_COL = min(7, GRID_COLS - 1)
    SPAWN_ROW = min(5, GRID_ROWS - 1)

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Treasure Hunt - Truy Tim Kho Bau')
        self.clock = pygame.time.Clock()
        self.running = True
        self.pressed_keys = set()
        self.pressed_scancodes = set()
        self.game_state = GameState()

        # Game components
        self.map1 = None
        self.map2 = None
        self.player1 = None
        self.player2 = None
        self.ui = UIManager()

        # Game logic
        self.selected_mode = 0

    def _is_human(self, actor):
        """Return True for human-controlled competitors."""
        return isinstance(actor, Player)

    def _is_split_screen_mode(self):
        """Return True when both maps should be shown side by side."""
        return self.player2 is not None and self.map2 is not None

    def _get_actor_name(self, actor):
        """Return a human-readable label for winners and HUD."""
        return getattr(actor, 'display_name', f"Player {actor.player_id}")

    def _resolve_difficulty(self, mode):
        """Map a game mode to the appropriate bot difficulty."""
        if mode == GameMode.PVE_EASY:
            return Difficulty.EASY
        if mode == GameMode.PVE_HARD:
            return Difficulty.HARD
        return Difficulty.NORMAL

    def _matches_control(self, key, binding):
        """Return True when the pressed key matches a control binding."""
        if isinstance(binding, (tuple, list, set)):
            return key in binding
        return key == binding

    def _matches_direction_input(self, event, controls, direction, fallback_text=''):
        """Return True when a movement key matches by keycode, scancode, or typed text."""
        if self._matches_control(event.key, controls[direction]):
            return True

        scan_code = controls.get(f'{direction}_scan')
        if scan_code is not None and event.scancode == scan_code:
            return True

        text_key = event.unicode.lower() if event.unicode else ''
        return bool(fallback_text) and text_key == fallback_text

    def _start_selected_mode(self):
        """Start the currently highlighted mode from the menu."""
        selected_mode = self.MODE_OPTIONS[self.selected_mode]
        self.game_state.set_game_mode(selected_mode)
        self._start_game()

    def _handle_player_input(self, event, player, game_map):
        """Route gameplay keys to the correct human-controlled player."""
        if not self._is_human(player):
            return

        key = event.key
        controls = player.controls

        # Movement is handled directly on KEYDOWN so short taps are not lost.
        if self._matches_direction_input(event, controls, 'up', 'w' if player.player_id == 1 else ''):
            player.move('up', game_map)
        elif self._matches_direction_input(event, controls, 'down', 's' if player.player_id == 1 else ''):
            player.move('down', game_map)
        elif self._matches_direction_input(event, controls, 'left', 'a' if player.player_id == 1 else ''):
            player.move('left', game_map)
        elif self._matches_direction_input(event, controls, 'right', 'd' if player.player_id == 1 else ''):
            player.move('right', game_map)
        elif self._matches_control(key, controls['dig']):
            player.dig(game_map)
        elif self._matches_control(key, controls['skill']):
            player.use_skill('freeze')

    def handle_events(self):
        """Process game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)
                self.pressed_scancodes.discard(event.scancode)
                continue

            if event.type != pygame.KEYDOWN:
                continue

            self.pressed_keys.add(event.key)
            self.pressed_scancodes.add(event.scancode)

            # Menu
            if self.game_state.is_menu():
                if event.key == pygame.K_RETURN:
                    self.game_state.set_state(GameState.MODE_SELECT)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            # Mode selection
            elif self.game_state.is_mode_select():
                if event.key == pygame.K_UP:
                    self.selected_mode = (self.selected_mode - 1) % len(self.MODE_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    self.selected_mode = (self.selected_mode + 1) % len(self.MODE_OPTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_selected_mode()
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    self.selected_mode = 0
                    self._start_selected_mode()
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.selected_mode = 1
                    self._start_selected_mode()
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.selected_mode = 2
                    self._start_selected_mode()
                elif event.key in (pygame.K_4, pygame.K_KP4):
                    self.selected_mode = 3
                    self._start_selected_mode()
                elif event.key in (pygame.K_5, pygame.K_KP5):
                    self.selected_mode = 4
                    self._start_selected_mode()
                elif event.key == pygame.K_ESCAPE:
                    self.game_state.set_state(GameState.MENU)

            # Gameplay
            elif self.game_state.is_playing():
                if event.key == pygame.K_p:
                    self.game_state.set_state(GameState.PAUSED)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self._handle_player_input(event, self.player1, self.map1)
                    self._handle_player_input(event, self.player2, self.map2)

            # Paused
            elif self.game_state.is_paused():
                if event.key == pygame.K_p:
                    self.game_state.set_state(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            # Game Over
            elif self.game_state.is_game_over():
                if event.key == pygame.K_RETURN:
                    self.game_state.set_state(GameState.MENU)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _start_game(self):
        """Initialize a new game."""
        game_mode = self.game_state.game_mode
        spawn_col = self.SPAWN_COL
        spawn_row = self.SPAWN_ROW
        spawn_positions = [(spawn_col, spawn_row)]
        shared_layout = Map(spawn_positions=spawn_positions).export_layout()
        self.map1 = Map(layout=shared_layout)
        self.map2 = Map(layout=shared_layout)

        if game_mode == GameMode.PVP:
            self.player1 = Player(spawn_col, spawn_row, player_id=1)
            self.player2 = Player(spawn_col, spawn_row, player_id=2)
        elif game_mode in (GameMode.PVE_EASY, GameMode.PVE_NORMAL, GameMode.PVE_HARD):
            solo_controls = {
                'up': (pygame.K_w, pygame.K_UP),
                'down': (pygame.K_s, pygame.K_DOWN),
                'left': (pygame.K_a, pygame.K_LEFT),
                'right': (pygame.K_d, pygame.K_RIGHT),
                'dig': (pygame.K_SPACE, pygame.K_RETURN, pygame.K_LCTRL, pygame.K_KP_ENTER),
                'skill': (pygame.K_e, pygame.K_RSHIFT),
            }
            self.player1 = Player(
                spawn_col,
                spawn_row,
                player_id=1,
                controls=solo_controls,
                control_hint='WASD or ARROWS / SPACE or ENTER',
            )
            self.player2 = BotAI(2, spawn_col, spawn_row, difficulty=self._resolve_difficulty(game_mode))
        elif game_mode == GameMode.EVE:
            self.player1 = BotAI(1, spawn_col, spawn_row, difficulty=Difficulty.NORMAL)
            self.player2 = BotAI(2, spawn_col, spawn_row, difficulty=Difficulty.NORMAL)
        else:
            raise ValueError(f"Unsupported game mode: {game_mode}")

        self.pressed_keys.clear()
        self.pressed_scancodes.clear()
        self.game_state.reset_round()
        self.game_state.set_state(GameState.PLAYING)

    def _check_victory_conditions(self):
        """Evaluate all end-of-round conditions."""
        if self.player1.found_treasure and self.player2.found_treasure:
            return "Draw", "Both competitors found the treasure!"
        if self.player1.found_treasure:
            return f"{self._get_actor_name(self.player1)} Wins!", "Found the treasure!"
        if self.player2.found_treasure:
            return f"{self._get_actor_name(self.player2)} Wins!", "Found the treasure!"

        if self.player1.health <= 0 and self.player2.health <= 0:
            return "Draw", "Both competitors were eliminated!"
        if self.player1.health <= 0:
            return (
                f"{self._get_actor_name(self.player2)} Wins!",
                f"{self._get_actor_name(self.player1)} eliminated!",
            )
        if self.player2.health <= 0:
            return (
                f"{self._get_actor_name(self.player1)} Wins!",
                f"{self._get_actor_name(self.player2)} eliminated!",
            )

        return None

    def update(self, dt):
        """Update game logic."""
        if not self.game_state.is_playing():
            return

        time_expired = self.game_state.update_timer(dt)
        if time_expired:
            self._end_game("Time's Up!", "Draw - No winner")
            return

        self.player1.update(dt, self.map1)
        self.player2.update(dt, self.map2)

        winner_info = self._check_victory_conditions()
        if winner_info:
            self._end_game(*winner_info)

    def _end_game(self, winner, reason):
        """End the current game."""
        self.game_state.winner = winner
        self.game_state.message = reason
        self.game_state.set_state(GameState.GAME_OVER)

    def _render_match(self):
        """Render gameplay views for the active game mode."""
        split_screen = self._is_split_screen_mode()

        if split_screen:
            half_width = SCREEN_WIDTH // 2
            self.map1.render(self.screen, x_offset=0, y_offset=HUD_HEIGHT)
            self.player1.render(self.screen, x_offset=0, y_offset=HUD_HEIGHT)
            self.map2.render(self.screen, x_offset=half_width, y_offset=HUD_HEIGHT)
            self.player2.render(self.screen, x_offset=half_width, y_offset=HUD_HEIGHT)
            pygame.draw.line(self.screen, WHITE, (half_width, HUD_HEIGHT), (half_width, SCREEN_HEIGHT), 2)

            clue_box_height = CLUE_BOX_HEIGHT
            clue_y = HUD_HEIGHT + MAP_HEIGHT
            self.ui.render_clue_box(
                self.screen,
                self.map1.get_clue_text(self.player1.current_hint_level),
                rect=pygame.Rect(0, clue_y, half_width, clue_box_height),
                label=self._get_actor_name(self.player1),
            )
            self.ui.render_clue_box(
                self.screen,
                self.map2.get_clue_text(self.player2.current_hint_level),
                rect=pygame.Rect(half_width, clue_y, half_width, clue_box_height),
                label=self._get_actor_name(self.player2),
            )
        else:
            self.map1.render(self.screen, y_offset=HUD_HEIGHT)
            self.player1.render(self.screen, y_offset=HUD_HEIGHT)
            self.ui.render_clue_box(
                self.screen,
                self.map1.get_clue_text(self.player1.current_hint_level),
            )

        self.ui.render_game_hud(
            self.screen,
            self.player1,
            self.player2,
            self.game_state.round_time_remaining,
        )

        if self.game_state.is_paused():
            self.ui.render_pause_overlay(self.screen)

    def render(self):
        """Render the current frame."""
        self.screen.fill(BLACK)

        if self.game_state.is_menu():
            self.ui.render_main_menu(self.screen)
        elif self.game_state.is_mode_select():
            self.ui.render_mode_select(self.screen, self.selected_mode)
        elif self.game_state.is_playing() or self.game_state.is_paused():
            self._render_match()
        elif self.game_state.is_game_over():
            self.ui.render_game_over(self.screen, self.game_state.winner, self.game_state.message)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
