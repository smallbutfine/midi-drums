"""Matt Halpern drummer plugin - Periphery-style using full AD2 kit vocabulary.

Fills now use ALL toms for polyrhythmic cascades, tom_edge rimshots for cross-metric
interlock, snare_shallow for atmospheric textures, crash(4-6) with cymbal_choke layering
for the heavy Periphery sound, and ride_bell/ride_shaft for odd-meter phrasing.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    OddTimeAdaptation,
    PolyrhythmApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class HalpernPlugin(DrummerPlugin):
    """Matt Halpern drummer style plugin.

    Characteristics:
    - Odd time signatures seamlessly integrated into grooves (7/8, 11/8)
    - Dense polyrhythmic fills with cross-metric layering across kit
    - Hybrid electronic/acoustic textures (synthetic rims, deep resonant toms)
    - Technical precision without sounding mechanical
    - Atmospheric builds blending heavy and spacey elements
    """

    def __init__(self):
        self.odd_time = OddTimeAdaptation(numerator=7, bar_length=4.0)
        self.polyrhythm = PolyrhythmApplication(
            kick_subdivisions=5,
            snare_subdivisions=4,
            tom_subdivisions=7,
            intensity=0.5,
        )

    @property
    def drummer_name(self) -> str:
        return "halpern"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "progressive", "djent", "experimental"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Matt Halpern's signature polyrhythmic odd-time style."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_halpern"

        # Layer polyrhythm first (dense tom/kick/snares interlock)
        styled = self.polyrhythm.apply(styled, intensity=0.5)
        # Then apply odd-time adaptation (creates the off-kilter phrasing)
        styled = self.odd_time.apply(styled, intensity=0.7)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Matt Halpern's signature fill patterns using full AD2 kit.

        Uses ALL toms for polyrhythmic cascades, tom_edge rimshots for cross-metric
        interlock, snare_shallow for atmospheric textures, crash(4-6) with cymbal_choke
        layering for the heavy Periphery sound, and ride_bell/ride_shaft for odd-meter phrasing.
        """
        return [
            Fill(
                pattern=self._create_juggernaut_odd_groove(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_spiderwebs_polyrhythm_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_cobalt_odd_groove(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_straylight_atmospheric_build(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_giant_riff_alignment(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_panic_switch_technical_fill(),
                trigger_probability=0.75,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_spectral_erosion_hybrid(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_mountain_valley_polyrhythm(),
                trigger_probability=0.65,
                section_position="middle",
            ),
        ]

    def _create_juggernaut_odd_groove(self) -> Pattern:
        """Juggernaut pt. II — 7/8 syncopated groove with ALL toms + snare_shallow."""

        builder = PatternBuilder("halpern_juggernaut")
        # Odd-time kick pattern (7/8 phrasing mapped to 4/4 grid)
        for i in range(7):
            pos = TIMING.EIGHTH * (i // 2)
            builder.kick(
                pos, min(VELOCITY.KICK_HEAVY + random.randint(-5, 10), 127)
            )
        # snare_shallow for atmospheric texture (Periphery's hybrid electronic feel)
        builder.snare_shallow(TIMING.QUARTER, VELOCITY.SNARE_GHOST + 8)
        # Tom cascade across ALL toms with rimshot accent
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            if i < 2:
                builder.tom(pos, variant, VELOCITY.TOM_NORMAL)
            else:
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
        # Heavy crash_4/5 layering (Periphery's big cymbal sound)
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "4")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_spiderwebs_polyrhythm_fill(self) -> Pattern:
        """Spiderwebs polyrhythm — dense tom cascade + double-bass + ride_bell."""

        builder = PatternBuilder("halpern_spiderwebs")
        # Double bass underpinning
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            builder.kick(pos, VELOCITY.KICK_HEAVY - (i % 3) * 5)
        # Tom cascade across ALL toms with rimshot texture
        for i in range(8):
            pos = TIMING.HALF + TIMING.SIXTEENTH * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            if i < 3:
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)
            else:
                builder.tom(
                    pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 8)
                )
        # ride_bell for polyrhythmic punctuation
        builder.ride_bell(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_BELL_ACCENT
        )
        return builder.build()

    def _create_cobalt_odd_groove(self) -> Pattern:
        """Cobalt odd-meter — tom_edge interlock + snare_rimshot + crash_6."""

        builder = PatternBuilder("halpern_cobalt")
        # Cross-metric kick/snare interlock with rimshot texture
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.snare_rimshot(pos, VELOCITY.SNARE_RIMSHOT)
        # tom_edge rimshots across ALL toms for cross-metric phrasing
        for i in range(4):
            pos = TIMING.HALF + TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY - (i * 3))
        # Big crash_6 resolution (Periphery's largest cymbal)
        builder.crash(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_straylight_atmospheric_build(self) -> Pattern:
        """Straylight atmospheric build — snare_shallow + tom_1 rimshot + cymbal swells."""

        builder = PatternBuilder("halpern_straylight")
        # snare_shallow for atmospheric texture (Periphery's spacey sound)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            vel = VELOCITY.SNARE_GHOST + random.randint(0, 10) - (i // 2) * 3
            builder.snare_shallow(pos, max(VELOCITY.SNARE_GHOST, vel))
        # tom_1 rimshot as metallic accent (synthetic rim texture)
        builder.tom_edge(TIMING.HALF, "1", VELOCITY.TOM_HEAVY)
        # ride_shaft for atmospheric cymbal work
        builder.ride_shaft(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL
        )
        # cymbal_choke layering for spacey punctuation
        builder.crash_choked(4.0 - TIMING.EIGHTH_TRIPLET, "3")
        return builder.build()

    def _create_giant_riff_alignment(self) -> Pattern:
        """Giant riff-alignment — polyrhythmic fills syncing to guitar chug."""

        builder = PatternBuilder("halpern_giant")
        # tom_edge rimshots synced to guitar chug rhythm
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            variant = ["HIGH", "MID"][i % 2]
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY - (i % 3) * 5)
        # snare_shallow for atmospheric layering
        builder.snare_shallow(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_GHOST + 5
        )
        # ride_bell + ride_shaft polyrhythmic interlock
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # crash_5 punctuated resolution
        builder.crash(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()

    def _create_panic_switch_technical_fill(self) -> Pattern:
        """Panic Switch technical fill — snare/kick odd-time sequence."""

        builder = PatternBuilder("halpern_panic_switch")
        # Odd-time snare/kick interlock (snare_rimshot + kick alternation)
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 3 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.snare_rimshot(pos, VELOCITY.SNARE_RIMSHOT)
        # FLOOR tom edge for low-end punch
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # snare_shallow + ride_bell resolution (Periphery's hybrid texture)
        builder.snare_shallow(
            4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_GHOST + 8
        )
        builder.ride_bell(4.0 - TIMING.SIXTEENTH, VELOCITY.RIDE_BELL_ACCENT)
        return builder.build()

    def _create_spectral_erosion_hybrid(self) -> Pattern:
        """Spectral erosion blast-odd hybrid — tom_FLOOR + snare_shallow layering."""

        builder = PatternBuilder("halpern_spectral")
        # Blast-beat style with snare_shallow texture
        for i in range(8):
            pos = TIMING.EIGHTH_TRIPLET * i
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.snare_shallow(pos, VELOCITY.SNARE_GHOST + 10)
        # FLOOR tom edge for low-end blast texture
        builder.tom_edge(TIMING.HALF * 3, "FLOOR", VELOCITY.TOM_HEAVY)
        # Tom cascade across HIGH → MID (Periphery's deep toms)
        builder.tom(4.0 - TIMING.EIGHTH_TRIPLET, "HIGH", VELOCITY.TOM_NORMAL)
        builder.tom_edge(4.0 - TIMING.SIXTEENTH, "MID", VELOCITY.TOM_HEAVY)
        # crash_6 with choke layering for blast punctuation
        builder.crash(4.0 - TIMING.EIGHTH_TRIPLET, "6")
        builder.crash_choked(4.0 - TIMING.SIXTEENTH, "6")
        return builder.build()

    def _create_mountain_valley_polyrhythm(self) -> Pattern:
        """Mountain valley polyrhythm — 11-over-7 tom cascade across ALL toms."""

        builder = PatternBuilder("halpern_mountain")
        # 11-over-7 polyrhythmic tom cascade through ALL toms
        for i in range(12):
            pos = TIMING.EIGHTH_TRIPLET * (i // 2)
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            if i < 6:
                builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY - (i % 3) * 5)
            else:
                builder.tom(
                    pos, variant, VELOCITY.TOM_NORMAL + random.randint(-5, 10)
                )
        # snare_rimshot for cross-metric accent
        builder.snare_rimshot(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.SNARE_RIMSHOT
        )
        # ride_bell/ride_shaft polyrhythmic punctuation
        builder.ride_bell(TIMING.HALF * 3, VELOCITY.RIDE_BELL_ACCENT)
        builder.ride_shaft(4.0 - TIMING.EIGHTH_TRIPLET, VELOCITY.RIDE_NORMAL)
        # Big crash_5 resolution
        builder.crash(4.0 - TIMING.SIXTEENTH, "5")
        return builder.build()
