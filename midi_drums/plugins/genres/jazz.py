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
    CrashAccents,
    FunkGhostNotes,
    JazzRidePattern,
    TemplateComposer,
    TomFill,
)
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin


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
                .add(CrashAccents(positions=[0.0], intensity=0.8))
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
                .add(CrashAccents(positions=[0.0], intensity=0.8))
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
                .add(CrashAccents(positions=[0.0], intensity=0.9))
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
                .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
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
                .add(TomFill(pattern="around", start_position=3.0))
                .add(CrashAccents(positions=[0.0], intensity=0.8))
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
                .add(TomFill(pattern="around", start_position=3.0))
                .build(bars=1, complexity=bridge_complexity)
            )
        else:
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(swing_ratio=0.33, accent_pattern="standard")
                )
                .add(TomFill(pattern="ascending", start_position=3.0))
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
