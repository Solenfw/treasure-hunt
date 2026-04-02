"""UI management for HUD, menu, and text rendering."""

import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, YELLOW, BLACK, GRAY
from src.game_mode import GameMode


class UIManager:
    """Manages all UI rendering including menus, HUD, and text."""
    
    def __init__(self):
        self.font_large = pygame.font.SysFont('Arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)
        self.font_tiny = pygame.font.SysFont('Arial', 16)
        self.clock_font = pygame.font.SysFont('monospace', 48, bold=True)
    
    def render_main_menu(self, surface):
        """Render main menu screen."""
        surface.fill(BLACK)
        
        # Title
        title_text = self.font_large.render('🏴‍☠️ TREASURE HUNT 🏴‍☠️', True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_small.render('Truy Tìm Kho Báu', True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Menu options
        options = [
            "PRESS ENTER TO START",
            "P - Settings",
            "ESC - Exit"
        ]
        
        y_offset = SCREEN_HEIGHT // 2
        for i, option in enumerate(options):
            option_text = self.font_small.render(option, True, WHITE if i == 0 else GRAY)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 50))
            surface.blit(option_text, option_rect)
    
    def render_mode_select(self, surface, selected_mode=0):
        """Render game mode selection screen."""
        surface.fill(BLACK)
        
        title_text = self.font_large.render('SELECT GAME MODE', True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_text, title_rect)
        
        modes = [
            "1 - PvP (2 Players)",
            "2 - PvE Easy (vs AI)",
            "3 - PvE Normal (vs AI)",
            "4 - PvE Hard (vs AI)",
            "5 - EvE (Watch AI)"
        ]
        
        y_offset = SCREEN_HEIGHT // 2 - 80
        for i, mode in enumerate(modes):
            color = YELLOW if i == selected_mode else WHITE
            mode_text = self.font_small.render(mode, True, color)
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 40))
            surface.blit(mode_text, mode_rect)
    
    def render_game_hud(self, surface, player, opponent=None, round_time=120.0):
        """Render heads-up display during gameplay."""
        # Timer (top center)
        minutes = int(round_time) // 60
        seconds = int(round_time) % 60
        time_text = self.clock_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        surface.blit(time_text, time_rect)
        
        # Player 1 info (left side)
        self._draw_player_status(surface, player, 20, 20, True)
        
        # Opponent info (right side) if multiplayer
        if opponent:
            self._draw_player_status(surface, opponent, SCREEN_WIDTH - 200, 20, False)
    
    def _draw_player_status(self, surface, player, x, y, is_left=True):
        """Draw individual player status panel."""
        panel_width = 180
        panel_height = 120
        
        # Background panel
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(surface, (50, 50, 50), panel_rect)
        pygame.draw.rect(surface, WHITE, panel_rect, 2)
        
        # Player name/ID
        name_text = self.font_small.render(f"Player {player.player_id}", True, player.color)
        surface.blit(name_text, (x + 10, y + 10))
        
        # Health (hearts)
        hearts_text = self.font_small.render(f"❤️ {player.health}", True, RED)
        surface.blit(hearts_text, (x + 10, y + 35))
        
        # Hint level
        hint_text = self.font_small.render(f"Hint: {max(0, player.current_hint_level + 1)}", True, GREEN)
        surface.blit(hint_text, (x + 10, y + 60))
        
        # Dig cooldown indicator
        if player.dig_cooldown > 0:
            cooldown_text = self.font_tiny.render(f"Cooldown: {player.dig_cooldown:.1f}s", True, YELLOW)
            surface.blit(cooldown_text, (x + 10, y + 85))
    
    def render_clue_box(self, surface, clue_text):
        """Render the hint/clue display box at bottom."""
        box_height = 80
        box_rect = pygame.Rect(0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height)
        
        # Background
        pygame.draw.rect(surface, (30, 30, 30), box_rect)
        pygame.draw.rect(surface, YELLOW, box_rect, 3)
        
        # Label
        label_text = self.font_small.render("📋 CLUE:", True, YELLOW)
        surface.blit(label_text, (20, SCREEN_HEIGHT - 70))
        
        # Clue text (wrapped)
        clue = self.font_small.render(clue_text[:60], True, WHITE)
        surface.blit(clue, (20, SCREEN_HEIGHT - 40))
        
        if len(clue_text) > 60:
            clue_continue = self.font_tiny.render(clue_text[60:], True, WHITE)
            surface.blit(clue_continue, (20, SCREEN_HEIGHT - 20))
    
    def render_progress_bar(self, surface, player1, player2):
        """Render progress comparison bars for multiplayer."""
        bar_width = 300
        bar_height = 30
        gap = 40
        
        total_width = bar_width * 2 + gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = 20
        
        # Player 1 progress
        p1_progress = (player1.current_hint_level + 1) / 5  # 5 hints total
        p1_rect = pygame.Rect(start_x, y, bar_width * p1_progress, bar_height)
        pygame.draw.rect(surface, GREEN, p1_rect)
        pygame.draw.rect(surface, WHITE, pygame.Rect(start_x, y, bar_width, bar_height), 2)
        
        # Player 2 progress
        p2_progress = (player2.current_hint_level + 1) / 5
        p2_rect = pygame.Rect(start_x + bar_width + gap, y, bar_width * p2_progress, bar_height)
        pygame.draw.rect(surface, (100, 149, 237), p2_rect)
        pygame.draw.rect(surface, WHITE, pygame.Rect(start_x + bar_width + gap, y, bar_width, bar_height), 2)
    
    def render_game_over(self, surface, winner, reason=""):
        """Render game over screen."""
        surface.fill(BLACK)
        
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Game Over text
        gameover_text = self.font_large.render('GAME OVER', True, RED)
        gameover_rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(gameover_text, gameover_rect)
        
        # Winner text
        winner_text = self.font_medium.render(f'🏆 {winner} 🏆', True, YELLOW)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(winner_text, winner_rect)
        
        # Reason
        if reason:
            reason_text = self.font_small.render(reason, True, WHITE)
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            surface.blit(reason_text, reason_rect)
        
        # Continue instruction
        continue_text = self.font_small.render('Press ENTER to continue...', True, GRAY)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        surface.blit(continue_text, continue_rect)
    
    def render_pause_overlay(self, surface):
        """Render pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render('⏸ PAUSED ⏸', True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(pause_text, pause_rect)
        
        # Resume instruction
        resume_text = self.font_small.render('Press P to Resume', True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        surface.blit(resume_text, resume_rect)
    
    def render_skill_bar(self, surface, player, x=10, y=100):
        """Render player's skill cooldown indicators."""
        skills_text = self.font_tiny.render("SKILLS:", True, WHITE)
        surface.blit(skills_text, (x, y))
        
        skill_y = y + 25
        for skill_name, skill_data in player.skills.items():
            cooldown = skill_data['cooldown']
            status = f"{skill_name.upper()}"
            
            if cooldown > 0:
                status += f" ({cooldown:.1f}s)"
                color = RED
            else:
                status += " [Ready]"
                color = GREEN
            
            skill_text = self.font_tiny.render(status, True, color)
            surface.blit(skill_text, (x, skill_y))
            skill_y += 20
