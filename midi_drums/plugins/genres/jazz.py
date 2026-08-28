"""Jazz genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~44% while maintaining
full functional equivalence with the original jazz.py plugin.
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
    BrushGroove,
    CrashAccents,
    FunkGhostNotes,
    JazzRidePattern,
    TemplateComposer,
    TomFill,
)
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin

# AD2 crash/ride variants for timbral variety in jazz
# Used via CrashAccents(crash_type=...) and TomFill(use_edge=...)
_AD2_CRASH_LIGHT = "light"  # CRASH_LIGHT (77) - verses, softer sections
_AD2_CRASH_HEAVY = "heavy"  # CRASH_HEAVY (89) - choruses, energy bursts
_AD2_CRASH_SPLASH = "splash"  # CRASH_SPLASH (93) - fills, bright endings


class JazzGenrePlugin(GenrePlugin):
    """Jazz genre plugin using template composition.

    Refactored version that uses declarative pattern templates instead of
    manual PatternBuilder construction. Supports all 7 original jazz styles
    with identical output characteristics.
    """

    @property
    def genre_name(self) -> str:
        return "jazz"

    @property
    def supported_styles(self) -> list[str]:
        return [
            "swing",
            "bebop",
            "fusion",
            "latin",
            "ballad",
            "hard_bop",
            "contemporary",
        ]

    DEFAULT_TEMPO_MAP: dict[str, int] = {
        "swing": 150,
        "bebop": 210,
        "fusion": 130,
        "latin": 125,
        "ballad": 70,
        "hard_bop": 200,
        "contemporary": 140,
    }

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Jazz genre intensity characteristics."""
        return {
            "aggression": 0.3,
            "speed": 0.7,
            "density": 0.6,
            "power": 0.4,
            "complexity": 0.85,
            "darkness": 0.3,
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate jazz pattern based on section and style."""
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
        elif section == "outro":
            pattern = self._generate_outro(style, complexity)
        else:
            pattern = self._generate_verse(style, complexity)

        return self._apply_ride_hihat_logic(pattern, section, parameters)

    def get_common_fills(self) -> list[Fill]:
        """Get common jazz fill patterns using templates."""
        fills = []

        # Jazz tom fill
        tom_fill_pattern = (
            TemplateComposer("jazz_tom_fill")
            .add(
                TomFill(
                    pattern="around",
                    subdivision=TIMING.EIGHTH_TRIPLET,
                    start_position=2.0,
                )
            )
            .build(bars=1, complexity=0.6)
        )
        fills.append(
            Fill(
                tom_fill_pattern,
                trigger_probability=0.7,
                section_position="end",
            )
        )

        # Ride-based fill
        ride_fill_pattern = (
            TemplateComposer("jazz_ride_fill")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="elvin"))
            .add(FunkGhostNotes(density=0.4, emphasize_one=False))
            .build(bars=1, complexity=0.7)
        )
        fills.append(
            Fill(
                ride_fill_pattern,
                trigger_probability=0.6,
                section_position="middle",
            )
        )

        return fills

    def get_section_flavors(
        self, section: str, parameters: GenerationParameters
    ) -> list[Pattern]:
        """Return 3 distinct jazz flavors for this (section, style)."""
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
        elif section == "outro":
            return self._flavors_outro(style, complexity)
        return []

    def get_section_grooves(
        self, section: str, complexity: float, style: str = "default"
    ) -> list[Pattern]:
        """Return 5+ structurally distinct grooves for this section.

        Jazz groove variation comes from:
        - Ride accent patterns (standard/Elvin/Tony) — changes feel significantly
        - Brush vs stick timekeeping for ballad vs up-tempo sections
        - Walking bass following kick (crucial! drummer follows the bassist)
        - Ghost note density and crash placement
        """
        c = complexity

        if section == "intro":
            # === SWING INTRO: traditional ride + sparse kick — classic era ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_intro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_swing_intro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_swing_intro_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === BEBOP INTRO: tight comping with ride accents — fast precision ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_intro_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_bebop_intro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === FUSION INTRO: straight-eighth timekeeper — electric energy ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_intro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_fusion_intro_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.2, accent_pattern="elvin")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === LATIN INTRO: clave-based sparse build — syncopated feel ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_intro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_latin_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === BALLAD INTRO: brush sweep timekeeper — intimate feel ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_intro_g1")
                    .add(BrushGroove(density=0.5))
                    .add(CrashAccents(positions=[3.5], intensity=0.6))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("jazz_ballad_intro_g2")
                    .add(BrushGroove(density=0.4))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === HARD_BOP INTRO: aggressive ride comping — energetic build ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_intro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_hbop_intro_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.35, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === CONTEMPORARY INTRO: modern stick/brush blend ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_intro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_contemp_intro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
        elif section == "verse":
            # === SWING VERSE: standard ride comping + walking bass follow — classic era ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_swing_verse_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_swing_verse_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === BEBOP VERSE: tight comping + dense ride accents — Parker/Gillespie ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_verse_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_bebop_verse_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_bebop_verse_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.32, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === FUSION VERSE: straight-eighth comping — electric energy ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_fusion_verse_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.2, accent_pattern="elvin")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_fusion_verse_g3")
                    .add(
                        JazzRidePattern(swing_ratio=0.25, accent_pattern="tony")
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === LATIN VERSE: clave-based kick + syncopated snare — Latin jazz tradition ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_latin_verse_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 2.5],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_latin_verse_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === BALLAD VERSE: brush timekeeper — intimate, sparse ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_verse_g1")
                    .add(BrushGroove(density=0.8))
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_ballad_verse_g2")
                    .add(BrushGroove(density=0.7))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_ballad_verse_g3")
                    .add(BrushGroove(density=0.9))
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === HARD_BOP VERSE: aggressive ride comping — energetic build ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_hbop_verse_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.35, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_hbop_verse_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === CONTEMPORARY VERSE: modern stick/brush blend ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_contemp_verse_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("jazz_contemp_verse_g3")
                    .add(
                        JazzRidePattern(swing_ratio=0.32, accent_pattern="tony")
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
        elif section == "chorus":
            # === SWING CHORUS: Elvin ride + walking bass — maximum energy ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.8))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.5, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_swing_chorus_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                    TemplateComposer("jazz_swing_chorus_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.85))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === BEBOP CHORUS: tight comping + heavy crashes — Parker era intensity ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_chorus_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_bebop_chorus_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="elvin")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0, 3.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.8))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
            # === FUSION CHORUS: straight-eighth comping — electric energy ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_fusion_chorus_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.25, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.95))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_fusion_chorus_g3")
                    .add(
                        JazzRidePattern(swing_ratio=0.2, accent_pattern="elvin")
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.85))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === LATIN CHORUS: clave-based crashes — energetic Latin jazz ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_latin_chorus_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 2.5],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
            # === BALLAD CHORUS: brush timekeeper with crashes — softer but active ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_chorus_g1")
                    .add(BrushGroove(density=0.9))
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.7))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.5, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                    TemplateComposer("jazz_ballad_chorus_g2")
                    .add(BrushGroove(density=0.85))
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(CrashAccents(positions=[0.0], intensity=0.7))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.5, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === HARD_BOP CHORUS: aggressive ride comping — maximum energy ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.8, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_hbop_chorus_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.35, accent_pattern="tony")
                    )
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_hbop_chorus_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.75, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.95))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
            # === CONTEMPORARY CHORUS: modern stick/brush blend ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("jazz_contemp_chorus_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(FunkGhostNotes(density=0.65, emphasize_one=False))
                    .add(CrashAccents(positions=[0.0], intensity=0.85))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                    TemplateComposer("jazz_contemp_chorus_g3")
                    .add(
                        JazzRidePattern(swing_ratio=0.32, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                ]
        elif section == "breakdown":
            # === SWING BREAKDOWN: sparse ride — bass carries everything ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_breakdown_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_swing_breakdown_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_swing_breakdown_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BEBOP BREAKDOWN: sparse ride comping — transition moment ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_breakdown_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_bebop_breakdown_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === FUSION BREAKDOWN: sparse straight comping — electronic energy drops ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_breakdown_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_fusion_breakdown_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === LATIN BREAKDOWN: sparse clave-based build — intimate ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_breakdown_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_latin_breakdown_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BALLAD BREAKDOWN: brush timekeeper — intimate breakdown ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_breakdown_g1")
                    .add(BrushGroove(density=0.4))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_ballad_breakdown_g2")
                    .add(BrushGroove(density=0.3))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_ballad_breakdown_g3")
                    .add(BrushGroove(density=0.4))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HARD_BOP BREAKDOWN: sparse aggressive comping — tension build ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_breakdown_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_hbop_breakdown_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === CONTEMPORARY BREAKDOWN: sparse stick comping — modern minimalism ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_breakdown_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_contemp_breakdown_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
        elif section in ("bridge", "pre_chorus"):
            # === SWING BRIDGE: sparse ride + sparse kick — minimal timekeeping ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_bridge_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_swing_bridge_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_swing_bridge_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === BEBOP BRIDGE: sparse comping — tension build for chorus ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_bridge_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_bebop_bridge_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === FUSION BRIDGE: sparse straight comping — electronic minimalism ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_bridge_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_fusion_bridge_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.2, accent_pattern="elvin")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === LATIN BRIDGE: sparse clave-based — tension build ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_bridge_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_latin_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === BALLAD BRIDGE: brush timekeeper + sparse kick — intimate bridge ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_bridge_g1")
                    .add(BrushGroove(density=0.6))
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_ballad_bridge_g2")
                    .add(BrushGroove(density=0.5))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_ballad_bridge_g3")
                    .add(BrushGroove(density=0.4))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === HARD_BOP BRIDGE: sparse aggressive comping — tension build ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_bridge_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_hbop_bridge_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === CONTEMPORARY BRIDGE: sparse stick comping — modern minimalism ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_bridge_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("jazz_contemp_bridge_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
        elif section == "outro":
            # === SWING OUTRO: sparse ride fading — classic jazz ending ===
            if style == "swing":
                return [
                    TemplateComposer("jazz_swing_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_swing_outro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_swing_outro_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="elvin"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BEBOP OUTRO: sparse ride comping fade — tight ending ===
            if style == "bebop":
                return [
                    TemplateComposer("jazz_bebop_outro_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="tony")
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_bebop_outro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === FUSION OUTRO: sparse straight comping fade — electronic ending ===
            if style == "fusion":
                return [
                    TemplateComposer("jazz_fusion_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_fusion_outro_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.25, accent_pattern="tony")
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === LATIN OUTRO: sparse clave fade — gentle ending ===
            if style == "latin":
                return [
                    TemplateComposer("jazz_latin_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_latin_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BALLAD OUTRO: brush sweep fading — intimate finish ===
            if style == "ballad":
                return [
                    TemplateComposer("jazz_ballad_outro_g1")
                    .add(BrushGroove(density=0.5))
                    .add(CrashAccents(positions=[3.5], intensity=0.6))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_ballad_outro_g2")
                    .add(BrushGroove(density=0.4))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_ballad_outro_g3")
                    .add(BrushGroove(density=0.5))
                    .add(CrashAccents(positions=[3.5], intensity=0.6))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HARD_BOP OUTRO: sparse aggressive comping fade — energetic ending ===
            if style == "hard_bop":
                return [
                    TemplateComposer("jazz_hbop_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_hbop_outro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === CONTEMPORARY OUTRO: sparse stick comping fade — modern ending ===
            if style == "contemporary":
                return [
                    TemplateComposer("jazz_contemp_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("jazz_contemp_outro_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
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
        """Filter/swap grooves based on jazz style."""
        if style not in ("ballad", "bebop", "fusion", "latin", "hard_bop"):
            return grooves  # swing/contemporary use default

        result = []
        for g in grooves:
            name_lower = g.name.lower()
            skip = False
            if style == "ballad" and section == "chorus":
                # ballad chorus: keep brush-based, remove heavy crash patterns
                if "crash" in name_lower or (
                    "ride" in name_lower and "elvin" in name_lower
                ):
                    skip = True
            elif style == "bebop" and section == "verse":
                # bebop verse: remove brush grooves, need tighter comping patterns
                if "brush" in name_lower:
                    skip = True
            elif style == "fusion" and section in ("intro", "verse"):
                # fusion: swap ride accent for straight-eighth feel
                if "elvin" in name_lower or "tony" in name_lower:
                    skip = True
            elif style == "latin" and section in ("verse", "chorus"):
                # latin: remove brush/timekeeper grooves, need syncopated patterns
                if "brush" in name_lower or "standard" in name_lower:
                    skip = True
            elif style == "hard_bop" and section == "bridge":
                # hard bop bridge: keep sparse patterns for tension building
                pass  # don't skip anything
            if not skip:
                result.append(g)

        return result

    def _flavors_intro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"jazz_{style}_intro"
        c = max(0.0, complexity - 0.3)
        # 1: sparse ballad ride with minimal kick
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .build(bars=1, complexity=c)
        )
        # 2: traditional swing with light brush pattern
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(JazzRidePattern(swing_ratio=0.35, accent_pattern="standard"))
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .build(bars=1, complexity=c)
        )
        # 3: modern minimal hi-hat comping
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="tony"))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_verse(self, style: str, complexity: float) -> list[Pattern]:
        name = f"jazz_{style}_verse"
        # 1: classic swing with ghost notes
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .add(
                FunkGhostNotes(
                    density=0.4,
                    emphasize_one=False,
                    main_snare_positions=[1.0, 3.0],
                )
            )
            .build(bars=1, complexity=complexity)
        )
        # 2: bebop-style with tighter comping
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(JazzRidePattern(swing_ratio=0.35, accent_pattern="tony"))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.75, 2.0, 2.33],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .build(bars=1, complexity=complexity)
        )
        # 3: fusion straight-eighth with tight hi-hat
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="standard"))
            .add(FunkGhostNotes(density=0.5, emphasize_one=True))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .build(bars=1, complexity=complexity)
        )
        return [f1, f2, f3]

    def _flavors_chorus(self, style: str, complexity: float) -> list[Pattern]:
        name = f"jazz_{style}_chorus"
        c = min(1.0, complexity + 0.2)
        # 1: heavy swing with crash accents
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.35, accent_pattern="elvin"))
            .add(FunkGhostNotes(density=0.6, emphasize_one=False))
            .add(CrashAccents(positions=[0.0], intensity=0.8))
            .build(bars=1, complexity=c)
        )
        # 2: bebop with tom fills and ride crashes
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="tony"))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.0, 2.0, 3.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=0.8))
            .build(bars=1, complexity=c)
        )
        # 3: latin-tinged with dense ghost notes
        groove_3 = BasicGroove(
            kick_positions=[0.0, 0.75, 2.0, 2.75],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(JazzRidePattern(swing_ratio=0.25, accent_pattern="elvin"))
            .add(FunkGhostNotes(density=0.7, emphasize_one=True))
            .add(groove_3)
            .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_breakdown(
        self, style: str, complexity: float
    ) -> list[Pattern]:
        name = f"jazz_{style}_breakdown"
        c = max(0.0, complexity - 0.3)
        # 1: sparse ballad ride only
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .build(bars=1, complexity=c)
        )
        # 2: tight hi-hat with sparse kick
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .build(bars=1, complexity=c)
        )
        # 3: minimal tom tap with cymbal swell
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(TomFill(pattern="around", start_position=0.0))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_bridge(self, style: str, complexity: float) -> list[Pattern]:
        name = f"jazz_{style}_bridge"
        c = max(0.0, complexity - 0.1)
        # 1: ballad feel with sparse ride
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.35, accent_pattern="standard"))
            .build(bars=1, complexity=c)
        )
        # 2: fusion-style with tight comping
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="standard"))
            .add(FunkGhostNotes(density=0.5, emphasize_one=False))
            .add(TomFill(pattern="around", start_position=3.0))
            .build(bars=1, complexity=c)
        )
        # 3: open cymbal build with ascending tom
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(TomFill(pattern="ascending", start_position=3.0))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_outro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"jazz_{style}_outro"
        c = max(0.0, complexity - 0.3)
        # 1: fade-out ride pattern
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .build(bars=1, complexity=c)
        )
        # 2: sparse ballad tap with crash on last beat
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(CrashAccents(positions=[3.5], intensity=0.6))
            .build(bars=1, complexity=c)
        )
        # 3: minimal hi-hat only
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[],
                    snare_positions=[],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _high_energy_timekeeper(
        self, section: str, parameters: GenerationParameters
    ) -> DrumInstrument:
        """Default ride cymbal for jazz timekeeping."""
        return super()._high_energy_timekeeper(section, parameters)

    # -------------------------------------------------------------------------
    # Section generators
    # -------------------------------------------------------------------------

    def _generate_intro(self, style: str, complexity: float) -> Pattern:
        """Intro pattern - sets the mood."""
        name = f"jazz_{style}_intro"
        intro_complexity = max(0.0, complexity - 0.3)

        if style in ["ballad"]:
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .build(bars=1, complexity=intro_complexity)
            )
        else:
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                # AD2: CRASH_LIGHT for intimate/gentle jazz intros
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.5, crash_type="light"
                    )
                )
                .build(bars=1, complexity=intro_complexity)
            )

    def _generate_verse(self, style: str, complexity: float) -> Pattern:
        """Verse pattern based on style."""
        name = f"jazz_{style}_verse"

        if style == "swing":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .add(
                    FunkGhostNotes(
                        density=0.3,
                        emphasize_one=False,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "bebop":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="tony"))
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 2.0, 2.33],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "fusion":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.2, accent_pattern="standard")
                )
                .add(
                    FunkGhostNotes(
                        density=0.4,
                        emphasize_one=True,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "latin":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 2.0, 2.75],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(
                    FunkGhostNotes(
                        density=0.5,
                        emphasize_one=True,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "ballad":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .build(bars=1, complexity=max(0.0, complexity - 0.3))
            )
        elif style == "hard_bop":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="elvin"))
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.5, 2.0, 3.5],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .add(CrashAccents(positions=[0.0], intensity=0.8))
                .build(bars=1, complexity=complexity)
            )
        else:  # contemporary
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.2, accent_pattern="standard")
                )
                .add(
                    FunkGhostNotes(
                        density=0.5,
                        emphasize_one=False,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .add(TomFill(pattern="around", start_position=3.5))
                .build(bars=1, complexity=complexity)
            )

    def _generate_chorus(self, style: str, complexity: float) -> Pattern:
        """Chorus pattern - more intense than verse."""
        name = f"jazz_{style}_chorus"
        chorus_complexity = min(1.0, complexity + 0.2)

        if style == "swing":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="elvin"))
                .add(
                    FunkGhostNotes(
                        density=0.5,
                        emphasize_one=False,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                # AD2: CRASH_LIGHT for jazz chorus (not too aggressive)
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.7, crash_type="light"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "bebop":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="tony"))
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                # AD2: CRASH_HEAVY for energy burst in bebop chorus
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.9, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "fusion":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="tony"))
                .add(
                    FunkGhostNotes(
                        density=0.6,
                        emphasize_one=True,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.5, 2.0, 2.5],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                # AD2: CRASH_HEAVY for fusion energy burst
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.95, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "hard_bop":
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="tony"))
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                # AD2: CRASH_LIGHT for both crashes in hard bop
                .add(
                    CrashAccents(
                        positions=[0.0, 2.0], intensity=0.85, crash_type="light"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        elif style == "ballad":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .add(
                    FunkGhostNotes(
                        density=0.3,
                        emphasize_one=False,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )
        else:  # latin, contemporary
            return (
                TemplateComposer(name)
                .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="elvin"))
                .add(
                    FunkGhostNotes(
                        density=0.6,
                        emphasize_one=True,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                # AD2: TomFill with edge tom for aggressive jazz fills
                .add(
                    TomFill(pattern="around", start_position=3.0, use_edge=True)
                )
                # AD2: CRASH_LIGHT for latin/contemporary chorus
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.8, crash_type="light"
                    )
                )
                .build(bars=1, complexity=chorus_complexity)
            )

    def _generate_breakdown(self, style: str, complexity: float) -> Pattern:
        """Breakdown pattern - sparse, minimal."""
        name = f"jazz_{style}_breakdown"
        return (
            TemplateComposer(name)
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .build(bars=1, complexity=max(0.0, complexity - 0.3))
        )

    def _generate_bridge(self, style: str, complexity: float) -> Pattern:
        """Bridge pattern - often a solo or transition."""
        name = f"jazz_{style}_bridge"
        bridge_complexity = max(0.0, complexity - 0.1)

        if style in ["fusion", "contemporary"]:
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.2, accent_pattern="standard")
                )
                .add(
                    FunkGhostNotes(
                        density=0.4,
                        emphasize_one=False,
                        main_snare_positions=[1.0, 3.0],
                    )
                )
                # AD2: TomFill with edge tom for fusion/contemporary bridge
                .add(
                    TomFill(pattern="around", start_position=3.0, use_edge=True)
                )
                .build(bars=1, complexity=bridge_complexity)
            )
        else:
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                # AD2: TomFill with edge tom for ascending bridge fill
                .add(
                    TomFill(
                        pattern="ascending", start_position=3.0, use_edge=True
                    )
                )
                .build(bars=1, complexity=bridge_complexity)
            )

    def _generate_outro(self, style: str, complexity: float) -> Pattern:
        """Outro pattern - winds down."""
        name = f"jazz_{style}_outro"
        outro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(JazzRidePattern(swing_ratio=0.33, accent_pattern="standard"))
            .build(bars=1, complexity=outro_complexity)
        )


# backward-compat alias for existing test imports
JazzGenrePluginRefactored = JazzGenrePlugin
