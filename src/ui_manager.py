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
        self.font_icon = pygame.font.SysFont('Segoe UI Symbol', 22, bold=True)
        self._background_cache = {}

    def _interpolate_color(self, start, end, progress):
        """Blend two RGB colors."""
        return tuple(
            int(start[index] + (end[index] - start[index]) * progress)
            for index in range(3)
        )

    def _draw_screen_background(self, surface, variant='menu'):
        """Draw a full-screen themed background so the menus do not sit on pure black."""
        size = surface.get_size()
        cache_key = (size, variant)
        if cache_key not in self._background_cache:
            self._background_cache[cache_key] = self._build_background_surface(size, variant)
        surface.blit(self._background_cache[cache_key], (0, 0))

    def _build_background_surface(self, size, variant):
        """Build one cached background surface."""
        width, height = size
        bg = pygame.Surface(size)

        top_color = (34, 20, 11)
        middle_color = (71, 42, 18)
        bottom_color = (96, 57, 23)
        if variant == 'result':
            top_color = (27, 18, 12)
            middle_color = (82, 47, 24)
            bottom_color = (108, 61, 24)
        elif variant == 'settings':
            top_color = (28, 22, 16)
            middle_color = (66, 44, 26)
            bottom_color = (88, 60, 32)

        for y in range(height):
            progress = y / max(1, height - 1)
            if progress < 0.55:
                color = self._interpolate_color(top_color, middle_color, progress / 0.55)
            else:
                color = self._interpolate_color(middle_color, bottom_color, (progress - 0.55) / 0.45)
            pygame.draw.line(bg, color, (0, y), (width, y))

        self._draw_background_pattern(bg)
        self._draw_background_dunes(bg)
        self._draw_background_map_marks(bg, variant)
        self._draw_background_frame(bg)
        return bg

    def _draw_background_pattern(self, surface):
        """Add a faint diagonal treasure-map texture."""
        width, height = surface.get_size()
        pattern = pygame.Surface((width, height), pygame.SRCALPHA)

        for offset in range(-height, width, 28):
            pygame.draw.line(pattern, (255, 226, 158, 14), (offset, 0), (offset + height, height), 2)

        for offset in range(0, width, 120):
            pygame.draw.line(pattern, (255, 240, 200, 8), (offset, 0), (offset, height), 1)

        surface.blit(pattern, (0, 0))

    def _draw_background_dunes(self, surface):
        """Layer large silhouettes near the bottom edge to reduce empty space."""
        width, height = surface.get_size()
        far_layer = [
            (0, height),
            (0, height - 128),
            (150, height - 152),
            (280, height - 122),
            (420, height - 160),
            (580, height - 118),
            (760, height - 166),
            (940, height - 126),
            (1110, height - 150),
            (width, height - 112),
            (width, height),
        ]
        mid_layer = [
            (0, height),
            (0, height - 72),
            (180, height - 96),
            (350, height - 54),
            (520, height - 118),
            (720, height - 64),
            (910, height - 106),
            (1090, height - 72),
            (width, height - 90),
            (width, height),
        ]
        front_layer = [
            (0, height),
            (0, height - 26),
            (240, height - 42),
            (490, height - 18),
            (740, height - 36),
            (1000, height - 12),
            (width, height - 28),
            (width, height),
        ]

        pygame.draw.polygon(surface, (58, 34, 18), far_layer)
        pygame.draw.polygon(surface, (84, 49, 24), mid_layer)
        pygame.draw.polygon(surface, (111, 66, 30), front_layer)

    def _draw_background_map_marks(self, surface, variant):
        """Draw compass/path details around the card area."""
        width, height = surface.get_size()
        marks = pygame.Surface((width, height), pygame.SRCALPHA)

        self._draw_compass_rose(marks, (138, 170), 72, alpha=90)
        self._draw_compass_rose(marks, (width - 152, height - 140), 58, alpha=80)

        path_points = [
            (92, height - 164),
            (180, height - 244),
            (278, height - 214),
            (390, height - 286),
            (width - 360, 190),
            (width - 214, 168),
        ]
        if variant == 'settings':
            path_points = [
                (88, height - 184),
                (198, height - 250),
                (322, height - 228),
                (width - 310, 248),
                (width - 208, 184),
            ]
        self._draw_dashed_path(marks, path_points, color=(250, 225, 165, 84))

        for point in ((110, height - 120), (width - 216, 116), (width - 122, 228)):
            self._draw_x_mark(marks, point, 13, (255, 233, 179, 85))

        chest_rect = pygame.Rect(width - 214, height - 190, 88, 58)
        self._draw_chest_silhouette(marks, chest_rect)
        self._draw_palm_silhouette(marks, (116, height - 122), scale=0.9)

        surface.blit(marks, (0, 0))

    def _draw_background_frame(self, surface):
        """Draw a subtle frame around the whole screen."""
        width, height = surface.get_size()
        frame_rect = pygame.Rect(14, 14, width - 28, height - 28)
        pygame.draw.rect(surface, (143, 103, 44), frame_rect, 2, border_radius=22)
        inner_rect = frame_rect.inflate(-18, -18)
        pygame.draw.rect(surface, (92, 61, 29), inner_rect, 1, border_radius=20)

        for corner in (
            frame_rect.topleft,
            frame_rect.topright,
            frame_rect.bottomleft,
            frame_rect.bottomright,
        ):
            pygame.draw.circle(surface, (190, 145, 58), corner, 9, 2)

    def _draw_compass_rose(self, surface, center, radius, alpha=90):
        """Draw a low-contrast compass decoration."""
        color = (240, 211, 142, alpha)
        outer = [
            (center[0], center[1] - radius),
            (center[0] + radius * 0.22, center[1] - radius * 0.22),
            (center[0] + radius, center[1]),
            (center[0] + radius * 0.22, center[1] + radius * 0.22),
            (center[0], center[1] + radius),
            (center[0] - radius * 0.22, center[1] + radius * 0.22),
            (center[0] - radius, center[1]),
            (center[0] - radius * 0.22, center[1] - radius * 0.22),
        ]
        pygame.draw.polygon(surface, color, outer, 2)
        pygame.draw.circle(surface, color, center, int(radius * 0.44), 2)
        pygame.draw.line(surface, color, (center[0], center[1] - radius), (center[0], center[1] + radius), 2)
        pygame.draw.line(surface, color, (center[0] - radius, center[1]), (center[0] + radius, center[1]), 2)

    def _draw_dashed_path(self, surface, points, color):
        """Draw a treasure-map style dashed route."""
        for start, end in zip(points, points[1:]):
            self._draw_dashed_line(surface, start, end, color)

    def _draw_dashed_line(self, surface, start, end, color, dash_length=10, gap=7):
        """Draw a dashed line between two points."""
        vector = pygame.Vector2(end[0] - start[0], end[1] - start[1])
        distance = vector.length()
        if distance == 0:
            return

        direction = vector.normalize()
        progress = 0.0
        while progress < distance:
            seg_start = pygame.Vector2(start) + direction * progress
            seg_end = pygame.Vector2(start) + direction * min(progress + dash_length, distance)
            pygame.draw.line(surface, color, seg_start, seg_end, 2)
            progress += dash_length + gap

    def _draw_x_mark(self, surface, center, size, color):
        """Draw a small X mark."""
        pygame.draw.line(surface, color, (center[0] - size, center[1] - size), (center[0] + size, center[1] + size), 3)
        pygame.draw.line(surface, color, (center[0] - size, center[1] + size), (center[0] + size, center[1] - size), 3)

    def _draw_chest_silhouette(self, surface, rect):
        """Draw a treasure chest silhouette near the screen edge."""
        fill = (34, 20, 10, 115)
        edge = (232, 202, 133, 70)
        lid_rect = pygame.Rect(rect.x + 8, rect.y, rect.width - 16, rect.height // 2)
        body_rect = pygame.Rect(rect.x, rect.y + rect.height // 3, rect.width, rect.height - rect.height // 3)
        pygame.draw.rect(surface, fill, body_rect, border_radius=10)
        pygame.draw.rect(surface, fill, lid_rect, border_radius=12)
        pygame.draw.rect(surface, edge, body_rect, 2, border_radius=10)
        pygame.draw.rect(surface, edge, lid_rect, 2, border_radius=12)
        lock_rect = pygame.Rect(rect.centerx - 7, rect.y + rect.height // 2 - 4, 14, 18)
        pygame.draw.rect(surface, edge, lock_rect, 2, border_radius=4)

    def _draw_palm_silhouette(self, surface, origin, scale=1.0):
        """Draw a small palm silhouette to make the edges feel intentional."""
        trunk_color = (34, 20, 10, 105)
        leaf_color = (245, 215, 145, 54)
        base_x, base_y = origin
        pygame.draw.line(surface, trunk_color, (base_x, base_y), (base_x + 12 * scale, base_y - 72 * scale), max(2, int(5 * scale)))
        leaf_center = (int(base_x + 12 * scale), int(base_y - 72 * scale))
        leaf_offsets = [(-42, -4), (-22, -24), (0, -30), (22, -20), (38, -2)]
        for dx, dy in leaf_offsets:
            pygame.draw.line(
                surface,
                leaf_color,
                leaf_center,
                (int(leaf_center[0] + dx * scale), int(leaf_center[1] + dy * scale)),
                max(2, int(3 * scale)),
            )

    def _card_rect(self, width=460, height=620):
        """Return the main centered menu card rectangle."""
        rect = pygame.Rect(0, 0, min(width, SCREEN_WIDTH - 40), min(height, SCREEN_HEIGHT - 40))
        rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        return rect

    def _draw_card(self, surface, rect):
        """Draw a themed menu card inspired by the provided HTML/CSS mockups."""
        shadow_rect = rect.move(0, 10)
        pygame.draw.rect(surface, (12, 8, 6), shadow_rect, border_radius=28)
        pygame.draw.rect(surface, (58, 35, 17), rect, border_radius=28)
        pygame.draw.rect(surface, (195, 145, 58), rect, 3, border_radius=28)

        corner_radius = 52
        pygame.draw.circle(surface, (96, 66, 30), rect.topleft, corner_radius, 2)
        pygame.draw.circle(surface, (96, 66, 30), rect.bottomright, corner_radius, 2)

    def _draw_header(self, surface, rect, eyebrow, title, subtitle=''):
        """Draw the menu header block."""
        eyebrow_text = self.font_micro.render(eyebrow.upper(), True, YELLOW)
        eyebrow_rect = eyebrow_text.get_rect(center=(rect.centerx, rect.y + 42))
        surface.blit(eyebrow_text, eyebrow_rect)

        title_font = self.font_large if len(title) <= 16 else self.font_medium
        title_text = title_font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(rect.centerx, rect.y + 86))
        surface.blit(title_text, title_rect)

        if subtitle:
            lines = self._wrap_text(subtitle, self.font_tiny, rect.width - 70)
            for index, line in enumerate(lines[:3]):
                subtitle_text = self.font_tiny.render(line, True, (244, 231, 188))
                subtitle_rect = subtitle_text.get_rect(center=(rect.centerx, rect.y + 128 + index * 18))
                surface.blit(subtitle_text, subtitle_rect)

    def _draw_button(self, surface, rect, label, variant='default', small=False, selected=False):
        """Draw a rounded menu button and return its rect."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        if variant == 'primary':
            fill = (228, 182, 74)
            text_color = (41, 24, 11)
        elif variant == 'secondary':
            fill = (72, 44, 21)
            text_color = WHITE
        else:
            fill = (112, 68, 31)
            text_color = WHITE

        border_color = (255, 215, 120) if hovered or selected else (190, 145, 58)
        pygame.draw.rect(surface, fill, rect, border_radius=18)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=18)

        font = self.font_tiny if small else self.font_small
        label_text = font.render(label, True, text_color)
        label_rect = label_text.get_rect(center=rect.center)
        surface.blit(label_text, label_rect)
        return rect

    def _draw_icon_button(self, surface, rect, label):
        """Draw a compact footer icon/button."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        fill = (76, 50, 26) if hovered else (52, 33, 18)
        pygame.draw.rect(surface, fill, rect, border_radius=14)
        pygame.draw.rect(surface, (204, 164, 75), rect, 2, border_radius=14)
        text = self.font_tiny.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        return rect

    def _draw_pill(self, surface, rect, label):
        """Draw a footer pill."""
        pygame.draw.rect(surface, (66, 49, 24), rect, border_radius=18)
        pygame.draw.rect(surface, (160, 133, 74), rect, 1, border_radius=18)
        text = self.font_micro.render(label, True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    def _draw_switch_row(self, surface, rect, label, enabled):
        """Draw one settings row with a toggle-like control."""
        pygame.draw.rect(surface, (63, 41, 22), rect, border_radius=16)
        pygame.draw.rect(surface, (164, 129, 63), rect, 1, border_radius=16)

        label_text = self.font_small.render(label, True, WHITE)
        label_rect = label_text.get_rect(midleft=(rect.x + 18, rect.centery))
        surface.blit(label_text, label_rect)

        switch_rect = pygame.Rect(rect.right - 88, rect.centery - 16, 64, 32)
        switch_fill = (226, 180, 74) if enabled else (92, 60, 31)
        pygame.draw.rect(surface, switch_fill, switch_rect, border_radius=16)
        pygame.draw.rect(surface, (210, 173, 92), switch_rect, 1, border_radius=16)

        knob_x = switch_rect.right - 16 if enabled else switch_rect.left + 16
        pygame.draw.circle(surface, WHITE, (knob_x, switch_rect.centery), 12)
        return rect

    def render_gameplay_background(self, surface, split_screen=False):
        """Render the in-match background so gameplay shares the same theme as the menus."""
        self._draw_screen_background(surface, variant='play')

        width, height = surface.get_size()
        top_glow = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(top_glow, (255, 215, 150, 28), pygame.Rect(width // 2 - 250, -120, 500, 220))
        pygame.draw.ellipse(top_glow, (255, 210, 120, 18), pygame.Rect(-120, height - 210, 380, 180))
        pygame.draw.ellipse(top_glow, (255, 210, 120, 18), pygame.Rect(width - 260, height - 200, 360, 170))
        surface.blit(top_glow, (0, 0))

        band_rect = pygame.Rect(0, HUD_HEIGHT - 6, width, height - HUD_HEIGHT - CLUE_BOX_HEIGHT + 12)
        pygame.draw.rect(surface, (40, 25, 14), band_rect, border_radius=18)
        pygame.draw.rect(surface, (133, 98, 42), band_rect, 2, border_radius=18)

        if split_screen:
            divider_rect = pygame.Rect(width // 2 - 10, HUD_HEIGHT + 8, 20, height - HUD_HEIGHT - CLUE_BOX_HEIGHT - 16)
            pygame.draw.rect(surface, (57, 35, 20), divider_rect, border_radius=10)
            pygame.draw.rect(surface, (169, 129, 62), divider_rect, 2, border_radius=10)

    def render_playfield_frame(self, surface, rect, label, accent_color):
        """Draw a decorative frame around a map area."""
        border_rect = rect.inflate(8, 8)
        shadow_rect = border_rect.move(0, 6)
        pygame.draw.rect(surface, (14, 9, 6), shadow_rect, 4, border_radius=18)
        pygame.draw.rect(surface, (68, 42, 22), border_rect, 6, border_radius=18)
        pygame.draw.rect(surface, (194, 147, 66), border_rect, 2, border_radius=18)
        pygame.draw.rect(surface, accent_color, rect, 2, border_radius=6)

        if label:
            label_rect = pygame.Rect(border_rect.x + 18, border_rect.y - 6, min(190, border_rect.width - 36), 28)
            pygame.draw.rect(surface, (78, 50, 24), label_rect, border_radius=12)
            pygame.draw.rect(surface, (204, 164, 75), label_rect, 1, border_radius=12)
            label_text = self.font_micro.render(label, True, WHITE)
            label_text_rect = label_text.get_rect(center=label_rect.center)
            surface.blit(label_text, label_text_rect)

    def _draw_footer(self, surface, rect, center_label, left_label='SET', right_label='HOME'):
        """Draw the standard footer nav."""
        footer_y = rect.bottom - 52
        left_rect = pygame.Rect(rect.x + 24, footer_y, 52, 40)
        center_rect = pygame.Rect(rect.centerx - 82, footer_y + 2, 164, 36)
        right_rect = pygame.Rect(rect.right - 76, footer_y, 52, 40)

        self._draw_icon_button(surface, left_rect, left_label)
        self._draw_pill(surface, center_rect, center_label)
        self._draw_icon_button(surface, right_rect, right_label)
        return left_rect, center_rect, right_rect

    def _draw_hero_coin(self, surface, center):
        """Draw the large circular hero ornament used on the start screen."""
        pygame.draw.circle(surface, (218, 169, 60), center, 68)
        pygame.draw.circle(surface, (255, 224, 154), center, 68, 4)
        points = [
            (center[0] - 12, center[1] - 24),
            (center[0] - 12, center[1] + 24),
            (center[0] + 28, center[1]),
        ]
        pygame.draw.polygon(surface, (44, 26, 10), points)

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
        self._draw_screen_background(surface, variant='menu')
        card_rect = self._card_rect(height=560)
        self._draw_card(surface, card_rect)
        self._draw_header(
            surface,
            card_rect,
            'Adventure Begins',
            'Treasure Hunt',
            'Follow the old map, avoid traps, and race to the hidden treasure chest.',
        )
        self._draw_hero_coin(surface, (card_rect.centerx, card_rect.y + 258))

        start_rect = pygame.Rect(card_rect.x + 40, card_rect.y + 340, card_rect.width - 80, 58)
        exit_rect = pygame.Rect(card_rect.x + 40, card_rect.y + 412, card_rect.width - 80, 52)
        actions = {
            'start': self._draw_button(surface, start_rect, 'Start Game', variant='primary'),
            'quit': self._draw_button(surface, exit_rect, 'Exit', variant='secondary', small=True),
        }

        left_rect, _, right_rect = self._draw_footer(surface, card_rect, 'Brown & Gold Theme', left_label='SET', right_label='MODE')
        actions['settings'] = left_rect
        actions['mode'] = right_rect

        hint = self.font_micro.render('ENTER to start  |  ESC to exit', True, GRAY)
        hint_rect = hint.get_rect(center=(card_rect.centerx, card_rect.bottom - 78))
        surface.blit(hint, hint_rect)
        return actions

    def render_mode_select(self, surface, selected_mode=0):
        """Render game mode selection screen."""
        self._draw_screen_background(surface, variant='mode')
        card_rect = self._card_rect(height=580)
        self._draw_card(surface, card_rect)
        self._draw_header(
            surface,
            card_rect,
            'Choose Match Type',
            'Select Game Mode',
            'Start with mode selection, then move into a dedicated difficulty screen before the match begins.',
        )

        modes = [
            ('pvp', 'Player vs Player', 'primary'),
            ('pve', 'Player vs Machine', 'default'),
            ('eve', 'Machine vs Machine', 'secondary'),
        ]
        actions = {}
        start_y = card_rect.y + 212
        for index, (action_name, label, variant) in enumerate(modes):
            rect = pygame.Rect(card_rect.x + 38, start_y + index * 72, card_rect.width - 76, 56)
            actions[action_name] = self._draw_button(
                surface,
                rect,
                label,
                variant=variant,
                selected=index == selected_mode,
            )

        left_rect, _, right_rect = self._draw_footer(surface, card_rect, 'Map Room', left_label='SET', right_label='HOME')
        actions['settings'] = left_rect
        actions['home'] = right_rect

        help_text = self.font_micro.render('1-3 or Up/Down + Enter', True, GRAY)
        help_rect = help_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 78))
        surface.blit(help_text, help_rect)
        return actions

    def render_difficulty_select(self, surface, mode_family, options, selected_option=0):
        """Render the difficulty selection screen."""
        self._draw_screen_background(surface, variant='difficulty')
        card_rect = self._card_rect(height=600)
        self._draw_card(surface, card_rect)

        mode_title = {
            'pvp': 'Classic Duel Setup',
            'pve': 'Choose AI Difficulty',
            'eve': 'Choose Bot Difficulty',
        }.get(mode_family, 'Choose Difficulty')
        subtitle = {
            'pvp': 'PvP keeps the same gameplay rules. Use this confirmation screen before entering the match.',
            'pve': 'Select how strong and efficient the bot should be before the hunt begins.',
            'eve': 'Set the difficulty both bots will use while you spectate the full match.',
        }.get(mode_family, '')

        self._draw_header(surface, card_rect, 'Danger Level', mode_title, subtitle)
        actions = {}
        start_y = card_rect.y + 210
        for index, option in enumerate(options):
            rect = pygame.Rect(card_rect.x + 40, start_y + index * 68, card_rect.width - 80, 54)
            variant = 'primary' if index == 0 else ('secondary' if index == len(options) - 1 else 'default')
            actions[f'difficulty_{index}'] = self._draw_button(
                surface,
                rect,
                option,
                variant=variant,
                small=(len(option) > 18),
                selected=index == selected_option,
            )

        left_rect, _, right_rect = self._draw_footer(surface, card_rect, 'Temple Gate', left_label='SET', right_label='BACK')
        actions['settings'] = left_rect
        actions['back'] = right_rect

        help_text = self.font_micro.render('1-3 or Up/Down + Enter', True, GRAY)
        help_rect = help_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 78))
        surface.blit(help_text, help_rect)
        return actions

    def render_settings_menu(self, surface, settings_values, return_label='Back'):
        """Render the settings screen with simple toggles."""
        self._draw_screen_background(surface, variant='settings')
        card_rect = self._card_rect(height=610)
        self._draw_card(surface, card_rect)
        self._draw_header(
            surface,
            card_rect,
            'Control Panel',
            'Settings',
            'Adjust your adventure before entering the treasure island.',
        )

        actions = {}
        rows = [
            ('music', 'Music'),
            ('sfx', 'SFX'),
            ('hints', 'Hints'),
        ]
        for index, (key, label) in enumerate(rows):
            rect = pygame.Rect(card_rect.x + 32, card_rect.y + 184 + index * 72, card_rect.width - 64, 56)
            actions[f'toggle_{key}'] = self._draw_switch_row(surface, rect, label, settings_values[key])

        section_text = self.font_small.render('Quick Actions', True, YELLOW)
        section_rect = section_text.get_rect(center=(card_rect.centerx, card_rect.y + 410))
        surface.blit(section_text, section_rect)

        back_rect = pygame.Rect(card_rect.x + 32, card_rect.y + 440, card_rect.width - 64, 48)
        save_rect = pygame.Rect(card_rect.x + 32, card_rect.y + 498, card_rect.width - 64, 48)
        quit_rect = pygame.Rect(card_rect.x + 32, card_rect.y + 556, card_rect.width - 64, 42)
        actions['settings_back'] = self._draw_button(surface, back_rect, return_label, variant='secondary', small=True)
        actions['settings_save'] = self._draw_button(surface, save_rect, 'Save & Return', variant='primary', small=True)
        actions['settings_quit'] = self._draw_button(surface, quit_rect, 'Back To Start', variant='secondary', small=True)
        return actions

    def render_game_hud(self, surface, player, opponent=None, round_time=120.0):
        """Render heads-up display during gameplay."""
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT)
        hud_surface = pygame.Surface(hud_rect.size, pygame.SRCALPHA)
        for y in range(hud_rect.height):
            progress = y / max(1, hud_rect.height - 1)
            color = self._interpolate_color((40, 24, 13), (19, 12, 8), progress)
            pygame.draw.line(hud_surface, (*color, 244), (0, y), (hud_rect.width, y))
        pygame.draw.rect(hud_surface, (193, 146, 67, 180), hud_surface.get_rect(), 2, border_radius=18)
        surface.blit(hud_surface, hud_rect.topleft)

        accent_rect = pygame.Rect(0, HUD_HEIGHT - 14, SCREEN_WIDTH, 14)
        pygame.draw.rect(surface, (62, 40, 22), accent_rect)
        pygame.draw.line(surface, YELLOW, (18, HUD_HEIGHT - 2), (SCREEN_WIDTH - 18, HUD_HEIGHT - 2), 2)

        minutes = int(round_time) // 60
        seconds = int(round_time) % 60
        timer_box = pygame.Rect((SCREEN_WIDTH // 2) - 95, 12, 190, 60)
        pygame.draw.rect(surface, (54, 37, 20), timer_box, border_radius=16)
        pygame.draw.rect(surface, YELLOW, timer_box, 2, border_radius=16)
        time_text = self.clock_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        time_rect = time_text.get_rect(center=timer_box.center)
        surface.blit(time_text, time_rect)

        self._draw_player_status(surface, player, 20, 14)
        if opponent:
            self._draw_player_status(surface, opponent, SCREEN_WIDTH - 240, 14)

        fullscreen_rect = pygame.Rect(timer_box.right + 18, 18, 52, 38)
        settings_rect = pygame.Rect(fullscreen_rect.right + 10, 18, 52, 38)
        self._draw_icon_button(surface, fullscreen_rect, 'F11')
        self._draw_icon_button(surface, settings_rect, 'SET')
        return {'fullscreen': fullscreen_rect, 'settings': settings_rect}

    def _draw_player_status(self, surface, player, x, y):
        """Draw individual player status panel."""
        panel_width = 240
        panel_height = 56

        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(surface, (36, 36, 40), panel_rect, border_radius=14)
        pygame.draw.rect(surface, player.color, panel_rect, 2, border_radius=14)

        name_text = self.font_small.render(self._get_player_label(player), True, player.color)
        surface.blit(name_text, (x + 12, y + 8))
        self._draw_effect_badges(surface, player, x + panel_width - 86, y + 8)

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

    def _draw_effect_badges(self, surface, player, x, y):
        """Draw compact active effect tags on the player card."""
        badges = []
        if getattr(player, 'is_frozen', False):
            badges.append(('ICE', (80, 190, 255), getattr(player, 'freeze_time', 0.0)))
        if getattr(player, 'is_blinded', False):
            badges.append(('BLD', (170, 110, 255), getattr(player, 'blind_time', 0.0)))

        for index, (label, color, remaining) in enumerate(badges[:2]):
            rect = pygame.Rect(x + index * 42, y, 38, 22)
            pygame.draw.rect(surface, (25, 25, 30), rect, border_radius=8)
            pygame.draw.rect(surface, color, rect, 1, border_radius=8)
            text = self.font_micro.render(f"{label}", True, color)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

    def render_blind_overlay(self, surface, rect, actor):
        """Render a dark view overlay for a blinded actor."""
        if not getattr(actor, 'is_blinded', False):
            return

        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((8, 6, 18, 185))

        for x in range(-rect.height, rect.width, 48):
            pygame.draw.line(overlay, (70, 45, 120, 90), (x, 0), (x + rect.height, rect.height), 3)

        label = self.font_medium.render('BLINDED', True, (190, 150, 255))
        label_rect = label.get_rect(center=(rect.width // 2, rect.height // 2))
        overlay.blit(label, label_rect)

        time_text = self.font_tiny.render(f"{getattr(actor, 'blind_time', 0.0):.1f}s", True, WHITE)
        time_rect = time_text.get_rect(center=(rect.width // 2, rect.height // 2 + 34))
        overlay.blit(time_text, time_rect)

        surface.blit(overlay, rect.topleft)

    def render_clue_box(self, surface, clue_text, rect=None, label="CLUE", player=None):
        """Render the hint/clue display box."""
        if rect is None:
            box_height = CLUE_BOX_HEIGHT
            box_rect = pygame.Rect(0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height)
        else:
            box_rect = rect

        outer_rect = box_rect.inflate(-12, -8)
        shadow_rect = outer_rect.move(0, 6)
        pygame.draw.rect(surface, (14, 9, 6), shadow_rect, border_radius=18)
        pygame.draw.rect(surface, (58, 35, 18), outer_rect, border_radius=18)
        pygame.draw.rect(surface, (195, 146, 67), outer_rect, 2, border_radius=18)

        header_rect = pygame.Rect(outer_rect.x + 16, outer_rect.y + 10, min(180, outer_rect.width - 32), 28)
        pygame.draw.rect(surface, (86, 57, 28), header_rect, border_radius=12)
        pygame.draw.rect(surface, (211, 173, 92), header_rect, 1, border_radius=12)

        label_text = self.font_micro.render(f"{label}", True, YELLOW)
        label_rect = label_text.get_rect(center=header_rect.center)
        surface.blit(label_text, label_rect)

        text_y = outer_rect.y + 46

        max_width = outer_rect.width - 32
        lines = self._wrap_text(clue_text, self.font_tiny, max_width)
        for index, line in enumerate(lines[:2]):
            clue = self.font_tiny.render(line, True, (248, 236, 207))
            surface.blit(clue, (outer_rect.x + 18, text_y + index * 18))

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

    def render_game_over(self, surface, winner, reason="", mode_label=""):
        """Render game over screen."""
        self._draw_screen_background(surface, variant='result')
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 7, 5, 122))
        surface.blit(overlay, (0, 0))

        card_rect = self._card_rect(width=520, height=430)
        self._draw_card(surface, card_rect)
        self._draw_header(surface, card_rect, 'Round Complete', winner, mode_label)

        if reason:
            lines = self._wrap_text(reason, self.font_small, card_rect.width - 70)
            for index, line in enumerate(lines[:3]):
                reason_text = self.font_small.render(line, True, WHITE)
                reason_rect = reason_text.get_rect(center=(card_rect.centerx, card_rect.y + 196 + index * 24))
                surface.blit(reason_text, reason_rect)

        rematch_rect = pygame.Rect(card_rect.x + 38, card_rect.bottom - 124, card_rect.width - 76, 54)
        mode_rect = pygame.Rect(card_rect.x + 38, card_rect.bottom - 62, (card_rect.width - 86) // 2, 44)
        menu_rect = pygame.Rect(mode_rect.right + 10, card_rect.bottom - 62, (card_rect.width - 86) // 2, 44)
        actions = {
            'end_rematch': self._draw_button(surface, rematch_rect, 'Play Again', variant='primary'),
            'end_mode_select': self._draw_button(surface, mode_rect, 'Mode Select', variant='secondary', small=True),
            'end_menu': self._draw_button(surface, menu_rect, 'Main Menu', variant='secondary', small=True),
        }
        return actions

    def render_pause_overlay(self, surface):
        """Render pause overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 7, 5, 176))
        surface.blit(overlay, (0, 0))

        card_rect = self._card_rect(width=500, height=340)
        self._draw_card(surface, card_rect)
        self._draw_header(surface, card_rect, 'Rest Point', 'Paused', 'Take a breath, then resume or restart the current hunt.')

        resume_button = pygame.Rect(card_rect.x + 34, card_rect.bottom - 122, card_rect.width - 68, 48)
        restart_button = pygame.Rect(card_rect.x + 34, card_rect.bottom - 64, (card_rect.width - 78) // 2, 44)
        menu_button = pygame.Rect(restart_button.right + 10, card_rect.bottom - 64, (card_rect.width - 78) // 2, 44)
        actions = {
            'pause_resume': self._draw_button(surface, resume_button, 'Resume', variant='primary', small=True),
            'pause_restart': self._draw_button(surface, restart_button, 'Restart', variant='secondary', small=True),
            'pause_menu': self._draw_button(surface, menu_button, 'Mode Select', variant='secondary', small=True),
        }
        return actions

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
