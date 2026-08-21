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
        """Winding rhythmic motif."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_labyrinthine")
        # Non-linear accent placement
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom_edge(TIMING.EIGHTH + TIMING.SIXTEENTH, "4", VELOCITY.TOM_ACCENT)
        builder.snare(TIMING.HALF, VELOCITY.SNARE_LIGHT)
        builder.kick(TIMING.DOTTED_EIGHTH * 2, VELOCITY.KICK_NORMAL)
        builder.tom_edge(
            TIMING.QUARTER * 3 + TIMING.EIGHTH_TRIPLET,
            "3",
            VELOCITY.TOM_HEAVY,
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
        builder.pattern.add_beat(TIMING.HALF, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_ACCENT)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH,
            DrumInstrument.FLOOR_TOM,
            min(VELOCITY.TOM_HEAVY + 5, 127),
        )
        return builder.build()


# backward-compat alias for existing test imports
RoederPluginRefactored = RoederPlugin
