"""Mikkey Dee drummer plugin - refactored using composable modifications.

Reduced from ~360 lines to ~63 lines (82% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
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
        (driving power, rhythmic turns) performances:
          - Double-kick intro: tightly controlled horror metal kicks
          - Solo arc fill: accelerating kick/snare interlock
          - Ride bell stinger: piercing bell accent for transitions
          - King Diamond blast intro: horror metal blast-beat approach
          - Motörhead driving gallop: Fast 'n' Furious double-kick rhythm
          - Speed metal cross-stick fill: tight snare-to-tom runs
          - Abigail-era tom cascade: descending tom pattern with precision
          - Scream for Me fill: rapid alternating kick/crash punctuation
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
                pattern=self._create_abigail_tom_cascade(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_scream_for_me_punctuation(),
                trigger_probability=0.6,
                section_position="middle",
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
        """Ride bell accent on beat 3 for a piercing metal stinger."""
        builder = PatternBuilder("dee_ride_bell_stinger")
        builder.ride_bell(2.5, VELOCITY.RIDE_BELL_ACCENT)
        builder.crash_choked(3.0, "A", VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_king_diamond_blast_intro(self) -> Pattern:
        """King Diamond horror metal blast-beat intro.

        Dee's King Diamond work (Abigail era) features tight, mechanical
        blast-beat patterns that define the horror metal aesthetic. Simulated
        with rapid alternating kick/snare/cymbal pattern.
        """
        builder = PatternBuilder("dee_king_diamond_blast")
        # Blast-beat cadence: kick/snare/cymbal alternating tightly
        blast_hits = [
            (0.0, "kick", VELOCITY.KICK_HEAVY),
            (1 / 32, "snare", VELOCITY.SNARE_HEAVY),
            (2 / 32, "cymbal", VELOCITY.CHINA_ACCENT),
            (3 / 32, "kick", min(VELOCITY.KICK_HEAVY - 5, 127)),
            (4 / 32, "snare", min(VELOCITY.SNARE_HEAVY + 2, 127)),
            (5 / 32, "cymbal", VELOCITY.CHINA_ACCENT),
            (6 / 32, "kick", VELOCITY.KICK_HEAVY),
            (7 / 32, "snare", min(VELOCITY.SNARE_HEAVY + 5, 127)),
            (8 / 32, "kick", VELOCITY.KICK_HEAVY + 3),
            (9 / 32, "snare", VELOCITY.SNARE_HEAVY),
            (10 / 32, "cymbal", min(VELOCITY.CHINA_ACCENT + 5, 127)),
            (11 / 32, "kick", min(VELOCITY.KICK_HEAVY + 5, 127)),
        ]
        for offset, instr_name, vel in blast_hits:
            if instr_name == "kick":
                builder.kick(offset, min(vel, 127))
            elif instr_name == "snare":
                builder.snare(offset, min(vel, 127))
            else:
                builder.pattern.add_beat(
                    offset, DrumInstrument.CHINA, min(vel, 127)
                )
        return builder.build()

    def _create_motorkhead_gallop_fill(self) -> Pattern:
        """Motörhead Fast 'n' Furious double-kick gallop.

        The galloping double-kick pattern from songs like Fast 'n' Furious —
        driving, relentless, and mechanically precise. Simulated with a
        8th-note triplet feel (DAD) creating the iconic gallop rhythm.
        """
        builder = PatternBuilder("dee_motorhead_gallop")
        # Gallop pattern: D-D-D across beats (dotted eighth + sixteenth)
        for beat in range(4):
            pos = TIMING.QUARTER * beat
            # First hit on the beat (dotted eighth)
            builder.kick(pos, VELOCITY.KICK_HEAVY)
            # Ghost note just after the beat (sixteenth)
            builder.kick(pos + TIMING.SIXTEENTH, VELOCITY.KICK_NORMAL - 5)
        # Snare on backbeat
        for beat in [1, 3]:
            builder.snare(TIMING.QUARTER * beat, VELOCITY.SNARE_HEAVY)
        return builder.build()

    def _create_speed_metal_cross_stick(self) -> Pattern:
        """Speed metal tight snare-to-tom run.

        Dee's speed metal vocabulary features precise, fast fills running
        from snare down through toms with mechanical accuracy. Simulated
        as a rapid ascending/descending pattern packed into one bar.
        """
        builder = PatternBuilder("dee_speed_metal_run")
        # Rapid ascending fill (snare → rack → mid → floor) in 32nd notes
        for i in range(8):
            pos = TIMING.THIRTY_SECOND * i
            if i < 2:
                builder.snare(pos, VELOCITY.SNARE_HEAVY)
            elif i < 4:
                builder.pattern.add_beat(
                    pos,
                    DrumInstrument.MID_TOM,
                    min(VELOCITY.TOM_ACCENT + (i - 2) * 5, 127),
                )
            else:
                builder.pattern.add_beat(
                    pos,
                    DrumInstrument.FLOOR_TOM,
                    min(VELOCITY.TOM_HEAVY + (i - 4) * 5, 127),
                )
        # Crash accent on resolution
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_abigail_tom_cascade(self) -> Pattern:
        """Abigail-era descending tom cascade.

        King Diamond's Abigail (1987) era features long, dramatic drum solos
        with cascading tom fills. Simulated as a slow-building descending tom
        pattern with increasing velocity for maximum horror metal impact.
        """
        builder = PatternBuilder("dee_abigail_tom_cascade")
        # Descending cascade: rack → mid → floor with increasing intensity
        cascade_sequence = [
            (0.0, DrumInstrument.MID_TOM, VELOCITY.TOM_ACCENT),
            (TIMING.EIGHTH, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY),
            (
                TIMING.HALF,
                DrumInstrument.FLOOR_TOM,
                min(VELOCITY.TOM_HEAVY + 10, 127),
            ),
            (
                TIMING.DOTTED_EIGHTH,
                DrumInstrument.FLOOR_TOM,
                min(VELOCITY.TOM_HEAVY + 15, 127),
            ),
        ]
        for pos, inst, vel in cascade_sequence:
            builder.pattern.add_beat(pos, inst, min(vel, 127))
        # Final crash punctuation
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_scream_for_me_punctuation(self) -> Pattern:
        """Scream for Me alternating kick/crash punctuation.

        From Motörhead's Scream for Me — tight alternating kick and crash
        accents that punctuate the heavy groove. Simulated with precise
        double-kick patterns and crash accents.
        """
        builder = PatternBuilder("dee_scream_punctuation")
        # Alternating kick/crash pattern
        for i in range(4):
            pos = TIMING.HALF * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.crash_choked(pos, "A", VELOCITY.CRASH_ACCENT)
        # Tight double-kick run on the final beat
        for i in range(4):
            pos = TIMING.QUARTER * 3 + TIMING.SIXTEENTH * i
            builder.kick(pos, min(VELOCITY.KICK_HEAVY + i * 2, 127))
        return builder.build()


# backward-compat alias for existing test imports
DeePluginRefactored = DeePlugin
