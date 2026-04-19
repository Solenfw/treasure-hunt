"""Generate simple placeholder WAV sound effects for Treasure Hunt."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
MAX_AMPLITUDE = 32_767
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "sounds"


def clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    """Limit sample values to the valid PCM range."""
    return max(low, min(high, value))


def lerp(start: float, end: float, progress: float) -> float:
    """Linear interpolation helper."""
    return start + (end - start) * progress


def phase_wave(phase: float, waveform: str = "sine") -> float:
    """Return one oscillator value for the requested waveform."""
    wrapped = phase % 1.0
    if waveform == "square":
        return 1.0 if wrapped < 0.5 else -1.0
    if waveform == "triangle":
        return 4.0 * abs(wrapped - 0.5) - 1.0
    if waveform == "saw":
        return 2.0 * wrapped - 1.0
    return math.sin(2.0 * math.pi * wrapped)


def apply_envelope(progress: float, attack: float = 0.02, release: float = 0.18) -> float:
    """Basic attack/release amplitude envelope."""
    if progress < attack:
        return progress / max(attack, 1e-6)
    if progress > 1.0 - release:
        return max(0.0, (1.0 - progress) / max(release, 1e-6))
    return 1.0


def synth(
    duration: float,
    start_freq: float,
    end_freq: float | None = None,
    *,
    waveform: str = "sine",
    volume: float = 0.5,
    noise_amount: float = 0.0,
    vibrato_hz: float = 0.0,
    vibrato_depth: float = 0.0,
    attack: float = 0.02,
    release: float = 0.18,
) -> list[float]:
    """Create one pitched tone with optional sweep, vibrato, and noise."""
    sample_count = max(1, int(SAMPLE_RATE * duration))
    end_freq = start_freq if end_freq is None else end_freq
    samples: list[float] = []
    phase = 0.0

    for index in range(sample_count):
        progress = index / sample_count
        base_freq = lerp(start_freq, end_freq, progress)
        if vibrato_hz and vibrato_depth:
            base_freq += math.sin(2.0 * math.pi * vibrato_hz * (index / SAMPLE_RATE)) * vibrato_depth
        phase += base_freq / SAMPLE_RATE
        sample = phase_wave(phase, waveform)
        if noise_amount:
            sample += random.uniform(-1.0, 1.0) * noise_amount
        sample *= volume * apply_envelope(progress, attack=attack, release=release)
        samples.append(clamp(sample))

    return samples


def silence(duration: float) -> list[float]:
    """Return a silent gap."""
    return [0.0] * max(1, int(SAMPLE_RATE * duration))


def mix_layers(*layers: list[float]) -> list[float]:
    """Mix several sample layers to one track."""
    if not layers:
        return []
    length = max(len(layer) for layer in layers)
    mixed = [0.0] * length
    for layer in layers:
        for index, sample in enumerate(layer):
            mixed[index] += sample
    return [clamp(sample) for sample in mixed]


def sequence(*parts: list[float]) -> list[float]:
    """Concatenate several sample parts."""
    output: list[float] = []
    for part in parts:
        output.extend(part)
    return output


def repeat_note(frequencies: list[tuple[float, float]], gap: float = 0.01, **kwargs) -> list[float]:
    """Concatenate a short sequence of note sweeps."""
    parts: list[float] = []
    for index, (start_freq, end_freq) in enumerate(frequencies):
        parts.append(synth(0.08, start_freq, end_freq, **kwargs))
        if index != len(frequencies) - 1:
            parts.append(silence(gap))
    return sequence(*parts)


def to_pcm16(samples: list[float]) -> bytes:
    """Convert floating-point samples to 16-bit PCM bytes."""
    pcm = bytearray()
    for sample in samples:
        pcm.extend(struct.pack("<h", int(clamp(sample) * MAX_AMPLITUDE)))
    return bytes(pcm)


def write_wav(path: Path, samples: list[float]) -> None:
    """Write a mono PCM WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(to_pcm16(samples))


def build_ui_click() -> list[float]:
    return mix_layers(
        synth(0.06, 1800, 1250, waveform="triangle", volume=0.42, release=0.32),
        synth(0.04, 900, 700, waveform="sine", volume=0.18, release=0.4),
    )


def build_ui_confirm() -> list[float]:
    return sequence(
        synth(0.07, 980, 1100, waveform="triangle", volume=0.36),
        silence(0.01),
        synth(0.11, 1320, 1480, waveform="triangle", volume=0.42),
    )


def build_ui_back() -> list[float]:
    return sequence(
        synth(0.06, 860, 740, waveform="triangle", volume=0.35),
        silence(0.008),
        synth(0.08, 640, 420, waveform="triangle", volume=0.34),
    )


