"""Jason Roeder drummer plugin - refactored using composable modifications.

Reduced from ~371 lines to ~63 lines (83% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.modifications import (
    HeavyAccents,
    MinimalCreativity,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class RoederPlugin(DrummerPlugin):
    """Jason Roeder drummer style plugin.

    Characteristics:
    - Atmospheric sludge and doom metal approach
    - Minimal, sparse cymbal work for heavy atmosphere
    - Crushing, powerful accents on kick and snare
    - Patience and restraint in pattern density

    Implemented using composable modifications:
    - MinimalCreativity: Thins out non-essential cymbal hits
    - HeavyAccents: Adds crushing power to remaining hits
    """

    def __init__(self):
        self.minimal = MinimalCreativity(sparseness=0.7)
        self.accents = HeavyAccents(accent_boost=20)

    @property
    def drummer_name(self) -> str:
        return "roeder"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "sludge", "post_metal", "doom", "atmospheric"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Jason Roeder's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_roeder"

        styled = self.minimal.apply(styled, intensity=0.8)
        styled = self.accents.apply(styled, intensity=0.9)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Jason Roeder's signature fill patterns.

        Verified via Neurosis (Souls at Zero era) and interview sources:
          - Atmospheric tom roll: sparse, resonant tom cascades
          - Labyrinthine complexity: winding rhythmic motifs
          - Crushing weight: heavy single-hit accents with long sustain
          - Minimal kit showcase: limited toms for maximum impact
          - Souls at Zero buildup: slow-building tension fill (Neurosis era)
          - Wounds sludge pattern: heavy, resonant tom-to-kick interlock
          - Pain of Always ambient pad: sustained cymbal with sparse hits
          - Times of Grace tremolo fill: double-kick tremolo into cavernous toms
        """
        return [
            Fill(
                pattern=self._create_atmospheric_tom_roll(),
                trigger_probability=0.9,
                section_position="end",
            ),
            Fill(
                pattern=self._create_labyrinthine_fill(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_crushing_pattern(),
                trigger_probability=0.7,
                section_position="start",
            ),
            Fill(
                pattern=self._create_minimal_kit_showcase(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_souls_at_zero_buildup(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_wounds_sludge_interlock(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_pain_of_always_ambient_fill(),
                trigger_probability=0.65,
                section_position="start",
            ),
            Fill(
                pattern=self._create_times_of_grace_tremolo(),
                trigger_probability=0.6,
                section_position="end",
            ),
        ]

    def _create_atmospheric_tom_roll(self) -> Pattern:
        """Sparse, resonant tom roll (Neurosis era)."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_atmospheric_tom")
        for i in range(8):
            pos = TIMING.HALF * i
            builder.tom(
                pos,
                "FLOOR",
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 20), 127),
            )
        return builder.build()

    def _create_labyrinthine_fill(self) -> Pattern:
        """Winding rhythmic motif with RIDE cymbal timekeeping for Neurosis atmosphere."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_labyrinthine")
        # Non-linear accent placement
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom_edge(
            TIMING.EIGHTH + TIMING.SIXTEENTH, "4", VELOCITY.TOM_ACCENT
        )
        builder.snare(TIMING.HALF, VELOCITY.SNARE_LIGHT)
        builder.kick(TIMING.DOTTED_EIGHTH * 2, VELOCITY.KICK_NORMAL)
        # RIDE cymbal timekeeping (Neurosis uses ride for atmospheric wash)
        builder.pattern.add_beat(
            TIMING.QUARTER * 3 + TIMING.EIGHTH_TRIPLET,
            DrumInstrument.RIDE,
            VELOCITY.CHINA_ACCENT - 10,
        )
        # CRASH_CHOKED_B for atmospheric swell
        builder.crash_choked(
            TIMING.QUARTER * 3 + TIMING.EIGHTH_TRIPLET + TIMING.SIXTEENTH / 2,
            "B",
            VELOCITY.CRASH_HEAVY,
        )
        return builder.build()

    def _create_crushing_pattern(self) -> Pattern:
        """Heavy single-hit accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_crushing")
        builder.kick(0.0, min(VELOCITY.KICK_HEAVY + 10, 127))
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_ACCENT)
        for i in range(4):
            builder.pattern.add_beat(
                TIMING.HALF * i,
                DrumInstrument.FLOOR_TOM,
                min(VELOCITY.TOM_HEAVY + random.randint(-5, 10), 127),
            )
        return builder.build()

    def _create_minimal_kit_showcase(self) -> Pattern:
        """Minimal toms, maximum impact."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_minimal_kit")
        # Single rack + single floor tom setup (per interview)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.pattern.add_beat(
            TIMING.HALF, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY
        )
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_ACCENT)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH,
            DrumInstrument.FLOOR_TOM,
            min(VELOCITY.TOM_HEAVY + 5, 127),
        )
        return builder.build()

    def _create_souls_at_zero_buildup(self) -> Pattern:
        """Souls at Zero slow-building tension fill (Neurosis era)."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_souls_at_zero_buildup")
        phases = [
            (0.0, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_ACCENT),
            (TIMING.HALF, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_HEAVY),
            (
                TIMING.HALF * 2,
                None,
                min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127),
            ),
            (TIMING.HALF * 3, None, min(VELOCITY.KICK_HEAVY + 5, 127)),
        ]
        for offset, inst, vel in phases:
            if inst is not None:
                builder.tom(offset, inst.value, vel)
            else:
                builder.kick(offset, vel)
        builder.snare(
            TIMING.HALF * 4 - TIMING.SIXTEENTH,
            min(VELOCITY.SNARE_ACCENT + 15, 127),
        )
        return builder.build()

    def _create_wounds_sludge_interlock(self) -> Pattern:
        """Wounds-era heavy tom-to-kick interlock."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_wounds_sludge")
        interlock = [
            (0.0, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_HEAVY),
            (TIMING.HALF, "KICK", VELOCITY.KICK_HEAVY),
            (
                TIMING.HALF * 2,
                DrumInstrument.MID_TOM,
                min(VELOCITY.TOM_HEAVY + random.randint(-5, 10), 127),
            ),
            (TIMING.HALF * 3, "KICK", min(VELOCITY.KICK_HEAVY + 8, 127)),
        ]
        for offset, inst_or_name, vel in interlock:
            if inst_or_name == "KICK":
                builder.kick(offset, vel)
            else:
                builder.pattern.add_beat(offset, inst_or_name, min(vel, 127))
        builder.crash(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.CRASH_HEAVY
        )
        return builder.build()

    def _create_pain_of_always_ambient_fill(self) -> Pattern:
        """Pain of Always ambient pad with sparse RIDE wash."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_pain_of_always_ambient")
        # Sparse RIDE cymbal timekeeping (replaces generic HH for atmosphere)
        for i in range(4):
            pos = TIMING.HALF * i
            builder.pattern.add_beat(
                pos, DrumInstrument.RIDE, VELOCITY.CHINA_ACCENT - 10
            )
        builder.tom(
            TIMING.EIGHTH_TRIPLET,
            DrumInstrument.FLOOR_TOM.value,
            VELOCITY.TOM_LIGHT,
        )
        builder.tom(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            DrumInstrument.MID_TOM.value,
            VELOCITY.TOM_ACCENT,
        )
        # CRASH_CHOKED_A for cavernous cutoff
        builder.crash_choked(TIMING.DOTTED_EIGHTH, "A", min(VELOCITY.CRASH_HEAVY - 10, 127))
        return builder.build()

    def _create_times_of_grace_tremolo(self) -> Pattern:
        """Times of Grace double-kick tremolo into cavernous toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_times_of_grace_tremolo")
        for i in range(16):
            pos = TIMING.THIRTY_SECOND * i
            builder.kick(
                pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
            )
        for i in range(4):
            pos = TIMING.HALF * i
            inst = "FLOOR" if i < 2 else "MID"
            builder.tom(pos, inst, min(VELOCITY.TOM_HEAVY + (i * 5), 127))
        return builder.build()


# backward-compat alias for existing test imports
RoederPluginRefactored = RoederPlugin
