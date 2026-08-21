"""Mikkey Dee drummer plugin - refactored using composable modifications.

Reduced from ~360 lines to ~63 lines (82% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

import random

from midi_drums.config import VELOCITY
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

    Implemented using composable modifications:
    - SpeedPrecision: Normalizes velocities and tightens timing
    - TwistedAccents: Displaces accents to unexpected positions
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
        """Return Mikkey Dee's signature fill patterns.

        Based on documented King Diamond (horror metal precision) and Motörhead
        (driving power, rhythmic turns) performances.
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
        ]

    def _create_king_diamond_double_kick_intro(self) -> Pattern:
        """King Diamond era double-kick intro fill.

        Mickey Dee's King Diamond work (Fatal Portrait / Abigail era) features
        tightly controlled double-kick patterns that define horror metal's
        menacing atmosphere. Simulated with precise alternating kick voicings.
        """
        builder = PatternBuilder("dee_king_diamond_kick")

        # Alternating double-kick (8 notes in one beat)
        for i in range(8):
            pos = i * 0.25 / 2
            velocity = VELOCITY.KICK_HEAVY + random.randint(-10, 10)
            builder.kick(pos, min(velocity, 127))

        # Snare accent on the one of the next bar
        builder.snare(1.0, VELOCITY.SNARE_ACCENT)
        return builder.build()

    def _create_motorhead_solo_arc_fill(self) -> Pattern:
        """Motörhead solo arc fill.

        Documented on Sacrifice: "In the Name of Tragedy" and "The One to Sing
        the Blues" — Dee performs 5-15 minute drum solos where he builds from
        a single beat into cascading fills then collapses back. Simulated with
        accelerating kick/snare interlock across the bar.
        """
        builder = PatternBuilder("dee_motorhead_solo_arc")

        # Accelerating kick/snare interlock (within one bar)
        for i in range(16):
            pos = i * 0.25 / 4
            velocity = VELOCITY.KICK_NORMAL + i * 3
            builder.kick(pos, min(velocity, 127))
            if i % 2 == 0:
                builder.snare(
                    pos,
                    min(VELOCITY.SNARE_HEAVY + i * 2, 127),
                )

        # Crash punctuation at the end of the arc
        builder.crash(4.0, VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_ride_bell_stinger(self) -> Pattern:
        """Ride bell accent on beat 3 for a piercing metal stinger.

        AD2 ride_bell (note 61) gives the sharp bell attack that cuts through
        heavy guitar distortion - useful for power/speed metal transitions.
        """
        builder = PatternBuilder("dee_ride_bell_stinger")
        builder.ride_bell(2.5, VELOCITY.RIDE_BELL_ACCENT)
        builder.crash_choked(3.0, "A", VELOCITY.CRASH_HEAVY)

        return builder.build()


# backward-compat alias for existing test imports
DeePluginRefactored = DeePlugin
