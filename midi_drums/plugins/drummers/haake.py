"""Thomas Haake drummer plugin - Meshuggah-style polyrhythmic extreme metal.

Thomas Haake (Meshuggah) pioneered what became the "djent" sound through:
- Polyrhythmic complexity (simultaneous different meters across limbs)
- Odd time signatures (7/8, 11/8, 5/4) adapted to 4/4 framework
- Mechanical precision — machine-like quantization with mathematical exactness
- Sparse but devastating hit density — minimal notes maximum impact
- Cross-rhythms between limbs at fundamentally different subdivision rates
- Palm-muted gallops synced to guitars
- Influence on djent and progressive metal

This plugin implements his style using composable modifications:
- PolyrhythmApplication: 5-over-4, 7-over-4, etc. cross-meter patterns
- MechanicalPrecision: Machine-like timing and velocity consistency
"""

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    MechanicalPrecision,
    PolyrhythmApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class HaakePlugin(DrummerPlugin):
    """Thomas Haake drummer style plugin.

    Characteristics:
    - Polynrhythmic layering (simultaneous different meters across limbs)
    - Machine-like precision and inhuman consistency
    - Sparse but devastating pattern density
    - Odd time signature adaptation to 4/4 framework
    - Palm-muted gallop patterns synced to guitars

    Implemented using composable modifications:
    - PolyrrhythmApplication: Cross-metric patterns (7-over-5-over-4)
    - MechanicalPrecision: Extreme timing/velocity quantization
    """

    def __init__(self):
        self.polyrhythm = PolyrhythmApplication(
            kick_subdivisions=7,
            snare_subdivisions=4,
            tom_subdivisions=5,
            intensity=0.6,
        )
        self.precision = MechanicalPrecision(quantize_amount=1.0)

    @property
    def drummer_name(self) -> str:
        return "haake"

    @property
    def preferred_genres(self) -> list[str]:
        return ["metal", "progressive", "djent", "experimental"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Thomas Haake's signature polyrhythmic style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_haake"

        # Layer polyrhythm first (creates the mathematical complexity)
        styled = self.polyrhythm.apply(styled, intensity=0.7)
        # Then apply mechanical precision (makes it sound like a machine)
        styled = self.precision.apply(styled, intensity=1.0)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Thomas Haake's signature fill patterns.

        Based on Meshuggah discography (Destroy Erase Improve / Kobayashi):
          - Polynrhythmic tom cascade: 7-over-5 split between hands
          - Destroy Erase palm mute gallop: matching guitar chugging rhythm
          - Coobayashi odd-meter fill: 11/8 adapted to 4/4 grid
          - Nothing polyrhythm showcase: kick 5 vs snare 4 interlock
          - Rational-gesture machine-gun: industrial tom-edge staccato
          - Catch-32 blast-polyrhythm: hybrid blast + cross-meter
          - Flesh cadence: sparse devastating hit placement (Haake's philosophy)
          - Bleed polyrhythm: ride/crash in non-traditional metric grid
        """
        return [
            Fill(
                pattern=self._create_polyrhythm_tom_cascade(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_destroy_erase_gallop(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_kobayashi_odd_meter_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_nothing_polyrhythm_showcase(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_rational_gesture_machine(),
                trigger_probability=0.7,
                section_position="end",
            ),
            Fill(
                pattern=self._create_catch32_polyrhythm_blast(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_flesh_cadence_sparse(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_bleed_polyrhythm(),
                trigger_probability=0.55,
                section_position="middle",
            ),
        ]

    def _create_polyrhythm_tom_cascade(self) -> Pattern:
        """7-over-5 tom cascade — Haake's signature cross-meter approach.

        Simultaneously plays 7 hits on one hand and 5 on the other across
        a single bar, creating a polyrhythmic cascading effect that doesn't
        resolve until the next bar. Documented in Meshuggah live performances.
        """
        builder = PatternBuilder("haake_poly_tom_cascade")

        # Left hand: 7 hits across 4/4 (odd subdivision)
        left_interval = TIMING.HALF * 2 / 7
        for i in range(7):
            pos = round(i * left_interval, 6)
            builder.pattern.add_beat(
                pos, InstrumentRegistry.get("tom_3_open_hit"), VELOCITY.TOM_HEAVY
            )

        # Right hand: 5 hits offset (creates 7-over-5 interlock)
        right_interval = TIMING.HALF * 2 / 5
        for i in range(5):
            pos = round(i * right_interval + right_interval / 2, 6)
            builder.pattern.add_beat(
                pos, InstrumentRegistry.get("tom_4_open_hit"), VELOCITY.TOM_ACCENT
            )

        # Sparse double-kick foundation on the "one" and syncopated
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.HALF * 2 / 3, min(VELOCITY.KICK_NORMAL + 10, 127))

        return builder.build()

    def _create_destroy_erase_gallop(self) -> Pattern:
        """Destroy Erase Improve palm-muted gallop fill.

        From the title track of Meshuggah's breakthrough album. Haake plays
        a polyrhythmic pattern that mirrors the palm-muted guitar chugging —
        typically 4/4 guitar riff with drum playing 5-over-4 or similar.
        Simulated as sparse but devastating hits synced to gallop rhythm.
        """
        builder = PatternBuilder("haake_destroy_gallop")

        # Sparse kick pattern mimicking palm-muted guitar (5 notes in 4/4)
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5, 6)
            builder.kick(pos, VELOCITY.KICK_HEAVY)

        # Snare accents on the "downbeats" of the gallop
        snare_hits = [0.0, TIMING.HALF * 2 / 5, 2.0, TIMING.HALF * 6 / 5]
        for pos in snare_hits:
            builder.snare(pos, VELOCITY.SNARE_ACCENT)

        # Tom-edge accents (sparse but cutting through)
        builder.pattern.add_beat(
            TIMING.HALF * 4 / 5, InstrumentRegistry.get("tom_3_rimshot_open_hit_dbl"), VELOCITY.TOM_HEAVY
        )
        builder.pattern.add_beat(
            TIMING.HALF * 8 / 5,
            InstrumentRegistry.get("tom_4_rimshot_open_hit_dbl"),
            VELOCITY.TOM_ACCENT,
        )

        # Sparse hi-hat (not busy — sparse is key to Haake's style)
        for i in range(4):
            builder.hihat(i * TIMING.HALF, VELOCITY.HIHAT_NORMAL)

        # Chug-chick choked crash accents — defining Meshuggah articulation
        builder.pattern.add_beat(
            TIMING.HALF * 3 / 2,
            InstrumentRegistry.get("cymbal_1_choke"),
            VELOCITY.CRASH_ACCENT,
        )
        builder.pattern.add_beat(
            TIMING.HALF * 7 / 4,
            InstrumentRegistry.get("cymbal_4_choke"),
            VELOCITY.CHINA_NORMAL,
        )

        return builder.build()

    def _create_kobayashi_odd_meter_fill(self) -> Pattern:
        """Kobayashi odd-meter fill adapted to 4/4 grid.

        From the Kobayashi album where Meshuggah experiments with odd meters.
        Haake adapts 11/8 and 7/8 patterns onto a 4/4 framework — creating
        rhythmic displacement that feels "off" until it snaps back on beat.
        """
        builder = PatternBuilder("haake_kobayashi_odd")

        # 11-note pattern stretched across 4 bars (creates odd-meter feel)
        for i in range(11):
            pos = round(i * TIMING.HALF * 2 * 4 / 11, 6)
            builder.kick(
                pos, VELOCITY.KICK_HEAVY if i % 3 == 0 else VELOCITY.KICK_NORMAL
            )

        # Snare on the "implied" downbeats of the odd meter (not obvious)
        snare_pos = [0.0, 1.82, 3.64, 5.45]  # 11/8 subdivisions in 4/4
        for pos in snare_pos:
            builder.snare(pos, VELOCITY.SNARE_HEAVY)

        # Tom fills at odd positions (syncopated)
        for i in range(4):
            tom_pos = round(TIMING.HALF * 2 + i * TIMING.QUARTER + 0.3, 6)
            builder.pattern.add_beat(
                tom_pos, InstrumentRegistry.get("tom_3_open_hit"), VELOCITY.TOM_ACCENT
            )

        return builder.build()

    def _create_nothing_polyrhythm_showcase(self) -> Pattern:
        """Nothing polyrhythmic interlock showcase.

        From Nothing Meshuggah — the quintessential Haake pattern featuring
        simultaneous independent rhythms: kick at 5 notes, snare at 4 notes,
        each with their own internal logic. The two rhythms only align on bar
        boundaries creating constant tension/release.
        """
        builder = PatternBuilder("haake_nothing_polyrhythm")

        # Kick: 5 evenly spaced hits across the bar
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5, 6)
            builder.kick(pos, VELOCITY.KICK_HEAVY)

        # Snare: 4 hits (traditional backbeat but displaced)
        for i in range(4):
            pos = round(i * TIMING.HALF * 2 / 4 + 0.15, 6)  # slight offset
            builder.snare(pos, VELOCITY.SNARE_ACCENT)

        # Tom accents at yet another subdivision (7 over bar)
        for i in range(7):
            pos = round(i * TIMING.HALF * 2 / 7 + 0.1, 6)
            builder.pattern.add_beat(
                pos,
                (
                    InstrumentRegistry.get("tom_4_open_hit")
                    if i % 2 == 0
                    else InstrumentRegistry.get("tom_3_open_hit")
                ),
                VELOCITY.TOM_NORMAL,
            )

        return builder.build()

    def _create_rational_gesture_machine(self) -> Pattern:
        """Rational-gesture industrial machine pattern.

        From Rational-gesture Meshuggah — mechanical, staccato hits that
        mimic industrial machinery. Haake uses tom-edge and rim shots for
        their tight, metallic timbre creating a "machine" sound. Sparse but
        precise every hit lands on a distinct grid point.
        """
        builder = PatternBuilder("haake_rational_gesture")

        # Machine-gun tom edge pattern (tight, metallic)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            variant = "3" if i % 2 == 0 else "4"
            builder.tom_edge(pos, variant, VELOCITY.TOM_HEAVY)

        # Double-kick on downbeats (mechanical, not busy)
        for i in range(4):
            builder.kick(i * TIMING.HALF, VELOCITY.KICK_ACCENT)

        return builder.build()

    def _create_catch32_polyrhythm_blast(self) -> Pattern:
        """Catch-32 hybrid blast-polyrhythm fill.

        Combines blast-beat density with polynrhythmic complexity — kick/snare
        alternating in a 7-over-5 pattern at extreme velocity. Only Haake could
        make this sound musical rather than mathematical. Based on live Meshuggah
        performances where he bridges traditional blast beats with djent rhythms.
        """
        builder = PatternBuilder("haake_catch32_poly_blast")

        # 7-hit kick pattern (polyrhythmic) at blast speed
        for i in range(7):
            pos = round(i * TIMING.SIXTEENTH / 2, 6)
            builder.kick(
                pos, VELOCITY.KICK_HEAVY if i % 2 == 0 else VELOCITY.KICK_NORMAL
            )

        # 5-hit snare pattern (offset from kick) at blast speed
        for i in range(5):
            pos = round(i * TIMING.SIXTEENTH / 2 + TIMING.SIXTEENTH / 4, 6)
            builder.snare(pos, VELOCITY.SNARE_HEAVY)

        # Ride cymbal accents every 3rd hit (creates 3-over-7 feel)
        for i in range(3):
            pos = round(i * TIMING.HALF * 2 / 3, 6)
            builder.pattern.add_beat(
                pos, InstrumentRegistry.get("ride_1_tip_hit_softer"), VELOCITY.CHINA_ACCENT
            )

        return builder.build()

    def _create_flesh_cadence_sparse(self) -> Pattern:
        """Flesh cadence sparse but devastating placement.

        Haake's philosophical approach to fills: fewer hits placed with perfect
        timing for maximum impact. Each hit lands exactly where it should — not
        "busy" but surgically precise. This is the core of his signature style:
        minimal density, maximum consequence.
        """
        builder = PatternBuilder("haake_flesh_sparse")

        # Sparse kick (only 3 hits in the bar — devastating when they land)
        builder.kick(0.0, VELOCITY.KICK_ACCENT)
        builder.kick(TIMING.HALF * 1.5, VELOCITY.KICK_HEAVY)
        builder.kick(
            TIMING.DOTTED_EIGHTH * 3, min(VELOCITY.KICK_NORMAL + 12, 127)
        )

        # Snare on the off-beats (unexpected placement creates tension)
        builder.snare(TIMING.EIGHTH + TIMING.SIXTEENTH, VELOCITY.SNARE_ACCENT)
        builder.snare(
            TIMING.HALF + TIMING.EIGHTH_TRIPLET,
            min(VELOCITY.SNARE_HEAVY + 2, 127),
        )

        # Single devastating tom accent (sparse but impactful)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH * 2,
            InstrumentRegistry.get("tom_4_open_hit"),
            VELOCITY.TOM_ACCENT,
        )

        return builder.build()

    def _create_bleed_polyrhythm(self) -> Pattern:
        """Bleed polyrhythmic cymbal placement.

        From Bleed Meshuggah — Haake places ride/crash accents on non-traditional
        metric grids creating cross-rhythms between cymbals and the kit backbone.
        The crash hits "in the cracks" of the kick pattern rather than on downbeats.
        """
        builder = PatternBuilder("haake_bleed_polyrhythm")

        # Kick backbone: traditional but sparse
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.HALF, min(VELOCITY.KICK_NORMAL + 10, 127))

        # Ride accents on odd subdivisions (creates polyrhythmic tension)
        for i in range(5):
            pos = round(i * TIMING.HALF * 2 / 5 + 0.1, 6)
            builder.pattern.add_beat(
                pos, InstrumentRegistry.get("ride_1_tip_hit_softer"), VELOCITY.CHINA_ACCENT - 10
            )

        # Crash accents placed between beat positions (unconventional)
        for i in range(3):
            pos = round(TIMING.HALF + i * TIMING.QUARTER + 0.25, 6)
            builder.pattern.add_beat(
                pos, InstrumentRegistry.get("cymbal_1_hit"), VELOCITY.CHINA_ACCENT - 15
            )

        # Snare on backbeats (anchoring the polyrhythm)
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_HEAVY)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)

        return builder.build()


# backward-compat alias for existing test imports
HaakePluginRefactored = HaakePlugin
