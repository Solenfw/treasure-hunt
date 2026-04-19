"""Safe audio backend for music and sound effects."""

from pathlib import Path

import pygame


class AudioManager:
    """Load and play music/SFX without crashing when assets or audio devices are missing."""

    BASE_DIR = Path(__file__).resolve().parent.parent
    MUSIC_TRACKS = {
        'menu': (
            BASE_DIR / 'assets' / 'music' / 'menu.ogg',
            BASE_DIR / 'assets' / 'music' / 'menu.mp3',
        ),
        'gameplay': (
            BASE_DIR / 'assets' / 'music' / 'gameplay.ogg',
            BASE_DIR / 'assets' / 'music' / 'gameplay.mp3',
        ),
    }
    MUSIC_FALLBACKS = {}
    SFX_TRACKS = {
        'ui_click': BASE_DIR / 'assets' / 'sounds' / 'ui_click.wav',
        'ui_confirm': BASE_DIR / 'assets' / 'sounds' / 'ui_confirm.wav',
        'ui_back': BASE_DIR / 'assets' / 'sounds' / 'ui_back.wav',
        'pause': BASE_DIR / 'assets' / 'sounds' / 'pause.wav',
        'dig': BASE_DIR / 'assets' / 'sounds' / 'dig.wav',
        'locked': BASE_DIR / 'assets' / 'sounds' / 'locked.wav',
        'bomb': BASE_DIR / 'assets' / 'sounds' / 'bomb.wav',
        'key': BASE_DIR / 'assets' / 'sounds' / 'key.wav',
        'treasure': BASE_DIR / 'assets' / 'sounds' / 'treasure.wav',
        'freeze': BASE_DIR / 'assets' / 'sounds' / 'freeze.wav',
        'blind': BASE_DIR / 'assets' / 'sounds' / 'blind.wav',
        'extra_hint': BASE_DIR / 'assets' / 'sounds' / 'extra_hint.wav',
        'win': BASE_DIR / 'assets' / 'sounds' / 'win.wav',
        'lose': BASE_DIR / 'assets' / 'sounds' / 'lose.wav',
    }

    def __init__(self, settings=None):
        self.available = False
        self.music_enabled = True
        self.sfx_enabled = True
        self.current_music_key = None
        self.requested_music_key = None
        self._sound_cache = {}
        self._missing_sfx = set()
        self._missing_music = set()
        self._init_mixer()
        self.sync_settings(settings or {})

    def _init_mixer(self):
        """Try to initialize pygame mixer once."""
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self.available = pygame.mixer.get_init() is not None
        except pygame.error:
            self.available = False

    def sync_settings(self, settings):
        """Apply current settings toggles."""
        previous_music = self.music_enabled
        self.music_enabled = bool(settings.get('music', True))
        self.sfx_enabled = bool(settings.get('sfx', True))

        if not self.available:
            return

        if not self.music_enabled:
            self.stop_music()
        elif not previous_music and self.requested_music_key:
            self.play_music(self.requested_music_key)

    def stop_music(self):
        """Stop any currently playing background music."""
        if not self.available:
            self.current_music_key = None
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self.current_music_key = None

    def _resolve_music_path(self, track_key):
        """Return the best music path for a requested state."""
        checked_keys = []
        current_key = track_key
        while current_key and current_key not in checked_keys:
            checked_keys.append(current_key)
            for path in self.MUSIC_TRACKS.get(current_key, ()):
                if path.exists():
                    return current_key, path
            self._missing_music.add(current_key)
            current_key = self.MUSIC_FALLBACKS.get(current_key)
        return None, None

    def play_music(self, track_key, loops=-1):
        """Play music for the given track key if possible."""
        self.requested_music_key = track_key
        if track_key is None:
            self.stop_music()
            return False

        if not self.available or not self.music_enabled:
            return False

        resolved_key, path = self._resolve_music_path(track_key)
        if path is None:
            self.stop_music()
            return False

        if resolved_key == self.current_music_key and pygame.mixer.music.get_busy():
            return True

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(loops=loops, fade_ms=350)
            pygame.mixer.music.set_volume(0.55)
            self.current_music_key = resolved_key
            return True
        except pygame.error:
            self.current_music_key = None
            return False

    def _load_sound(self, cue):
        """Load one sound effect lazily."""
        if cue in self._sound_cache:
            return self._sound_cache[cue]
        if cue in self._missing_sfx:
            return None

        path = self.SFX_TRACKS.get(cue)
        if path is None or not path.exists():
            self._missing_sfx.add(cue)
            return None

        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(0.78)
            self._sound_cache[cue] = sound
            return sound
        except pygame.error:
            self._missing_sfx.add(cue)
            return None

    def play_sfx(self, cue):
        """Play a sound effect if enabled and available."""
        if not self.available or not self.sfx_enabled:
            return False

        sound = self._load_sound(cue)
        if sound is None:
            return False

        try:
            sound.play()
            return True
        except pygame.error:
            return False
