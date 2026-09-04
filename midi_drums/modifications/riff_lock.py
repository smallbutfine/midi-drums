"""RiffLockTransform — locks kick patterns to detected riff accents.

Post-processes a genre-plugin pattern so that kick hits land on (or near)
the rhythmic accents extracted from an audio riff. The snare/hi-hat/cymbal
and drummer styling pass through untouched — only the kick is modified, and
only at accent positions where ``lock_strength > 0``.

This is the core transformation for "riff-locked drum generation": a guitar
or bass riff's rhythmic accents become the kick pattern's skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass

from midi_drums.config import VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.value_objects.riff_accent import RiffAccentMap
from midi_drums.modifications.drummer_mods import DrummerModification

kick = InstrumentRegistry.get("kick")


@dataclass
class RiffLockTransform(DrummerModification):
    """Transform that locks a pattern's kick beats to riff accent positions.

    Attributes:
        riff_accents: Detected accents from the audio riff (output of ``audio_analysis.analyze_onsets``).
        lock_strength: How strictly kicks follow accents. 0.0 = no locking, 1.0 = exact match.
                       Intermediate values interpolate between the original kick position and the accent.
        max_displacement_beats: Maximum allowed displacement of a kick from its original position (in beats).
                                Prevents kicks from being pulled too far toward an accent if it would create unnatural patterns.
    """

    riff_accents: RiffAccentMap
    lock_strength: float = 1.0
    max_displacement_beats: float = 0.25

    def apply(
        self, pattern: Pattern, intensity_pt: tuple | None = None
    ) -> Pattern:
        """Return a new ``Pattern`` with kicks locked to riff accents.

        For each riff accent with strength >= threshold, finds the nearest kick
        in the pattern and pulls it toward the accent's position (scaled by
        lock_strength). Kicks already within ``max_displacement_beats`` of an
        accent are nudged; those beyond the displacement limit are added at
        the accent position.

        Args:
            pattern: Input pattern (unchanged — returns a new pattern).
            intensity_pt: Unused by riff_lock but kept for DrummerModification compat.

        Returns:
            New ``Pattern`` with modified/additional kick beats.
        """
        if self.lock_strength <= 0 or not self.riff_accents.accents:
            # No locking requested — return a copy untouched
            import copy  # noqa: PLC0415

            return copy.deepcopy(pattern)

        new_pattern = Pattern(f"{pattern.name}_riff_locked")
        new_pattern.beats = (
            [copy.copy(b) for b in pattern.beats]
            if hasattr(pattern, "beats")
            else []
        )
        new_pattern.metadata = (
            dict(pattern.metadata) if pattern.metadata else {}
        )
        new_pattern.metadata["riff_locked"] = True

        kicks = [b for b in new_pattern.beats if b.instrument == kick]
        kicks.sort(key=lambda k: k.position)

        beats_per_bar = self.riff_accents.beats_per_bar

        for accent in self.riff_accents.accents:
            if accent.strength < 0.3:  # Skip weak accents
                continue

            # Find nearest kick within max_displacement_beats (wrapping within bar)
            closest_kick = None
            min_dist = float("inf")

            for kick in kicks:
                dist = self._beat_distance(
                    kick.position, accent.position, beats_per_bar
                )
                if dist < min_dist and dist <= self.max_displacement_beats:
                    min_dist = dist
                    closest_kick = kick

            # If no nearby kick exists, create one at the accent position
            if closest_kick is None or min_dist > self.max_displacement_beats:
                new_kick = Beat(
                    position=accent.position,
                    instrument=kick,
                    velocity=int(VELOCITY.KICK_HEAVY * accent.strength),
                    duration=0.1,
                    ghost_note=False,
                    accent=True,
                )
                # Insert in sorted position
                inserted = False
                for i, existing in enumerate(new_pattern.beats):
                    if existing.instrument != kick:
                        continue
                    if (
                        self._beat_distance(
                            existing.position, new_kick.position, beats_per_bar
                        )
                        > min_dist
                        and new_kick.position < existing.position + 0.5
                    ):
                        new_pattern.beats.insert(i, new_kick)
                        inserted = True
                        break
                if not inserted:
                    new_pattern.beats.append(new_kick)
            else:
                # Pull the kick toward the accent position by lock_strength * distance
                displacement = (
                    accent.position - closest_kick.position
                ) * self.lock_strength

                # Wrap within bar bounds
                new_position = closest_kick.position + displacement
                if new_position >= beats_per_bar:
                    new_position -= beats_per_bar
                elif new_position < 0:
                    new_position += beats_per_bar

                closest_kick.position = new_position
                # Increase velocity based on accent strength
                closest_kick.velocity = int(
                    max(
                        closest_kick.velocity,
                        VELOCITY.KICK_NORMAL * (0.5 + 0.5 * accent.strength),
                    )
                )
                closest_kick.accent = True

        return new_pattern

    @staticmethod
    def _beat_distance(
        pos_a: float, pos_b: float, beats_per_bar: float
    ) -> float:
        """Circular distance between two beat positions within a bar."""
        dist1 = abs(pos_a - pos_b)
        dist2 = beats_per_bar - dist1
        return min(dist1, dist2)


def lock_to_riff(
    pattern: Pattern,
    riff_accents: RiffAccentMap,
    lock_strength: float = 1.0,
) -> Pattern:
    """Convenience function to apply riff locking to a pattern.

    Args:
        pattern: Input drum pattern.
        riff_accents: Detected riff accents from audio analysis.
        lock_strength: How strictly to follow the riff (0.0-1.0).

    Returns:
        New pattern with kicks locked to riff accents.
    """
    transform = RiffLockTransform(
        riff_accents=riff_accents, lock_strength=lock_strength
    )
    return transform.apply(pattern)
