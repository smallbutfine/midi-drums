"""Onset detection for riff-locked drum generation via librosa.

This module converts audio (guitar/bass riff) into rhythmic accent positions
that can be used to lock kick patterns — the core of the "riff lock" feature.

All timing is expressed in beats relative to the provided BPM and time signature,
matching Beat.position semantics in midi_drums.core.models.pattern.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from midi_drums.core.value_objects.riff_accent import RiffAccent, RiffAccentMap


def analyze_onsets(
    audio_path: str | Path,
    bpm: int = 120,
    beats_per_bar: float = 4.0,
    onset_threshold: float = 0.3,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> RiffAccentMap:
    """Detect rhythmic onsets in an audio file and return a ``RiffAccentMap``.

    Uses librosa's onset detection to find accent positions, then converts
    them from seconds to beat positions relative to the given BPM.

    Args:
        audio_path: Path to WAV/MP3 audio file (guitar/bass riff).
        bpm: Tempo in beats per minute. Used to convert onset times → beat positions.
        beats_per_bar: Time signature numerator (usually 4).
        onset_threshold: Minimum onset strength to be included as an accent.
                          Higher = fewer accents, lower = more sensitive.
        frame_length: FFT frame length for librosa's onset detection.
        hop_length: Hop size between frames for onset detection.

    Returns:
        A ``RiffAccentMap`` with one bar's worth of detected accents.

    Raises:
        FileNotFoundError: If audio_path does not exist.
        ImportError: If librosa or soundfile is not installed (install via ``midi_drums[rfi]``).
    """
    try:
        import librosa  # noqa: PLC0415 - optional dependency
    except ImportError as e:
        raise ImportError(
            "librosa is required for riff-locked drum generation. "
            "Install with: pip install 'midi-drums[rfi]'"
        ) from e

    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load audio (mono, sr=22050 is standard for onset detection)
    y, sr = librosa.load(path, sr=22050, mono=True)

    # Compute onset envelope and detect onsets
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, frame_length=frame_length, hop_length=hop_length)
    onset_frames = librosa.util.amp_to_db(onset_env) > librosa.util.peak_tonality(onset_env, top_k=10) * 3

    # Convert frame indices to times (seconds)
    onsets_beat_times = librosa.frames_to_time(np.where(onset_frames)[0], sr=sr, hop_length=hop_length)

    # Calculate beat positions within the bar
    seconds_per_beat = 60.0 / bpm
    accent_map_accents = []

    for onset_time in onsets_beat_times:
        # Position within current bar (0 to beats_per_bar)
        position_in_bar = onset_time % (seconds_per_beat * beats_per_bar)
        beat_position = position_in_bar / seconds_per_beat

        # Use onset strength as normalized strength
        frame_idx = librosa.time_to_frames(onset_time, sr=sr, hop_length=hop_length)
        if 0 <= frame_idx < len(onset_env):
            raw_strength = float(onset_env[frame_idx])
            # Normalize to 0-1 range using a simple heuristic
            strength = min(1.0, max(0.0, (raw_strength + 30) / 40))  # shift by -30dB floor

        if beat_position >= 0 and strength >= onset_threshold:
            accent_map_accents.append(RiffAccent(position=beat_position, strength=strength))

    return RiffAccentMap(accents=tuple(accent_map_accents), beats_per_bar=beats_per_bar)


def detect_beats(
    audio_path: str | Path,
    bpm: int = 120,
    beats_per_bar: float = 4.0,
) -> RiffAccentMap:
    """Simpler beat detection using librosa's tempo estimation + onset detection.

    This is a convenience wrapper that uses librosa's built-in beat tracking
    instead of raw onset detection. Good for clean recordings where beats
    are already well-defined.

    Args:
        audio_path: Path to audio file.
        bpm: Initial tempo estimate (used if tempo estimation fails).
        beats_per_bar: Expected beats per bar.

    Returns:
        A ``RiffAccentMap`` representing the detected beat pattern.
    """
    try:
        import librosa  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "librosa is required for riff-locked drum generation. "
            "Install with: pip install 'midi-drums[rfi]'"
        ) from e

    y, sr = librosa.load(audio_path, sr=22050, mono=True)

    # Estimate tempo first
    tempoi, _ = librosa.beat.tempo(y=y, sr=sr, aggregate=None, trim=False)
    if len(tempoi) > 0 and tempoi[0] > 40:
        estimated_bpm = tempoi[0]
    else:
        estimated_bpm = bpm

    # Use onset strength as confidence for each beat
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_times = librosa.frames_to_time(np.where(librosa.util.peak_pick(onset_env, 1, 1, 1, 0, 50, 0.1))[0], sr=sr)

    seconds_per_beat = 60.0 / estimated_bpm
    accents = []
    for t in onset_times:
        pos = (t % (seconds_per_beat * beats_per_bar)) / seconds_per_beat
        if 0 <= pos < beats_per_bar:
            # Use onset strength as accent strength (normalized)
            frame_idx = int(t * sr / 512) if 512 > 0 else 0
            strength = float(min(1.0, max(0.0, (onset_env[frame_idx] + 30) / 40))) if frame_idx < len(onset_env) else 0.5
            accents.append(RiffAccent(position=pos, strength=strength))

    return RiffAccentMap(accents=tuple(accents), beats_per_bar=beats_per_bar)
