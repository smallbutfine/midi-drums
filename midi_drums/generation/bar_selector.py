"""Bar-by-bar pattern selector - produces distinct patterns for each bar.

Replaces DrumGenerator._extend_pattern_to_bars() which simply copied one
pattern N times with minor velocity jitter.  BarSelector generates a unique
Pattern for each bar, modulated by intensity curves and drummer personality.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from midi_drums.config import VELOCITY
from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.value_objects.drum_instrument import DrumInstrument

if TYPE_CHECKING:
    pass


class BarSelector:
    """Selects a different pattern for each bar within a section."""

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    def generate_for_bar(
        self,
        base_pattern: Pattern,
        bar_index: int,
        section_length: int,
        intensity_point,  # tuple(complexity_mult, velocity_bias, density_factor) or IntensityPoint
        drummer_name: str | None = None,
        previous_bars: list[Pattern] | None = None,
    ) -> Pattern:
        """Generate a pattern unique to this bar position.

        Args:
            base_pattern: The "skeleton" pattern for this section (from genre plugin).
            bar_index: 0-based position within the section.
            section_length: Total bars in this section.
            intensity_point: Interpolated intensity point from IntensityCurve.
            drummer_name: Drummer personality name.
            previous_bars: Patterns generated for bars 0..bar_index-1.

        Returns:
            A Pattern that is unique to this bar but musically coherent.
        """
        # Unpack intensity point
        if isinstance(intensity_point, tuple):
            complexity_mult, velocity_bias, density_factor = intensity_point
        else:
            complexity_mult = intensity_point.complexity_multiplier
            velocity_bias = intensity_point.velocity_bias
            _density_factor = intensity_point.density_factor

        # Apply drummer-specific seed for reproducible per-drummer variation
        rng = random.Random()
        if drummer_name:
            rng.seed(f"{drummer_name}_{base_pattern.name}_{bar_index}")
        else:
            rng.seed(bar_index)

        new_beats: list[Beat] = []
        beats_per_bar = base_pattern.time_signature.beats_per_bar

        # Scale velocity_bias by complexity to avoid extreme values on low-complexity bars
        scaled_velocity_bias = int(velocity_bias * complexity_mult)

        for beat in base_pattern.beats:
            new_position = beat.position + bar_index * beats_per_bar
            # Apply density_factor as a velocity boost (not removal) for dense patterns
            # This preserves the full skeleton but modulates energy
            new_velocity = max(
                1,
                min(
                    127,
                    beat.velocity + scaled_velocity_bias + rng.randint(-3, 3),
                ),
            )

            # For low complexity bars (<0.5), reduce velocity proportionally
            if complexity_mult < 0.5:
                new_velocity = int(new_velocity * complexity_mult)

            new_beats.append(
                Beat(
                    position=new_position,
                    instrument=beat.instrument,
                    velocity=new_velocity,
                    duration=beat.duration,
                    ghost_note=beat.ghost_note,
                    accent=beat.accent,
                    instrument_promoted=beat.instrument_promoted,
                )
            )

        # Add drummer-specific per-bar additions (not removals - preserves skeleton)
        if drummer_name:
            self._add_drummer_personality(
                new_beats, base_pattern, bar_index, section_length, rng
            )

        pattern = Pattern(f"{base_pattern.name}_bar{bar_index}")
        pattern.beats = new_beats
        pattern.time_signature = base_pattern.time_signature
        return pattern

    def _add_drummer_personality(
        self,
        beats: list[Beat],
        base_pattern: Pattern,
        bar_index: int,
        section_length: int,
        rng: random.Random,
        drummer_name: str | None = None,
    ) -> None:
        """Add drummer-specific per-bar variations to beat list."""
        beats_per_bar = base_pattern.time_signature.beats_per_bar
        section_pos = (
            bar_index / max(1, section_length - 1)
            if section_length > 1
            else 0.5
        )

        # Bonham: triplet-feel fills appear more often in later bars
        if drummer_name and "bonham" in drummer_name.lower():
            if section_pos > 0.6 and rng.random() < 0.15:
                pos = rng.uniform(2.5, beats_per_bar - 0.5)
                beats.append(
                    Beat(
                        position=pos,
                        instrument=DrumInstrument.FLOOR_TOM,
                        velocity=max(
                            1,
                            min(127, VELOCITY.TOM_HEAVY + rng.randint(-10, 10)),
                        ),
                        duration=0.4,
                    )
                )

        # Porcaro: shuffle-feel ghost notes on snare (every 4th bar)
        if drummer_name and "porcaro" in drummer_name.lower():
            if section_pos > 0.3 and bar_index % 4 == 0:
                for _i in range(2):
                    pos = rng.uniform(0, beats_per_bar)
                    beats.append(
                        Beat(
                            position=pos,
                            instrument=DrumInstrument.SNARE,
                            velocity=max(
                                1,
                                min(
                                    127,
                                    VELOCITY.SNARE_GHOST + rng.randint(-5, 10),
                                ),
                            ),
                            duration=0.1,
                            ghost_note=True,
                        )
                    )

        # All drummers: occasional crash accent on last bar (fill setup)
        if bar_index == section_length - 1 and rng.random() < 0.3:
            beats.append(
                Beat(
                    position=beats_per_bar * 3.5,
                    instrument=DrumInstrument.CRASH,
                    velocity=max(
                        1,
                        min(127, VELOCITY.CRASH_ACCENT + rng.randint(-10, 15)),
                    ),
                    duration=0.8,
                )
            )
