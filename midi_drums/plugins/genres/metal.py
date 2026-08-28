"""Metal genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~22% while maintaining
full functional equivalence with the original metal.py plugin.
"""

from midi_drums.config import TIMING
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.patterns import (
    BasicGroove,
    BlastBeat,
    CrashAccents,
    DoubleBassPedal,
    TemplateComposer,
    TomFill,
)
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin

# AD2 extended crash/tom variants for timbral variety across metal styles
_AD2_CRASH = {
    "heavy": DrumInstrument.CRASH_HEAVY,
    "light": DrumInstrument.CRASH_LIGHT,
    "splash": DrumInstrument.CRASH_SPLASH,
}

# Styles that use china cymbal (rather than ride) as the high-energy
# timekeeper, per issue #18's research: china-as-ride-substitute is a
# documented convention in extreme/thrash metal, distinct from rock's
# crash-riding convention.
_CHINA_TIMEKEEPER_STYLES = frozenset({"thrash", "death"})


class MetalGenrePlugin(GenrePlugin):
    """Metal genre plugin using template composition.

    Refactored version that uses declarative pattern templates instead of
    manual PatternBuilder construction. Supports all 7 original metal styles
    with identical output characteristics.
    """

    @property
    def genre_name(self) -> str:
        return "metal"

    @property
    def supported_styles(self) -> list[str]:
        return [
            "heavy",
            "death",
            "power",
            "progressive",
            "thrash",
            "doom",
            "breakdown",
        ]

    DEFAULT_TEMPO_MAP: dict[str, int] = {
        "heavy": 140,
        "death": 195,
        "power": 160,
        "progressive": 140,
        "thrash": 200,
        "doom": 70,
        "breakdown": 100,
    }

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Metal genre intensity characteristics."""
        return {
            "aggression": 0.9,
            "speed": 0.8,
            "density": 0.8,
            "power": 1.0,
            "complexity": 0.6,
            "darkness": 0.9,
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate metal pattern based on section and style."""
        style = parameters.style
        complexity = parameters.complexity

        if section == "intro":
            pattern = self._generate_intro(style, complexity)
        elif section == "verse":
            pattern = self._generate_verse(style, complexity)
        elif section == "chorus":
            pattern = self._generate_chorus(style, complexity)
        elif section == "breakdown":
            pattern = self._generate_breakdown(style, complexity)
        elif section in ["bridge", "pre_chorus"]:
            pattern = self._generate_bridge(style, complexity)
        elif section in ["outro", "ending"]:
            pattern = self._generate_outro(style, complexity)
        else:
            pattern = self._generate_verse(style, complexity)

        return self._apply_ride_hihat_logic(pattern, section, parameters)

    def get_common_fills(self) -> list[Fill]:
        """Get common metal fill patterns using TomFill template."""
        fills = []

        # Tom roll fill using TomFill template with AD2 edge tom accents
        tom_roll_pattern = (
            TemplateComposer("metal_tom_roll")
            .add(
                TomFill(
                    pattern="descending",
                    subdivision=TIMING.SIXTEENTH,
                    start_position=0.0,
                    use_edge=True,  # AD2: TOM_EDGE_1/2 for aggressive attack
                )
            )
            .build(bars=1, complexity=0.8)
        )
        fills.append(Fill(tom_roll_pattern, 0.8))

        # Blast beat fill using BlastBeat template
        blast_pattern = (
            TemplateComposer("metal_blast_fill")
            .add(BlastBeat(style="traditional", intensity=0.9))
            .build(bars=1)
        )
        fills.append(Fill(blast_pattern, 0.6))

        return fills

    def get_section_flavors(
        self, section: str, parameters: GenerationParameters
    ) -> list[Pattern]:
        """Return 3 distinct pattern flavors for this (section, style).

        Each flavor differs in kick placement, snare density, or timekeeper so
        ComposerV2 can rotate skeletons bar-by-bar instead of repeating the same
        skeleton with velocity tweaks only.
        """
        style = parameters.style
        complexity = parameters.complexity

        if section == "intro":
            return self._flavors_intro(style, complexity)
        elif section == "verse":
            return self._flavors_verse(style, complexity)
        elif section == "chorus":
            return self._flavors_chorus(style, complexity)
        elif section == "breakdown":
            return self._flavors_breakdown(style, complexity)
        elif section in ("bridge", "pre_chorus"):
            return self._flavors_bridge(style, complexity)
        elif section in ("outro", "ending"):
            return self._flavors_outro(style, complexity)
        return []

    def get_section_grooves(
        self, section: str, complexity: float, style: str = "default"
    ) -> list[Pattern]:
        """Return 6+ structurally distinct grooves for this section.

        Extreme metal variation comes from blast style (traditional/hammer/gravity),
        kick subdivision density (sixteenth vs eighth-triplet), snare displacement,
        and cymbal timekeeping — not just BlastBeat + DoubleBassPedal combos.
        """
        c = complexity

        if section == "intro":
            grooves = [
                # g1: Sparse quarter-hat with tom build to splash crash (classic metal intro)
                (
                    TemplateComposer("metal_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="splash"
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g2: Double-kick pulse with china accent (black metal intro feel)
                (
                    TemplateComposer("metal_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 1.5, 3.0], intensity=0.7))
                    .build(bars=1, complexity=c)
                ),
                # g3: Rising double-kick with build to crash (doom metal intro)
                (
                    TemplateComposer("metal_intro_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[
                                0.0,
                                0.5,
                                1.0,
                                1.5,
                                2.0,
                                2.5,
                                3.0,
                                3.5,
                            ],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[3.0], intensity=1.0))
                    .build(bars=1, complexity=c)
                ),
            ]
        elif section == "verse":
            # === DEATH METAL: dense blast beats, aggressive double bass ===
            if style == "death":
                return [
                    TemplateComposer("metal_death_verse_g1")
                    .add(BlastBeat(style="gravity", intensity=1.0))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_death_verse_g2")
                    .add(BlastBeat(style="hammer", intensity=0.95))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.8,
                            pattern_type="burst",
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_death_verse_g3")
                    .add(BlastBeat(style="traditional", intensity=0.9))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.85,
                            pattern_type="continuous",
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === DOOM METAL: slow/tom-heavy, sparse blasts, crushing weight ===
            if style == "doom":
                return [
                    TemplateComposer("metal_doom_verse_g1")
                    .add(
                        BlastBeat(style="traditional", intensity=0.5)
                    )  # very sparse blast
                    .add(TomFill(pattern="around", start_position=3.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("metal_doom_verse_g2")
                    .add(
                        BlastBeat(style="gravity", intensity=0.6)
                    )  # sparse gravity blast
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("metal_doom_verse_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === THRASH METAL: fast gallop, tight crashes, aggression ===
            if style == "thrash":
                return [
                    TemplateComposer("metal_thrash_verse_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.9,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.7))
                    .add(CrashAccents(positions=[3.5], intensity=0.9))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_thrash_verse_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="hammer", intensity=0.6))
                    .add(
                        CrashAccents(
                            positions=[3.5], intensity=0.9, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_thrash_verse_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.8,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.65))
                    .build(bars=1, complexity=max(0.3, c)),
                ]
            # === POWER METAL: anthemic energy, big crash accents, driving rhythm ===
            if style == "power":
                return [
                    TemplateComposer("metal_power_verse_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.7))
                    .add(CrashAccents(positions=[3.5], intensity=0.9))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_power_verse_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.8,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.75))
                    .add(CrashAccents(positions=[3.5], intensity=0.85))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_power_verse_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.75,
                            pattern_type="continuous",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.65))
                    .build(bars=1, complexity=c),
                ]
            # === PROGRESSIVE METAL: odd-meter grooves, complex ride/syncopation ===
            if style == "progressive":
                return [
                    TemplateComposer("metal_prog_verse_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.7,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.65))
                    .add(CrashAccents(positions=[3.5], intensity=0.85))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_prog_verse_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.65,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.6))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_prog_verse_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.7,
                            pattern_type="burst",
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === BREAKDOWN METAL: syncopated breakdown patterns ===
            if style == "breakdown":
                return [
                    TemplateComposer("metal_breakdown_verse_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.5],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="descending", start_position=3.0))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_breakdown_verse_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=c),
                    TemplateComposer("metal_breakdown_verse_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 3.0],
                            snare_positions=[1.5],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.15)),
                ]
            # === HEAVY (default): balanced blast patterns ===
            grooves = [
                # g1: Gravity blast — kick-led blasts with snare accents (Blastbeat gravity + sparse snare)
                # Different from traditional: snare hits only on 2&4, kicks do the work
                (
                    TemplateComposer("metal_verse_g_gravity")
                    .add(BlastBeat(style="gravity", intensity=1.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g2: Hammer blast — snare-led with sixteenth double-bass under it (hoglan-style)
                # Maximum density; kick follows snare's aggressive attack
                (
                    TemplateComposer("metal_verse_g_hammer")
                    .add(BlastBeat(style="hammer", intensity=0.95))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g3: Traditional blast — classic blast with snare on every beat
                # Standard death metal verse; balanced kick/snare interplay
                (
                    TemplateComposer("metal_verse_g_trad")
                    .add(BlastBeat(style="traditional", intensity=0.85))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.7,
                            pattern_type="burst",
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g4: Gallop verse — Iron Maiden-style gallop (dada-dada) with crash accents
                # More rhythmic drive than straight blasts; works for power/progressive metal
                (
                    TemplateComposer("metal_verse_g_gallop")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.7))
                    .add(CrashAccents(positions=[3.5], intensity=0.9))
                    .build(bars=1, complexity=c)
                ),
                # g5: Sparse blast verse — slower blast with tom accents (doom/sludge feel)
                # Less density allows space for guitar drones
                (
                    TemplateComposer("metal_verse_g_sparse")
                    .add(BlastBeat(style="traditional", intensity=0.6))
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2))
                ),
            ]
        elif section == "chorus":
            # === DEATH METAL CHORUS: maximum blast energy ===
            if style == "death":
                return [
                    TemplateComposer("metal_death_chorus_g1")
                    .add(BlastBeat(style="gravity", intensity=1.0))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("metal_death_chorus_g2")
                    .add(BlastBeat(style="hammer", intensity=1.0))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 1.0, 2.0, 3.0], intensity=0.85
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("metal_death_chorus_g3")
                    .add(BlastBeat(style="traditional", intensity=0.95))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.95,
                            pattern_type="continuous",
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                ]
            # === DOOM METAL CHORUS: sparse tom-heavy ===
            if style == "doom":
                return [
                    TemplateComposer("metal_doom_chorus_g1")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(TomFill(pattern="around", start_position=3.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c + 0.1)),
                    TemplateComposer("metal_doom_chorus_g2")
                    .add(BlastBeat(style="gravity", intensity=0.6))
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c + 0.1)),
                ]
            # === THRASH METAL CHORUS: gallop-driven with big crashes ===
            if style == "thrash":
                return [
                    TemplateComposer("metal_thrash_chorus_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.95,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.8))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                    TemplateComposer("metal_thrash_chorus_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.9,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.75))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                ]
            # === POWER METAL CHORUS: anthemic gallop energy ===
            if style == "power":
                return [
                    TemplateComposer("metal_power_chorus_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.95,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.8))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                    TemplateComposer("metal_power_chorus_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.9,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.75))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                    TemplateComposer("metal_power_chorus_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.9,
                            pattern_type="continuous",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.85))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
            # === PROGRESSIVE METAL CHORUS: complex timekeeping ===
            if style == "progressive":
                return [
                    TemplateComposer("metal_prog_chorus_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.95,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.85))
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.9,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("metal_prog_chorus_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.9,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.8))
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("metal_prog_chorus_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.85,
                            pattern_type="continuous",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.75))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                ]
            # === BREAKDOWN METAL CHORUS: driving stomp patterns ===
            if style == "breakdown":
                return [
                    TemplateComposer("metal_breakdown_chorus_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("metal_breakdown_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
            # === HEAVY (default) CHORUS: maximum blast energy ===
            grooves = [
                # g1: Full gravity blast + heavy crash (maximum impact chorus opener)
                # Gravity blast provides drive; big crashes mark each bar
                (
                    TemplateComposer("metal_chorus_g1")
                    .add(BlastBeat(style="gravity", intensity=1.0))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.2))
                ),
                # g2: Hammer blast + every-beat crash (wall of sound)
                # Unrelenting energy; snare drives the blast while crashes add attack
                (
                    TemplateComposer("metal_chorus_g2")
                    .add(BlastBeat(style="hammer", intensity=1.0))
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 1.0, 2.0, 3.0], intensity=0.85
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2))
                ),
                # g3: Gallop chorus — double-bass gallop with ride/timekeeping
                # Rhythmic variation from straight blasts; feels more dynamic/less mechanical
                (
                    TemplateComposer("metal_chorus_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.95,
                            pattern_type="gallop",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.8))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=min(1.0, c + 0.15))
                ),
            ]
        elif section == "breakdown":
            grooves = [
                # g1: Sparse kick pattern with descending tom (classic breakdown fill-in)
                (
                    TemplateComposer("metal_breakdown_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.5],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="descending", start_position=3.0))
                    .build(bars=1, complexity=c)
                ),
                # g2: Four-on-floor stomp with heavy crash (doom/alt-metal breakdown)
                # Driving single-note feel; contrasts with blast-heavy sections
                (
                    TemplateComposer("metal_breakdown_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=c)
                ),
                # g3: Half-time groove with snare displacement (groove-oriented breakdown)
                (
                    TemplateComposer("metal_breakdown_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 3.0],
                            snare_positions=[1.5],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.15))
                ),
            ]
        elif section in ("bridge", "pre_chorus"):
            # === DEATH METAL BRIDGE: sparse blast building to tension ===
            if style == "death":
                return [
                    TemplateComposer("metal_death_bridge_g1")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_death_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.7,
                            pattern_type="gallop",
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_death_bridge_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.95,
                            pattern_type="continuous",
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=0.8))
                    .build(bars=1, complexity=max(0.0, c - 0.05)),
                ]
            # === DOOM METAL BRIDGE: slow sparse build with tom emphasis ===
            if style == "doom":
                return [
                    TemplateComposer("metal_doom_bridge_g1")
                    .add(BlastBeat(style="traditional", intensity=0.3))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("metal_doom_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === THRASH METAL BRIDGE: gallop build accelerating energy ===
            if style == "thrash":
                return [
                    TemplateComposer("metal_thrash_bridge_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_thrash_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.8,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === POWER METAL BRIDGE: anthemic build with tom cascades ===
            if style == "power":
                return [
                    TemplateComposer("metal_power_bridge_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_power_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.8,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_power_bridge_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=0.75,
                            pattern_type="continuous",
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=0.8))
                    .build(bars=1, complexity=max(0.0, c - 0.05)),
                ]
            # === PROGRESSIVE METAL BRIDGE: complex timekeeping builds ===
            if style == "progressive":
                return [
                    TemplateComposer("metal_prog_bridge_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.65,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.5))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("metal_prog_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.6,
                            pattern_type="burst",
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === BREAKDOWN METAL BRIDGE: sparse stomp build ===
            if style == "breakdown":
                return [
                    TemplateComposer("metal_breakdown_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("metal_breakdown_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === HEAVY (default) BRIDGE: standard blast builds ===
            grooves = [
                # g1: Sparse blast with tom accents (building tension)
                (
                    TemplateComposer("metal_bridge_g1")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1))
                ),
                # g2: Gallop build — accelerating energy toward next section
                (
                    TemplateComposer("metal_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1))
                ),
                # g3: Heavy double-bass wall (maximum intensity bridge)
                (
                    TemplateComposer("metal_bridge_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=0.8))
                    .build(bars=1, complexity=max(0.0, c - 0.05))
                ),
            ]
        elif section in ("outro", "ending"):
            # === DEATH METAL OUTRO: heavy tom+crash finale ===
            if style == "death":
                return [
                    TemplateComposer("metal_death_outro_g1")
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_death_outro_g2")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === DOOM METAL OUTRO: sparse blast fade ===
            if style == "doom":
                return [
                    TemplateComposer("metal_doom_outro_g1")
                    .add(BlastBeat(style="traditional", intensity=0.4))
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_doom_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === THRASH METAL OUTRO: descending tom + crash finale ===
            if style == "thrash":
                return [
                    TemplateComposer("metal_thrash_outro_g1")
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_thrash_outro_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.6,
                            pattern_type="burst",
                        )
                    )
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === POWER METAL OUTRO: anthemic finale with tom cascade ===
            if style == "power":
                return [
                    TemplateComposer("metal_power_outro_g1")
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_power_outro_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.5,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="traditional", intensity=0.4))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_power_outro_g3")
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PROGRESSIVE METAL OUTRO: complex timekeeping fade ===
            if style == "progressive":
                return [
                    TemplateComposer("metal_prog_outro_g1")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH_TRIPLET,
                            intensity=0.5,
                            pattern_type="burst",
                        )
                    )
                    .add(BlastBeat(style="gravity", intensity=0.4))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_prog_outro_g2")
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BREAKDOWN METAL OUTRO: half-time stomp + crash finale ===
            if style == "breakdown":
                return [
                    TemplateComposer("metal_breakdown_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("metal_breakdown_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HEAVY (default) OUTRO: standard metal finale patterns ===
            grooves = [
                # g1: Sparse blast with tom accents (building tension)
                (
                    TemplateComposer("metal_bridge_g1")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1))
                ),
                # g2: Gallop build — accelerating energy toward next section
                (
                    TemplateComposer("metal_bridge_g2")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.EIGHTH,
                            intensity=0.85,
                            pattern_type="gallop",
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1))
                ),
                # g3: Heavy double-bass wall (maximum intensity bridge)
                (
                    TemplateComposer("metal_bridge_g3")
                    .add(
                        DoubleBassPedal(
                            subdivision=TIMING.SIXTEENTH,
                            intensity=1.0,
                            pattern_type="continuous",
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=0.8))
                    .build(bars=1, complexity=max(0.0, c - 0.05))
                ),
            ]
        elif section in ("outro", "ending"):
            grooves = [
                # g1: Descending tom + heavy crash finale
                (
                    TemplateComposer("metal_outro_g1")
                    .add(TomFill(pattern="descending", start_position=0.0))
                    .add(CrashAccents(positions=[3.75], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3))
                ),
                # g2: Sparse blast fade with tom accents
                (
                    TemplateComposer("metal_outro_g2")
                    .add(BlastBeat(style="traditional", intensity=0.5))
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3))
                ),
                # g3: Half-time stomp + crash (epic finale)
                (
                    TemplateComposer("metal_outro_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[3.5], intensity=1.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3))
                ),
            ]
        else:
            # Fallback: use flavors as grooves (with actual style)
            from midi_drums.core.value_objects.generation_parameters import (
                GenerationParameters,
            )

            flavors = self.get_section_flavors(
                section,
                GenerationParameters(genre=self.genre_name, style=style),
            )
            grooves = flavors[:6] if len(flavors) > 6 else flavors

        return self._style_grooves(section, grooves, style)

    def _style_grooves(
        self, section: str, grooves: list[Pattern], style: str
    ) -> list[Pattern]:
        """Filter/swap grooves based on metal style."""
        if style not in ("doom", "power", "progressive", "thrash"):
            return grooves  # heavy/death use default dense grooves

        result = []
        for g in grooves:
            name_lower = g.name.lower()
            skip = False
            if style == "doom" and section == "verse":
                # doom: sparse blasts with tom accents, not dense hammer blasts
                if "hammer" in name_lower or "continuous" in name_lower:
                    skip = True
            elif style == "power" and section == "verse":
                # power metal: gallop patterns are key
                if "sparse" in name_lower:
                    skip = True
            elif style == "progressive" and section == "verse":
                # progressive: avoid straight blast beats, keep grooves
                if "gravity" in name_lower:
                    skip = True
            elif style == "thrash" and section == "chorus":
                # thrash chorus: keep gallop, remove sparse patterns
                pass  # keep all for high energy
            if not skip:
                result.append(g)

        return result

    def _flavors_intro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"metal_{style}_intro"
        # Flavor 1: sparse quarter-hat with crash on beat 1 (use splash for dramatic intro)
        f1 = (
            TemplateComposer(f"{name}_i_sparse")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(
                CrashAccents(
                    positions=[0.0], intensity=1.0, crash_type="splash"
                )
            )
            .build(bars=1, complexity=complexity)
        )
        # Flavor 2: double-kick build with crash at end (use light crash for buildup)
        f2 = (
            TemplateComposer(f"{name}_i_double")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(
                CrashAccents(positions=[3.0], intensity=1.0, crash_type="light")
            )
            .build(bars=1, complexity=complexity)
        )
        # Flavor 3: crash-sparse with tom fill (use light crashes to build tension)
        f3 = (
            TemplateComposer(f"{name}_i_crash")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(
                CrashAccents(
                    positions=[0.0, 1.5, 3.0], intensity=0.7, crash_type="light"
                )
            )
            .build(bars=1, complexity=complexity)
        )
        return [f1, f2, f3]

    def _flavors_verse(self, style: str, complexity: float) -> list[Pattern]:
        name = f"metal_{style}_verse"
        # Flavor 1: sparse blast — less dense timekeeper
        f1 = (
            TemplateComposer(f"{name}_v_sparse")
            .add(
                DoubleBassPedal(
                    subdivision=TIMING.EIGHTH_TRIPLET,
                    intensity=0.7,
                    pattern_type="burst",
                )
            )
            .add(BlastBeat(style="traditional", intensity=0.85))
            .build(bars=1, complexity=complexity)
        )
        # Flavor 2: continuous double bass (maximum density)
        f2 = (
            TemplateComposer(f"{name}_v_full")
            .add(
                DoubleBassPedal(
                    subdivision=TIMING.SIXTEENTH,
                    intensity=1.0,
                    pattern_type="continuous",
                )
            )
            .add(BlastBeat(style="hammer", intensity=0.95))
            .build(bars=1, complexity=complexity)
        )
        # Flavor 3: syncopated gallop pattern
        f3 = (
            TemplateComposer(f"{name}_v_sync")
            .add(
                DoubleBassPedal(
                    subdivision=TIMING.EIGHTH,
                    intensity=0.85,
                    pattern_type="gallop",
                )
            )
            .add(BlastBeat(style="traditional", intensity=0.7))
            .build(bars=1, complexity=complexity)
        )
        return [f1, f2, f3]

    def _flavors_chorus(self, style: str, complexity: float) -> list[Pattern]:
        name = f"metal_{style}_chorus"
        c = min(1.0, complexity + 0.2)
        # Flavor 1: blast + crash on 1 and 3 (use HEAVY for maximum impact)
        f1 = (
            TemplateComposer(f"{name}_c_blast")
            .add(BlastBeat(style="traditional", intensity=1.0))
            .add(
                CrashAccents(
                    positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                )
            )
            .build(bars=1, complexity=c)
        )
        # Flavor 2: gallop + crash on every quarter (HEAVY crashes for wall of sound)
        f2 = (
            TemplateComposer(f"{name}_c_gallop")
            .add(
                DoubleBassPedal(
                    subdivision=TIMING.EIGHTH,
                    intensity=0.95,
                    pattern_type="gallop",
                )
            )
            .add(
                CrashAccents(
                    positions=[0.0, 1.0, 2.0, 3.0],
                    intensity=0.85,
                    crash_type="heavy",
                )
            )
            .build(bars=1, complexity=c)
        )
        # Flavor 3: heavy double-bass wall with HEAVY crash (maximum crushing impact)
        f3 = (
            TemplateComposer(f"{name}_c_wall")
            .add(
                DoubleBassPedal(
                    subdivision=TIMING.SIXTEENTH,
                    intensity=1.0,
                    pattern_type="continuous",
                )
            )
            .add(
                CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy")
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_breakdown(
        self, style: str, complexity: float
    ) -> list[Pattern]:
        name = f"metal_{style}_breakdown"
        # Flavor 1: sparse syncopated groove with EDGE tom fills (aggressive attack)
        f1 = (
            TemplateComposer(f"{name}_b_sparse")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.5],
                    snare_positions=[1.5],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(
                TomFill(pattern="descending", start_position=3.0, use_edge=True)
            )
            .build(bars=1, complexity=complexity)
        )
        # Flavor 2: heavy stomp with HEAVY crash (crushing impact)
        f2 = (
            TemplateComposer(f"{name}_b_stomp")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.0, 2.0, 3.0],
                    snare_positions=[2.0],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(
                CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy")
            )
            .build(bars=1, complexity=complexity)
        )
        # Flavor 3: half-time slow groove with EDGE tom accents
        f3 = (
            TemplateComposer(f"{name}_b_half")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 3.0],
                    snare_positions=[1.5],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(TomFill(pattern="around", start_position=0.0, use_edge=True))
            .build(bars=1, complexity=max(0.0, complexity - 0.15))
        )
        return [f1, f2, f3]

    def _flavors_bridge(self, style: str, complexity: float) -> list[Pattern]:
        name = f"metal_{style}_bridge"
        c = max(0.0, complexity - 0.1)
        # Flavor 1: tom-heavy bridge with EDGE fills (transition to next section)
        f1 = (
            TemplateComposer(f"{name}_br_tom")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(
                TomFill(pattern="descending", start_position=0.0, use_edge=True)
            )
            .build(bars=1, complexity=c)
        )
        # Flavor 2: sparse groove with fill (LIGHT crash for subtle transition)
        f2 = (
            TemplateComposer(f"{name}_br_sparse")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.5],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(TomFill(pattern="around", start_position=3.0, use_edge=True))
            .build(bars=1, complexity=c)
        )
        # Flavor 3: ride/crash-based with LIGHT crash (smooth transition)
        f3 = (
            TemplateComposer(f"{name}_br_ride")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.5, 3.0],
                    snare_positions=[1.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(
                CrashAccents(positions=[3.5], intensity=0.8, crash_type="light")
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_outro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"metal_{style}_outro"
        c = max(0.0, complexity - 0.3)
        # Flavor 1: descending tom + crash
        f1 = (
            TemplateComposer(f"{name}_o_desc")
            .add(
                TomFill(pattern="descending", start_position=0.0, use_edge=True)
            )
            # AD2: CRASH_HEAVY for epic metal outro ending
            .add(
                CrashAccents(
                    positions=[3.75], intensity=1.0, crash_type="heavy"
                )
            )
            .build(bars=1, complexity=c)
        )
        # Flavor 2: sparse hits fading out with light crash
        f2 = (
            TemplateComposer(f"{name}_o_sparse")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            # AD2: CRASH_LIGHT for fading metal outro
            .add(
                CrashAccents(positions=[3.5], intensity=0.6, crash_type="light")
            )
            .build(bars=1, complexity=c)
        )
        # Flavor 3: tom roll finale with heavy crash
        f3 = (
            TemplateComposer(f"{name}_o_rollo")
            .add(
                TomFill(pattern="ascending", start_position=0.0, use_edge=True)
            )
            # AD2: CRASH_HEAVY for epic metal outro finale
            .add(
                CrashAccents(positions=[3.5], intensity=1.0, crash_type="heavy")
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _high_energy_timekeeper(
        self, section: str, parameters: GenerationParameters
    ) -> DrumInstrument:
        """China cymbal for thrash/death styles, ride cymbal otherwise.

        See _CHINA_TIMEKEEPER_STYLES.

        Near-identical in shape to RockGenrePlugin's override of this
        method (fixed style set -> fixed DrumInstrument, else defer to
        super()). This is a deliberate rule-of-three call, not an
        oversight: with only 2 instances, a shared declarative
        abstraction on the base GenrePlugin isn't yet justified - see
        issue #36 item 3.
        """
        if parameters.style in _CHINA_TIMEKEEPER_STYLES:
            return DrumInstrument.CHINA
        return super()._high_energy_timekeeper(section, parameters)

    # -------------------------------------------------------------------------
    # Section generators
    # -------------------------------------------------------------------------

    def _generate_intro(self, style: str, complexity: float) -> Pattern:
        """Intro pattern - builds energy with crash accent (use splash for dramatic intro)."""
        name = f"metal_{style}_intro"

        if style == "death":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="splash"
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        else:
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[2.0],
                        hihat_subdivision=TIMING.QUARTER,
                    )
                )
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="splash"
                    )
                )
                .build(bars=1, complexity=complexity)
            )

    def _generate_verse(self, style: str, complexity: float) -> Pattern:
        """Verse pattern based on style."""
        name = f"metal_{style}_verse"

        if style == "death":
            return (
                TemplateComposer(name)
                .add(
                    DoubleBassPedal(
                        subdivision=TIMING.EIGHTH,
                        intensity=1.0,
                        pattern_type="continuous",
                    )
                )
                .add(BlastBeat(style="traditional", intensity=0.9))
                .build(bars=1, complexity=complexity)
            )
        elif style == "power":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.QUARTER,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "doom":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.QUARTER,
                    )
                )
                .build(bars=1, complexity=max(0.0, complexity - 0.2))
            )
        elif style == "progressive":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 1.5, 2.25, 3.0],
                        snare_positions=[1.0, 2.75, 3.0],
                        hihat_subdivision=TIMING.SIXTEENTH,
                    )
                )
                .add(TomFill(pattern="around", start_position=3.5))
                .build(bars=1, complexity=complexity)
            )
        elif style == "thrash":
            return (
                TemplateComposer(name)
                .add(
                    DoubleBassPedal(
                        subdivision=TIMING.SIXTEENTH,
                        intensity=0.9,
                        pattern_type="gallop",
                    )
                )
                .add(BlastBeat(style="hammer", intensity=0.8))
                .build(bars=1, complexity=complexity)
            )
        elif style == "breakdown":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.5, 2.5],
                        snare_positions=[2.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .add(TomFill(pattern="descending", start_position=3.0))
                .build(bars=1, complexity=complexity)
            )
        else:  # heavy
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=complexity)
            )

    def _generate_chorus(self, style: str, complexity: float) -> Pattern:
        """Chorus pattern - more intense than verse (use HEAVY crashes for wall of sound)."""
        name = f"metal_{style}_chorus"
        # Increase intensity by 20%
        chorus_complexity = min(1.0, complexity + 0.2)

        if style == "death":
            return (
                TemplateComposer(name)
                .add(BlastBeat(style="traditional", intensity=1.0))
                .add(
                    CrashAccents(
                        positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "power":
            return (
                TemplateComposer(name)
                .add(
                    DoubleBassPedal(
                        subdivision=TIMING.EIGHTH,
                        intensity=0.9,
                        pattern_type="gallop",
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.QUARTER,
                    )
                )
                .add(
                    CrashAccents(
                        positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "doom":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.5, 2.0, 3.5],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        else:  # heavy, progressive, thrash, breakdown
            return (
                TemplateComposer(name)
                .add(
                    DoubleBassPedal(
                        subdivision=TIMING.EIGHTH,
                        intensity=0.9,
                        pattern_type="continuous",
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.QUARTER,
                    )
                )
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )

    def _generate_breakdown(self, style: str, complexity: float) -> Pattern:
        """Breakdown pattern - syncopated, heavy with EDGE tom fills for aggressive attack."""
        name = f"metal_{style}_breakdown"
        return (
            TemplateComposer(name)
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.5, 2.5],
                    snare_positions=[2.0],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(
                TomFill(pattern="descending", start_position=3.0, use_edge=True)
            )
            .build(bars=1, complexity=complexity)
        )

    def _generate_bridge(self, style: str, complexity: float) -> Pattern:
        """Bridge pattern - often simpler, with EDGE tom fills for transition."""
        name = f"metal_{style}_bridge"
        # Reduce complexity slightly for bridge
        bridge_complexity = max(0.0, complexity - 0.1)

        return (
            TemplateComposer(name)
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(TomFill(pattern="around", start_position=3.0, use_edge=True))
            .build(bars=1, complexity=bridge_complexity)
        )

    def _generate_outro(self, style: str, complexity: float) -> Pattern:
        """Outro pattern - descending tom fill with final crash."""
        name = f"metal_{style}_outro"
        # Reduce intensity by 30% for outro
        outro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(TomFill(pattern="descending", start_position=0.0))
            .add(CrashAccents(positions=[3.75], intensity=1.0))
            .build(bars=1, complexity=outro_complexity)
        )


# backward-compat alias for existing test imports
MetalGenrePluginRefactored = MetalGenrePlugin
