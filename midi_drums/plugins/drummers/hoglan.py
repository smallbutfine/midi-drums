"""Gene Hoglan drummer plugin - refactored using composable modifications.

Reduced from ~389 lines to ~63 lines (84% reduction) by using the
DrummerModification system instead of manual pattern manipulation.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
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

        Based on Death (Individual Thought Patterns / Symbolic), Dark Angel,
        and SYL discography. Documented as "The Atomic Clock" for precision:
          - Blast tom accents: metallic tom edge accents in blast context
          - Chicken lights: open/rim tom rudiment across the kit
          - Death blast cadence: kick/snare/cymbal blast interlock
          - SYL ghost note cascade: Strapping Young Lad-era ghost-note fills
          - Dark Angel speed run: thrash-speed descending tom pattern
          - Mechanical precision roll: extreme 32nd-note snare roll
          - Dethklok wall-of-sound: thick double-kick/crash blast fill
          - Fear Factory industrial fill: metallic rim/tom machine-gun fills
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
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_fear_factory_industrial_fill(),
                trigger_probability=0.6,
                section_position="middle",
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
            # Rim accent: alternate TOM_EDGE_1 (rack) and TOM_EDGE_3 (tom 3)
            edge_variant = "1" if beat % 2 == 0 else "3"
            builder.tom_edge(pos + 0.5, edge_variant, VELOCITY.TOM_HEAVY)

        return builder.build()

    def _create_death_blast_cadence(self) -> Pattern:
        """Death metal blast cadence fill."""
        builder = PatternBuilder("hoglan_death_blast")
        # 16-hit cadence: kick/snare/cymbal alternating (within one beat)
        cadence = [
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
            pos = offset
            velocity = min(127, raw_velocity)
            if instr_name == "kick":
                builder.kick(pos, velocity)
            elif instr_name == "snare":
                builder.snare(pos, velocity)
            elif instr_name == "ride_cymbal":
                builder.pattern.add_beat(
                    pos, InstrumentRegistry.get("ride_1_shaft_hit_stronger"), velocity
                )
        return builder.build()

    def _create_syl_ghost_cascade(self) -> Pattern:
        """SYL-era ghost note cascade.

        Strapping Young Lad's complex arrangements feature Hoglan incorporating
        ghost-note density into blast-beat contexts — rapid snare ghosts layered
        beneath double-kick patterns, creating a rolling texture. Documented
        on The New Black album.
        """
        builder = PatternBuilder("hoglan_syl_ghost_cascade")
        # Dense ghost notes across one bar (snare ghosts + kick foundation)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY + random.randint(-3, 5))
            if random.random() < 0.8:  # 80% ghost-note density
                builder.snare(
                    pos + TIMING.SIXTEENTH / 2,
                    min(VELOCITY.SNARE_GHOST + random.randint(0, 10), 127),
                )
        return builder.build()

    def _create_dark_angel_speed_run(self) -> Pattern:
        """Dark Angel thrash-speed descending tom run.

        Hoglan's Dark Angel era (Dark Angel album, 1986) featured blistering
        thrash tempos with fast descending tom fills. Simulated as a rapid
        ascending rack-to-floor tom pattern at extreme velocity.
        """
        builder = PatternBuilder("hoglan_dark_angel_run")
        # Rapid ascending cascade: rack → mid → floor in 16th notes
        for i in range(8):
            pos = TIMING.SIXTEENTH * i
            if i < 2:
                inst = "MID"
                vel = min(VELOCITY.TOM_HEAVY + (i * 5), 127)
            elif i < 6:
                inst = "FLOOR"
                vel = min(VELOCITY.TOM_HEAVY + ((i - 2) * 8), 127)
            else:
                inst = "FLOOR"
                vel = min(VELOCITY.TOM_HEAVY + (i * 5), 127)
            builder.tom(pos, inst, min(vel, 127))
            # Final crash punctuation with CRASH_CHOKED_A cutoff
        builder.crash_choked(TIMING.DOTTED_EIGHTH, "A", VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_mechanical_precision_roll(self) -> Pattern:
        """Extreme mechanical precision snare roll.

        Hoglan's trademark "Atomic Clock" precision — every hit at the exact
        same velocity and timing, creating an almost machine-like effect.
        Simulated with 32nd-note snare roll at uniform velocity.
        """
        builder = PatternBuilder("hoglan_mechanical_roll")
        # Uniform 32nd-note snare roll (mechanical precision)
        for i in range(16):
            pos = TIMING.THIRTY_SECOND * i
            builder.snare(
                pos, VELOCITY.SNARE_HEAVY
            )  # All hits at same velocity
        return builder.build()

    def _create_dethklok_wall_of_sound(self) -> Pattern:
        """Dethklok wall-of-sound blast fill.

        From Dethklok (Metalocalypse), Hoglan's cartoon metal project features
        thick, heavy blast-beat patterns with massive double-kick and cymbal
        attacks. Simulated as a sustained blast pattern with crash punctuation.
        """
        builder = PatternBuilder("hoglan_dethklok_blast")
        # Sustained blast beats: kick/snare/cymbal for 2 bars worth of hits
        for i in range(16):
            pos = TIMING.SIXTEENTH * i / 2  # 32nd-note speed across bar
            builder.kick(pos, VELOCITY.KICK_HEAVY)
            if i % 2 == 0:
                builder.snare(pos, VELOCITY.SNARE_HEAVY)
        # Massive crash on the final hit
        builder.crash(
            TIMING.DOTTED_EIGHTH * 2, min(VELOCITY.CRASH_HEAVY + 10, 127)
        )
        return builder.build()

    def _create_fear_factory_industrial_fill(self) -> Pattern:
        """Fear Factory industrial machine-gun fill.

        Fear Factory's industrial metal era features Hoglan playing mechanical,
        staccato patterns that mimic machinery — tight rim/tom hits with
        double-kick underneath. Simulated with rapid tom-edge patterns.
        """
        builder = PatternBuilder("hoglan_fear_factory_industrial")
        # Machine-gun tom edge pattern (tight, metallic timbre)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            variant = "3" if i % 2 == 0 else "4"
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_ACCENT + random.randint(-3, 8), 127),
            )
        # Double-kick underpinning on beats 1 and 3
        builder.kick(0.0, min(VELOCITY.KICK_HEAVY, 127))
        builder.kick(TIMING.HALF, min(VELOCITY.KICK_HEAVY, 127))
        # RIDE cymbal for Dethklok/Metallica metallic timekeeping
        builder.pattern.add_beat(
            TIMING.QUARTER, InstrumentRegistry.get("ride_1_tip_hit_softer"), VELOCITY.CHINA_ACCENT - 5
        )
        return builder.build()


# backward-compat alias for existing test imports
HoglanPluginRefactored = HoglanPlugin
