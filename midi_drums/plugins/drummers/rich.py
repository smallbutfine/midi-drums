"""Buddy Rich drummer plugin.

Implements Buddy Rich's (big band/swing) signature drumming techniques:
virtuosic single-stroke speed, dramatic dynamic contrast (whisper-soft
ghost notes to thunderous accents), and showmanship-driven fill vocabulary.
Built using the composable DrummerModification system, matching the
pattern established by the other drummer plugins.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    FastChopsTriplets,
    GhostNoteLayer,
    HeavyAccents,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class RichPlugin(DrummerPlugin):
    """Buddy Rich drummer style plugin.

    Characteristics:
    - Virtuosic single-stroke speed across fast fill passages
    - Extreme dynamic contrast, whisper-soft ghost notes to thunderous
      accents
    - Showmanship-driven, full-kit fills that build and release tension

    Implemented using composable modifications:
    - FastChopsTriplets: rapid technical fill vocabulary
    - GhostNoteLayer: soft ghost notes providing the "whisper" end of the
      dynamic range
    - HeavyAccents: sharp accent contrast providing the "thunder" end of
      the dynamic range
    """

    def __init__(self):
        self.fast_chops = FastChopsTriplets(probability=0.35)
        self.ghost_notes = GhostNoteLayer(density=0.5)
        self.accents = HeavyAccents(accent_boost=18)

    @property
    def drummer_name(self) -> str:
        return "rich"

    @property
    def preferred_genres(self) -> list[str]:
        return ["jazz", "rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Buddy Rich's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_rich"

        styled = self.ghost_notes.apply(styled, intensity=0.6)
        styled = self.fast_chops.apply(styled, intensity=0.7)
        styled = self.accents.apply(styled, intensity=0.9)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Buddy Rich's signature fill patterns.

        Research-backed fills traceable to documented drum battles (Krupa, Roach)
        and Big Band era performances:
          - Single-stroke roll: rapid snare crescendo (Rich's single-stroke speed)
          - Dynamic cascade: descending snare-to-tom with swing dynamics
          - Showman crash: fast triplet buildup punctuated by dramatic crash
          - Drum battle vocabulary: call-and-response fill from documented battles
          - Big Band swing solo fill: ascending toms with swing-pattern ride cadence
          - Cross-stick/snap combo: tight rim-click/snare interlock
          - Paradiddle tom excursion: RLRL pattern across toms (big band tradition)
          - Double paradiddle roll: RLLR/RRLL rapid snare-tom vocabulary
        """
        return [
            Fill(
                pattern=self._create_single_stroke_roll_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_dynamic_cascade_fill(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_showman_crash_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_drum_battle_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_big_band_swing_solo_fill(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_cross_stick_snap_combo(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_paradiddle_tom_excursion(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_double_paradiddle_roll(),
                trigger_probability=0.65,
                section_position="middle",
            ),
        ]

    def _create_single_stroke_roll_fill(self) -> Pattern:
        """Rapid single-stroke snare roll with a rising dynamic curve.

        8 evenly spaced 32nd-note snare hits crescendo from a ghost-note
        whisper to a full accent, showcasing single-stroke speed and
        dynamic control in one breath.
        """
        builder = PatternBuilder("rich_single_stroke_roll")
        velocities = [
            VELOCITY.SNARE_GHOST,
            VELOCITY.SNARE_GHOST,
            VELOCITY.SNARE_LIGHT,
            VELOCITY.SNARE_LIGHT,
            VELOCITY.SNARE_NORMAL,
            VELOCITY.SNARE_NORMAL,
            VELOCITY.SNARE_HEAVY,
            VELOCITY.SNARE_ACCENT,
        ]
        for i, velocity in enumerate(velocities):
            position = i * TIMING.THIRTY_SECOND
            builder.snare(position, velocity)
        return builder.build()

    def _create_dynamic_cascade_fill(self) -> Pattern:
        """Descending snare-to-tom cascade with a soft-loud-soft-LOUD swing.

        Fills render only the portion of their pattern before beat 1.0
        (see midi_drums/export/midi/engine.py's fill-rendering gate), so
        the full cascade is packed into a single beat via 16th-note
        subdivision.
        """
        builder = PatternBuilder("rich_dynamic_cascade")
        builder.pattern.add_beat(
            0.0, DrumInstrument.SNARE, VELOCITY.SNARE_LIGHT
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH, DrumInstrument.MID_TOM, VELOCITY.TOM_ACCENT
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 2, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_HEAVY
        )
        builder.kick(TIMING.SIXTEENTH * 3, VELOCITY.KICK_ACCENT)
        return builder.build()

    def _create_showman_crash_fill(self) -> Pattern:
        """Fast triplet buildup punctuated by a dramatic crash accent.

        Kept entirely within beat 1.0 (see midi_drums/export/midi/engine.py's
        fill-rendering gate) - the climactic crash sits at 0.75, not exactly
        at 1.0, so it isn't silently dropped by the rendering boundary check.
        """
        builder = PatternBuilder("rich_showman_crash")
        builder.snare(0.0, VELOCITY.SNARE_NORMAL)
        builder.snare(TIMING.SIXTEENTH_TRIPLET, VELOCITY.SNARE_HEAVY)
        builder.snare(TIMING.SIXTEENTH_TRIPLET * 2, VELOCITY.SNARE_ACCENT)
        builder.kick(TIMING.DOTTED_EIGHTH, VELOCITY.KICK_ACCENT)
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_ACCENT)
        return builder.build()

    def _create_drum_battle_fill(self) -> Pattern:
        """Drum battle call-and-response fill.

        Rich's legendary drum battles (with Krupa, Roach) featured aggressive
        cross-stick/snare/crash interplay — short "calls" answered by loud responses.
        Simulated here as alternating rim-click and snare patterns with crash punctuation.
        """
        builder = PatternBuilder("rich_drum_battle")
        # Call-and-response within one beat (fits fill-render window)
        calls_and_responses = [
            (0.0, "rim", VELOCITY.SNARE_LIGHT),  # Rim-call
            (1 / 8, "snare", VELOCITY.SNARE_HEAVY),  # Loud response
            (2 / 8, "rim", VELOCITY.SNARE_LIGHT),  # Rim-call
            (3 / 8, "snare", VELOCITY.SNARE_ACCENT),  # Louder response
            (4 / 8, "rim", VELOCITY.SNARE_NORMAL),
            (5 / 8, "snare", min(127, VELOCITY.SNARE_HEAVY + 2)),
            (6 / 8, "rim", VELOCITY.SNARE_LIGHT),
            (7 / 8, "snare", VELOCITY.SNARE_ACCENT),
        ]
        for offset, instr_name, velocity in calls_and_responses:
            if instr_name == "rim":
                builder.pattern.add_beat(offset, DrumInstrument.RIM, velocity)
            else:
                builder.snare(offset, min(127, velocity))

        # Crash punctuation at resolution
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_ACCENT)
        return builder.build()

    def _create_big_band_swing_solo_fill(self) -> Pattern:
        """Big Band swing solo fill (Basie/Gillespie era)."""
        builder = PatternBuilder("rich_big_band_swing")
        # Ascending tom cascade packed into one beat (fills render < 1.0)
        for i in range(4):
            pos = TIMING.SIXTEENTH * i
            instrument = (
                DrumInstrument.MID_TOM
                if i % 2 == 0
                else DrumInstrument.FLOOR_TOM
            )
            velocity = min(VELOCITY.TOM_HEAVY + (i % 4) * 3, 127)
            builder.pattern.add_beat(pos, instrument, velocity)
        # Swing-pattern ride cadence (ding-ding-a-da on RIDE + bell accents)
        for i in range(4):
            pos = TIMING.SIXTEENTH * i
            if i % 2 == 0:
                builder.ride(pos, VELOCITY.RIDE_NORMAL)
                # Bell accent only when it fits within fill render window
                bell_pos = pos + TIMING.DOTTED_EIGHTH
                if bell_pos < 1.0:
                    builder.pattern.add_beat(
                        bell_pos,
                        DrumInstrument.RIDE_BELL,
                        VELOCITY.RIDE_BELL_ACCENT,
                    )
            else:
                builder.ride(pos, VELOCITY.RIDE_LIGHT)
        # Final crash accent at resolution (within fill window)
        builder.crash(TIMING.DOTTED_EIGHTH, min(VELOCITY.CRASH_ACCENT, 127))
        return builder.build()

    def _create_cross_stick_snap_combo(self) -> Pattern:
        """Cross-stick/snap tight rim-click and snare interlock.

        Rich's Big Band vocabulary featured rapid cross-stick (rim-click) patterns
        that cut through the band — simulating the snap and precision of his
        signature cross-stick technique.
        """
        builder = PatternBuilder("rich_cross_stick_snap")
        # Tight rim-click/snare alternation packed into one beat (fills render < 1.0)
        for i in range(8):
            pos = TIMING.THIRTY_SECOND * i  # 8 hits within <1.0 bar
            if i % 2 == 0:
                builder.pattern.add_beat(
                    pos, DrumInstrument.RIM, VELOCITY.SNARE_LIGHT
                )
            else:
                builder.snare(
                    pos, min(VELOCITY.SNARE_NORMAL + random.randint(0, 5), 127)
                )
        # Resolution crash (within fill window)
        builder.crash(TIMING.DOTTED_EIGHTH, min(VELOCITY.CRASH_ACCENT, 127))
        return builder.build()

    def _create_paradiddle_tom_excursion(self) -> Pattern:
        """Paradiddle tom excursion (RLRL across toms).

        Buddy Rich's paradigm-based vocabulary: the classic RLRL paradiddle
        pattern played sequentially across toms — a staple of big band drum
        solo technique. Simulated with alternating right/left voicings.
        """
        builder = PatternBuilder("rich_paradiddle_toms")
        # Paradiddle pattern (RLRL) packed into one beat (fills render < 1.0)
        paradiddle_voicings = [
            DrumInstrument.MID_TOM,
            DrumInstrument.MID_TOM,
            DrumInstrument.FLOOR_TOM,
            DrumInstrument.FLOOR_TOM,
        ]
        for i, tom in enumerate(paradiddle_voicings):
            pos = TIMING.SIXTEENTH * i
            vel = VELOCITY.TOM_NORMAL + (i % 2) * 5
            builder.pattern.add_beat(pos, tom, min(vel, 127))
        return builder.build()

    def _create_double_paradiddle_roll(self) -> Pattern:
        """Double paradiddle rapid snare-tom vocabulary (RLLR/RRLL).

        Rich's documented drum battle vocabulary featured double-paradiddle
        fills — alternating between snare and toms with RLLR/RRLL sticking.
        Simulated as a rapid four-stroke pattern across the kit.
        """
        builder = PatternBuilder("rich_double_paradiddle")
        # Four groups of double paradiddles packed into one beat (fills render < 1.0)
        for group in range(4):
            offset = TIMING.THIRTY_SECOND * group  # 4 subdivisions within <1.0
            if group % 2 == 0:
                # RLLR pattern: snare → mid tom → floor tom → snare
                builder.snare(offset, min(VELOCITY.SNARE_HEAVY, 127))
                builder.pattern.add_beat(
                    offset + TIMING.THIRTY_SECOND,
                    DrumInstrument.MID_TOM,
                    VELOCITY.TOM_ACCENT,
                )
                builder.pattern.add_beat(
                    offset + TIMING.THIRTY_SECOND * 2,
                    DrumInstrument.FLOOR_TOM,
                    VELOCITY.TOM_HEAVY,
                )
                builder.pattern.add_beat(
                    offset + TIMING.THIRTY_SECOND * 3,
                    min(VELOCITY.SNARE_ACCENT, 127),
                )
            else:
                # LRLR pattern: floor tom → mid tom → snare → tom edge
                builder.pattern.add_beat(
                    offset,
                    DrumInstrument.FLOOR_TOM,
                    VELOCITY.TOM_HEAVY,
                )
                builder.pattern.add_beat(
                    offset + TIMING.THIRTY_SECOND,
                    DrumInstrument.MID_TOM,
                    VELOCITY.TOM_ACCENT,
                )
                builder.snare(
                    offset + TIMING.THIRTY_SECOND * 2,
                    min(VELOCITY.SNARE_HEAVY, 127),
                )
                builder.tom_edge(
                    offset + TIMING.THIRTY_SECOND * 3,
                    "MID",
                    VELOCITY.TOM_LIGHT + random.randint(0, 5),
                )
        return builder.build()
