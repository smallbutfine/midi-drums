"""Buddy Rich drummer plugin using full AD2 kit vocabulary for blazing fills.

Fills now use ALL toms in cascading paradiddles, snare_rimshot/snare_side_stick for
accent texture, crash(4-6) with cymbal_choke layering for dramatic punctuation, and
ride_bell/ride_shaft for big band swing timekeeping — matching his Krupa/Roach drum battle
vocabulary and big band solo sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
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
    - Extreme dynamic contrast, whisper-soft ghost notes to thunderous accents
    - Showmanship-driven, full-kit fills that build and release tension
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
        """Return Buddy Rich's signature fill patterns using full AD2 kit.

        Uses ALL toms in cascading paradiddles (RLRL across the full kit), snare_rimshot and
        snare_side_stick for accent texture, crash(4-6) with cymbal_choke layering for dramatic
        punctuation, and ride_bell/ride_shaft for big band swing timekeeping — matching his
        documented drum battle vocabulary and big band solo sound.
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
                pattern=self._create_big_band_swing_fill(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_cross_stick_snap_combo(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_paradiddle_tom_excursion(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_double_paradiddle_roll(),
                trigger_probability=0.65,
                section_position="middle",
            ),
        ]

    def _create_single_stroke_roll_fill(self) -> Pattern:
        """Single-stroke roll — rapid snare_rimshot crescendo across ALL toms."""

        builder = PatternBuilder("rich_single_stroke")
        # Rapid snare rimshot single-stroke speed (Rich's legendary speed)
        for i in range(16):
            pos = TIMING.EIGHTH_TRIPLET * i
            vel = VELOCITY.SNARE_HEAVY + random.randint(-5, 10) + (i // 4) * 3
            builder.snare_rimshot(pos, min(vel, 127))
        # tom cascading across ALL toms with rimshot texture
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom_edge(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # Big crash_6 resolution (dramatic showman punctuation)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_dynamic_cascade_fill(self) -> Pattern:
        """Dynamic cascade — ascending toms with swing dynamics + ride_bell accents."""

        builder = PatternBuilder("rich_dynamic_cascade")
        # Ascending tom cascade through ALL toms (HIGH → FLOOR) with dynamic swell
        for i in range(5):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i] if i < 4 else "FLOOR"
            vel = VELOCITY.TOM_NORMAL + (i * 8)
            builder.tom(pos, variant, min(vel, 127))
        # snare_rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # ride_bell + ride_shaft for swing timekeeping (big band style)
        builder.ride_bell(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # crash_5/6 double-layering (dramatic punctuation)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_showman_crash_fill(self) -> Pattern:
        """Showman crash — fast triplet buildup with ALL crashes (1-6)."""

        builder = PatternBuilder("rich_showman")
        # Fast triplet buildup using all toms (HIGH → FLOOR)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW"][i % 3]
            builder.tom(pos, variant, min(VELOCITY.TOM_HEAVY + (i * 5), 127))
        # snare_side_stick for accent texture
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 10)
        # ALL crashes cycled rapidly (showman drama — cymbal_1 through cymbal_6)
        for i in range(6):
            pos = TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.crash(pos, str(i + 1))
        return builder.build()

    def _create_drum_battle_fill(self) -> Pattern:
        """Drum battle fill — call-and-response with tom_FLOOR + snare_rimshot."""

        builder = PatternBuilder("rich_drum_battle")
        # Call-and-response pattern (documented Krupa/Roach drum battles)
        # "Call" — FLOOR tom accents
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.tom(
                pos, "FLOOR", VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # "Response" — snare_rimshot rapid-fire (Rich's single-stroke speed)
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            builder.snare_rimshot(
                pos, VELOCITY.SNARE_HEAVY + random.randint(-5, 10)
            )
        # tom cascading with rimshot texture across ALL toms
        for i in range(4):
            pos = TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # Big crash_4/5 double-punctuation (showman finish)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_big_band_swing_fill(self) -> Pattern:
        """Big Band swing solo fill — ascending toms with swing-pattern ride cadence."""

        builder = PatternBuilder("rich_big_band")
        # Ascending toms (HIGH → FLOOR) for swing feel
        for i in range(5):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i] if i < 4 else "FLOOR"
            builder.tom(pos, variant, min(VELOCITY.TOM_HEAVY + (i * 3), 127))
        # snare_rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # ride_bell + ride_shaft for swing timekeeping (big band era)
        builder.ride_bell(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            VELOCITY.RIDE_BELL_ACCENT,
        )
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # cymbal_5/6 dramatic punctuation (big band finale sound)
        builder.cymbal_open(4.0 - TIMING.SIXTEENTH, "5")
        builder.crash(4.0, "6")
        return builder.build()

    def _create_cross_stick_snap_combo(self) -> Pattern:
        """Cross-stick/snap combo — snare_side_stick + tom_1 rimshot interlock."""

        builder = PatternBuilder("rich_crossstick")
        # Dense snare side stick for snap texture (cross-stick as primary voice)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(3, 10)
            )
        # tom_1 rimshot accents for interlock (big band tradition)
        builder.tom_edge(TIMING.QUARTER, "1", VELOCITY.TOM_HEAVY)
        builder.tom_edge(TIMING.HALF, "1", VELOCITY.TOM_HEAVY - 3)
        # snare_rimshot + ride_bell resolution (swing punctuation)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_paradiddle_tom_excursion(self) -> Pattern:
        """Paradiddle tom excursion — RLRL pattern across ALL toms (big band tradition)."""

        builder = PatternBuilder("rich_paradiddle")
        # RLRL paradiddle pattern across all 4 toms (big band snare drum tradition)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # snare_rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # tom_edge final on FLOOR (deepest note of the excursion)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # Big crash_6 punctuation (showman finale)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_double_paradiddle_roll(self) -> Pattern:
        """Double paradiddle roll — RLLR/RRLL rapid snare-tom vocabulary."""

        builder = PatternBuilder("rich_double_paradiddle")
        # Rapid snare rimshot + tom edge interlock (RLLR/RRLL paradiddle pattern)
        for i in range(16):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i < 8:
                builder.snare_rimshot(
                    pos, VELOCITY.SNARE_HEAVY + random.randint(-5, 10)
                )
            else:
                variant = ["HIGH", "MID"][i % 2]
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # cymbal_open + crash_choked layering for dramatic punctuation
        builder.cymbal_open(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()
