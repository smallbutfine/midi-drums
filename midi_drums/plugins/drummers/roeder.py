"""Jason Roeder drummer plugin using full AD2 kit for atmospheric sludge fills.

Fills now use tom_FLOOR emphasis (deep cavernous sound), cymbal_choke(5-6) for sustained
crashes, tom_EDGE rimshots with heavy accents for crushing weight, snare_shallow for sparse
atmospheric textures, and ride_bell/ride_shaft with long sustain — matching his Neurosis
(Souls at Zero era) sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
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
        """Return Jason Roeder's signature fill patterns using full AD2 kit.

        Uses tom_FLOOR emphasis (deep cavernous sound), cymbal_choke(5-6) for sustained
        crashes, tom_EDGE rimshots with heavy accents for crushing weight, snare_shallow for
        sparse atmospheric textures, and ride_bell/ride_shaft with long sustain — matching
        his Neurosis (Souls at Zero era) sound.
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
                section_position="end",
            ),
            Fill(
                pattern=self._create_times_of_grace_tremolo(),
                trigger_probability=0.7,
                section_position="middle",
            ),
        ]

    def _create_atmospheric_tom_roll(self) -> Pattern:
        """Atmospheric tom roll — sparse FLOOR/LOW toms with cymbal_choke sustain."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_atmospheric")
        # Sparse, resonant FLOOR/LOW tom cascades (atmospheric sludge feel)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = "FLOOR" if i % 2 == 0 else "LOW"
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 5), 127),
            )
        # snare_shallow for sparse atmospheric texture
        builder.snare_shallow(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # cymbal_choke(6) for sustained cavernous crash (long sustain)
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_labyrinthine_fill(self) -> Pattern:
        """Labyrinthine complexity — winding toms across FULL KIT with ride_bell."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_labyrinthine")
        # Winding rhythmic motif using all 4 toms (HIGH → MID → LOW → FLOOR)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i % 3) * 5)
        # tom_EDGE rimshot with heavy accents for crushing weight
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_ACCENT)
        # ride_bell + ride_shaft for atmospheric timekeeping
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.ride_shaft(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_NORMAL)
        return builder.build()

    def _create_crushing_pattern(self) -> Pattern:
        """Crushing weight — single heavy hits with tom_FLOOR + cymbal_choke."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_crushing")
        # Only 3-4 hits, each with maximum crushing impact (Roeder's philosophy)
        builder.tom(0.0, "FLOOR", min(VELOCITY.TOM_HEAVY + 10, 127))
        builder.snare_rimshot(TIMING.HALF, VELOCITY.SNARE_HEAVY)
        # tom_EDGE rimshot on FLOOR with massive accent
        builder.tom_edge(
            TIMING.HALF * 3, "FLOOR", min(VELOCITY.TOM_HEAVY + 5, 127)
        )
        # cymbal_choke(6) for cavernous sustain (long crash tail)
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_minimal_kit_showcase(self) -> Pattern:
        """Minimal kit showcase — limited to FLOOR/LOW with crash_choke."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_minimal")
        # Only LOW and FLOOR toms (minimal kit for maximum impact)
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = "LOW" if i % 2 == 0 else "FLOOR"
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 15), 127),
            )
        # tom_EDGE rimshot for texture (minimal but devastating)
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # cymbal_choke(5) for tight atmospheric punctuation
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_souls_at_zero_buildup(self) -> Pattern:
        """Souls at Zero buildup — slow-building FLOOR/LOW tension with ride_bell."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_souls_zero")
        # Slow-building tom tension through LOW → FLOOR (Neurosis-era build)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = "LOW" if i < 4 else "FLOOR"
            vel = VELOCITY.TOM_NORMAL + (i // 2) * 5  # Gradual velocity swell
            builder.tom(pos, variant, min(vel, 127))
        # snare_shallow for atmospheric texture
        builder.snare_shallow(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # ride_bell + cymbal_choke layering (atmospheric punctuation)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_wounds_sludge_interlock(self) -> Pattern:
        """Wounds sludge interlock — heavy FLOOR/kick with tom_EDGE rimshots."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_wounds")
        # Heavy FLOOR toms locking with kick (sludge metal interlock)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
                builder.tom(pos, "FLOOR", VELOCITY.TOM_HEAVY)
            else:
                builder.tom(
                    pos, "LOW", VELOCITY.TOM_NORMAL + random.randint(-5, 10)
                )
        # tom_EDGE rimshot for crushing weight
        builder.tom_edge(
            TIMING.HALF * 3, "FLOOR", min(VELOCITY.TOM_ACCENT, 127)
        )
        # cymbal_choke(6) cavernous resolution
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_pain_of_always_ambient_fill(self) -> Pattern:
        """Pain of Always ambient pad — sustained cymbal with sparse hits."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_ambient")
        # Only 3-4 sparse hits (atmospheric ambient pad approach)
        builder.tom(0.0, "FLOOR", VELOCITY.TOM_HEAVY + random.randint(-5, 10))
        # snare_shallow for atmospheric texture (sparse but intentional)
        builder.snare_shallow(TIMING.HALF, VELOCITY.SNARE_GHOST + 5)
        # ride_bell + ride_shaft for sustained atmospheric timekeeping
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # cymbal_choke(6) for cavernous sustain (long crash tail)
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_times_of_grace_tremolo(self) -> Pattern:
        """Times of Grace tremolo — double-kick tremolo into cavernous toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("roeder_tremolo")
        # Double-kick tremolo (fast, mechanical precision like doom metal)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(
                pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
            )
        # Cavernous FLOOR/LOW toms with tom_EDGE texture
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = "FLOOR" if i < 2 else "LOW"
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # cymbal_choke(6) cavernous punctuation (long crash sustain)
        builder.crash_choked(TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()
