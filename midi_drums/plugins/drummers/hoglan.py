"""Gene Hoglan drummer plugin using full AD2 kit vocabulary for extreme metal precision.

Fills now use tom_edge rimshots for metallic blast-beat texture, snare_rimshot for
accent punctuation, cymbal_choke(1-6) for tight transitions, crash_choked for industrial
punctuation, and FLOOR/LOW toms for deep blast accents matching his Death / SYL sound.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    HeavyAccents,
    MechanicalPrecision,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class HoglanPlugin(DrummerPlugin):
    """Gene Hoglan drummer style plugin.

    Characteristics:
    - Mechanical precision and extreme consistency
    - Blast beats and progressive complexity
    - Heavy accents for extreme metal power
    - Machine-like quantization and uniformity
    """

    def __init__(self):
        self.precision = MechanicalPrecision(quantize_amount=0.98)
        self.accents = HeavyAccents(accent_boost=18)

    @property
    def drummer_name(self) -> str:
        return "hoglan"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "death", "thrash", "progressive"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Gene Hoglan's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_hoglan"

        styled = self.precision.apply(styled, intensity=1.0)
        styled = self.accents.apply(styled, intensity=0.9)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Gene Hoglan's signature fill patterns using full AD2 kit.

        Uses tom_edge rimshots for metallic blast-beat texture, snare_rimshot for accent
        punctuation, cymbal_choke(1-6) for tight transitions, crash_choked for industrial
        punctuation, and FLOOR/LOW toms for deep blast accents — matching his Death / SYL
        / Dark Angel sound.
        """
        return [
            Fill(
                pattern=self._create_blast_tom_accents(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_chicken_lights_rudiment(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_death_blast_cadence(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_syl_ghost_cascade(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_dark_angel_speed_run(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_mechanical_precision_roll(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_dethklok_wall_of_sound(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_fear_factory_industrial_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
        ]

    def _create_blast_tom_accents(self) -> Pattern:
        """Blast tom accents — tom_edge rimshots across ALL toms in blast context."""

        builder = PatternBuilder("hoglan_blast_tom")
        # Tom edge rimshots in blast-beat texture across ALL toms
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # snare_rimshot for blast punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # crash_choked for tight industrial resolution
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        return builder.build()

    def _create_chicken_lights_rudiment(self) -> Pattern:
        """Chicken lights — open + rim toms in rudiment pattern across full kit."""

        builder = PatternBuilder("hoglan_chicken_lights")
        # Open/rim tom rudiment (alternating tom and tom_edge) across ALL toms
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            if i % 2 == 0:
                builder.tom(pos, variant, VELOCITY.TOM_HEAVY)
            else:
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY + 10)
        # snare_rimshot for accent texture (Death-era signature)
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # Big crash_6 resolution (his biggest cymbal)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_death_blast_cadence(self) -> Pattern:
        """Death blast cadence — double-kick/snare + crash_choke interlock."""

        builder = PatternBuilder("hoglan_death_blast")
        # Blast-beat style with snare_shallow texture (Death-era Individual Thought Patterns)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.snare_shallow(pos, VELOCITY.SNARE_GHOST + 15)
        # FLOOR tom edge for deep blast accent (Death's massive low-end)
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # crash_choked layering (tight industrial punctuation)
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        return builder.build()

    def _create_syl_ghost_cascade(self) -> Pattern:
        """SYL ghost note cascade — tom_edge across ALL toms with snare_rimshot accents."""

        builder = PatternBuilder("hoglan_syl_ghost")
        # Tom edge rimshots with ghost-note velocity (SYL-era Strapping Young Lad)
        for i in range(10):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            vel = VELOCITY.TOM_HEAVY + random.randint(-8, 15) - (i // 2) * 3
            builder.tom_edge(pos, variant, min(max(VELOCITY.TOM_HEAVY - 10, vel), 127))
        # snare_rimshot for accent texture
        builder.snare_rimshot(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_RIMSHOT
        )
        # ride_bell stinger (mechanical precision resolution)
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_dark_angel_speed_run(self) -> Pattern:
        """Dark Angel speed run — descending FLOOR/LOW toms with snare_rimshot accents."""

        builder = PatternBuilder("hoglan_dark_angel")
        # Descending tom pattern focused on FLOOR and LOW (thrash-speed)
        for i in range(6):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = "FLOOR" if i < 3 else "LOW"
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 5))
        # Snare rimshot for accent punctuation
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        # tom_edge final hit on FLOOR
        builder.tom_edge(
            4.0 - TIMING.EIGHTH_TRIPLET, "FLOOR", VELOCITY.TOM_HEAVY
        )
        # Big crash_4/5 layering (thrash-era double cymbal hits)
        builder.crash(4.0 - TIMING.SIXTEENTH, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH * 2, "5")
        return builder.build()

    def _create_mechanical_precision_roll(self) -> Pattern:
        """Mechanical precision roll — rapid tom_edge across ALL toms."""

        builder = PatternBuilder("hoglan_mechanical")
        # Rapid tom edge rimshots across ALL toms (atomic clock precision)
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-3, 5)
            )
        # snare_rimshot for precision accent
        builder.snare_rimshot(TIMING.HALF * 3, VELOCITY.SNARE_RIMSHOT)
        # crash_choked(6) resolution (tightest industrial punctuation)
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_dethklok_wall_of_sound(self) -> Pattern:
        """Dethklok wall-of-sound — double-kick + crash blast with FLOOR tom accents."""

        builder = PatternBuilder("hoglan_dethklok")
        # Double-kick wall of sound (Dethklok's massive blast-beat style)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(
                pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
            )
        # FLOOR tom edge accents with snare_rimshot interlock
        for i in [2, 5]:
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.tom_edge(pos, "FLOOR", VELOCITY.TOM_HEAVY)
            builder.snare_rimshot(
                pos + TIMING.SIXTEENTH / 2, VELOCITY.SNARE_HEAVY
            )
        # Massive crash_5/6 layering (Dethklok's huge cymbal sound)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "5")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_fear_factory_industrial_fill(self) -> Pattern:
        """Fear Factory industrial fill — tom_edge + snare_shallow machine-gun."""

        builder = PatternBuilder("hoglan_fear_factory")
        # Tom edge rimshots in metallic machine-gun pattern (Fear Factory's industrial sound)
        for i in range(10):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos, variant, VELOCITY.TOM_HEAVY + random.randint(-5, 10)
            )
        # snare_shallow for industrial texture (synthetic metallic feel)
        builder.snare_shallow(TIMING.HALF * 3, VELOCITY.SNARE_GHOST + 15)
        # cymbal_choke layering for tight punctuation (industrial metal style)
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "3")
        return builder.build()
