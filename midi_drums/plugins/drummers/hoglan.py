"""Gene Hoglan drummer plugin - refactored using composable modifications.

Reduced from ~389 lines to ~63 lines (84% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

import random

from midi_drums.config import VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
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

    Implemented using composable modifications:
    - MechanicalPrecision: Extreme quantization for machine-like feel
    - HeavyAccents: Boosts accent contrast for extreme metal power
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
        """Return Gene Hoglan's signature fill patterns.

        Based on Death (Individual Thought Patterns / Symbolic) and SYL discography.
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
        ]

    def _create_blast_tom_accents(self) -> Pattern:
        """Tom edge accents - the metallic tom sound that defines Hoglan's blast beats.

        AD2 TOM_EDGE (rimmed/edge toms, notes 65-69) produce a tighter,
        more aggressive attack than standard open toms. Critical for death metal
        where each tom hit in a cascade must cut through double-kick blasts.
        """
        builder = PatternBuilder("hoglan_blast_tom_accents")

        # Rapid tom_edge accents (mimicking blast-beat tom work)
        for i in range(8):
            pos = i * 0.5
            variant = "3" if i % 2 == 0 else "FLOOR"
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_ACCENT + random.randint(-5, 10), 127),
            )

        # Choked crash cutoff (AD2 crash_choked - sharp "chick" to end the blast)
        builder.crash_choked(4.0, "A", VELOCITY.CRASH_HEAVY)

        return builder.build()

    def _create_chicken_lights_rudiment(self) -> Pattern:
        """Chicken Lights - Hoglan's trademark open/rim tom rudiment.

        Alternates open toms with rimshots across the kit. Uses tom_edge for the rim
        portions (tight metallic attack), and standard tom for the open body.
        """
        builder = PatternBuilder("hoglan_chicken_lights")

        # Open/rim alternation on quarter notes (4 bars, 16 hits total)
        for beat in range(4):
            pos = beat * 1.0
            # Open tom body
            if beat % 2 == 0:
                builder.tom(pos, "FLOOR", VELOCITY.TOM_ACCENT)
            else:
                builder.tom(pos, "MID", VELOCITY.TOM_ACCENT)
            # Rim accent
            builder.tom_edge(
                pos + 0.5, "4" if beat % 2 == 0 else "3", VELOCITY.TOM_HEAVY
            )

        return builder.build()

    def _create_death_blast_cadence(self) -> Pattern:
        """Death metal blast cadence fill.

        Inspired by Hoglan's Death-era recordings (Individual Thought Patterns,
        Symbolic). Blast beats alternate kick, snare, and cymbal (ride/crash)
        in a tight cadence — not pure blast-beat wall-of-sound, but rhythmic
        interlock between limbs.
        """
        builder = PatternBuilder("hoglan_death_blast")

        # 16-hit cadence: kick/snare/cymbal alternating (within one beat)
        cadence = [
            # Format: (offset, instrument, raw_velocity) — capped at 127 on write
            (0.0, "kick", VELOCITY.KICK_HEAVY),
            (1 / 32, "snare", VELOCITY.SNARE_HEAVY),
            (2 / 32, "ride_cymbal", VELOCITY.CHINA_ACCENT),
            (3 / 32, "kick", VELOCITY.KICK_HEAVY - 5),
            (4 / 32, "snare", min(127, VELOCITY.SNARE_HEAVY + 2)),
            (5 / 32, "ride_cymbal", VELOCITY.CHINA_ACCENT - 3),
            (6 / 32, "kick", VELOCITY.KICK_HEAVY),
            (7 / 32, "snare", VELOCITY.SNARE_HEAVY),
            # Acceleration phase
            (8 / 32, "kick", min(127, VELOCITY.KICK_HEAVY + 2)),
            (9 / 32, "snare", VELOCITY.SNARE_ACCENT),
            (10 / 32, "ride_cymbal", VELOCITY.CHINA_ACCENT),
            (11 / 32, "kick", min(127, VELOCITY.KICK_HEAVY + 5)),
            (12 / 32, "snare", min(127, VELOCITY.SNARE_ACCENT + 2)),
            (13 / 32, "ride_cymbal", min(127, VELOCITY.CHINA_ACCENT + 5)),
            (14 / 32, "kick", min(127, VELOCITY.KICK_HEAVY + 8)),
            (15 / 32, "snare", min(127, VELOCITY.SNARE_ACCENT + 5)),
        ]

        for offset, instr_name, raw_velocity in cadence:
            pos = offset  # All within one beat
            velocity = min(127, raw_velocity)
            if instr_name == "kick":
                builder.kick(pos, velocity)
            elif instr_name == "snare":
                builder.snare(pos, velocity)
            elif instr_name == "ride_cymbal":
                builder.pattern.add_beat(pos, DrumInstrument.CHINA, velocity)

        return builder.build()


# backward-compat alias for existing test imports
HoglanPluginRefactored = HoglanPlugin
