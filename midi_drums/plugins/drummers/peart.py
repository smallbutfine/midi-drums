"""Neil Peart drummer plugin using full AD2 kit vocabulary for complex fills.

Fills now use ALL toms in polyrhythmic sequences, ALL crashes with cymbal_choke layering,
tom_edge rimshots for linear precision, ride_bell/ride_shaft for metronomic timekeeping,
snare_rimshot/snare_side_stick for accent texture, and cymbal_open for pitched cymbals —
matching his Rush-era massive kit (up to 42 pieces) with full-range articulations.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    LinearCoordination,
    SpeedPrecision,
    TripletVocabulary,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class PeartPlugin(DrummerPlugin):
    """Neil Peart drummer style plugin.

    Characteristics:
    - Extreme timing precision, metronomic yet musical
    - Linear coordination - sophisticated limb independence
    - Extensive polyrhythmic/triplet fill vocabulary across the full kit
    - Dramatic, full-kit fills punctuated by china cymbal
    """

    def __init__(self):
        self.linear = LinearCoordination()
        self.precision = SpeedPrecision(consistency=0.85)
        self.triplets = TripletVocabulary(triplet_probability=0.35)

    @property
    def drummer_name(self) -> str:
        return "peart"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "progressive", "metal"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Neil Peart's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_peart"

        styled = self.linear.apply(styled, intensity=0.7)
        styled = self.precision.apply(styled, intensity=0.9)
        styled = self.triplets.apply(styled, intensity=0.6)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Neil Peart's signature fill patterns using full AD2 kit.

        Uses ALL toms in polyrhythmic sequences, ALL crashes with cymbal_choke layering,
        tom_edge rimshots for linear precision, ride_bell/ride_shaft for metronomic timekeeping,
        snare_rimshot/snare_side_stick for accent texture, and cymbal_open for pitched cymbals —
        matching his Rush-era massive kit with full-range articulations.
        """
        return [
            Fill(
                pattern=self._create_quintuplet_tom_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_linear_precision_fill(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_china_punctuation_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_r30_riser_rotation_fill(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_malletkat_electronic_fill(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_swiss_army_triplets_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_polyrhythm_tom_rainbow(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_linear_full_kit_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
        ]

    def _create_quintuplet_tom_fill(self) -> Pattern:
        """Quintuplet tom cascade — polyrhythmic through ALL toms (HIGH→MID→LOW→FLOOR)."""

        builder = PatternBuilder("peart_quintuplet_tom")
        # Polyrhythmic quintuplet tom cascade across ALL toms
        for i in range(10):
            pos = TIMING.SIXTEENTH_QUINTUPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY + (i % 3) * 5)
        # snare_rimshot for linear accent (no simultaneous hits)
        builder.snare_rimshot(
            TIMING.HALF + TIMING.SIXTEENTH,
            VELOCITY.SNARE_RIMSHOT,
        )
        # tom_edge final hit on FLOOR
        builder.tom_edge(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY,
        )
        # ride_bell for metronomic precision punctuation
        builder.ride_bell(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_BELL_ACCENT)
        return builder.build()

    def _create_linear_precision_fill(self) -> Pattern:
        """Linear precision — no simultaneous limb hits using ALL kit elements."""

        builder = PatternBuilder("peart_linear")
        # Linear sequence (no simultaneous hits) across full kit
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom(TIMING.EIGHTH_TRIPLET, "HIGH", VELOCITY.TOM_NORMAL)
        builder.snare_rimshot(TIMING.EIGHTH_TRIPLET * 2, VELOCITY.SNARE_RIMSHOT)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY)
        builder.ride_bell(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET,
            VELOCITY.RIDE_BELL_ACCENT,
        )
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY)
        # tom_FLOOR + ride_bell resolution
        builder.tom(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY - 5,
        )
        builder.ride_bell(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_ACCENT)
        return builder.build()

    def _create_china_punctuation_fill(self) -> Pattern:
        """China punctuation — descending toms into cymbal_5 (china) + crash_choked."""

        builder = PatternBuilder("peart_china")
        # Descending tom cascade (HIGH → FLOOR) with snare_rimshot accents
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 3))
        # snare_rimshot for linear accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # cymbal_5 as china cymbal (Peart's signature china punctuation)
        builder.cymbal_open(TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "5")
        # crash_choked for tight resolution
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3")
        return builder.build()

    def _create_r30_riser_rotation_fill(self) -> Pattern:
        """R30 riser rotation — 4-tom cascade through HIGH/MID/LOW/FLOOR with crash_6."""

        builder = PatternBuilder("peart_r30")
        # Full ascending/descending tom pattern (Rush's rotating-riser kit)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            vel = VELOCITY.TOM_HEAVY + (i // 2) * 5
            builder.tom(pos, variant, min(vel, 127))
        # snare_rimshot for accent texture
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # tom_edge final hit on FLOOR (deepest note of the cascade)
        builder.tom_edge(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY,
        )
        # crash_6 resolution (biggest cymbal for dramatic punctuation)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_malletkat_electronic_fill(self) -> Pattern:
        """MalletKAT electronic fill — snare_shallow + tom_edge metallic texture."""

        builder = PatternBuilder("peart_malletkat")
        # snare_shallow for synthetic rim texture (MalletKAT electronic percussion)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_shallow(
                pos, VELOCITY.SNARE_GHOST + random.randint(5, 15)
            )
        # tom_edge rimshots as metallic resonance (simulating electronic pads)
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # ride_shaft for metronomic timekeeping (Peart's precision)
        builder.ride_shaft(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            VELOCITY.RIDE_NORMAL,
        )
        return builder.build()

    def _create_swiss_army_triplets_fill(self) -> Pattern:
        """Swiss Army triplets — rapid snare/tom with cymbal_4/5 punctuation."""

        builder = PatternBuilder("peart_swiss_army")
        # Rapid snare/tom triplet rolls (Swiss Army Snare Roll technique)
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i < 6:
                builder.snare_rimshot(
                    pos, VELOCITY.SNARE_HEAVY + random.randint(-5, 10)
                )
            else:
                variant = ["HIGH", "MID"][i % 2]
                builder.tom(pos, variant, VELOCITY.TOM_HEAVY)
        # cymbal_4/5 layering for dramatic punctuation
        builder.cymbal_open(TIMING.HALF * 3, "4")
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        return builder.build()

    def _create_polyrhythm_tom_rainbow(self) -> Pattern:
        """Polyrhythm tom rainbow — ALL toms in ascending sequence with ride_bell."""

        builder = PatternBuilder("peart_tom_rainbow")
        # Ascending tom sequence through all 4 (HIGH → FLOOR) — "tom rainbow"
        for i in range(5):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i] if i < 4 else "FLOOR"
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY + (i * 3))
        # snare_side_stick for linear accent texture
        builder.snare_side_stick(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET,
            VELOCITY.SNARE_GHOST,
        )
        # ride_bell/ride_shaft polyrhythmic punctuation
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # tom_FLOOR final accent + crash_choked resolution
        builder.tom_edge(4.0 - TIMING.SIXTEENTH, "FLOOR", VELOCITY.TOM_HEAVY)
        builder.crash_choked(4.0, "3")
        return builder.build()

    def _create_linear_full_kit_fill(self) -> Pattern:
        """Linear full-kit fill — no simultaneous hits using ALL kit elements."""

        builder = PatternBuilder("peart_linear_full_kit")
        # Linear sequence across full kit (kick → toms → snare_rimshot → rides → crashes)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom(TIMING.EIGHTH_TRIPLET, "HIGH", VELOCITY.TOM_NORMAL)
        builder.tom(TIMING.EIGHTH_TRIPLET * 2, "MID", VELOCITY.TOM_HEAVY)
        builder.snare_rimshot(
            TIMING.HALF,
            VELOCITY.SNARE_RIMSHOT,
        )
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "LOW", VELOCITY.TOM_HEAVY
        )
        builder.ride_bell(
            TIMING.HALF * 3,
            VELOCITY.RIDE_BELL_ACCENT,
        )
        builder.tom_edge(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY,
        )
        builder.snare_side_stick(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET * 2,
            VELOCITY.SNARE_GHOST,
        )
        # cymbal_6 (largest) for dramatic punctuation
        builder.cymbal_open(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()
