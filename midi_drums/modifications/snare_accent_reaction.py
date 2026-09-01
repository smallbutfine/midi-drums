"""Snare-accent-reaction modification — reacts the snare to riff accents.

Post-processes a pattern that has already been riff-locked (kicks on riff accents)
so the snare can optionally react to those same accents too, without repositioning
the backbeat.

Two independent, opt-in modes (never both at once):

- ``"reinforce"``: existing snare beats near strong accents get velocity boost.
- ``"stab"``: insert a unison snare hit at very strong accents where no snare exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.value_objects.riff_accent import RiffAccentMap
from midi_drums.modifications.drummer_mods import DrummerModification

snare_sticks = InstrumentRegistry.get("snare_sticks")


@dataclass
class SnareAccentReaction(DrummerModification):
    """React snare hits to riff accent positions.

    Attributes:
        riff_accents: Detected accents (same source as the riff lock).
        mode: ``"reinforce"`` or ``"stab"``. Never both at once.
        threshold: Minimum accent strength for this mode to activate (0.0-1.0).
        collapse_tolerance_beats: If a stab lands near an existing snare, merge instead of stacking.
    """

    riff_accents: RiffAccentMap
    mode: Literal["off", "reinforce", "stab"] = "off"
    threshold: float = 0.85
    collapse_tolerance_beats: float = 0.125

    def apply(
        self, pattern: Pattern, intensity_pt: tuple | None = None
    ) -> Pattern:
        """Return a new ``Pattern`` with snare reactions to riff accents.

        Args:
            pattern: Input riff-locked pattern (unchanged).
            intensity_pt: Unused but kept for DrummerModification compatibility.

        Returns:
            New ``Pattern`` with snare modifications based on mode.
        """
        import copy  # noqa: PLC0415

        new_pattern = copy.deepcopy(pattern)

        if self.mode == "off" or not self.riff_accents.accents:
            return new_pattern

        beats_per_bar = self.riff_accents.beats_per_bar

        if self.mode == "reinforce":
            # Find snare beats near strong accents and boost their velocity
            for accent in self.riff_accents.accents:
                if accent.strength < self.threshold:
                    continue

                # Find nearest non-ghost snare beat
                for beat in new_pattern.beats:
                    if (
                        beat.instrument != snare_sticks
                        or beat.ghost_note
                    ):
                        continue

                    dist = abs(beat.position - accent.position)
                    # Wrap distance within bar
                    wrapped_dist = min(dist, beats_per_bar - dist)
                    if wrapped_dist <= self.collapse_tolerance_beats:
                        # Calculate the velocity ceiling (loudest snare in pattern or default)
                        snare_velocities = [
                            b.velocity
                            for b in new_pattern.beats
                            if b.instrument == snare_sticks
                            and not b.ghost_note
                        ]
                        velocity_ceiling = (
                            max(snare_velocities)
                            if snare_velocities
                            else VELOCITY.SNARE_ACCENT
                        )

                        # Boost toward the ceiling, weighted by accent strength
                        current_boost = int(
                            (velocity_ceiling - beat.velocity)
                            * accent.strength
                            * 0.7
                        )
                        beat.velocity = min(
                            beat.velocity + current_boost, velocity_ceiling
                        )
                        break  # One accent per beat max

        elif self.mode == "stab":
            # Insert a snare hit at strong accent positions where no snare exists
            for accent in self.riff_accents.accents:
                if accent.strength < self.threshold:
                    continue

                # Check if an existing snare is already near this accent
                has_nearby_snare = False
                for beat in new_pattern.beats:
                    if (
                        beat.instrument == snare_sticks
                        or abs(beat.position - accent.position)
                        <= self.collapse_tolerance_beats
                    ):
                        wrapped = min(
                            abs(beat.position - accent.position),
                            beats_per_bar
                            - abs(beat.position - accent.position),
                        )
                        if wrapped <= self.collapse_tolerance_beats:
                            # Collapse into the existing snare (reinforce instead of new hit)
                            has_nearby_snare = True
                            current_boost = int(
                                (VELOCITY.SNARE_ACCENT - beat.velocity)
                                * accent.strength
                                * 0.5
                            )
                            beat.velocity = min(
                                beat.velocity + current_boost,
                                VELOCITY.SNARE_ACCENT,
                            )
                            break

                if not has_nearby_snare:
                    # Insert a new unison snare hit at the kick's position
                    stab_velocity = int(
                        VELOCITY.KICK_HEAVY * 0.85 * accent.strength
                    )
                    new_snare = Beat(
                        position=accent.position,
                        instrument=snare_sticks,
                        velocity=min(stab_velocity, VELOCITY.SNARE_ACCENT),
                        duration=TIMING.SIXTEENTH,
                        ghost_note=False,
                        accent=True,
                    )
                    # Insert in sorted order among snare beats
                    inserted = False
                    for i, existing in enumerate(new_pattern.beats):
                        if existing.instrument == snare_sticks:
                            if (
                                self._beat_distance(
                                    existing.position,
                                    new_snare.position,
                                    beats_per_bar,
                                )
                                > 0.5
                            ):
                                new_pattern.beats.insert(i + 1, new_snare)
                                inserted = True
                                break
                    if not inserted:
                        new_pattern.beats.append(new_snare)

        return new_pattern

    @staticmethod
    def _beat_distance(
        pos_a: float, pos_b: float, beats_per_bar: float
    ) -> float:
        """Circular distance between beat positions within a bar."""
        dist1 = abs(pos_a - pos_b)
        dist2 = beats_per_bar - dist1
        return min(dist1, dist2)


def react_snare_to_riff(
    pattern: Pattern,
    riff_accents: RiffAccentMap,
    mode: Literal["off", "reinforce", "stab"] = "off",
    threshold: float = 0.85,
) -> Pattern:
    """Convenience function to apply snare accent reaction to a pattern.

    Args:
        pattern: Input riff-locked pattern.
        riff_accents: Detected riff accents (same source as riff lock).
        mode: ``"reinforce"`` or ``"stab"``.
        threshold: Minimum accent strength (0.0-1.0).

    Returns:
        New ``Pattern`` with snare modifications.
    """
    transform = SnareAccentReaction(
        riff_accents=riff_accents, mode=mode, threshold=threshold
    )
    return transform.apply(pattern)
