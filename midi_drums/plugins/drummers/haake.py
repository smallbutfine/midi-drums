"""Thomas Haake drummer plugin - Meshuggah-style using full AD2 kit vocabulary.

Fills now use tom_edge rimshots for mechanical staccato, snare_shallow for
atmospheric textures, crash(4-6) with choke for tight industrial punctuation,
and ride_bell/ride_shaft for non-traditional metric grid work.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    MechanicalPrecision,
    PolyrhythmApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class HaakePlugin(DrummerPlugin):
    """Thomas Haake drummer style plugin.

    Characteristics:
    - Polyrrhythmic layering (simultaneous different meters across limbs)
    - Machine-like precision and inhuman consistency
    - Sparse but devastating pattern density
    - Odd time signature adaptation to 4/4 framework
    - Palm-muted gallop patterns synced to guitars
    """

    def __init__(self):
        self.polyrhythm = PolyrhythmApplication(
            kick_subdivisions=7,
            snare_subdivisions=4,
            tom_subdivisions=5,
            intensity=0.6,
        )
        self.precision = MechanicalPrecision(quantize_amount=1.0)

    @property
    def drummer_name(self) -> str:
        return "haake"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "progressive", "djent", "experimental"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Thomas Haake's signature polyrhythmic style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_haake"

        styled = self.polyrhythm.apply(styled, intensity=0.7)
        styled = self.precision.apply(styled, intensity=1.0)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Thomas Haake's signature fill patterns using full AD2 kit.

        Uses tom_edge rimshots for mechanical staccato, snare_shallow for
        atmospheric textures, crash(4-6) with choke for tight industrial
        punctuation, and ride_bell/ride_shaft for non-traditional metric work.
        """
        return [
            Fill(
                pattern=self._create_polyrhythm_tom_cascade(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_destroy_erase_gallop(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_kobayashi_odd_meter_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_nothing_polyrhythm_showcase(),
                trigger_probability=0.85,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_rational_gesture_machine_gun(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_catch_32_blast_polyrhythm(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_flesh_cadence(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_bleed_polyrhythm(),
                trigger_probability=0.7,
                section_position="middle",
            ),
        ]

    def _create_polyrhythm_tom_cascade(self) -> Pattern:
        """Polyrhythmic tom cascade — 7-over-5 split using ALL toms with rimshot."""

        builder = PatternBuilder("haake_polyrhythm_tom")
        # 7-over-5 polyrhythmic tom pattern across ALL toms (rimshot/edge)
        for i in range(10):
            pos = i * TIMING.SIXTEENTH
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            # Alternate between normal tom and tom_edge rimshot for texture
            if i % 3 == 0:
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
            else:
                builder.tom(
                    pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 10)
                )
        # Tight crash_choke for mechanical punctuation
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3", VELOCITY.CRASH_ACCENT)
        return builder.build()

    def _create_destroy_erase_gallop(self) -> Pattern:
        """Destroy Erase gallop — snare_shallow + tom_FLOOR matching guitar chug."""

        builder = PatternBuilder("haake_destroy_erase")
        # snare_shallow for tight rhythmic texture (djent palm-muted feel)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_shallow(pos, VELOCITY.SNARE_GHOST + 5)
        # FLOOR tom edge hits matching guitar chug rhythm
        for i in [0, 3, 6]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.tom_edge(pos, "FLOOR", VELOCITY.TOM_HEAVY)
        # Crash_4 with choke for industrial punctuation
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "4")
        return builder.build()

    def _create_kobayashi_odd_meter_fill(self) -> Pattern:
        """Kobayashi odd-meter fill — tom_1 + ride_shaft across 11/8 grid."""

        builder = PatternBuilder("haake_kobayashi")
        # Sparse hits adapted to 4/4 grid (odd meter feel)
        builder.tom(0.0, "1", VELOCITY.TOM_HEAVY)
        builder.kick(TIMING.HALF, VELOCITY.KICK_NORMAL)
        # ride_shaft for non-traditional metric grid sound
        builder.ride_shaft(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL
        )
        builder.tom_edge(4.0 - TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY)
        # snare_shallow for atmospheric texture
        builder.snare_shallow(4.0 - TIMING.SIXTEENTH, VELOCITY.SNARE_GHOST + 5)
        return builder.build()

    def _create_nothing_polyrhythm_showcase(self) -> Pattern:
        """Nothing polyrhythm — kick 5 vs snare 4 with tom_edge rimshots."""

        builder = PatternBuilder("haake_nothing")
        # Sparse but devastating (Haake's philosophy: minimal notes, maximum impact)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.snare_rimshot(TIMING.QUARTER * 1, VELOCITY.SNARE_RIMSHOT)
        builder.tom_edge(TIMING.HALF, "HIGH", VELOCITY.TOM_HEAVY)
        # Snare rimshot + tom_FLOOR edge hits on off-beats
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # Tight crash_choke resolution
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_rational_gesture_machine_gun(self) -> Pattern:
        """Rational gesture machine-gun — tom_edge staccato across ALL toms."""

        builder = PatternBuilder("haake_rational_gesture")
        # Tom edge rimshots in rapid staccato (industrial machine-gun feel)
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-3, 8), 127),
            )
        # crash_choke for tight industrial punctuation
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_catch_32_blast_polyrhythm(self) -> Pattern:
        """Catch-32 blast-polyrhythm — tom_FLOOR + snare_shallow hybrid."""

        builder = PatternBuilder("haake_catch32")
        # Hybrid blast-beat with snare_shallow texture
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.snare_shallow(pos, VELOCITY.SNARE_GHOST + 10)
        # FLOOR tom edge for low-end blast texture
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # Big crash_5/6 layering for blast punctuation
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_flesh_cadence(self) -> Pattern:
        """Flesh cadence — sparse devastating single hits (Haake's philosophy)."""

        builder = PatternBuilder("haake_flesh")
        # Only 3-4 hits, each with maximum impact (Haake's "sparse but devastating")
        builder.tom_edge(0.0, "FLOOR", VELOCITY.TOM_ACCENT)
        # Long space between hits
        builder.snare_rimshot(TIMING.HALF * 2, VELOCITY.SNARE_HEAVY)
        # ride_bell accent for atmospheric punctuation
        builder.ride_bell(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        # Final devastating FLOOR tom hit
        builder.tom(4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY)
        return builder.build()

    def _create_bleed_polyrhythm(self) -> Pattern:
        """Bleed polyrhythm — ride_bell/ride_shaft in non-traditional grid."""

        builder = PatternBuilder("haake_bleed")
        # Ride bell + shaft across non-traditional metric grid
        for i in range(7):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            if i % 2 == 0:
                builder.ride_bell(
                    pos, VELOCITY.RIDE_BELL_ACCENT - random.randint(-5, 10)
                )
            else:
                builder.ride_shaft(pos, VELOCITY.RIDE_NORMAL)
        # Sparse tom hits with rimshot texture
        builder.tom_edge(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY
        )
        # crash_choke for tight resolution
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3")
        return builder.build()
