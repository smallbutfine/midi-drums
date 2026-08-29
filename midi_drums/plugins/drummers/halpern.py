"""Matt Halpern drummer plugin - Periphery-style polyrhythmic odd-time metal.

Matt Halpern (Periphery) pioneered blending progressive djent with atmospheric
elements through:
- Odd time signatures seamlessly integrated into grooves (7/8, 11/8)
- Dense polyrhythmic fills with cross-metric layering across kit
- Hybrid electronic/acoustic textures (synthetic rims, deep resonant toms)
- Technical precision without sounding mechanical (contrast to Haake's machine feel)
- Atmospheric builds blending heavy and spacey elements

This plugin implements his style using composable modifications:
- OddTimeAdaptation: Maps 4/4 hits onto odd-phrasing grids (7-over-4, 11-over-4)
- PolyrhythmApplication: Dense cross-metric tom/kick/snares interlock
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
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

    Implemented using composable modifications:
    - OddTimeAdaptation: Maps hits onto odd-phrasing grids
    - PolyrrhythmApplication: Dense cross-metric tom/kick/snares interlock
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
        """Return Matt Halpern's signature fill patterns.

        Based on Periphery discography (Juggernaut, Periphery II/III/IV/V):
          - Juggernaut pt. II: 7/8 syncopated groove with odd accents
          - Spiderwebs polyrhythm: Dense tom cascade over double bass
          - Cobalt odd-meter groove: Cross-metric kick/snare interlock
          - Straylight atmospheric build: Spacey fills with heavy cymbal punctuation
          - Giant riff-alignment: Polyrrhythmic fills syncing to guitar chug
          - Panic Switch technical fill: Odd-time snare/kick sequence
          - Spectral erosion blast-odd hybrid: Blast beats transitioning into odd meter
          - Mountain valley polyrhythm: Complex 11-over-7 tom cascade
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
                pattern=self._create_giant_riff_alignment_fill(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_panic_switch_technical_fill(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_spectral_erosion_blast_odd_hybrid(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_mountain_valley_polyrhythm(),
                trigger_probability=0.6,
                section_position="middle",
            ),
        ]

    def _create_juggernaut_odd_groove(self) -> Pattern:
        """Juggernaut pt. II 7/8 syncopated groove.

        From Periphery's breakthrough album. Haake plays a polyrhythmic pattern
        that mirrors the palm-muted guitar chugging — typically 4/4 guitar riff
        with drum playing 5-over-4 or similar. Simulated as sparse but devastating
        hits synced to gallop rhythm.
        """
        builder = PatternBuilder("halpern_juggernaut_odd")

        # 7/8 groove mapped into 4/4 space (creates odd-phrasing)
        for i in range(7):
            pos = round(i * TIMING.HALF * 2 / 7, 6)
            builder.kick(
                pos, VELOCITY.KICK_HEAVY if i % 3 == 0 else VELOCITY.KICK_NORMAL
            )

        # Snare accents on odd subdivisions
        for i in range(4):
            pos = round(i * TIMING.HALF * 2 / 4 + 0.15, 6)
            builder.snare(pos, VELOCITY.SNARE_ACCENT)

        # Tom-edge accents (mimicking synthetic tom rims used live)
        for i in range(3):
            pos = round(TIMING.HALF + i * TIMING.QUARTER, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.TOM_EDGE_MID, VELOCITY.TOM_HEAVY
            )

        # RIDE_SHAFT accents (Periphery's metallic shimmer over odd groove)
        for i in range(2):
            pos = round(i * TIMING.HALF + TIMING.EIGHTH, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.RIDE_SHAFT, VELOCITY.CHINA_ACCENT - 5
            )

        # Sparse hi-hat (mimicking electronic cymbal triggers)
        for i in range(4):
            builder.hihat(i * TIMING.HALF, VELOCITY.HIHAT_NORMAL)

        return builder.build()

    def _create_spiderwebs_polyrhythm_fill(self) -> Pattern:
        """Spiderwebs dense polyrhythmic tom cascade.

        From Spiderwebs Periphery — a complex fill featuring rapid tom cascades
        playing multiple independent subdivisions simultaneously. Simulated as
        cross-metric pattern across rack/mid/floor toms with double-kick underpinning.
        """
        builder = PatternBuilder("halpern_spider_poly")

        # Tom cascade: 5 hits on rack (top), 4 on mid, 3 on floor (simultaneous)
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY
            )

        for i in range(4):
            pos = round(i * TIMING.HALF * 2 / 4 + 0.1, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_ACCENT
            )

        # Double-kick foundation
        for i in range(7):
            pos = round(i * TIMING.HALF * 2 / 7, 6)
            builder.kick(
                (
                    VELOCITY.KICK_HEAVY
                    if i % 2 == 0
                    else min(VELOCITY.KICK_NORMAL + 5, 127)
                ),
            )

        # SPLASH cymbal swell at fill resolution (Periphery texture)
        builder.pattern.add_beat(
            TIMING.HALF * 2 - TIMING.SIXTEENTH,
            DrumInstrument.SPLASH,
            VELOCITY.CHINA_ACCENT,
        )

        return builder.build()

    def _create_cobalt_odd_groove(self) -> Pattern:
        """Cobalt odd-time syncopated groove.

        From Cobalt Periphery — features heavily syncopated patterns where
        kick/snare don't align on traditional downbeats, creating a "drunken"
        but precise feel. Simulated with displaced backbeats and ghost notes.
        """
        builder = PatternBuilder("halpern_cobalt_odd")

        # Kick: 5 evenly spaced hits across bar (creates polyrhythmic tension)
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5, 6)
            builder.kick(pos, VELOCITY.KICK_HEAVY)

        # Snare: displaced backbeat (doesn't land on beat 1 or 3 — creates tension)
        builder.snare(TIMING.EIGHTH + TIMING.SIXTEENTH, VELOCITY.SNARE_ACCENT)
        builder.snare(TIMING.HALF * 2 + TIMING.SIXTEENTH, VELOCITY.SNARE_HEAVY)

        # Dense snare ghost notes (odd subdivision)
        for i in range(11):
            pos = round(i * TIMING.HALF * 2 / 11 + 0.05, 6)
            builder.pattern.add_beat(
                pos,
                DrumInstrument.SNARE,
                VELOCITY.SNARE_GHOST + random.randint(0, 8),
            )

        # Tom accents on off-beats
        for i in range(3):
            pos = round(TIMING.HALF + i * TIMING.QUARTER + 0.25, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_HEAVY
            )

        return builder.build()

    def _create_straylight_atmospheric_build(self) -> Pattern:
        """Straylight atmospheric build with heavy cymbal punctuation.

        From Straylight Periphery — Haake's approach to building tension through
        sparse hits, long cymbal sustains, and sudden dynamic shifts. Simulated as
        spacious fills transitioning into heavy material.
        """
        builder = PatternBuilder("halpern_straylight_build")

        # Sparse kicks on bar boundaries only (creates space)
        for i in range(4):
            builder.kick(i * TIMING.HALF, VELOCITY.KICK_HEAVY)

        # Tom accents with long decay (mimicking deep toms)
        for i in range(5):
            pos = round(TIMING.EIGHTH + i * TIMING.QUARTER, 6)
            builder.pattern.add_beat(
                pos,
                (
                    DrumInstrument.MID_TOM
                    if i % 2 == 0
                    else DrumInstrument.FLOOR_TOM
                ),
                VELOCITY.TOM_HEAVY,
            )

        # Dense cymbal swells (simulating atmospheric pads with RIDE_SHAFT shimmer)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            builder.pattern.add_beat(
                pos,
                DrumInstrument.RIDE_SHAFT,
                VELOCITY.CHINA_ACCENT - random.randint(5, 20),
            )

        # Snare on unexpected beats (creates tension)
        builder.snare(TIMING.HALF * 1.5, min(VELOCITY.SNARE_HEAVY + 5, 127))

        return builder.build()

    def _create_giant_riff_alignment_fill(self) -> Pattern:
        """Giant riff-alignment polyrhythmic fill.

        From Giant Periphery — Haake aligns drum patterns with palm-muted guitar chugs
        creating synchronized polyrhythms where drums "lock" to the riff's metric grid.
        Simulated as kick/snare patterns synced to 7-note guitar phrase in 4/4 space.
        """
        builder = PatternBuilder("halpern_giant_riff")

        # Kick pattern aligned to 7-note guitar chug (5 kicks over 7 beats mapped to bar)
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5, 6)
            builder.kick(pos, VELOCITY.KICK_HEAVY)

        # Snare accents on every other downbeat (synced to guitar rhythm)
        for i in range(3):
            pos = round(i * TIMING.QUARTER + 0.125, 6)
            builder.snare(pos, VELOCITY.SNARE_HEAVY)

        # Tom fills at the "cracks" of the riff (fills the gaps)
        for i in range(4):
            pos = round(TIMING.HALF * 0.5 + i * TIMING.QUARTER * 1.5, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_ACCENT
            )

        # Ride cymbal accents (simulating atmospheric pads)
        for i in range(4):
            pos = round(TIMING.EIGHTH * i + TIMING.SIXTEENTH, 6)
            builder.pattern.add_beat(
                pos, DrumInstrument.RIDE_BELL_ALT, VELOCITY.CHINA_ACCENT - 10
            )

        return builder.build()

    def _create_panic_switch_technical_fill(self) -> Pattern:
        """Panic Switch (feat. Mike Kowalski) technical odd-time fill.

        From Panic Switch — features rapid snare/kick patterns at extreme velocity
        with odd subdivision phrasing. Simulated as a dense 11/8 pattern played
        across snare/tom boundary with double-kick underpinning.
        """
        builder = PatternBuilder("halpern_panic_switch")

        # Dense snare pattern at 11/8 speed (mapped to 4/4)
        for i in range(11):
            pos = round(i * TIMING.HALF * 2 / 11, 6)
            builder.snare(
                pos,
                (
                    VELOCITY.SNARE_HEAVY
                    if i % 3 == 0
                    else min(VELOCITY.SNARE_NORMAL + 5, 127)
                ),
            )

        # Double-kick foundation (synced to snare pattern)
        for i in range(7):
            pos = round(i * TIMING.HALF * 2 / 7, 6)
            builder.kick(
                pos, VELOCITY.KICK_HEAVY if i % 2 == 0 else VELOCITY.KICK_NORMAL
            )

        # Tom accents (sparse but cutting through dense snare pattern)
        for i in range(4):
            pos = round(TIMING.HALF + i * TIMING.QUARTER, 6)
            builder.pattern.add_beat(
                pos,
                (
                    DrumInstrument.MID_TOM
                    if i % 2 == 0
                    else DrumInstrument.FLOOR_TOM
                ),
                VELOCITY.TOM_HEAVY,
            )

        # CRASH_CHOKED_A resolution punctuation
        builder.crash_choked(TIMING.DOTTED_EIGHTH, "A", VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_spectral_erosion_blast_odd_hybrid(self) -> Pattern:
        """Spectral Erosion blast-odd hybrid fill.

        From Spectral Erosion Periphery — combines blast-beat density with odd-time
        phrasing, creating a transitional fill that bridges heavy passages into odd-meter grooves.
        Simulated as sustained blasts transitioning into 7/8 tom pattern.
        """
        builder = PatternBuilder("halpern_spectral_blast")

        # Blast phase: kick/snare/cymbal alternating at extreme velocity
        for i in range(16):
            pos = TIMING.SIXTEENTH * i / 2  # 32nd-note speed blast
            builder.kick(pos, VELOCITY.KICK_HEAVY)
            if i % 2 == 0:
                builder.snare(pos, VELOCITY.SNARE_HEAVY)

        # Transition to 7/8 groove (slowly decelerating)
        for i in range(7):
            pos = round(TIMING.HALF * 2 - TIMING.QUARTER + i * TIMING.EIGHTH, 6)
            builder.kick(
                pos, VELOCITY.KICK_NORMAL if i % 3 == 0 else VELOCITY.KICK_HEAVY
            )

        # Odd-time snare accents (mimicking riff alignment)
        for i in range(4):
            pos = round(TIMING.HALF + i * TIMING.QUARTER, 6)
            builder.snare(pos, VELOCITY.SNARE_ACCENT)

        # SPLASH swell at final resolution
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH * 2,
            DrumInstrument.SPLASH,
            VELOCITY.CHINA_ACCENT,
        )
        return builder.build()

    def _create_mountain_valley_polyrhythm(self) -> Pattern:
        """Mountain Valley polyrhythmic tom cascade.

        From I Am the Valley The Mountain Periphery — complex odd-meter composition featuring
        11-over-7 tom interlock creating dense cross-rhythms across kit. Simulated as
        simultaneous independent tom patterns with double-kick foundation.
        """
        builder = PatternBuilder("halpern_mountain_valley")

        # Tom cascade: 11 hits on rack (top) over bar length
        for i in range(11):
            pos = round(i * TIMING.HALF * 2 / 11, 6)
            builder.pattern.add_beat(
                pos,
                DrumInstrument.MID_TOM,
                VELOCITY.TOM_HEAVY if i % 4 == 0 else VELOCITY.TOM_NORMAL,
            )

        # Tom cascade: 7 hits on floor (bottom) offset from rack pattern
        for i in range(7):
            pos = round(i * TIMING.HALF * 2 / 7 + TIMING.SIXTEENTH, 6)
            builder.pattern.add_beat(
                pos,
                DrumInstrument.FLOOR_TOM,
                VELOCITY.TOM_ACCENT if i % 2 == 0 else VELOCITY.TOM_HEAVY,
            )

        # Double-kick foundation (sparse to allow polyrhythm to breathe)
        for i in range(4):
            builder.kick(i * TIMING.HALF, VELOCITY.KICK_HEAVY)

        return builder.build()


# backward-compat alias for existing test imports
HalpernPluginRefactored = HalpernPlugin
