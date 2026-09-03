"""Chad Smith drummer plugin using full AD2 kit for RHCP funk-rock style.

Fills now use ALL toms (HIGH/MID/LOW/FLOOR) for massive tom fills, snare_rimshot/snare_side_stick
for funk groove texture, crash(4-6) + cymbal_open layering for RHCP big cymbal sound, and
tight_hh + ride_bell for tight pocket timekeeping — matching his RHCP / Chickenfoot sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.modifications import (
    BehindBeatTiming,
    FastChopsTriplets,
    GhostNoteLayer,
    HeavyAccents,
    PocketStretching,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class SmithPlugin(DrummerPlugin):
    """Chad Smith drummer style plugin.

    Characteristics:
    - Funk-rock fusion groove — deep pocket with hard rock power
    - Heavy snare ghost notes (P-Funk lineage via Larry Fratangelo)
    - Fast double-bass technique (Buddy Rich / Bonham influence)
    - Syncopated kick patterns locking with bass guitar
    - Massive tom fills across large drum kits
    - Behind-the-beat pocket feel with driving forward motion
    """

    def __init__(self):
        self.ghost_notes = GhostNoteLayer(density=0.75)  # Heavy ghost notes
        self.behind_beat = BehindBeatTiming(max_delay_ms=18.0)
        self.accents = HeavyAccents(accent_boost=20)
        self.fast_chops = FastChopsTriplets(probability=0.35)
        self.pocket = PocketStretching(variation_ms=6.0)

    @property
    def drummer_name(self) -> str:
        return "chadsmith"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "funk", "alternative", "hard_rock", "funk_rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Chad Smith's signature funk-rock style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_chadsmith"

        styled = self.ghost_notes.apply(styled, intensity=0.8)
        styled = self.behind_beat.apply(styled, intensity=0.5)
        styled = self.accents.apply(styled, intensity=0.7)
        styled = self.fast_chops.apply(styled, intensity=0.6)
        styled = self.pocket.apply(styled, intensity=0.6)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Chad Smith's signature fill patterns using full AD2 kit.

        Uses ALL toms (HIGH/MID/LOW/FLOOR) for massive tom fills, snare_rimshot/snare_side_stick
        for funk groove texture, crash(4-6) + cymbal_open layering for RHCP big cymbal sound, and
        tight_hh + ride_bell for tight pocket timekeeping — matching his RHCP / Chickenfoot sound.
        """
        return [
            Fill(
                pattern=self._create_give_it_away_funk_fill(),
                trigger_probability=0.9,
                section_position="start",
            ),
            Fill(
                pattern=self._create_cant_stop_gallop_fill(),
                trigger_probability=0.85,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_dani_california_drive_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_under_the_bridge_sparse_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_snowjob_chickenfoot_fill(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_bombastic_meatbats_funk_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_rhcp_live_one_drop_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_fast_hand_chops_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
        ]

    def _create_give_it_away_funk_fill(self) -> Pattern:
        """Give It Away funk fill — syncopated kick + snare_side_stick + ALL toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_give_it_away")
        # Syncopated kick locked with bass (RHCP signature lock)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 3 == 0:
                builder.kick(
                    pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
                )
            else:
                # Snare side stick (ghost note groove texture)
                builder.snare_side_stick(
                    pos, VELOCITY.SNARE_GHOST + random.randint(3, 8)
                )
        # tom cascading across ALL toms (massive RHCP kit sound)
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 3))
        # tight_hh + crash_4/5 layering (RHCP big cymbal sound)
        builder.tight_hh(4.0 - TIMING.EIGHTH_TRIPLET, open=True)
        builder.crash(4.0 - TIMING.SIXTEENTH, "4")
        return builder.build()

    def _create_cant_stop_gallop_fill(self) -> Pattern:
        """Can't Stop gallop — double-kick + snare_ghost notes + tom_FLOOR accent."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_cant_stop")
        # Double-kick gallop (signature Can't Stop rhythm)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(
                pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
            )
        # snare_side_stick ghost notes (funk groove texture)
        for i in [2, 5]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(pos, VELOCITY.SNARE_GHOST + 5)
        # tom_MID + FLOOR accents for funk-tom vocabulary
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY
        )
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # ride_bell for funk rhythm punctuation
        builder.ride_bell(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_BELL_ACCENT)
        return builder.build()

    def _create_dani_california_drive_fill(self) -> Pattern:
        """Dani California driving rock — ALL toms with heavy snare_rimshot accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_dani_california")
        # Driving tom cascade through ALL toms (RHCP forward motion)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # snare_rimshot for hard rock accent texture
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # tom_EDGE rimshot on FLOOR (low-end punch)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # Big crash_5/6 layering (RHCP big cymbal sound)
        builder.crash(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_under_the_bridge_sparse_fill(self) -> Pattern:
        """Under the Bridge sparse atmospheric — FLOOR/LOW toms + ride_bell."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_under_bridge")
        # Sparse but powerful (minimal tom work with maximum impact)
        builder.tom(0.0, "FLOOR", min(VELOCITY.TOM_HEAVY + 15, 127))
        # ride_bell for atmospheric timekeeping (sparse RHCP era feel)
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * (i + 2)
            builder.ride_bell(pos, VELOCITY.RIDE_BELL_ACCENT - (i * 3))
        # tom_LOW accent with heavy accent
        builder.tom(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY - 5)
        # cymbal_open + crash_choke layering for sparse punctuation
        builder.cymbal_open(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3")
        return builder.build()

    def _create_snowjob_chickenfoot_fill(self) -> Pattern:
        """Snowjob Chickenfoot — massive tom fills across ALL toms + crash_6."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_snowjob")
        # Massive tom fills across ALL toms (Chickenfoot's hard rock power)
        for i in range(10):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-5, 20), 127),
            )
        # snare_rimshot for hard rock accent texture
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # tom_EDGE rimshot on FLOOR (deepest punch)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY + 10
        )
        # Big crash_6 resolution (Chickenfoot's massive cymbal sound)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_bombastic_meatbats_funk_fill(self) -> Pattern:
        """Bombastic Meatbats funk — ALL toms + snare_side_stick funk groove."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_bombastic")
        # Funk-tom vocabulary across ALL toms (RHCP funk mastery)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # snare_side_stick for funk groove texture (P-Funk lineage)
        for i in [1, 3, 5]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(3, 8)
            )
        # tom_MID + FLOOR accents + ride_bell resolution
        builder.tom(TIMING.HALF * 3, "MID", VELOCITY.TOM_HEAVY)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_rhcp_live_one_drop_fill(self) -> Pattern:
        """RHCP live one-drop — deep pocket with tom_FLOOR + crash_4/5."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_one_drop")
        # Deep pocket groove (one-drop feel with double-bass accent)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 3 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.tom(
                    pos, "FLOOR", VELOCITY.TOM_HEAVY + random.randint(-5, 10)
                )
        # snare_side_stick for pocket texture (behind-the-beat feel)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # tom_FLOOR edge + crash_4/5 punctuated resolution
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        builder.crash(4.0 - TIMING.SIXTEENTH, "4")
        return builder.build()

    def _create_fast_hand_chops_fill(self) -> Pattern:
        """Fast hand chops — Buddy Rich-style rapid-fire snare/tom vocabulary."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("smith_fast_chops")
        # Rapid snare rimshot (Buddy Rich single-stroke speed influence)
        for i in range(16):
            pos = TIMING.EIGHTH_TRIPLET * i
            vel = VELOCITY.SNARE_HEAVY + random.randint(-5, 10) + (i // 4) * 3
            builder.snare_rimshot(pos, min(vel, 127))
        # Tom cascading with rimshot texture across HIGH/MID → LOW/FLOOR
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = "HIGH" if i < 2 else "LOW"
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # tom_FLOOR final accent + crash_6 punctuation (massive finish)
        builder.tom(
            4.0 - TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            min(VELOCITY.TOM_HEAVY + 15, 127),
        )
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()
