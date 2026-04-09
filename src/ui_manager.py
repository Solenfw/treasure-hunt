"""UI management for HUD, menu, and text rendering."""

import pygame

from src.map import Map
from src.settings import CLUE_BOX_HEIGHT, HUD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, YELLOW, BLACK, GRAY


class UIManager:
    """Manages all UI rendering including menus, HUD, and text."""

    def __init__(self):
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.font_tiny = pygame.font.SysFont('Arial', 16)
        self.clock_font = pygame.font.SysFont('monospace', 48, bold=True)
        self.font_micro = pygame.font.SysFont('Arial', 14, bold=True)

    def _get_player_label(self, player):
        """Return a friendly label for any human or bot competitor."""
        return getattr(player, 'display_name', f"Player {player.player_id}")

    def _wrap_text(self, text, font, max_width):
        """Wrap text to the available width using simple word boundaries."""
        words = text.split()
        if not words:
            return [text]

        lines = []
        current_line = words[0]

        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def _draw_heart_icon(self, surface, x, y, filled=True):
        """Draw a small heart indicator."""
        color = RED if filled else (95, 50, 50)
        points = [
            (x + 6, y + 3),
            (x + 10, y),
            (x + 14, y + 3),
            (x + 14, y + 8),
            (x + 10, y + 13),
            (x + 6, y + 8),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.circle(surface, color, (x + 7, y + 4), 4)
        pygame.draw.circle(surface, color, (x + 13, y + 4), 4)

    def _draw_key_chip(self, surface, x, y, keys_found):
        """Draw a compact progress badge for collected keys."""
        chip_rect = pygame.Rect(x, y, 70, 22)
        pygame.draw.rect(surface, (58, 52, 22), chip_rect, border_radius=11)
        pygame.draw.rect(surface, YELLOW, chip_rect, 1, border_radius=11)
        key_label = self.font_micro.render(f"KEY {keys_found}/{Map.HINT_CHAIN_LENGTH}", True, YELLOW)
        key_rect = key_label.get_rect(center=chip_rect.center)
        surface.blit(key_label, key_rect)

    def render_main_menu(self, surface):
        """Render main menu screen."""
        surface.fill(BLACK)

        title_text = self.font_large.render('TREASURE HUNT', True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        surface.blit(title_text, title_rect)

        subtitle_text = self.font_small.render('Truy Tim Kho Bau', True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(subtitle_text, subtitle_rect)

        options = [
            'PRESS ENTER TO START',
            'ESC - EXIT',
        ]

        y_offset = SCREEN_HEIGHT // 2
        for index, option in enumerate(options):
            option_text = self.font_small.render(option, True, WHITE if index == 0 else GRAY)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + index * 50))
            surface.blit(option_text, option_rect)

    def render_mode_select(self, surface, selected_mode=0):
        """Render game mode selection screen."""
        surface.fill(BLACK)

        title_text = self.font_large.render('SELECT GAME MODE', True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_text, title_rect)

        modes = [
            '1 - PvP (2 Players)',
            '2 - PvE Easy (vs AI)',
            '3 - PvE Normal (vs AI)',
            '4 - PvE Hard (vs AI)',
            '5 - EvE (Watch AI)',
        ]

        y_offset = SCREEN_HEIGHT // 2 - 80
        for index, mode in enumerate(modes):
            color = YELLOW if index == selected_mode else WHITE
            mode_text = self.font_small.render(mode, True, color)
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + index * 40))
            surface.blit(mode_text, mode_rect)

        help_text = self.font_tiny.render('Use 1-5, numpad 1-5, or Up/Down + Enter', True, GRAY)
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        surface.blit(help_text, help_rect)

    def render_game_hud(self, surface, player, opponent=None, round_time=120.0):
        """Render heads-up display during gameplay."""
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, (14, 14, 16), hud_rect)
        accent_rect = pygame.Rect(0, HUD_HEIGHT - 14, SCREEN_WIDTH, 14)
        pygame.draw.rect(surface, (30, 24, 10), accent_rect)
        pygame.draw.line(surface, YELLOW, (0, HUD_HEIGHT - 2), (SCREEN_WIDTH, HUD_HEIGHT - 2), 2)

        minutes = int(round_time) // 60
        seconds = int(round_time) % 60
        timer_box = pygame.Rect((SCREEN_WIDTH // 2) - 95, 12, 190, 60)
        pygame.draw.rect(surface, (36, 30, 18), timer_box, border_radius=16)
        pygame.draw.rect(surface, YELLOW, timer_box, 2, border_radius=16)
        time_text = self.clock_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=timer_box.center)
        surface.blit(time_text, time_rect)

        self._draw_player_status(surface, player, 20, 14)
        if opponent:
            self._draw_player_status(surface, opponent, SCREEN_WIDTH - 240, 14)

    def _draw_player_status(self, surface, player, x, y):
        """Draw individual player status panel."""
        panel_width = 240
        panel_height = 56

        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(surface, (36, 36, 40), panel_rect, border_radius=14)
        pygame.draw.rect(surface, player.color, panel_rect, 2, border_radius=14)

        name_text = self.font_small.render(self._get_player_label(player), True, player.color)
        surface.blit(name_text, (x + 12, y + 8))

        for heart_index in range(2):
            self._draw_heart_icon(surface, x + 14 + heart_index * 20, y + 33, heart_index < player.health)

        hints_found = max(0, player.current_hint_level + 1)
        if getattr(player, 'found_treasure', False):
            treasure_text = self.font_micro.render("TREASURE", True, YELLOW)
            treasure_rect = treasure_text.get_rect(midleft=(x + 60, y + 42))
            surface.blit(treasure_text, treasure_rect)
        else:
            self._draw_key_chip(surface, x + 60, y + 31, hints_found)

        if player.dig_cooldown > 0:
            cooldown_text = self.font_tiny.render(f"Recovering {player.dig_cooldown:.1f}s", True, YELLOW)
            cooldown_rect = cooldown_text.get_rect(topright=(x + panel_width - 12, y + 34))
            surface.blit(cooldown_text, cooldown_rect)

    def render_clue_box(self, surface, clue_text, rect=None, label="CLUE", player=None):
        """Render the hint/clue display box."""
        if rect is None:
            box_height = CLUE_BOX_HEIGHT
            box_rect = pygame.Rect(0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height)
        else:
            box_rect = rect

        pygame.draw.rect(surface, (24, 24, 26), box_rect)
        pygame.draw.rect(surface, YELLOW, box_rect, 3)

        header_rect = pygame.Rect(box_rect.x, box_rect.y, box_rect.width, 32)
        pygame.draw.rect(surface, (42, 34, 14), header_rect)

        label_text = self.font_small.render(f"{label}:", True, YELLOW)
        surface.blit(label_text, (box_rect.x + 18, box_rect.y + 6))

        text_y = box_rect.y + 44

        max_width = box_rect.width - 40
        lines = self._wrap_text(clue_text, self.font_tiny, max_width)
        for index, line in enumerate(lines[:2]):
            clue = self.font_tiny.render(line, True, WHITE)
            surface.blit(clue, (box_rect.x + 20, text_y + index * 18))

    def render_progress_bar(self, surface, player1, player2):
        """Render progress comparison bars for multiplayer."""
        bar_width = 300
        bar_height = 30
        gap = 40

        total_width = bar_width * 2 + gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = 20

        max_hints = max(1, Map.HINT_CHAIN_LENGTH)
        p1_progress = min(1.0, max(0.0, (player1.current_hint_level + 1) / max_hints))
        p1_rect = pygame.Rect(start_x, y, bar_width * p1_progress, bar_height)
        pygame.draw.rect(surface, GREEN, p1_rect)
        pygame.draw.rect(surface, WHITE, pygame.Rect(start_x, y, bar_width, bar_height), 2)

        p2_progress = min(1.0, max(0.0, (player2.current_hint_level + 1) / max_hints))
        p2_rect = pygame.Rect(start_x + bar_width + gap, y, bar_width * p2_progress, bar_height)
        pygame.draw.rect(surface, (100, 149, 237), p2_rect)
        pygame.draw.rect(surface, WHITE, pygame.Rect(start_x + bar_width + gap, y, bar_width, bar_height), 2)

    def render_game_over(self, surface, winner, reason=""):
        """Render game over screen."""
        surface.fill(BLACK)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        gameover_text = self.font_large.render('GAME OVER', True, RED)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(gameover_text, gameover_rect)

        winner_text = self.font_medium.render(winner, True, YELLOW)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(winner_text, winner_rect)

        if reason:
            reason_text = self.font_small.render(reason, True, WHITE)
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            surface.blit(reason_text, reason_rect)

        continue_text = self.font_small.render('Press ENTER to continue...', True, GRAY)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        surface.blit(continue_text, continue_rect)

    def render_pause_overlay(self, surface):
        """Render pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        pause_text = self.font_large.render('PAUSED', True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(pause_text, pause_rect)

        resume_text = self.font_small.render('Press P to Resume', True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        surface.blit(resume_text, resume_rect)

    def render_skill_bar(self, surface, player, x=10, y=100):
        """Render player's skill cooldown indicators."""
        skills_text = self.font_tiny.render('SKILLS:', True, WHITE)
        surface.blit(skills_text, (x, y))

        skill_y = y + 25
        for skill_name, skill_data in player.skills.items():
            cooldown = skill_data['cooldown']
            status = skill_name.upper()

            if cooldown > 0:
                status += f" ({cooldown:.1f}s)"
                color = RED
            else:
                status += ' [Ready]'
                color = GREEN

            skill_text = self.font_tiny.render(status, True, color)
            surface.blit(skill_text, (x, skill_y))
            skill_y += 20
