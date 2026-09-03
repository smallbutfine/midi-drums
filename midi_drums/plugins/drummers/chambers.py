"""Dennis Chambers drummer plugin - funk mastery using full AD2 vocabulary.

Fills now use snare_side_stick for ghost-note punctuation, tight_hh for
tight hi-hat textures, ride_bell for syncopated accents, and tom variations
across the full kit to match his Sugar Hill / P-Funk sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.modifications import (
    BehindBeatTiming,
    FastChopsTriplets,
    GhostNoteLayer,
    PocketStretching,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class ChambersPlugin(DrummerPlugin):
    """Dennis Chambers drummer style plugin.

    Characteristics:
    - Funk mastery with incredible technical chops
    - Pocket stretching and groove tension/release
    - Ghost note layers for deep funk texture
    - Fast triplet chops for technical display
    - Slightly behind the beat for laid-back feel
    """

    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=15.0)
        self.fast_chops = FastChopsTriplets(probability=0.3)
        self.ghost_notes = GhostNoteLayer(density=0.6)
        self.pocket = PocketStretching(variation_ms=8.0)

    @property
    def drummer_name(self) -> str:
        return "chambers"

    @property
    def preferred_genres(self) -> list[str]:
        return ["funk", "jazz", "fusion", "rock", "r&b"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Dennis Chambers' signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_chambers"

        styled = self.behind_beat.apply(styled, intensity=0.5)
        styled = self.fast_chops.apply(styled, intensity=0.7)
        styled = self.ghost_notes.apply(styled, intensity=0.8)
        styled = self.pocket.apply(styled, intensity=0.6)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Dennis Chambers' signature fill patterns using full AD2 kit.

        Uses snare_side_stick for ghost-note punctuation, tight_hh for tight
        hi-hat textures, ride_bell for syncopated accents, and tom variations
        across the full kit — matching his Sugar Hill / P-Funk / Santana sound.
        """
        return [
            Fill(
                pattern=self._create_pfunk_groove(),
                trigger_probability=0.95,
                section_position="start",
            ),
            Fill(
                pattern=self._create_fast_chops_showcase(),
                trigger_probability=0.9,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_pocket_stretch_demo(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_fusion_technical_showcase(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_santana_latin_pocket(),
                trigger_probability=0.75,
                section_position="start",
            ),
            Fill(
                pattern=self._create_funky_drummer_fill(),
                trigger_probability=0.85,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_ghost_note_tom_fills(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_pocket_funk_one_drop(),
                trigger_probability=0.65,
                section_position="start",
            ),
        ]

    def _create_pfunk_groove(self) -> Pattern:
        """P-Funk groove — heavy downbeat with syncopated kicks + snare side stick."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_pfunk")
        # Heavy kick on 1 with syncopated ghost notes
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.QUARTER * 1.5, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF * 3 - TIMING.SIXTEENTH, VELOCITY.KICK_HEAVY)
        # Snare side stick ghost-note accents
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_ACCENT)
        builder.snare_side_stick(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_GHOST
        )
        # Tight hi-hat for tight pocket feel
        builder.tight_hh(TIMING.EIGHTH * 3, VELOCITY.HIHAT_NORMAL)
        return builder.build()

    def _create_fast_chops_showcase(self) -> Pattern:
        """Fast chops showcase — triplet snare side sticks + tom variations."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_fast_chops")
        # Rapid snare side stick ghost notes (Chambers' technical chops)
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(-5, 8)
            )
        # Tom accents across MID and FLOOR
        builder.tom(TIMING.HALF * 3, "MID", VELOCITY.TOM_ACCENT)
        builder.tom(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # Tight hi-hat resolution
        builder.tight_hh(4.0, open=True, velocity=VELOCITY.HIHAT_NORMAL + 5)
        return builder.build()

    def _create_pocket_stretch_demo(self) -> Pattern:
        """Pocket stretch demo — snare rimshot accents + tom edge fills."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_pocket_stretch")
        # Pocket-focused with snare rimshot accents
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.snare_rimshot(TIMING.QUARTER, VELOCITY.SNARE_RIMSHOT)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_NORMAL)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # FLOOR tom edge hit for low-end punch
        builder.tom_edge(4.0 - TIMING.SIXTEENTH, "FLOOR", VELOCITY.TOM_HEAVY)
        return builder.build()

    def _create_fusion_technical_showcase(self) -> Pattern:
        """Fusion technical showcase — cross-stick snare + ride_bell accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_fusion_technical")
        # Cross-stick / side stick for fusion texture
        builder.snare_side_stick(0.0, VELOCITY.SNARE_GHOST)
        builder.snare(TIMING.EIGHTH_TRIPLET * 2, VELOCITY.SNARE_NORMAL)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_NORMAL)
        # Ride bell accent for fusion punctuation
        builder.ride_bell(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_ACCENT)
        builder.ride_bell(4.0, VELOCITY.RIDE_ACCENT)
        return builder.build()

    def _create_santana_latin_pocket(self) -> Pattern:
        """Santana Latin pocket — tom_1 open + tight HH with crash accents."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_santana_latin")
        # Latin-influenced tom pattern
        builder.tom(0.0, "1", VELOCITY.TOM_NORMAL)
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_ACCENT)
        builder.tom(TIMING.HALF, "MID", VELOCITY.TOM_HEAVY)
        # Tight hi-hat with open variation for Latin feel
        builder.tight_hh(TIMING.HALF + TIMING.EIGHTH_TRIPLET, open=True)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_NORMAL)
        # Crash_4 accent for Latin punctuation
        builder.crash(4.0 - TIMING.SIXTEENTH, "4")
        return builder.build()

    def _create_funky_drummer_fill(self) -> Pattern:
        """Funky Drummer double-kick syncopation with full-tom fills."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_funky_drummer")
        # Double bass approach (Chambers' P-Funk era technique)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.EIGHTH_TRIPLET * 2, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.KICK_HEAVY)
        # Tom fills across MID and FLOOR
        for i in range(4):
            pos = TIMING.QUARTER * 2 + i * TIMING.SIXTEENTH
            variant = "MID" if i % 2 == 0 else "FLOOR"
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 3))
        # Snare side stick resolution
        builder.snare_side_stick(4.0, VELOCITY.SNARE_GHOST)
        return builder.build()

    def _create_ghost_note_tom_fills(self) -> Pattern:
        """Ghost-note tom fills — tight HH + snare side stick ghost notes."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_ghost_tom")
        # Tight hi-hat base (Chambers' tight pocket feel)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            if i % 2 == 0:
                builder.tight_hh(
                    pos, open=False, velocity=VELOCITY.HIHAT_NORMAL - 5
                )
            else:
                builder.tight_hh(
                    pos, open=True, velocity=VELOCITY.HIHAT_NORMAL + 3
                )
        # Snare side stick ghost notes between toms
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST)
        builder.snare(TIMING.HALF, VELOCITY.SNARE_ACCENT)
        # Tom accents across MID and FLOOR
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "MID", VELOCITY.TOM_HEAVY
        )
        builder.tom(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY - 3)
        return builder.build()

    def _create_pocket_funk_one_drop(self) -> Pattern:
        """Pocket funk one-drop — snare_shallow texture + ride_bell work."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("chambers_one_drop")
        # Reggae-funk hybrid (one-drop feel with pocket groove)
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        # Snare shallow for textural variation
        builder.snare_shallow(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # Ride bell accents for funk texture
        builder.ride_bell(TIMING.QUARTER, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_bell(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT - 5
        )
        # Tom accents on MID and FLOOR
        builder.tom(
            TIMING.HALF * 3 + TIMING.SIXTEENTH, "MID", VELOCITY.TOM_NORMAL
        )
        return builder.build()
