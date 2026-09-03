"""Stewart Copeland drummer plugin using full AD2 vocabulary.

Fills now prominently feature snare_side_stick (cross-stick), tight_hh for
off-beat hi-hat work, ride_bell accents, and tom variations matching his
Police / Peter Gabriel era sound. crash_choke used for tight reggae skank fills.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    GhostNoteLayer,
    PocketStretching,
    TwistedAccents,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class CopelandPlugin(DrummerPlugin):
    """Stewart Copeland drummer style plugin.

    Characteristics:
    - Reggae/ska-influenced off-beat hi-hat emphasis
    - Cross-stick (rim click) snare texture in signature fills
    - Unconventional, displaced accent placement
    """

    def __init__(self):
        self.twisted_accents = TwistedAccents(displacement=0.45)
        self.pocket_stretch = PocketStretching(variation_ms=8.0)
        self.ghost_notes = GhostNoteLayer(density=0.4)

    @property
    def drummer_name(self) -> str:
        return "copeland"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "funk"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Stewart Copeland's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_copeland"

        styled = self.ghost_notes.apply(styled, intensity=0.5)
        styled = self.pocket_stretch.apply(styled, intensity=0.7)
        styled = self.twisted_accents.apply(styled, intensity=0.8)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Stewart Copeland's signature fill patterns using full AD2 kit.

        Prominently features snare_side_stick (cross-stick), tight_hh for
        off-beat hi-hat work, ride_bell accents, and tom variations matching
        his Police / Peter Gabriel era sound. crash_choke used for tight skank fills.
        """
        return [
            Fill(
                pattern=self._create_skank_hihat_fill(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_displaced_accent_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_syncopated_tom_skip_fill(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_octoban_off_beat_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_gamelan_percussion_fill(),
                trigger_probability=0.5,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_reggae_skank_groove_fill(),
                trigger_probability=0.75,
                section_position="start",
            ),
            Fill(
                pattern=self._create_message_in_a_box_tom_pattern(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_ghost_note_interlock(),
                trigger_probability=0.7,
                section_position="start",
            ),
        ]

    def _create_skank_hihat_fill(self) -> Pattern:
        """Reggae/ska off-beat hi-hat fill — tight HH + snare side stick."""

        builder = PatternBuilder("copeland_skank")
        # Tight hi-hat on off-beats (reggae skank feel)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            is_offbeat = i % 2 == 1
            if is_offbeat:
                builder.tight_hh(
                    pos, open=True, velocity=VELOCITY.HIHAT_NORMAL + 5
                )
            else:
                builder.tight_hh(pos, open=False, velocity=VELOCITY.HIHAT_LIGHT)
        # Snare side stick on backbeats (his signature cross-stick style)
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST)
        # Crash_choke for tight skank punctuation
        builder.crash_choked(
            4.0 - TIMING.SIXTEENTH, "2", VELOCITY.CRASH_ACCENT - 8
        )
        return builder.build()

    def _create_displaced_accent_fill(self) -> Pattern:
        """Displaced accent fill — ride_bell + tom_edge with unexpected accents."""

        builder = PatternBuilder("copeland_displaced")
        # Ride bell for displaced rhythmic feel
        builder.ride_bell(0.0, VELOCITY.RIDE_BELL_ACCENT)
        builder.tom(TIMING.EIGHTH_TRIPLET * 2, "MID", VELOCITY.TOM_NORMAL)
        builder.ride_bell(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT - 5
        )
        # Tom_edge rimshot for unexpected accent texture
        builder.tom_edge(TIMING.HALF * 3, "LOW", VELOCITY.TOM_HEAVY)
        builder.snare(TIMING.HALF * 3 + TIMING.SIXTEENTH, VELOCITY.SNARE_ACCENT)
        # Tight hi-hat resolution
        builder.tight_hh(4.0 - TIMING.SIXTEENTH, open=True)
        return builder.build()

    def _create_syncopated_tom_skip_fill(self) -> Pattern:
        """Syncopated tom skip — HIGH/FLOOR with snare side stick punctuation."""

        builder = PatternBuilder("copeland_syncopated_tom")
        # Hesitating tom with alternating HIGH and FLOOR (Copeland's style)
        builder.tom(0.0, "HIGH", VELOCITY.TOM_NORMAL)
        builder.tom(
            TIMING.EIGHTH_TRIPLET * 2 + TIMING.SIXTEENTH,
            "FLOOR",
            VELOCITY.TOM_HEAVY,
        )
        # Snare side stick (cross-stick) as punctuation between toms
        builder.snare_side_stick(
            TIMING.HALF - TIMING.SIXTEENTH, VELOCITY.SNARE_GHOST
        )
        builder.tom_edge(TIMING.HALF * 3, "MID", VELOCITY.TOM_HEAVY)
        # Tight hi-hat open for fill resolution
        builder.tight_hh(
            4.0 - TIMING.SIXTEENTH,
            open=True,
            velocity=VELOCITY.HIHAT_NORMAL + 8,
        )
        return builder.build()

    def _create_octoban_off_beat_fill(self) -> Pattern:
        """Octoban off-beat fill — HIGH/FLOOR toms as stand-ins for octoban."""

        builder = PatternBuilder("copeland_octoban")
        # Off-beat tom pattern (using HIGH and FLOOR as octoban equivalents)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            is_offbeat = i % 2 == 1
            if is_offbeat:
                variant = "HIGH" if i < 4 else "FLOOR"
                builder.tom(
                    pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 5)
                )
        # Snare side stick for Police-era cross-stick texture
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST)
        # Tight hi-hat close for off-beat punctuation
        builder.tight_hh(
            4.0 - TIMING.SIXTEENTH, open=False, velocity=VELOCITY.HIHAT_NORMAL
        )
        return builder.build()

    def _create_gamelan_percussion_fill(self) -> Pattern:
        """Gamelan percussion fill — ride_bell + tom_1 rimshot (Dallas Symphony)."""

        builder = PatternBuilder("copeland_gamelan")
        # Ride bell for percussive texture (gamelan-inspired)
        builder.ride_bell(0.0, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_bell(
            TIMING.EIGHTH_TRIPLET * 2, VELOCITY.RIDE_BELL_ACCENT - 5
        )
        # Tom_1 rimshot as metal resonance (gamelan timbre)
        builder.tom_edge(TIMING.HALF, "1", VELOCITY.TOM_HEAVY)
        # Snare side stick for sparse punctuation
        builder.snare_side_stick(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_GHOST
        )
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        # Tight hi-hat resolution
        builder.tight_hh(
            4.0 - TIMING.SIXTEENTH, open=False, velocity=VELOCITY.HIHAT_NORMAL
        )
        return builder.build()

    def _create_reggae_skank_groove_fill(self) -> Pattern:
        """Reggae skank groove — tight HH + snare side stick + crash_choke."""

        builder = PatternBuilder("copeland_reggae_skank")
        # Tight hi-hat on off-beats (classic reggae skank)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            is_offbeat = i % 2 == 1
            if is_offbeat:
                builder.tight_hh(
                    pos, open=True, velocity=VELOCITY.HIHAT_NORMAL + 5
                )
            else:
                builder.tight_hh(pos, open=False, velocity=VELOCITY.HIHAT_LIGHT)
        # Snare side stick (cross-stick) on backbeats
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST + 3)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 3)
        # Crash_choke for tight skank punctuation
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "2")
        return builder.build()

    def _create_message_in_a_box_tom_pattern(self) -> Pattern:
        """Message in a Box syncopated tom — HIGH/MID/FLOOR with ride_bell accents."""

        builder = PatternBuilder("copeland_message_in_box")
        # Alternating left/right hand tom pattern (HIGH + MID)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            variant = "HIGH" if i % 2 == 0 else "MID"
            builder.tom(
                pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 8)
            )
        # Ride bell accents for syncopated punctuation
        builder.ride_bell(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT - 5)
        # Snare side stick resolution
        builder.snare_side_stick(4.0 - TIMING.SIXTEENTH, VELOCITY.SNARE_GHOST)
        return builder.build()

    def _create_ghost_note_interlock(self) -> Pattern:
        """Every Breath ghost-note interlock — tight HH + snare side stick."""

        builder = PatternBuilder("copeland_ghost_interlock")
        # Tight hi-hat base with off-beat accents (his signature tight HH work)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            is_offbeat = i % 2 == 1
            if is_offbeat:
                builder.tight_hh(
                    pos, open=True, velocity=VELOCITY.HIHAT_NORMAL + 3
                )
            else:
                builder.tight_hh(pos, open=False, velocity=VELOCITY.HIHAT_LIGHT)
        # Snare side stick ghost notes interlocking with hi-hat
        for i in [2, 6, 10, 14]:
            pos = TIMING.SIXTEENTH * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(-3, 5)
            )
        # Tom_1 accent for structure
        builder.tom(TIMING.HALF, "1", VELOCITY.TOM_NORMAL)
        return builder.build()
