"""Riff accent value objects for riff-locked drum generation.

These carry the output of midi_drums.analysis.audio_analysis (onset detection
on a rendered riff) into RiffLockTransform. Plain frozen dataclasses — no DSP
dependency so they can be constructed directly in tests.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiffAccent:
    """A single rhythmic accent within one bar.

    Attributes:
        position: Beat position within the bar (0.0-based, same as ``Beat.position`` mod beats_per_bar).
        strength: Onset strength from onset detection, normalized 0.0-1.0.
    """

    position: float
    strength: float

    def __post_init__(self) -> None:
        if self.position < 0:
            raise ValueError(
                f"position cannot be negative, got {self.position}"
            )
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                f"strength must be between 0.0 and 1.0, got {self.strength}"
            )


@dataclass(frozen=True)
class RiffAccentMap:
    """A bar's worth of rhythmic accents extracted from a riff.

    Represents exactly one representative bar. All accent positions are
    expected to fall within [0, beats_per_bar).

    Attributes:
        accents: Tuple of RiffAccent objects for this bar.
        beats_per_bar: Number of beats in the bar (e.g., 4 for 4/4 time).
    """

    accents: tuple[RiffAccent, ...] = ()
    beats_per_bar: float = 4.0

    def __post_init__(self) -> None:
        if self.beats_per_bar <= 0:
            raise ValueError(
                f"beats_per_bar must be positive, got {self.beats_per_bar}"
            )
        for accent in self.accents:
            if not 0.0 <= accent.position < self.beats_per_bar:
                raise ValueError(
                    f"accent position {accent.position} out of range "
                    f"[0, {self.beats_per_bar})"
                )
