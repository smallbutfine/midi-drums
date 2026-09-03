"""Jeff Porcaro drummer plugin using full AD2 kit vocabulary for studio precision.

Fills now use snare_side_stick prominently (cross-stick/groove texture), tight_hh for
tight hi-hat work, ride_bell/ride_shaft for half-time shuffle timekeeping, tom variations
(HIGH/MID/LOW/FLOOR) across the full kit, and cymbal_open + crash_choked for tight studio
transitions — matching his Toto / Steely Dan session-work sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.modifications import (
    GhostNoteLayer,
    ShuffleFeelApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class PorcaroPlugin(DrummerPlugin):
    """Jeff Porcaro drummer style plugin.

    Characteristics:
    - Half-time shuffle mastery (Rosanna shuffle)
    - Ghost notes for groove texture
    - Studio precision and consistency
    - Sophisticated feel and dynamics
    """

    def __init__(self):
        self.shuffle = ShuffleFeelApplication(shuffle_amount=0.6)
        self.ghost_notes = GhostNoteLayer(density=0.4)

    @property
    def drummer_name(self) -> str:
        return "porcaro"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "pop", "blues", "funk", "jazz"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Jeff Porcaro's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_porcaro"

        styled = self.shuffle.apply(styled, intensity=0.8)
        styled = self.ghost_notes.apply(styled, intensity=0.7)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Jeff Porcaro's signature fill patterns using full AD2 kit.

        Uses snare_side_stick prominently for cross-stick/groove texture, tight_hh for tight
        hi-hat work, ride_bell/ride_shaft for half-time shuffle timekeeping, tom variations
        (HIGH/MID/LOW/FLOOR) across the full kit, and cymbal_open + crash_choked for tight
        studio transitions — matching his Toto / Steely Dan sound.
        """
        return [
            Fill(
                pattern=self._create_rosanna_shuffle(),
                trigger_probability=0.95,
                section_position="start",
            ),
            Fill(
                pattern=self._create_half_time_shuffle_fill(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_ghost_note_showcase(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_studio_precision_fill(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_aja_fusion_groove(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_chain_of_fools_grooves(),
                trigger_probability=0.7,
                section_position="start",
            ),
            Fill(
                pattern=self._create_waiters_pad_interlock(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_rosanna_variation_fill(),
                trigger_probability=0.85,
                section_position="start",
            ),
        ]

    def _create_rosanna_shuffle(self) -> Pattern:
        """Rosanna shuffle — ride_bell timekeeping + snare_side_stick ghost notes + tom_FLOOR."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_rosanna")
        # Half-time shuffle with ride bell as timekeeper (signature Rosanna sound)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.ride_bell(pos, VELOCITY.RIDE_NORMAL + random.randint(-5, 8))
        # Snare side stick (cross-stick) for groove texture
        for i in [1, 3, 5]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(0, 5)
            )
        # tom_MID + FLOOR accents (half-time kick pattern)
        builder.tom(TIMING.QUARTER, "MID", VELOCITY.TOM_NORMAL)
        builder.tom(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY - 5)
        # Tight hi-hat open for shuffle punctuation
        builder.tight_hh(4.0 - TIMING.EIGHTH_TRIPLET, open=True)
        return builder.build()

    def _create_half_time_shuffle_fill(self) -> Pattern:
        """Half-time shuffle — ride_shaft + snare_side_stick ghost notes + tom_edge rimshots."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_half_time_shuffle")
        # ride_shaft as timekeeper for half-time shuffle feel
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.ride_shaft(pos, VELOCITY.RIDE_NORMAL)
        # snare_side_stick ghost notes (signature Porcaro groove texture)
        for i in [0, 2, 4]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(0, 5)
            )
        # tom_edge rimshots for shuffle accent texture
        builder.tom_edge(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY - 8
        )
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY - 5)
        # Tight hi-hat resolution
        builder.tight_hh(4.0 - TIMING.SIXTEENTH, open=False)
        return builder.build()

    def _create_ghost_note_showcase(self) -> Pattern:
        """Ghost note showcase — snare_side_stick dense grid + tom_1 rimshot accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_ghost_notes")
        # Dense snare side stick ghost-note grid (signature Porcaro technique)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(-3, 8)
            )
        # tom_1 rimshot accents for structure
        builder.tom_edge(TIMING.QUARTER, "1", VELOCITY.TOM_NORMAL)
        builder.tom_edge(TIMING.HALF * 3, "1", VELOCITY.TOM_HEAVY - 5)
        # Tight hi-hat open for groove punctuation
        builder.tight_hh(4.0 - TIMING.EIGHTH_TRIPLET, open=True)
        return builder.build()

    def _create_studio_precision_fill(self) -> Pattern:
        """Studio precision — tom cascade with ride_bell stinger + cymbal_choke."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_studio_precision")
        # Tom cascade through MID and FLOOR (tight studio feel)
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = "MID" if i < 2 else "FLOOR"
            builder.tom(
                pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 8)
            )
        # snare_rimshot for precision accent (studio perfection)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # ride_bell stinger resolution
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        # crash_choked for tight studio transition
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "2")
        return builder.build()

    def _create_aja_fusion_groove(self) -> Pattern:
        """Aja fusion groove — ride_bell/ride_shaft + tom variations + snare_rimshot."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_aja")
        # ride_bell for jazz fusion timekeeping (Steely Dan's Aja era)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i < 3:
                builder.ride_bell(
                    pos, VELOCITY.RIDE_BELL_ACCENT + random.randint(-5, 10)
                )
            else:
                builder.ride_shaft(pos, VELOCITY.RIDE_NORMAL)
        # tom_1 + MID accents for fusion texture
        builder.tom(TIMING.QUARTER, "1", VELOCITY.TOM_HEAVY)
        builder.tom_edge(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY - 3)
        # snare_rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # cymbal_open + crash_choked layering (fusion sophistication)
        builder.cymbal_open(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "3")
        return builder.build()

    def _create_chain_of_fools_grooves(self) -> Pattern:
        """Chain of fools grooves — tight HH + snare_side_stick pocket work."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_chain_fools")
        # Tight hi-hat for Motown-influenced pocket (Chain of Fools groove)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            builder.tight_hh(pos, open=False if i % 2 == 0 else True)
        # snare_side_stick for pocket texture
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST + 5)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # tom_MID accent for structure
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_NORMAL)
        return builder.build()

    def _create_waiters_pad_interlock(self) -> Pattern:
        """Waiter's pad interlock — tight snare/tom with ride_bell timekeeping."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_waiters_pad")
        # Tight snare/tom interlock (Toto live era waiter's pad technique)
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_NORMAL)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # tom_FLOOR edge for low-end accent
        builder.tom_edge(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            VELOCITY.TOM_HEAVY - 5,
        )
        # ride_bell timekeeping (signature Porcaro sound)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_rosanna_variation_fill(self) -> Pattern:
        """Rosanna variation — triplet shuffle on ride + snare_side_stick ghost notes."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("porcaro_rosanna_var")
        # Triplet shuffle on ride bell (signature Rosanna variation)
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i < 6:
                builder.ride_bell(
                    pos, VELOCITY.RIDE_NORMAL + random.randint(-5, 8)
                )
            else:
                builder.ride_shaft(pos, VELOCITY.RIDE_NORMAL)
        # snare_side_stick ghost notes for groove texture
        for i in [2, 5, 8]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(0, 5)
            )
        # tom_MID + FLOOR accents
        builder.tom(TIMING.HALF * 3, "MID", VELOCITY.TOM_HEAVY)
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY - 5
        )
        # Tight hi-hat open + crash_choked resolution
        builder.tight_hh(4.0 - TIMING.SIXTEENTH, open=True)
        builder.crash_choked(4.0, "2")
        return builder.build()
