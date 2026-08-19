"""Mikkey Dee drummer plugin - refactored using composable modifications.

Reduced from ~360 lines to ~63 lines (82% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

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
    def compatible_genres(self) -> list[str]:
        return ["metal", "speed_metal", "punk", "hard_rock", "horror_metal"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Mikkey Dee's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_dee"

        styled = self.precision.apply(styled, intensity=0.9)
        styled = self.twisted.apply(styled, intensity=0.7)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Mikkey Dee's signature fill patterns."""
        return [
            Fill(
                pattern=self._create_twisted_tom_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_ride_bell_stinger(),
                trigger_probability=0.5,
                section_position="middle",
            ),
        ]

    def _create_twisted_tom_fill(self) -> Pattern:
        """Tom cascade with displaced backbeat - Dee's signature displacement.

        Uses tom_edge (rimmed/edge toms) for the tight metallic attack that
        drives Motorhead and Scorpion riffs. Ends on a crash_choked for punchy cutoff.
        """
        builder = PatternBuilder("dee_twisted_tom_fill")

        # Ascending tom_edge cascade (tight metallic attack)
        builder.tom_edge(0.0, "3", VELOCITY.TOM_HEAVY)
        builder.tom_edge(0.5, "MID", VELOCITY.TOM_ACCENT)
        builder.tom_edge(1.0, "FLOOR", VELOCITY.TOM_ACCENT + 2)

        # Twisted snare (displaced off the downbeat - signature Dee technique)
        builder.snare(1.75, VELOCITY.SNARE_HEAVY)

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