def build_pause() -> list[float]:
    return sequence(
        synth(0.05, 720, 660, waveform="square", volume=0.24, release=0.3),
        silence(0.025),
        synth(0.05, 720, 660, waveform="square", volume=0.24, release=0.3),
    )


def build_dig() -> list[float]:
    return mix_layers(
        synth(0.14, 140, 90, waveform="triangle", volume=0.42, noise_amount=0.18, attack=0.0, release=0.55),
        synth(0.08, 320, 190, waveform="saw", volume=0.12, noise_amount=0.12, attack=0.0, release=0.7),
    )


def build_locked() -> list[float]:
    return sequence(
        synth(0.07, 210, 180, waveform="square", volume=0.24, noise_amount=0.06, release=0.35),
        silence(0.02),
        synth(0.08, 180, 130, waveform="square", volume=0.28, noise_amount=0.08, release=0.38),
    )


def build_bomb() -> list[float]:
    return mix_layers(
        synth(0.46, 120, 34, waveform="triangle", volume=0.55, noise_amount=0.42, attack=0.0, release=0.45),
        synth(0.24, 380, 90, waveform="saw", volume=0.18, noise_amount=0.2, attack=0.0, release=0.5),
    )


def build_key() -> list[float]:
    return sequence(
        synth(0.08, 1040, 1240, waveform="triangle", volume=0.34, vibrato_hz=8.0, vibrato_depth=10.0),
        silence(0.015),
        synth(0.16, 1560, 1760, waveform="sine", volume=0.38, vibrato_hz=9.0, vibrato_depth=18.0, release=0.45),
    )


def build_treasure() -> list[float]:
    return sequence(
        synth(0.09, 520, 620, waveform="triangle", volume=0.30),
        silence(0.01),
        synth(0.10, 780, 920, waveform="triangle", volume=0.32),
        silence(0.01),
        mix_layers(
            synth(0.28, 1040, 1320, waveform="sine", volume=0.38, vibrato_hz=6.0, vibrato_depth=14.0, release=0.55),
            synth(0.28, 1310, 1560, waveform="triangle", volume=0.14, release=0.6),
        ),
    )


def build_freeze() -> list[float]:
    return mix_layers(
        synth(0.24, 1400, 620, waveform="sine", volume=0.34, vibrato_hz=12.0, vibrato_depth=28.0, release=0.4),
        synth(0.18, 2100, 1200, waveform="triangle", volume=0.12, release=0.5),
    )


def build_blind() -> list[float]:
    return mix_layers(
        synth(0.26, 460, 180, waveform="saw", volume=0.18, vibrato_hz=7.0, vibrato_depth=30.0, release=0.48),
        synth(0.26, 220, 120, waveform="sine", volume=0.24, noise_amount=0.08, release=0.55),
    )


def build_extra_hint() -> list[float]:
    return repeat_note(
        [(820, 980), (1040, 1220), (1360, 1640)],
        waveform="triangle",
        volume=0.26,
        release=0.38,
    )


def build_win() -> list[float]:
    return sequence(
        repeat_note([(520, 620), (780, 920), (1040, 1320)], gap=0.012, waveform="triangle", volume=0.28, release=0.4),
        silence(0.015),
        mix_layers(
            synth(0.26, 1320, 1560, waveform="sine", volume=0.34, vibrato_hz=6.0, vibrato_depth=12.0, release=0.55),
            synth(0.26, 1760, 1980, waveform="triangle", volume=0.13, release=0.58),
        ),
    )


def build_lose() -> list[float]:
    return sequence(
        synth(0.10, 620, 520, waveform="triangle", volume=0.24, release=0.35),
        silence(0.014),
        synth(0.12, 420, 300, waveform="triangle", volume=0.25, release=0.38),
        silence(0.014),
        mix_layers(
            synth(0.22, 260, 120, waveform="saw", volume=0.16, noise_amount=0.06, release=0.52),
            synth(0.22, 180, 90, waveform="sine", volume=0.20, release=0.58),
        ),
    )


SOUND_BUILDERS = {
    "ui_click.wav": build_ui_click,
    "ui_confirm.wav": build_ui_confirm,
    "ui_back.wav": build_ui_back,
    "pause.wav": build_pause,
    "dig.wav": build_dig,
    "locked.wav": build_locked,
    "bomb.wav": build_bomb,
    "key.wav": build_key,
    "treasure.wav": build_treasure,
    "freeze.wav": build_freeze,
    "blind.wav": build_blind,
    "extra_hint.wav": build_extra_hint,
    "win.wav": build_win,
    "lose.wav": build_lose,
}


def main() -> None:
    """Generate all placeholder sound files."""
    random.seed(17)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, builder in SOUND_BUILDERS.items():
        write_wav(OUTPUT_DIR / filename, builder())
        print(f"generated {filename}")


if __name__ == "__main__":
    main()
