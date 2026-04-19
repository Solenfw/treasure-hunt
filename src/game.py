"""Main game loop and state management."""

import re

import pygame

from src.audio_manager import AudioManager
from src.bot_ai import BotAI
from src.game_mode import Difficulty, GameMode
from src.game_state import GameState
from src.map import Map
from src.player import Player
from src.settings import BLACK, CLUE_BOX_HEIGHT, FPS, GRID_COLS, GRID_ROWS, HUD_HEIGHT, MAP_HEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from src.ui_manager import UIManager


class Game:
    """Main game class handling the game loop and state."""

    PVP_PLAYER1_MOVE_REPEAT_INITIAL = 0.18
    PVP_PLAYER1_MOVE_REPEAT_HELD = 0.08
    MODE_FAMILIES = ['pvp', 'pve', 'eve']
    FAMILY_LABELS = {
        'pvp': 'PvP',
        'pve': 'PvE',
        'eve': 'EvE',
    }
    DIFFICULTY_OPTIONS = {
        'pvp': ['Classic PvP'],
        'pve': ['Easy', 'Normal', 'Hard'],
        'eve': ['Easy', 'Normal', 'Hard'],
    }
    SPAWN_COL = min(7, GRID_COLS - 1)
    SPAWN_ROW = min(5, GRID_ROWS - 1)
    MODE_LABELS = {
        GameMode.PVP: 'PvP',
        GameMode.PVE_EASY: 'PvE Easy',
        GameMode.PVE_NORMAL: 'PvE Normal',
        GameMode.PVE_HARD: 'PvE Hard',
        GameMode.EVE: 'EvE',
    }

    def __init__(self):
        self.base_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.fullscreen = False
        self.display_surface = None
        self.screen = None
        self.viewport_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._apply_display_mode()
        pygame.display.set_caption('Treasure Hunt - Truy Tìm Kho Báu')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState()

        # Game components
        self.map1 = None
        self.map2 = None
        self.player1 = None
        self.player2 = None
        self.ui = UIManager()

        # Game logic
        self.selected_mode = 0
        self.selected_mode_family = self.MODE_FAMILIES[self.selected_mode]
        self.selected_difficulty = 1
        self.bot_difficulty = Difficulty.NORMAL
        self.settings_values = {
            'music': True,
            'sfx': True,
            'hints': True,
            'language': 'en',
        }
        self.audio = AudioManager(self.settings_values)
        self.settings_return_state = GameState.MENU
        self.manual_return_state = GameState.SETTINGS
        self.ui_actions = {}

    def _apply_display_mode(self):
        """Create the real display surface and update the logical viewport."""
        driver = pygame.display.get_driver() if pygame.display.get_init() else ''
        use_dummy_fullscreen = driver == 'dummy'
        mode_size = (0, 0) if self.fullscreen and not use_dummy_fullscreen else self.base_size
        flags = pygame.FULLSCREEN if self.fullscreen and not use_dummy_fullscreen else 0

        self.display_surface = pygame.display.set_mode(mode_size, flags)
        if self.screen is None:
            self.screen = pygame.Surface(self.base_size).convert()
        self._update_viewport()

    def _update_viewport(self):
        """Recompute the letterboxed viewport used to present the logical canvas."""
        display_width, display_height = self.display_surface.get_size()
        if display_width <= 0 or display_height <= 0:
            display_width, display_height = self.base_size

        scale = min(display_width / self.base_size[0], display_height / self.base_size[1])
        viewport_width = max(1, int(self.base_size[0] * scale))
        viewport_height = max(1, int(self.base_size[1] * scale))
        viewport_x = (display_width - viewport_width) // 2
        viewport_y = (display_height - viewport_height) // 2
        self.viewport_rect = pygame.Rect(viewport_x, viewport_y, viewport_width, viewport_height)

    def _toggle_fullscreen(self, force=None):
        """Toggle fullscreen presentation without changing logical layout coordinates."""
        target_state = (not self.fullscreen) if force is None else force
        if target_state == self.fullscreen:
            return

        self.fullscreen = target_state
        self._apply_display_mode()

    def _present_frame(self):
        """Scale the logical frame to the active window or fullscreen display."""
        self.display_surface.fill((18, 11, 7))

        if self.viewport_rect.size == self.base_size:
            self.display_surface.blit(self.screen, self.viewport_rect.topleft)
        else:
            scaled = pygame.transform.smoothscale(self.screen, self.viewport_rect.size)
            self.display_surface.blit(scaled, self.viewport_rect.topleft)
            pygame.draw.rect(self.display_surface, (176, 132, 60), self.viewport_rect, 2, border_radius=12)

        pygame.display.flip()

    def _display_to_logical(self, position):
        """Convert a real display coordinate into the logical canvas coordinate space."""
        if not self.viewport_rect.collidepoint(position):
            return None

        local_x = position[0] - self.viewport_rect.x
        local_y = position[1] - self.viewport_rect.y
        logical_x = int(local_x * self.base_size[0] / self.viewport_rect.width)
        logical_y = int(local_y * self.base_size[1] / self.viewport_rect.height)
        logical_x = max(0, min(self.base_size[0] - 1, logical_x))
        logical_y = max(0, min(self.base_size[1] - 1, logical_y))
        return logical_x, logical_y

    def _sync_audio_preferences(self):
        """Apply the current settings toggles to the audio backend."""
        self.audio.sync_settings(self.settings_values)

    def _ui_language(self):
        """Return the active UI language code."""
        return self.settings_values.get('language', 'en')

    def _ui_text(self, key, default=None):
        """Return one translated UI string."""
        return self.ui.translate(self._ui_language(), key, default)

    def _desired_music_key(self):
        """Map the current state to the right background music track."""
        if self.game_state.is_playing() or self.game_state.is_paused():
            return 'gameplay'
        if self.game_state.is_settings() and self.settings_return_state in (GameState.PLAYING, GameState.PAUSED):
            return 'gameplay'
        if self.game_state.is_game_over():
            return None
        return 'menu'

    def _sync_music(self):
        """Keep background music aligned with the visible screen."""
        self.audio.play_music(self._desired_music_key())

    def _play_actor_audio(self, actor):
        """Drain any gameplay audio cues queued by an actor."""
        if actor is None or not hasattr(actor, 'consume_audio_events'):
            return

        for cue in actor.consume_audio_events():
            self.audio.play_sfx(cue)

    def _play_result_sound(self, winner):
        """Play a one-shot result sting when the round ends."""
        if winner == "Draw":
            return

        player1_name = self._get_actor_name(self.player1) if self.player1 else ''
        if self.game_state.game_mode in (GameMode.PVE_EASY, GameMode.PVE_NORMAL, GameMode.PVE_HARD):
            cue = 'win' if winner.startswith(player1_name) else 'lose'
        else:
            cue = 'win'
        self.audio.play_sfx(cue)

    def _play_ui_sound_for_action(self, action):
        """Choose an appropriate click/confirm/back sound for one UI action."""
        if action.startswith('toggle_') or action in ('settings', 'fullscreen', 'cycle_language'):
            cue = 'ui_click'
        elif action in ('back', 'home', 'settings_back', 'settings_quit', 'manual_back', 'end_menu', 'end_mode_select', 'pause_menu'):
            cue = 'ui_back'
        else:
            cue = 'ui_confirm'
        self.audio.play_sfx(cue)

    def _toggle_setting(self, setting_name):
        """Flip one settings flag and sync dependent systems."""
        self.settings_values[setting_name] = not self.settings_values[setting_name]
        self._sync_audio_preferences()

    def _cycle_language(self):
        """Toggle UI language between English and Vietnamese."""
        self.settings_values['language'] = 'vi' if self._ui_language() == 'en' else 'en'

    def _is_human(self, actor):
        """Return True for human-controlled competitors."""
        return isinstance(actor, Player)

    def _is_split_screen_mode(self):
        """Return True when both maps should be shown side by side."""
        return self.player2 is not None and self.map2 is not None

    def _get_actor_name(self, actor):
        """Return a human-readable label for winners and HUD."""
        return getattr(actor, 'display_name', f"Player {actor.player_id}")

    def _localized_actor_name(self, actor):
        """Return the UI-localized actor name for the current language."""
        return self.ui.get_actor_label(actor, language=self._ui_language())

    def _resolve_difficulty(self, mode):
        """Map a game mode to the appropriate bot difficulty."""
        if mode == GameMode.PVE_EASY:
            return Difficulty.EASY
        if mode == GameMode.PVE_HARD:
            return Difficulty.HARD
        return Difficulty.NORMAL

    def _difficulty_from_index(self, index):
        """Convert menu index to bot difficulty."""
        return [Difficulty.EASY, Difficulty.NORMAL, Difficulty.HARD][max(0, min(index, 2))]

    def _difficulty_label(self, difficulty):
        """Return a short label for a difficulty enum."""
        return {
            Difficulty.EASY: 'Easy',
            Difficulty.NORMAL: 'Normal',
            Difficulty.HARD: 'Hard',
        }[difficulty]

    def _localized_difficulty_label(self, difficulty):
        """Return the localized difficulty label used by the UI."""
        key = {
            Difficulty.EASY: 'option_easy',
            Difficulty.NORMAL: 'option_normal',
            Difficulty.HARD: 'option_hard',
        }[difficulty]
        return self._ui_text(key, self._difficulty_label(difficulty))

    def _sync_selected_mode(self):
        """Keep the menu highlight aligned with the active game mode."""
        game_mode = self.game_state.game_mode
        if game_mode == GameMode.PVP:
            self.selected_mode_family = 'pvp'
            self.selected_mode = 0
            self.selected_difficulty = 0
        elif game_mode in (GameMode.PVE_EASY, GameMode.PVE_NORMAL, GameMode.PVE_HARD):
            self.selected_mode_family = 'pve'
            self.selected_mode = 1
            self.selected_difficulty = {
                GameMode.PVE_EASY: 0,
                GameMode.PVE_NORMAL: 1,
                GameMode.PVE_HARD: 2,
            }[game_mode]
            self.bot_difficulty = self._resolve_difficulty(game_mode)
        elif game_mode == GameMode.EVE:
            self.selected_mode_family = 'eve'
            self.selected_mode = 2
            self.selected_difficulty = {
                Difficulty.EASY: 0,
                Difficulty.NORMAL: 1,
                Difficulty.HARD: 2,
            }.get(self.bot_difficulty, 1)

    def _restart_current_mode(self):
        """Restart the current mode immediately."""
        self._sync_selected_mode()
        self._start_game()

    def _go_to_mode_select(self):
        """Return to mode selection while preserving the active highlight."""
        self._sync_selected_mode()
        self.game_state.set_state(GameState.MODE_SELECT)

    def _get_mode_label(self):
        """Return the active mode label for HUD and summaries."""
        if self.game_state.game_mode == GameMode.EVE:
            return f"EvE {self._difficulty_label(self.bot_difficulty)}"
        return self.MODE_LABELS.get(self.game_state.game_mode, 'Match')

    def _localized_mode_label(self):
        """Return a localized mode label for summary screens."""
        game_mode = self.game_state.game_mode
        if game_mode == GameMode.PVP:
            return 'PvP'
        if game_mode == GameMode.PVE_EASY:
            return f"PvE {self._localized_difficulty_label(Difficulty.EASY)}"
        if game_mode == GameMode.PVE_NORMAL:
            return f"PvE {self._localized_difficulty_label(Difficulty.NORMAL)}"
        if game_mode == GameMode.PVE_HARD:
            return f"PvE {self._localized_difficulty_label(Difficulty.HARD)}"
        if game_mode == GameMode.EVE:
            return f"EvE {self._localized_difficulty_label(self.bot_difficulty)}"
        return self._get_mode_label()

    def _difficulty_labels(self):
        """Return current menu difficulty labels."""
        return self.DIFFICULTY_OPTIONS[self.selected_mode_family]

    def _compose_selected_mode(self):
        """Build the actual match configuration from family + difficulty selection."""
        family = self.selected_mode_family
        if family == 'pvp':
            self.bot_difficulty = Difficulty.NORMAL
            return GameMode.PVP
        if family == 'pve':
            mode = [GameMode.PVE_EASY, GameMode.PVE_NORMAL, GameMode.PVE_HARD][self.selected_difficulty]
            self.bot_difficulty = self._resolve_difficulty(mode)
            return mode

        self.bot_difficulty = self._difficulty_from_index(self.selected_difficulty)
        return GameMode.EVE

    def _confirm_mode_family(self, family):
        """Move from mode selection into difficulty selection."""
        self.selected_mode_family = family
        self.selected_mode = self.MODE_FAMILIES.index(family)
        self.selected_difficulty = 0 if family == 'pvp' else 1
        self.game_state.set_state(GameState.DIFFICULTY_SELECT)

    def _start_selected_difficulty(self, index=None):
        """Start the match after difficulty confirmation."""
        options = self._difficulty_labels()
        if index is not None:
            self.selected_difficulty = max(0, min(index, len(options) - 1))

        selected_mode = self._compose_selected_mode()
        self.game_state.set_game_mode(selected_mode)
        self._start_game()

    def _open_settings(self, return_state=None):
        """Open settings and remember where to return."""
        self.settings_return_state = return_state or self.game_state.current_state
        self.game_state.set_state(GameState.SETTINGS)

    def _open_manual(self):
        """Open the manual page from settings."""
        self.manual_return_state = self.game_state.current_state
        self.game_state.set_state(GameState.MANUAL)

    def _close_settings(self, to_start=False):
        """Leave settings either back to the caller or to the main menu."""
        self._sync_audio_preferences()
        if to_start:
            self.game_state.set_state(GameState.MENU)
            return

        target_state = self.settings_return_state or GameState.MENU
        self.game_state.set_state(target_state)

    def _close_manual(self):
        """Return from the manual page to the previous UI state."""
        target_state = self.manual_return_state or GameState.SETTINGS
        self.game_state.set_state(target_state)

    def _action_at_pos(self, position):
        """Return the currently rendered UI action under the cursor."""
        logical_position = self._display_to_logical(position)
        if logical_position is None:
            return None

        for action, rect in self.ui_actions.items():
            if rect.collidepoint(logical_position):
                return action
        return None

    def _activate_ui_action(self, action):
        """Handle one UI button click."""
        self._play_ui_sound_for_action(action)
        if action in ('start', 'mode'):
            self.game_state.set_state(GameState.MODE_SELECT)
            return
        if action == 'quit':
            self.running = False
            return
        if action == 'settings':
            self._open_settings()
            return
        if action == 'home':
            self.game_state.set_state(GameState.MENU)
            return
        if action in ('pvp', 'pve', 'eve'):
            self._confirm_mode_family(action)
            return
        if action.startswith('difficulty_'):
            self._start_selected_difficulty(int(action.split('_')[-1]))
            return
        if action == 'back':
            self.game_state.set_state(GameState.MODE_SELECT)
            return
        if action.startswith('toggle_'):
            setting_name = action.split('_', 1)[1]
            self._toggle_setting(setting_name)
            return
        if action == 'cycle_language':
            self._cycle_language()
            return
        if action == 'settings_manual':
            self._open_manual()
            return
        if action in ('settings_back', 'settings_save'):
            self._close_settings()
            return
        if action == 'settings_quit':
            self._close_settings(to_start=True)
            return
        if action == 'manual_back':
            self._close_manual()
            return
        if action == 'end_rematch':
            self._restart_current_mode()
            return
        if action in ('end_mode_select', 'pause_menu'):
            self._go_to_mode_select()
            return
        if action == 'end_menu':
            self.game_state.set_state(GameState.MENU)
            return
        if action == 'pause_resume':
            self.game_state.set_state(GameState.PLAYING)
            return
        if action == 'pause_restart':
            self._restart_current_mode()
            return
        if action == 'fullscreen':
            self._toggle_fullscreen()
            return

    def _matches_control(self, key, binding):
        """Return True when the pressed key matches a control binding."""
        if isinstance(binding, (tuple, list, set)):
            return key in binding
        return key == binding

    def _binding_text_matches(self, event, binding):
        """Return True when typed text matches a single-letter binding."""
        text_key = event.unicode.lower() if getattr(event, 'unicode', '') else ''
        if not text_key:
            return False

        bindings = binding if isinstance(binding, (tuple, list, set)) else (binding,)
        for key in bindings:
            key_name = pygame.key.name(key).lower() if isinstance(key, int) else ''
            if len(key_name) == 1 and key_name == text_key:
                return True
        return False

    def _matches_input_binding(self, event, binding):
        """Return True when a KEYDOWN event matches a control binding."""
        return self._matches_control(event.key, binding) or self._binding_text_matches(event, binding)

    def _matches_direction_input(self, event, controls, direction, fallback_text=''):
        """Return True when a movement key matches by keycode, scancode, or typed text."""
        if self._matches_input_binding(event, controls[direction]):
            return True

        scan_code = controls.get(f'{direction}_scan')
        if scan_code is not None and event.scancode == scan_code:
            return True

        text_key = event.unicode.lower() if event.unicode else ''
        return bool(fallback_text) and text_key == fallback_text

    def _move_player(self, player, direction, game_map):
        """Move one human actor and arm PvP Player 1 held-key repeat when needed."""
        moved = player.move(direction, game_map)
        game_mode = getattr(getattr(self, 'game_state', None), 'game_mode', None)
        if moved and game_mode == GameMode.PVP and player.player_id == 1:
            player.move_repeat_timer = self.PVP_PLAYER1_MOVE_REPEAT_INITIAL
        return moved

    def _poll_pvp_player1_movement(self, player, game_map):
        """Fallback movement path for PvP Player 1 using pressed-key state."""
        game_mode = getattr(getattr(self, 'game_state', None), 'game_mode', None)
        if game_mode != GameMode.PVP or player.player_id != 1:
            return
        if player.move_repeat_timer > 0:
            return

        pressed = pygame.key.get_pressed()
        held_keys = (
            pressed[pygame.K_w],
            pressed[pygame.K_s],
            pressed[pygame.K_a],
            pressed[pygame.K_d],
        )
        if not any(held_keys):
            player.move_repeat_timer = 0.0
            return

        direction = None
        if held_keys[0]:
            direction = 'up'
        elif held_keys[1]:
            direction = 'down'
        elif held_keys[2]:
            direction = 'left'
        elif held_keys[3]:
            direction = 'right'

        if direction and player.move(direction, game_map):
            player.move_repeat_timer = self.PVP_PLAYER1_MOVE_REPEAT_HELD

    def _start_selected_mode(self):
        """Start the currently highlighted mode from the menu."""
        self.selected_mode_family = self.MODE_FAMILIES[self.selected_mode]
        self._confirm_mode_family(self.selected_mode_family)

    def _handle_player_input(self, event, player, game_map, opponent=None, opponent_map=None):
        """Route gameplay keys to the correct human-controlled player."""
        if not self._is_human(player):
            return

        key = event.key
        text_key = event.unicode.lower() if getattr(event, 'unicode', '') else ''
        scan_code = getattr(event, 'scancode', None)
        controls = player.controls
        game_mode = getattr(getattr(self, 'game_state', None), 'game_mode', None)

        if game_mode == GameMode.PVP and player.player_id == 1:
            if key == pygame.K_w or text_key == 'w' or scan_code in (26, 17):
                self._move_player(player, 'up', game_map)
                return
            if key == pygame.K_s or text_key == 's' or scan_code in (22, 31):
                self._move_player(player, 'down', game_map)
                return
            if key == pygame.K_a or text_key == 'a' or scan_code in (4, 30):
                self._move_player(player, 'left', game_map)
                return
            if key == pygame.K_d or text_key == 'd' or scan_code in (7, 32):
                self._move_player(player, 'right', game_map)
                return
            if key == pygame.K_q or text_key == 'q' or scan_code in (20, 16):
                player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if key == pygame.K_e or text_key == 'e' or scan_code in (8, 18):
                player.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if key == pygame.K_f or text_key == 'f' or scan_code in (9, 33):
                player.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
        if game_mode == GameMode.PVP and player.player_id == 2:
            if scan_code == 12:
                player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if scan_code == 18:
                player.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if scan_code == 19:
                player.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return

        if player.player_id == 1:
            if text_key == 'q':
                player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if text_key == 'e':
                player.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if text_key == 'f':
                player.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
        elif player.player_id == 2:
            if text_key == 'i':
                player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if text_key == 'o':
                player.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return
            if text_key == 'p':
                player.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)
                self._play_actor_audio(player)
                return

        # Movement is handled directly on KEYDOWN so short taps are not lost.
        if self._matches_direction_input(event, controls, 'up', 'w' if player.player_id == 1 else ''):
            self._move_player(player, 'up', game_map)
        elif self._matches_direction_input(event, controls, 'down', 's' if player.player_id == 1 else ''):
            self._move_player(player, 'down', game_map)
        elif self._matches_direction_input(event, controls, 'left', 'a' if player.player_id == 1 else ''):
            self._move_player(player, 'left', game_map)
        elif self._matches_direction_input(event, controls, 'right', 'd' if player.player_id == 1 else ''):
            self._move_player(player, 'right', game_map)
        elif self._matches_input_binding(event, controls['dig']):
            player.dig(game_map)
        elif self._matches_input_binding(event, controls.get('skill_freeze', controls.get('skill'))):
            player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
        elif self._matches_input_binding(event, controls.get('skill_blind')):
            player.use_skill('blind', own_map=game_map, target=opponent, target_map=opponent_map)
        elif self._matches_input_binding(event, controls.get('skill_extra_hint')):
            player.use_skill('extra_hint', own_map=game_map, target=opponent, target_map=opponent_map)
        elif self._matches_input_binding(event, controls.get('skill')):
            player.use_skill('freeze', own_map=game_map, target=opponent, target_map=opponent_map)
        self._play_actor_audio(player)

    def handle_events(self):
        """Process game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self._action_at_pos(event.pos)
                if action:
                    self._activate_ui_action(action)
                continue

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT):
                self.audio.play_sfx('ui_click')
                self._toggle_fullscreen()
                continue
            if event.key == pygame.K_ESCAPE and self.fullscreen:
                self.audio.play_sfx('ui_back')
                self._toggle_fullscreen(force=False)
                continue

            # Menu
            if self.game_state.is_menu():
                if event.key == pygame.K_RETURN:
                    self.audio.play_sfx('ui_confirm')
                    self.game_state.set_state(GameState.MODE_SELECT)
                elif event.key == pygame.K_s:
                    self.audio.play_sfx('ui_click')
                    self._open_settings(GameState.MENU)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            # Mode selection
            elif self.game_state.is_mode_select():
                if event.key == pygame.K_UP:
                    self.selected_mode = (self.selected_mode - 1) % len(self.MODE_FAMILIES)
                    self.selected_mode_family = self.MODE_FAMILIES[self.selected_mode]
                    self.audio.play_sfx('ui_click')
                elif event.key == pygame.K_DOWN:
                    self.selected_mode = (self.selected_mode + 1) % len(self.MODE_FAMILIES)
                    self.selected_mode_family = self.MODE_FAMILIES[self.selected_mode]
                    self.audio.play_sfx('ui_click')
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_mode()
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    self.selected_mode = 0
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_mode()
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.selected_mode = 1
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_mode()
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.selected_mode = 2
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_mode()
                elif event.key == pygame.K_s:
                    self.audio.play_sfx('ui_click')
                    self._open_settings(GameState.MODE_SELECT)
                elif event.key == pygame.K_ESCAPE:
                    self.audio.play_sfx('ui_back')
                    self.game_state.set_state(GameState.MENU)

            elif self.game_state.is_difficulty_select():
                max_index = len(self._difficulty_labels())
                if event.key == pygame.K_UP:
                    self.selected_difficulty = (self.selected_difficulty - 1) % max_index
                    self.audio.play_sfx('ui_click')
                elif event.key == pygame.K_DOWN:
                    self.selected_difficulty = (self.selected_difficulty + 1) % max_index
                    self.audio.play_sfx('ui_click')
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_difficulty()
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_difficulty(0)
                elif event.key in (pygame.K_2, pygame.K_KP2) and max_index >= 2:
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_difficulty(1)
                elif event.key in (pygame.K_3, pygame.K_KP3) and max_index >= 3:
                    self.audio.play_sfx('ui_confirm')
                    self._start_selected_difficulty(2)
                elif event.key == pygame.K_s:
                    self.audio.play_sfx('ui_click')
                    self._open_settings(GameState.DIFFICULTY_SELECT)
                elif event.key == pygame.K_ESCAPE:
                    self.audio.play_sfx('ui_back')
                    self.game_state.set_state(GameState.MODE_SELECT)

            elif self.game_state.is_settings():
                if event.key == pygame.K_ESCAPE:
                    self.audio.play_sfx('ui_back')
                    self._close_settings()
                elif event.key == pygame.K_RETURN:
                    self.audio.play_sfx('ui_confirm')
                    self._close_settings()
                elif event.key == pygame.K_m:
                    self._toggle_setting('music')
                    self.audio.play_sfx('ui_click')
                elif event.key == pygame.K_x:
                    self.audio.play_sfx('ui_click')
                    self._toggle_setting('sfx')
                elif event.key == pygame.K_h:
                    self.audio.play_sfx('ui_click')
                    self._toggle_setting('hints')
                elif event.key == pygame.K_l:
                    self.audio.play_sfx('ui_click')
                    self._cycle_language()
                elif event.key == pygame.K_F1:
                    self.audio.play_sfx('ui_confirm')
                    self._open_manual()

            elif self.game_state.is_manual():
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_F1):
                    self.audio.play_sfx('ui_back')
                    self._close_manual()

            # Gameplay
            elif self.game_state.is_playing():
                if event.key == pygame.K_TAB:
                    self.audio.play_sfx('pause')
                    self.game_state.set_state(GameState.PAUSED)
                elif event.key == pygame.K_r:
                    self.audio.play_sfx('ui_confirm')
                    self._restart_current_mode()
                elif event.key == pygame.K_F10:
                    self.audio.play_sfx('ui_click')
                    self._open_settings(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self._handle_player_input(event, self.player1, self.map1, self.player2, self.map2)
                    self._handle_player_input(event, self.player2, self.map2, self.player1, self.map1)
                    self._play_actor_audio(self.player2)

            # Paused
            elif self.game_state.is_paused():
                if event.key == pygame.K_TAB:
                    self.audio.play_sfx('pause')
                    self.game_state.set_state(GameState.PLAYING)
                elif event.key == pygame.K_r:
                    self.audio.play_sfx('ui_confirm')
                    self._restart_current_mode()
                elif event.key == pygame.K_m:
                    self.audio.play_sfx('ui_back')
                    self._go_to_mode_select()
                elif event.key == pygame.K_F10:
                    self.audio.play_sfx('ui_click')
                    self._open_settings(GameState.PAUSED)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            # Game Over
            elif self.game_state.is_game_over():
                if event.key == pygame.K_r:
                    self.audio.play_sfx('ui_confirm')
                    self._restart_current_mode()
                elif event.key == pygame.K_RETURN:
                    self.audio.play_sfx('ui_confirm')
                    self._go_to_mode_select()
                elif event.key == pygame.K_m:
                    self.audio.play_sfx('ui_back')
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
                'skill': pygame.K_q,
                'skill_freeze': pygame.K_q,
                'skill_blind': pygame.K_e,
                'skill_extra_hint': pygame.K_f,
            }
            self.player1 = Player(
                spawn_col,
                spawn_row,
                player_id=1,
                controls=solo_controls,
                control_hint='WASD or ARROWS / SPACE or ENTER / QEF',
            )
            self.player2 = BotAI(2, spawn_col, spawn_row, difficulty=self._resolve_difficulty(game_mode))
        elif game_mode == GameMode.EVE:
            self.player1 = BotAI(1, spawn_col, spawn_row, difficulty=self.bot_difficulty)
            self.player2 = BotAI(2, spawn_col, spawn_row, difficulty=self.bot_difficulty)
        else:
            raise ValueError(f"Unsupported game mode: {game_mode}")

        self.game_state.reset_round()
        self.game_state.set_state(GameState.PLAYING)

    def _check_victory_conditions(self):
        """Evaluate all end-of-round conditions."""
        if self.player1.found_treasure and self.player2.found_treasure:
            return "Draw", "Both competitors secured the treasure."
        if self.player1.found_treasure:
            return (
                f"{self._get_actor_name(self.player1)} Wins!",
                f"Secured the treasure after collecting all {Map.HINT_CHAIN_LENGTH} keys.",
            )
        if self.player2.found_treasure:
            return (
                f"{self._get_actor_name(self.player2)} Wins!",
                f"Secured the treasure after collecting all {Map.HINT_CHAIN_LENGTH} keys.",
            )

        if self.player1.health <= 0 and self.player2.health <= 0:
            return "Draw", "Both competitors lost all HP."
        if self.player1.health <= 0:
            return (
                f"{self._get_actor_name(self.player2)} Wins!",
                f"{self._get_actor_name(self.player1)} lost all HP.",
            )
        if self.player2.health <= 0:
            return (
                f"{self._get_actor_name(self.player1)} Wins!",
                f"{self._get_actor_name(self.player2)} lost all HP.",
            )

        return None

    def _update_actor(self, actor, actor_map, opponent, opponent_map, dt):
        """Update either a human player or a bot with the right inputs/context."""
        if self._is_human(actor):
            actor.update(dt, actor_map)
            self._poll_pvp_player1_movement(actor, actor_map)
        else:
            actor.update(dt, actor_map, opponent=opponent, opponent_map=opponent_map)

    def _get_clue_text_for_actor(self, actor, game_map):
        """Return clue text, respecting blind status without changing map rules."""
        if not self.settings_values['hints'] and self._is_human(actor):
            return self._ui_text('clue_disabled', "Hints disabled in settings.")
        if getattr(actor, 'is_blinded', False):
            return self._ui_text('clue_blinded', "Clue hidden while blinded.")
        clue_text = game_map.get_clue_text(actor.current_hint_level)
        if self._ui_language() == 'en':
            return clue_text

        if clue_text == "No more hints!":
            return self._ui_text('clue_no_more', clue_text)
        if clue_text == "Cannot compute next clue":
            return self._ui_text('clue_cannot_compute', clue_text)

        unavailable_match = re.fullmatch(r"Hint (\d+) is unavailable\.", clue_text)
        if unavailable_match:
            return self._ui_text('clue_hint_unavailable', clue_text).format(number=unavailable_match.group(1))

        hint_match = re.fullmatch(r"Hint (\d+) is at (X=\d+, Y=\d+)", clue_text)
        if hint_match:
            return self._ui_text('clue_hint_at', clue_text).format(number=hint_match.group(1), coords=hint_match.group(2))

        treasure_match = re.fullmatch(
            r"Treasure is at (X=\d+, Y=\d+)\. You need all (\d+) hints to open it\.",
            clue_text,
        )
        if treasure_match:
            return self._ui_text('clue_treasure_at', clue_text).format(
                coords=treasure_match.group(1),
                count=treasure_match.group(2),
            )

        return clue_text

    def update(self, dt):
        """Update game logic."""
        if not self.game_state.is_playing():
            return

        time_expired = self.game_state.update_timer(dt)
        if time_expired:
            self._end_game("Draw", "Timer expired before anyone won.")
            return

        self.map1.update(dt)
        self.map2.update(dt)
        self._update_actor(self.player1, self.map1, self.player2, self.map2, dt)
        self._update_actor(self.player2, self.map2, self.player1, self.map1, dt)
        self._play_actor_audio(self.player1)
        self._play_actor_audio(self.player2)

        winner_info = self._check_victory_conditions()
        if winner_info:
            self._end_game(*winner_info)

    def _end_game(self, winner, reason):
        """End the current game."""
        self.game_state.winner = winner
        self.game_state.message = reason
        self.game_state.set_state(GameState.GAME_OVER)
        self._play_result_sound(winner)

    def _localized_winner_text(self, winner):
        """Localize the winner title shown on the end screen."""
        if winner == "Draw":
            return self._ui_text('draw_title', winner)

        if self.player1 and winner.startswith(self._get_actor_name(self.player1)):
            return f"{self._localized_actor_name(self.player1)} {self._ui_text('winner_suffix', 'Wins!')}"
        if self.player2 and winner.startswith(self._get_actor_name(self.player2)):
            return f"{self._localized_actor_name(self.player2)} {self._ui_text('winner_suffix', 'Wins!')}"
        return winner

    def _localized_reason_text(self, reason):
        """Localize the end-of-round reason shown on the end screen."""
        if self._ui_language() == 'en':
            return reason

        if reason == "Both competitors secured the treasure.":
            return self._ui_text('end_reason_both_treasure', reason)
        if reason == "Both competitors lost all HP.":
            return self._ui_text('end_reason_both_hp', reason)
        if reason == "Timer expired before anyone won.":
            return self._ui_text('end_reason_timer', reason)

        treasure_match = re.fullmatch(r"Secured the treasure after collecting all (\d+) keys\.", reason)
        if treasure_match:
            return self._ui_text('end_reason_treasure', reason).format(count=treasure_match.group(1))

        lost_hp_match = re.fullmatch(r"(.+) lost all HP\.", reason)
        if lost_hp_match:
            actor_name = lost_hp_match.group(1)
            if self.player1 and actor_name == self._get_actor_name(self.player1):
                actor_name = self._localized_actor_name(self.player1)
            elif self.player2 and actor_name == self._get_actor_name(self.player2):
                actor_name = self._localized_actor_name(self.player2)
            return self._ui_text('end_reason_lost_hp', reason).format(actor=actor_name)

        return reason

    def _render_match(self):
        """Render gameplay views for the active game mode."""
        split_screen = self._is_split_screen_mode()
        language = self._ui_language()
        actions = {}
        self.ui.render_gameplay_background(self.screen, split_screen=split_screen)

        if split_screen:
            half_width = SCREEN_WIDTH // 2
            map_rect1 = pygame.Rect(0, HUD_HEIGHT, half_width, MAP_HEIGHT)
            map_rect2 = pygame.Rect(half_width, HUD_HEIGHT, half_width, MAP_HEIGHT)

            self.map1.render(self.screen, x_offset=0, y_offset=HUD_HEIGHT)
            self.player1.render(self.screen, x_offset=0, y_offset=HUD_HEIGHT)
            self.map2.render(self.screen, x_offset=half_width, y_offset=HUD_HEIGHT)
            self.player2.render(self.screen, x_offset=half_width, y_offset=HUD_HEIGHT)
            self.ui.render_playfield_frame(self.screen, map_rect1, None, self.player1.color)
            self.ui.render_playfield_frame(self.screen, map_rect2, None, self.player2.color)
            self.ui.render_blind_overlay(self.screen, map_rect1, self.player1, language=language)
            self.ui.render_blind_overlay(self.screen, map_rect2, self.player2, language=language)
            pygame.draw.line(self.screen, WHITE, (half_width, HUD_HEIGHT), (half_width, SCREEN_HEIGHT), 2)

            clue_box_height = CLUE_BOX_HEIGHT
            clue_y = HUD_HEIGHT + MAP_HEIGHT
            self.ui.render_clue_box(
                self.screen,
                self._get_clue_text_for_actor(self.player1, self.map1),
                rect=pygame.Rect(0, clue_y, half_width, clue_box_height),
                label=self.ui.get_actor_label(self.player1, language=language),
                language=language,
            )
            self.ui.render_clue_box(
                self.screen,
                self._get_clue_text_for_actor(self.player2, self.map2),
                rect=pygame.Rect(half_width, clue_y, half_width, clue_box_height),
                label=self.ui.get_actor_label(self.player2, language=language),
                language=language,
            )
        else:
            map_rect = pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH, MAP_HEIGHT)
            self.map1.render(self.screen, y_offset=HUD_HEIGHT)
            self.player1.render(self.screen, y_offset=HUD_HEIGHT)
            self.ui.render_playfield_frame(self.screen, map_rect, None, self.player1.color)
            self.ui.render_blind_overlay(self.screen, map_rect, self.player1, language=language)
            self.ui.render_clue_box(
                self.screen,
                self._get_clue_text_for_actor(self.player1, self.map1),
                language=language,
            )

        actions.update(
            self.ui.render_game_hud(
                self.screen,
                self.player1,
                self.player2,
                self.game_state.round_time_remaining,
                language=language,
            )
        )

        if self.game_state.is_paused():
            actions.update(self.ui.render_pause_overlay(self.screen, language=self._ui_language()))
        return actions

    def render(self):
        """Render the current frame."""
        self.screen.fill(BLACK)
        self._sync_music()
        actions = {}

        if self.game_state.is_menu():
            actions = self.ui.render_main_menu(self.screen, language=self._ui_language())
        elif self.game_state.is_mode_select():
            actions = self.ui.render_mode_select(self.screen, self.selected_mode, language=self._ui_language())
        elif self.game_state.is_difficulty_select():
            actions = self.ui.render_difficulty_select(
                self.screen,
                self.selected_mode_family,
                self._difficulty_labels(),
                self.selected_difficulty,
                language=self._ui_language(),
            )
        elif self.game_state.is_settings():
            return_label = self._ui_text('return_to_match') if self.settings_return_state in (GameState.PLAYING, GameState.PAUSED) else self._ui_text('back')
            actions = self.ui.render_settings_menu(self.screen, self.settings_values, return_label=return_label, language=self._ui_language())
        elif self.game_state.is_manual():
            actions = self.ui.render_manual_screen(self.screen, language=self._ui_language())
        elif self.game_state.is_playing() or self.game_state.is_paused():
            actions = self._render_match()
        elif self.game_state.is_game_over():
            actions = self.ui.render_game_over(
                self.screen,
                self._localized_winner_text(self.game_state.winner),
                self._localized_reason_text(self.game_state.message),
                mode_label=self._localized_mode_label(),
                language=self._ui_language(),
            )

        self.ui_actions = actions
        self._present_frame()

    def run(self):
        """Main game loop."""
        self.render()
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
