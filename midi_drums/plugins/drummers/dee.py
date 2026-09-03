"""Mikkey Dee drummer plugin using full AD2 vocabulary for metal precision.

Fills now use tom_edge rimshots for precise hits, crash(4-6) for big Metallica-style
cymbal punctuation, snare_rimshot for accent texture, and ride_bell/ride_shaft for
tight rhythmic work matching his King Diamond / Motörhead sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    SpeedPrecision,
    TwistedAccents,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class DeePlugin(DrummerPlugin):
    """Mikkey Dee drummer style plugin.

    Characteristics:
    - Speed and precision (Motorhead, Scorpions)
    - Versatile power across rock and metal
    - Twisted, displaced backbeats for interest
    - Extremely consistent timing and dynamics
    """

    def __init__(self):
        self.precision = SpeedPrecision(consistency=0.95)
        self.twisted = TwistedAccents(displacement=0.25)

    @property
    def drummer_name(self) -> str:
        return "dee"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "speed_metal", "punk", "hard_rock", "horror_metal"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Mikkey Dee's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_dee"

        styled = self.precision.apply(styled, intensity=0.9)
        styled = self.twisted.apply(styled, intensity=0.7)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Mikkey Dee's signature fill patterns using full AD2 kit.

        Uses tom_edge rimshots for precision hits, crash(4-6) for big cymbal
        punctuation, snare_rimshot for accent texture, and ride_bell/ride_shaft
        for tight rhythmic work — matching his King Diamond / Motörhead sound.
        """
        return [
            Fill(
                pattern=self._create_king_diamond_double_kick_intro(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_motorhead_solo_arc_fill(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_ride_bell_stinger(),
                trigger_probability=0.5,
                section_position="end",
            ),
            Fill(
                pattern=self._create_king_diamond_blast_intro(),
                trigger_probability=0.8,
                section_position="start",
            ),
            Fill(
                pattern=self._create_motorkhead_gallop_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_speed_metal_cross_stick(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_abigail_era_tom_cascade(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_scream_for_me_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
        ]

    def _create_king_diamond_double_kick_intro(self) -> Pattern:
        """King Diamond double-kick intro — tom_edge precision + crash_4/5."""

        builder = PatternBuilder("dee_king_diamond_kick")
        # Tightly controlled double-kick
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(pos, VELOCITY.KICK_HEAVY - (i % 2) * 10)
        # tom_edge rimshots for precision punctuation
        builder.tom_edge(TIMING.HALF * 3, "HIGH", VELOCITY.TOM_HEAVY)
        builder.tom_edge(4.0 - TIMING.SIXTEENTH, "LOW", VELOCITY.TOM_HEAVY)
        # Big crash_4/5 layering (King Diamond era big kit)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_motorhead_solo_arc_fill(self) -> Pattern:
        """Motörhead solo arc — accelerating kick/snare + ride_bell stinger."""

        builder = PatternBuilder("dee_motorhead_arc")
        # Accelerating double-kick into snare rimshot
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            velocity = VELOCITY.KICK_HEAVY + (i * 3) % 20
            builder.kick(pos, min(velocity, 127))
        # Snare rimshot for accent punch (Motörhead's driving style)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # Ride bell stinger resolution
        builder.ride_bell(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_BELL_ACCENT)
        return builder.build()

    def _create_ride_bell_stinger(self) -> Pattern:
        """Ride bell stinger — ride_bell + tom_edge precision fills."""

        builder = PatternBuilder("dee_ride_bell_stinger")
        # Ride bell for piercing stinger (Metallica-style big kit bells)
        builder.ride_bell(0.0, VELOCITY.RIDE_BELL_ACCENT)
        # tom_edge rimshots across ALL toms for precision
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY - (i * 3))
        # Snare rimshot + crash_5 punctuated resolution
        builder.snare_rimshot(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_HEAVY)
        builder.crash(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_king_diamond_blast_intro(self) -> Pattern:
        """King Diamond blast intro — double-kick into tom_edge cascade."""

        builder = PatternBuilder("dee_king_diamond_blast")
        # Blast-beat style double-kick
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(pos, VELOCITY.KICK_HEAVY - (i % 3) * 5)
        # tom_edge rimshot cascade across ALL toms
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # Big crash_6 resolution (his biggest cymbal)
        builder.crash(TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_motorkhead_gallop_fill(self) -> Pattern:
        """Motörhead gallop fill — double-kick with tom_FLOOR emphasis."""

        builder = PatternBuilder("dee_moto_gallop")
        # Motörhead-style driving gallop rhythm
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            is_doubled = i % 3 == 0
            vel = VELOCITY.KICK_HEAVY if is_doubled else VELOCITY.KICK_NORMAL
            builder.kick(pos, min(vel + random.randint(-5, 10), 127))
        # FLOOR tom edge rimshot for low-end punch
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # Crash_4 punctuated resolution
        builder.crash(4.0 - TIMING.SIXTEENTH, "4")
        return builder.build()

    def _create_speed_metal_cross_stick(self) -> Pattern:
        """Speed metal cross-stick fill — snare_side_stick + tom_edge rimshots."""

        builder = PatternBuilder("dee_speed_metal_cstick")
        # Snare side stick (cross-stick) for tight rhythmic texture
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(-3, 5)
            )
        # tom_edge rimshots across HIGH and MID (speed metal precision)
        builder.tom_edge(TIMING.HALF * 3, "HIGH", VELOCITY.TOM_HEAVY)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY - 5
        )
        # Big crash_5 punctuation
        builder.crash(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_abigail_era_tom_cascade(self) -> Pattern:
        """Abigail-era tom cascade — descending toms with snare_rimshot accents."""

        builder = PatternBuilder("dee_abigail_cascade")
        # Descending tom pattern through ALL toms (Abigail era big kit)
        for i in range(5):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 5))
        # Snare rimshot for accent texture
        builder.snare_rimshot(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_RIMSHOT
        )
        # tom_edge final hit on FLOOR
        builder.tom_edge(4.0 - TIMING.SIXTEENTH, "FLOOR", VELOCITY.TOM_HEAVY)
        # Big crash_6 resolution
        builder.crash(4.0, "6")
        return builder.build()

    def _create_scream_for_me_fill(self) -> Pattern:
        """Scream for Me fill — alternating kick/crash with ride_bell stingers."""

        builder = PatternBuilder("dee_scream_for_me")
        # Alternating kick and snare rimshot (fast n' furious style)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(
                    pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
                )
            else:
                builder.snare_rimshot(pos, min(VELOCITY.SNARE_HEAVY, 127))
                builder.snare_rimshot(
                    pos, min(VELOCITY.SNARE_HEAVY + random.randint(-5, 10), 127)
                )
        # Ride bell stinger for transition punctuation
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        # Big crash_4/5 layering (Metallica-style double cymbal hit)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()
