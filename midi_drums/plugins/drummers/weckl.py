"""Dave Weckl drummer plugin using full AD2 kit vocabulary for linear jazz-fusion.

Fills now use ALL toms in linear sequences (no simultaneous limb hits), snare_rimshot/snare_side_stick
for ghost note texture, ride_bell/ride_shaft for fusion timekeeping, cymbal_open + crash_choked for
tight transitions, and tom_EDGE rimshots for technical display — matching his Chick Corea Elektric Band
and Liquid Drummers signature sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.modifications import (
    GhostNoteLayer,
    LinearCoordination,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class WecklPlugin(DrummerPlugin):
    """Dave Weckl drummer style plugin.

    Characteristics:
    - Linear playing (no simultaneous limbs)
    - Sophisticated coordination and independence
    - Jazz-fusion expertise
    - Technical precision with musicality
    """

    def __init__(self):
        self.linear = LinearCoordination()
        self.ghost_notes = GhostNoteLayer(density=0.5)

    @property
    def drummer_name(self) -> str:
        return "weckl"

    @property
    def preferred_genres(self) -> list[str]:
        return ["jazz", "fusion", "funk", "rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Dave Weckl's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_weckl"

        styled = self.linear.apply(styled, intensity=0.8)
        styled = self.ghost_notes.apply(styled, intensity=0.7)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Dave Weckl's signature fill patterns using full AD2 kit.

        Uses ALL toms in linear sequences (no simultaneous limb hits), snare_rimshot/snare_side_stick
        for ghost note texture, ride_bell/ride_shaft for fusion timekeeping, cymbal_open + crash_choked
        for tight transitions, and tom_EDGE rimshots for technical display — matching his Chick Corea
        Elektric Band and Liquid Drummers sound.
        """
        return [
            Fill(
                pattern=self._create_weckl_9_pattern(),
                trigger_probability=0.9,
                section_position="end",
            ),
            Fill(
                pattern=self._create_linear_fusion_fill(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_ghost_note_pattern_fill(),
                trigger_probability=0.7,
                section_position="start",
            ),
            Fill(
                pattern=self._create_coordination_showcase(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_liquid_drummers_roll(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_electric_band_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_step_forward_groove(),
                trigger_probability=0.65,
                section_position="start",
            ),
            Fill(
                pattern=self._create_linear_tom_excursion(),
                trigger_probability=0.7,
                section_position="middle",
            ),
        ]

    def _create_weckl_9_pattern(self) -> Pattern:
        """Weckl 9 pattern — linear groove with ALL toms + snare_rimshot accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_9")
        # Linear sequence through kick, ALL toms, and snare (no simultaneous hits)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom(TIMING.EIGHTH_TRIPLET * 2, "HIGH", VELOCITY.TOM_NORMAL)
        builder.snare_rimshot(TIMING.HALF, VELOCITY.SNARE_RIMSHOT)
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY
        )
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY)
        # ride_bell/ride_shaft for fusion timekeeping
        builder.ride_bell(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            VELOCITY.RIDE_BELL_ACCENT,
        )
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        return builder.build()

    def _create_linear_fusion_fill(self) -> Pattern:
        """Linear fusion fill — no simultaneous hits across ALL kit elements."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_linear_fusion")
        # Linear sequence (no simultaneous limb hits) using full kit
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom(TIMING.EIGHTH_TRIPLET, "HIGH", VELOCITY.TOM_NORMAL)
        builder.snare_rimshot(
            TIMING.EIGHTH_TRIPLET * 2,
            VELOCITY.SNARE_RIMSHOT,
        )
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY)
        builder.tom_edge(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "LOW", VELOCITY.TOM_HEAVY
        )
        # ride_bell for fusion timekeeping (Elektric Band era sound)
        builder.ride_bell(
            TIMING.HALF * 3,
            VELOCITY.RIDE_BELL_ACCENT,
        )
        builder.tom(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY - 5,
        )
        # cymbal_open + crash_choked for tight transitions
        builder.cymbal_open(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "2")
        return builder.build()

    def _create_ghost_note_pattern_fill(self) -> Pattern:
        """Ghost note pattern — snare_side_stick + ride_bell timekeeping."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_ghost")
        # Dense snare side stick ghost-note grid (Weckl's sophisticated texturing)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(-3, 8)
            )
        # tom_MID accent for structure (linear — no simultaneous hits)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY)
        # ride_bell + ride_shaft for fusion timekeeping
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        return builder.build()

    def _create_coordination_showcase(self) -> Pattern:
        """Coordination showcase — three-way independence with ALL toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_coord")
        # Linear three-way independence (kick, snare_rimshot, toms — no overlap)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.tom(TIMING.EIGHTH_TRIPLET * 2, "HIGH", VELOCITY.TOM_NORMAL)
        builder.snare_rimshot(TIMING.HALF, VELOCITY.SNARE_RIMSHOT)
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY
        )
        # tom_edge rimshots for technical display (Weckl's precision)
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY)
        # ride_bell + cymbal_open layering (fusion sophistication)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.cymbal_open(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_liquid_drummers_roll(self) -> Pattern:
        """Liquid Drummers roll — rapid single-stroke across ALL toms with ride_bell."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_liquid")
        # Rapid single-stroke rolls using tom_edge rimshots across ALL toms
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-3, 8), 127),
            )
        # snare_side_stick for linear accent texture
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST)
        # ride_bell + ride_shaft timekeeping (fusion precision)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.ride_shaft(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_NORMAL)
        return builder.build()

    def _create_electric_band_fill(self) -> Pattern:
        """Elektric Band era fill — rapid linear coordination across ALL kit."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_electric")
        # Rapid linear sequence through ALL toms (Chick Corea Elektric Band era)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-5, 10), 127),
            )
        # snare_rimshot for accent punctuation (linear — no simultaneous hits)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # tom_FLOOR edge + cymbal_choke layering (fusion sophistication)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3")
        return builder.build()

    def _create_step_forward_groove(self) -> Pattern:
        """Step Forward groove — syncopated funk-jazz with snare_side_stick + ride_bell."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_step_forward")
        # Syncopated kick/tom pattern (funk-jazz hybrid)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            if i % 3 == 0:
                builder.kick(
                    pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
                )
            else:
                variant = ["HIGH", "MID"][i % 2]
                builder.tom(pos, variant, VELOCITY.TOM_NORMAL)
        # snare_side_stick for funk texture (ghost note groove work)
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST + 5)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # ride_bell for jazz timekeeping (fusion sophistication)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_linear_tom_excursion(self) -> Pattern:
        """Linear tom excursion — four-tom linear run across ALL kit + cymbal_choke."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("weckl_linear_tom")
        # Four-tom linear run (documented in Weckl tutorials) — all 4 toms, no overlap
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-5, 10), 127),
            )
        # snare_rimshot for accent punctuation (linear — no simultaneous hits)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # cymbal_open + crash_choked layering for tight transitions
        builder.cymbal_open(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "2")
        return builder.build()
