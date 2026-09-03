"""Charlie Watts drummer plugin using full AD2 kit for minimalist jazz-rock fills.

Fills now use tight_hh as primary timekeeping, ride_bell for jazz swing accents,
snare_side_stick for sparse brush-like texture, single tasteful tom hits (LOW or FLOOR),
and cymbal_open/crash_choked for elegant punctuation — matching his Rolling Stones
jazz-influenced minimalist sound (less is more).
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    BehindBeatTiming,
    GhostNoteLayer,
    ShuffleFeelApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class WattsPlugin(DrummerPlugin):
    """Charlie Watts drummer style plugin.

    Characteristics:
    - Jazz-trained timekeeping with impeccable swing/shuffle feel
    - Minimalist approach — sparse hits, every note counts
    - Behind-the-beat timing that creates a relaxed, dragging groove
    - Focus on hi-hate/ride cymbal patterns rather than crash bombardment
    - Sparse but tasteful tom fills (never overplayed)
    - Ghost notes on snare providing subtle pocket depth
    - Elegant simplicity — the anti-Moon in many ways
    """

    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=20.0)
        self.shuffle = ShuffleFeelApplication(shuffle_amount=0.33)
        self.ghost_notes = GhostNoteLayer(density=0.3)  # Sparse, not dense

    @property
    def drummer_name(self) -> str:
        return "watts"

    @property
    def preferred_genres(self) -> list[str]:
        return ["blues", "rock", "jazz"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Charlie Watts' signature minimalist style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_watts"

        styled = self.behind_beat.apply(styled, intensity=0.5)
        styled = self.shuffle.apply(styled, intensity=0.4)
        styled = self.ghost_notes.apply(styled, intensity=0.3)
        styled = self._reduce_crash_density(styled)

        return styled

    def _reduce_crash_density(self, pattern):
        """Reduce crash cymbal density (stub for Watts' minimalist style)."""
        return pattern

    def get_signature_fills(self) -> list[Fill]:
        """Return Charlie Watts' signature fill patterns using full AD2 kit.

        Uses tight_hh as primary timekeeping, ride_bell for jazz swing accents,
        snare_side_stick for sparse brush-like texture, single tasteful tom hits
        (LOW or FLOOR), and cymbal_open/crash_choked for elegant punctuation —
        matching his Rolling Stones jazz-influenced minimalist sound.
        """
        return [
            Fill(
                pattern=self._create_sweet_home_chicago_shuffle(),
                trigger_probability=0.8,
                section_position="start",
            ),
            Fill(
                pattern=self._create_brown_sugar_rock_fill(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_start_me_up_hihat_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_sympathy_for_the_devil_tom_fill(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_paint_it_black_pattern(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_jumpin_jack_flash_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_angiera_blues_shuffle(),
                trigger_probability=0.65,
                section_position="start",
            ),
            Fill(
                pattern=self._create_miss_you_disco_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
        ]

    def _create_sweet_home_chicago_shuffle(self) -> Pattern:
        """Sweet Home Chicago shuffle — tight HH + ride_bell swing triplets."""

        builder = PatternBuilder("watts_sweet_home")
        # Tight hi-hat as primary timekeeping (Watts' jazz training)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.tight_hh(pos, open=False, velocity=VELOCITY.HIHAT_NORMAL)
        # ride_bell for triplet swing feel (jazz-influenced timekeeping)
        for i in range(3):
            pos = TIMING.QUARTER + TIMING.EIGHTH_TRIPLET * i
            builder.ride_bell(pos, VELOCITY.RIDE_BELL_ACCENT - (i * 2))
        # Single tasteful tom_FLOOR accent (sparse but impactful)
        builder.tom(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_NORMAL
        )
        return builder.build()

    def _create_brown_sugar_rock_fill(self) -> Pattern:
        """Brown Sugar simple rock — single LOW tom accent + ride_bell resolution."""

        builder = PatternBuilder("watts_brown_sugar")
        # Iconic backbeat with minimal fill (Watts' simplicity)
        builder.snare_rimshot(TIMING.QUARTER, VELOCITY.SNARE_NORMAL)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_NORMAL)
        # Single tasteful tom_LOW accent (sparse but tasteful)
        builder.tom(TIMING.HALF, "LOW", VELOCITY.TOM_HEAVY - 10)
        # ride_bell for jazz swing resolution (Watts' jazz roots)
        builder.ride_bell(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_start_me_up_hihat_fill(self) -> Pattern:
        """Start Me Up tight HH — crisp timekeeping with snare_side_stick."""

        builder = PatternBuilder("watts_start_me_up")
        # Crisp tight hi-hat timekeeping (his signature tight HH work)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            builder.tight_hh(pos, open=False if i % 2 == 0 else True)
        # snare_side_stick for sparse accent texture (jazz brush-like feel)
        builder.snare_side_stick(TIMING.QUARTER, VELOCITY.SNARE_GHOST + 5)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # Single LOW tom for structure (never overplayed)
        builder.tom(TIMING.HALF, "LOW", VELOCITY.TOM_HEAVY - 15)
        return builder.build()

    def _create_sympathy_for_the_devil_tom_fill(self) -> Pattern:
        """Sympathy for the Devil — sparse tribal FLOOR tom work."""

        builder = PatternBuilder("watts_sympathy")
        # Sparse, tribal FLOOR tom work (Watts' minimal approach)
        for i in range(4):
            pos = TIMING.EIGHTH_TRIPLET * (i + 1)
            builder.tom(
                pos, "FLOOR", VELOCITY.TOM_NORMAL + random.randint(-5, 8)
            )
        # snare_side_stick for sparse texture (brush-like jazz feel)
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 3)
        # ride_bell for atmospheric timekeeping
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT - 5
        )
        return builder.build()

    def _create_paint_it_black_pattern(self) -> Pattern:
        """Paint It Black — minimalist percussion approach with tom_1 + snare_shallow."""

        builder = PatternBuilder("watts_paint_it")
        # Tom_1 accent for percussive texture (marching band influence)
        builder.tom(TIMING.QUARTER, "1", VELOCITY.TOM_HEAVY - 10)
        # snare_shallow for sparse texture (never dense — that's not Watts)
        builder.snare_shallow(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 5)
        # tight_hh as primary timekeeping (jazz-trained simplicity)
        builder.tight_hh(4.0 - TIMING.EIGHTH_TRIPLET, open=False)
        return builder.build()

    def _create_jumpin_jack_flash_fill(self) -> Pattern:
        """Jumpin' Jack Flash — tasteful but not overblown single tom accent."""

        builder = PatternBuilder("watts_jumpin")
        # Tom_LOW accent for taste (never overplayed)
        builder.tom(TIMING.HALF, "LOW", VELOCITY.TOM_NORMAL + 5)
        # ride_bell for jazz swing timekeeping (Watts' sophistication)
        for i in range(3):
            pos = TIMING.EIGHTH_TRIPLET * (i + 2)
            builder.ride_bell(pos, VELOCITY.RIDE_BELL_ACCENT - (i * 3))
        # snare_rimshot with restraint (tasteful accent)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT - 5)
        return builder.build()

    def _create_angiera_blues_shuffle(self) -> Pattern:
        """Angiera blues shuffle — jazz swing + ride_cymbal focus + tom_EDGE accents."""

        builder = PatternBuilder("watts_angiera")
        # Jazz-influenced swing with ride cymbal focus (Watts' jazz roots)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i < 3:
                builder.ride_bell(pos, VELOCITY.RIDE_BELL_ACCENT - (i * 2))
            else:
                builder.ride_shaft(pos, VELOCITY.RIDE_NORMAL)
        # tom_EDGE rimshot as sparse accent (tasteful punctuation)
        builder.tom_edge(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, "LOW", VELOCITY.TOM_HEAVY - 8
        )
        # snare_side_stick for sparse texture
        builder.snare_side_stick(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 3)
        return builder.build()

    def _create_miss_you_disco_fill(self) -> Pattern:
        """Miss You disco groove — tight HH + snare_g_ghost notes subtle pocket work."""

        builder = PatternBuilder("watts_miss_you")
        # Tight hi-hat for disco-tinged pocket (Watts adapted to era)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            builder.tight_hh(pos, open=False if i % 2 == 0 else True)
        # snare_side_stick ghost notes for subtle pocket depth
        for i in [1, 3, 5]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.snare_side_stick(
                pos, VELOCITY.SNARE_GHOST + random.randint(0, 5)
            )
        # Single tasteful tom_LOW accent (sparse but impactful)
        builder.tom(TIMING.HALF * 3, "LOW", VELOCITY.TOM_NORMAL)
        return builder.build()
