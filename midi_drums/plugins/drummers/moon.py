"""Keith Moon drummer plugin using full AD2 kit for explosive chaotic fills.

Fills now use ALL crashes (1-6), ALL toms cascading wildly, crash_choked for tight
punctuation, and snare_rimshot/snare_side_stick for his signature crash-heavy bombardment
style — matching his Who-era live performances with massive floor-tom arrays.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import BehindBeatTiming, HeavyAccents
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin

_CRYSTAL_VELOCITY = VELOCITY.HIHAT_NORMAL


class MoonPlugin(DrummerPlugin):
    """Keith Moon drummer style plugin.

    Characteristics:
    - Explosive, unpredictable tom fills (up to 5 floor toms in his setup)
    - Crash-heavy cymbal bombardment on every chord ("I play on every chord")
    - Loose, behind-the-beat timing — time as a suggestion
    - Dramatic dynamic contrasts (whisper-to-wall-of-sound)
    - Syncopated fills that occupy space between beats rather than on them
    - Minimal hi-hat/ride timekeeping; crash ride is his primary cymbal voice
    """

    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=30.0)
        self.accents = HeavyAccents(accent_boost=20)

    @property
    def drummer_name(self) -> str:
        return "moon"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "punk", "hard_rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Keith Moon's signature chaotic style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_moon"

        styled = self.behind_beat.apply(styled, intensity=0.85)
        styled = self.accents.apply(styled, intensity=0.95)
        styled = self._strip_timekeeping_cymbals(styled)
        max_new_beats = 10
        current_count = [0]

        def _track(n):
            if n > max(0, max_new_beats - current_count[0]):
                return max(0, max_new_beats - current_count[0])
            current_count[0] += n
            return n

        styled = self._add_crash_accent_layer(styled, _track)
        styled = self._add_tom_fill_between_beats(styled, _track)
        styled = self._add_downbeat_crash(styled)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Keith Moon's signature fill patterns using ALL crashes (1-6) and ALL toms.

        Chaotic fills spanning all 6 crash cymbals (cymbal_1 through cymbal_6), cascading
        tom fills across HIGH/MID/LOW/FLOOR, snare_rimshot/snare_side_stick for texture,
        and crash_choked for tight punctuation — matching his explosive Who-era style.
        """
        return [
            Fill(
                pattern=self._create_crash_barrage_fill(),
                trigger_probability=0.95,
                section_position="end",
            ),
            Fill(
                pattern=self._create_five_tom_cascade(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_chaotic_tom_crash_bombardment(),
                trigger_probability=0.9,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_wild_off_beat_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_solo_explosion_pattern(),
                trigger_probability=0.9,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_backbeat_crash_fill(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_who_tom_cascade(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_chaotic_groove_breakdown(),
                trigger_probability=0.8,
                section_position="middle",
            ),
        ]

    def _create_crash_barrage_fill(self) -> Pattern:
        """Crash barrage — ALL 6 crashes (cymbal_1 through cymbal_6) in rapid succession."""

        builder = PatternBuilder("moon_crash_barrage")
        # ALL crashes cycled rapidly (Moon's signature crash bombardment on every chord)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.crash(pos, str(i + 1))
        # tom_FLOOR accents between crashes
        for i in [2, 4]:
            pos = TIMING.HALF * i
            builder.tom(pos, "FLOOR", VELOCITY.TOM_HEAVY)
        # Snare rimshot for accent texture
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # Final crash_6 resolution (his biggest cymbal)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_five_tom_cascade(self) -> Pattern:
        """Five-tom cascade — ALL toms (HIGH→MID→LOW→FLOOR) with big crash_5/6 resolution."""

        builder = PatternBuilder("moon_five_tom")
        # Cascading tom fills through all 4 toms in rapid succession
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 20), 127),
            )
        # Snare side stick (cross-stick) for texture contrast
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # Big crash_5/6 double-hit resolution (Moon's signature big cymbal sound)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_chaotic_tom_crash_bombardment(self) -> Pattern:
        """Chaotic tom + crash bombardment — ALL toms alternating with ALL crashes."""

        builder = PatternBuilder("moon_chaotic_bomb")
        # Alternating toms and crashes for chaotic effect
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                variant = ["HIGH", "MID", "LOW", "FLOOR"][i // 2 % 4]
                builder.tom(
                    pos,
                    variant,
                    min(VELOCITY.TOM_HEAVY + random.randint(-15, 25), 127),
                )
            else:
                builder.crash(pos, str((i // 2) % 6 + 1))
        # Snare rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # Massive crash_4/5/6 layering (triple cymbal bombardment)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET * 2, "5")
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_wild_off_beat_fill(self) -> Pattern:
        """Wild off-beat fill — FLOOR/LOW toms with ALL crashes and snare_rimshot accents."""

        builder = PatternBuilder("moon_wild_offbeat")
        # Syncopated tom fills (Moon occupied space between beats, not on them)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1) + TIMING.SIXTEENTH / 2
            variant = "FLOOR" if i < 3 else "LOW"
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 20), 127),
            )
        # ALL crashes for bombardment (cymbal_1 → cymbal_5)
        for i in range(5):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.crash(pos, str(i + 1))
        # Snare rimshot accents for structure
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        return builder.build()

    def _create_solo_explosion_pattern(self) -> Pattern:
        """Solo explosion — tom_FLOOR + ALL crashes + snare_side_stick texture."""

        builder = PatternBuilder("moon_solo_explosion")
        # Deep FLOOR tom emphasis (Moon's massive floor-tom arrays)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.tom(
                pos,
                "FLOOR",
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 25), 127),
            )
            if i < 3:
                builder.tom(
                    pos + TIMING.SIXTEENTH, "LOW", VELOCITY.TOM_HEAVY - 5
                )
        # snare_side_stick for texture contrast (cross-stick amid chaos)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # ALL crashes from cymbal_2 to cymbal_6 (massive bombardment)
        for i in range(5):
            pos = TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.crash(pos, str(i + 2))
        return builder.build()

    def _create_backbeat_crash_fill(self) -> Pattern:
        """Backbeat crash fill — ALL toms with ALL crashes on every beat."""

        builder = PatternBuilder("moon_backbeat_crash")
        # Tom accents through all 4 toms (HIGH→MID→LOW→FLOOR cycling)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 20), 127),
            )
        # Crash on every beat (his "I play on every chord" philosophy)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            builder.crash(pos, str((i // 2) % 6 + 1))
        # Snare rimshot for accent punctuation
        builder.snare_rimshot(TIMING.QUARTER, VELOCITY.SNARE_HEAVY)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        return builder.build()

    def _create_who_tom_cascade(self) -> Pattern:
        """Who-era tom cascade — HIGH→MID→LOW→FLOOR with crash_choked punctuation."""

        builder = PatternBuilder("moon_who_cascade")
        # Cascading toms through all 4 (HIGH → FLOOR) repeated for explosive effect
        for bar in range(2):
            base = TIMING.HALF * bar
            for i in range(4):
                pos = base + TIMING.EIGHTH_TRIPLET * i
                variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
                vel = VELOCITY.TOM_HEAVY + (bar * 5)
                builder.tom(pos, variant, min(vel, 127))
        # Crash_choked for tight punctuation between cascades
        builder.crash_choked(TIMING.HALF + TIMING.EIGHTH_TRIPLET * 4, "3")
        # Massive crash_6 resolution (his biggest cymbal)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_chaotic_groove_breakdown(self) -> Pattern:
        """Chaotic groove breakdown — ALL crashes + snare_rimshot + tom_edge rimshots."""

        builder = PatternBuilder("moon_chaotic_breakdown")
        # Snare side stick (cross-stick) for texture beneath chaos
        builder.snare_side_stick(0.0, VELOCITY.SNARE_GHOST)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST)
        # Tom edge rimshots across ALL toms (rimshot-style chaotic fills)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 20), 127),
            )
        # ALL crashes cycled for bombardment (cymbal_1 → cymbal_6)
        for i in range(6):
            pos = TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET * (i // 2)
            builder.crash(pos, str((i // 2) % 6 + 1))
        return builder.build()
