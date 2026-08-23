"""Funk genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~41% while maintaining
full functional equivalence with the original funk.py plugin.
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

# AD2 tight hi-hat variants per funk style (CORE feature for pocket depth)
# These replace standard closed HH with tighter timbral variants
_FUNK_TIGHT_HH_BY_STYLE = {
    "classic": "tight_b",  # TIGHT_HH_B (56) - medium tight pocket
    "pfunk": "tight_b",  # TIGHT_HH_B (56) - medium tight for deep pocket
    "shuffle": "tight_c",  # TIGHT_HH_C (58) - tightest control (Purdie shuffle)
    "new_orleans": "tight_a",  # TIGHT_HH_A (54) - looser, bouncy second line feel
    "fusion": "tight_b",  # TIGHT_HH_B (56) - medium-tight fusion pocket
    "minimal": "tight_c",  # TIGHT_HH_C (58) - tightest for minimal control
    "heavy": "tight_c",  # TIGHT_HH_C (58) - tightest for rock-funk hybrid
}

# AD2 crash type mapping per style/section context
_FUNK_CRASH_BY_STYLE = {
    "classic": "splash",  # bright shimmer on "the one" chorus downbeat
    "pfunk": "heavy",  # powerful p-funk crashes
    "shuffle": "light",  # subtle shuffle crashes
    "new_orleans": "splash",
    "fusion": "heavy",
    "minimal": None,
    "heavy": "heavy",
}


class FunkGenrePlugin(GenrePlugin):
    """Funk genre plugin using template composition.

    Refactored version that uses declarative pattern templates instead of
    manual PatternBuilder construction. Supports all 7 original funk styles
    with identical output characteristics.
    """

    @property
    def genre_name(self) -> str:
        return "funk"

    @property
    def supported_styles(self) -> list[str]:
        return [
            "classic",
            "pfunk",
            "shuffle",
            "new_orleans",
            "fusion",
            "minimal",
            "heavy",
        ]

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Funk genre intensity characteristics."""
        return {
            "aggression": 0.5,
            "speed": 0.5,
            "density": 0.75,
            "power": 0.65,
            "complexity": 0.7,
            "darkness": 0.4,
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate funk pattern based on section and style."""
        style = parameters.style
        complexity = parameters.complexity

        match section:
            case "intro":
                pattern = self._generate_intro(style, complexity)
            case "verse":
                pattern = self._generate_verse(style, complexity)
            case "chorus":
                pattern = self._generate_chorus(style, complexity)
            case "breakdown":
                pattern = self._generate_breakdown(style, complexity)
            case "bridge" | "pre_chorus":
                pattern = self._generate_bridge(style, complexity)
            case "outro":
                pattern = self._generate_outro(style, complexity)
            case _:
                pattern = self._generate_verse(style, complexity)

        return self._apply_ride_hihat_logic(pattern, section, parameters)

    def get_common_fills(self) -> list[Fill]:
        """Get common funk fill patterns using templates."""
        fills = []

        # Ghost note fill
        ghost_fill_pattern = (
            TemplateComposer("funk_ghost_fill")
            .add(
                FunkGhostNotes(
                    density=0.8,
                    emphasize_one=True,
                    main_snare_positions=[1.0, 3.0],
                )
            )
            .build(bars=1, complexity=0.7)
        )
        fills.append(
            Fill(
                ghost_fill_pattern,
                trigger_probability=0.8,
                section_position="end",
            )
        )

        # Tom fill
        tom_fill_pattern = (
            TemplateComposer("funk_tom_fill")
            .add(
                # AD2: TomFill with edge tom for sharp funk fill accents
                TomFill(
                    pattern="descending",
                    subdivision=TIMING.SIXTEENTH,
                    start_position=2.0,
                    use_edge=True,
                )
            )
            .build(bars=1, complexity=0.6)
        )
        fills.append(
            Fill(
                tom_fill_pattern,
                trigger_probability=0.6,
                section_position="middle",
            )
        )

        # Crash accent fill
        crash_pattern = (
            TemplateComposer("funk_crash_fill")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.SIXTEENTH,
                )
            )
            # AD2: CRASH_HEAVY for funk fill crash accents
            .add(
                CrashAccents(positions=[0.0], intensity=0.9, crash_type="heavy")
            )
            .build(bars=1, complexity=0.6)
        )
        fills.append(
            Fill(
                crash_pattern, trigger_probability=0.5, section_position="start"
            )
        )

        return fills

    def get_section_flavors(
        self, section: str, parameters: GenerationParameters
    ) -> list[Pattern]:
        """Return 3 distinct funk flavors for this (section, style)."""
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
        name = f"funk_{style}_intro"
        # 1: building groove with tight hi-hat
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            # AD2: CRASH_SPLASH for funk intro buildup ending
            .add(
                CrashAccents(
                    positions=[3.5], intensity=1.0, crash_type="splash"
                )
            )
            .build(bars=1, complexity=max(0.0, complexity - 0.2))
        )
        # 2: sparse attack with building snare fills
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(TomFill(pattern="ascending", start_position=2.5))
            .build(bars=1, complexity=max(0.0, complexity - 0.3))
        )
        # 3: tight stomp with double-kick build
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            # AD2: CRASH_HEAVY for funk intro stomp
            .add(
                CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy")
            )
            .build(bars=1, complexity=max(0.0, complexity - 0.3))
        )
        return [f1, f2, f3]

    def _flavors_verse(self, style: str, complexity: float) -> list[Pattern]:
        name = f"funk_{style}_verse"
        # 1: classic "the one" groove with ghost notes
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                FunkGhostNotes(
                    density=0.7,
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
        # 2: syncopated pocket with tight hi-hat
        groove_f2 = BasicGroove(
            kick_positions=[0.0, 0.75, 2.0],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.SIXTEENTH,
        )
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(FunkGhostNotes(density=0.5, emphasize_one=False))
            .add(groove_f2)
            .build(bars=1, complexity=complexity)
        )
        # 3: ghost-note heavy with half-time kick
        groove_f3 = BasicGroove(
            kick_positions=[0.0, 3.0],
            snare_positions=[1.5],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(FunkGhostNotes(density=0.9, emphasize_one=False))
            .add(groove_f3)
            .build(bars=1, complexity=max(0.0, complexity - 0.1))
        )
        return [f1, f2, f3]

    def _flavors_chorus(self, style: str, complexity: float) -> list[Pattern]:
        name = f"funk_{style}_chorus"
        c = min(1.0, complexity + 0.2)
        # 1: double-kick funk with crash accents
        groove_c1 = BasicGroove(
            kick_positions=[0.0, 0.5, 2.0, 2.5],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(FunkGhostNotes(density=0.8, emphasize_one=True))
            .add(groove_c1)
            # AD2: CRASH_HEAVY for funk chorus flavor crashes
            .add(
                CrashAccents(
                    positions=[0.0, 2.0], intensity=0.9, crash_type="heavy"
                )
            )
            .build(bars=1, complexity=c)
        )
        # 2: crash-heavy with half-time shuffle
        groove_c2 = BasicGroove(
            kick_positions=[0.0, 3.0],
            snare_positions=[1.5],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(JazzRidePattern(swing_ratio=0.6, accent_pattern="standard"))
            .add(groove_c2)
            # AD2: CRASH_LIGHT for shuffle chorus flavor crashes
            .add(
                CrashAccents(
                    positions=[0.0, 1.0, 2.0, 3.0],
                    intensity=0.7,
                    crash_type="light",
                )
            )
            .build(bars=1, complexity=c)
        )
        # 3: straight-eighth with dense kick patterns
        groove_c3 = BasicGroove(
            kick_positions=[0.0, 1.0, 2.0, 3.0],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.SIXTEENTH,
        )
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="standard"))
            .add(groove_c3)
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_breakdown(
        self, style: str, complexity: float
    ) -> list[Pattern]:
        name = f"funk_{style}_breakdown"
        # 1: sparse minimal groove
        groove_b1 = BasicGroove(
            kick_positions=[0.0],
            snare_positions=[],
            hihat_subdivision=TIMING.HALF,
        )
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(groove_b1)
            .build(bars=1, complexity=max(0.0, complexity - 0.3))
        )
        # 2: half-time groove with ghost notes
        groove_b2 = BasicGroove(
            kick_positions=[0.0, 3.0],
            snare_positions=[1.5],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(FunkGhostNotes(density=0.4, emphasize_one=False))
            .add(groove_b2)
            .build(bars=1, complexity=max(0.0, complexity - 0.2))
        )
        # 3: syncopated bass drum with sparse snare
        groove_b3 = BasicGroove(
            kick_positions=[0.0, 1.25, 2.5],
            snare_positions=[],
            hihat_subdivision=TIMING.HALF,
        )
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(groove_b3)
            .add(TomFill(pattern="descending", start_position=3.0))
            .build(bars=1, complexity=max(0.0, complexity - 0.15))
        )
        return [f1, f2, f3]

    def _flavors_bridge(self, style: str, complexity: float) -> list[Pattern]:
        name = f"funk_{style}_bridge"
        c = max(0.0, complexity - 0.1)
        # 1: fusion-style with tight comping
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(JazzRidePattern(swing_ratio=0.2, accent_pattern="standard"))
            .add(FunkGhostNotes(density=0.6, emphasize_one=True))
            # AD2: TomFill with edge tom for funk bridge accents
            .add(TomFill(pattern="around", start_position=3.0, use_edge=True))
            .build(bars=1, complexity=c)
        )
        # 2: latin-funk with clave-pattern kick
        groove_f2 = BasicGroove(
            kick_positions=[0.0, 0.75, 1.5, 2.0, 2.75],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(FunkGhostNotes(density=0.7, emphasize_one=True))
            .add(groove_f2)
            .build(bars=1, complexity=c)
        )
        # 3: sparse pocket with tom accents
        groove_f3 = BasicGroove(
            kick_positions=[0.0, 2.5],
            snare_positions=[],
            hihat_subdivision=TIMING.EIGHTH,
        )
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(groove_f3)
            # AD2: TomFill with edge tom for funk bridge fill accents
            .add(TomFill(pattern="around", start_position=0.0, use_edge=True))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_outro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"funk_{style}_outro"
        c = max(0.0, complexity - 0.3)
        # 1: fade groove with ghost notes
        groove_o1 = BasicGroove(
            kick_positions=[0.0],
            snare_positions=[],
            hihat_subdivision=TIMING.HALF,
        )
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(FunkGhostNotes(density=0.5, emphasize_one=False))
            .add(groove_o1)
            .build(bars=1, complexity=c)
        )
        # 2: sparse hits with final tom roll
        groove_o2 = BasicGroove(
            kick_positions=[0.0],
            snare_positions=[],
            hihat_subdivision=TIMING.HALF,
        )
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(groove_o2)
            # AD2: TomFill with edge tom for funk outro fill accents
            .add(
                TomFill(pattern="descending", start_position=3.0, use_edge=True)
            )
            .build(bars=1, complexity=c)
        )
        # 3: sparse tom roll finale with crash
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(TomFill(pattern="descending", start_position=0.0))
            # AD2: CRASH_SPLASH for funk outro finale ending
            .add(
                CrashAccents(
                    positions=[3.75], intensity=1.0, crash_type="splash"
                )
            )
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _high_energy_timekeeper(
        self, section: str, parameters: GenerationParameters
    ) -> DrumInstrument:
        """Default ride cymbal for funk timekeeping."""
        return super()._high_energy_timekeeper(section, parameters)

    # -------------------------------------------------------------------------
    # Section generators
    # -------------------------------------------------------------------------

    def _generate_intro(self, style: str, complexity: float) -> Pattern:
        """Intro pattern - establishes the groove."""
        name = f"funk_{style}_intro"
        intro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(
                FunkGhostNotes(
                    density=0.5,
                    emphasize_one=True,
                    main_snare_positions=[1.0, 3.0],
                )
            )
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.SIXTEENTH,
                )
            )
            .build(bars=1, complexity=intro_complexity)
        )

    def _generate_verse(self, style: str, complexity: float) -> Pattern:
        """Verse pattern based on style."""
        name = f"funk_{style}_verse"

        match style:
            case "classic":
                # James Brown "the one" emphasis
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.7,
                            emphasize_one=True,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.75, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "pfunk":
                # Parliament-Funkadelic style
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.8,
                            emphasize_one=True,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.5, 2.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "shuffle":
                # Bernard Purdie shuffle
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.6,
                            emphasize_one=False,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "new_orleans":
                # Second line funk patterns
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.5, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 2.5, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(
                        FunkGhostNotes(
                            density=0.6,
                            emphasize_one=True,
                            main_snare_positions=[1.0, 2.5, 3.0],
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "fusion":
                # Jazz-funk fusion
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.6,
                            emphasize_one=False,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
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
            case "minimal":
                # Stripped-down pocket groove
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.3,
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
                    .build(bars=1, complexity=max(0.0, complexity - 0.1))
                )
            case "heavy":
                # Heavy funk with rock influence
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.7,
                            emphasize_one=True,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.8))
                    .build(bars=1, complexity=max(0.0, complexity + 0.1))
                )
        # fallback (should not reach)
        return (
            TemplateComposer(name)
            .add(FunkGhostNotes(density=0.5, emphasize_one=True))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.SIXTEENTH,
                )
            )
            .build(bars=1, complexity=complexity)
        )

    def _generate_chorus(self, style: str, complexity: float) -> Pattern:
        """Chorus pattern - more intense than verse."""
        name = f"funk_{style}_chorus"
        c = min(1.0, complexity + 0.2)

        match style:
            case "classic":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    # AD2: CRASH_SPLASH for bright shimmer on "the one" downbeat
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.9,
                            crash_type="splash",
                        )
                    )
                    .build(bars=1, complexity=c)
                )
            case "pfunk":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    # AD2: CRASH_HEAVY for powerful p-funk chorus crashes
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=c)
                )
            case "shuffle":
                return (
                    TemplateComposer(name)
                    .add(
                        FunkGhostNotes(
                            density=0.7,
                            emphasize_one=False,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=c)
                )
            case "new_orleans":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.5, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 2.5, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    # AD2: CRASH_SPLASH for bright second line feel
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=0.85, crash_type="splash"
                        )
                    )
                    .build(bars=1, complexity=c)
                )
            case "fusion":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.8, emphasize_one=False))
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
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
                    .build(bars=1, complexity=c)
                )
            case "minimal":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.4, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=c)
                )
            case "heavy":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    # AD2: CRASH_HEAVY for rock-funk hybrid power
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=1.0,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=c)
                )
        return (
            TemplateComposer(name)
            .add(FunkGhostNotes(density=0.7, emphasize_one=True))
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=0.8))
            .build(bars=1, complexity=c)
        )

    def _generate_breakdown(self, style: str, complexity: float) -> Pattern:
        """Breakdown pattern - sparse, minimal groove."""
        name = f"funk_{style}_breakdown"
        return (
            TemplateComposer(name)
            .add(FunkGhostNotes(density=0.3, emphasize_one=False))
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .build(bars=1, complexity=max(0.0, complexity - 0.3))
        )

    def _generate_bridge(self, style: str, complexity: float) -> Pattern:
        """Bridge pattern - often a transition or solo section."""
        name = f"funk_{style}_bridge"
        bridge_complexity = max(0.0, complexity - 0.1)

        match style:
            case "classic":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )
            case "fusion":
                return (
                    TemplateComposer(name)
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.2, accent_pattern="standard"
                        )
                    )
                    .add(
                        FunkGhostNotes(
                            density=0.5,
                            emphasize_one=False,
                            main_snare_positions=[1.0, 3.0],
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )
            case "pfunk":
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 3.0],
                            snare_positions=[1.0, 2.5],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=bridge_complexity)
                )
            case "minimal":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, bridge_complexity - 0.2))
                )
            case "shuffle":
                return (
                    TemplateComposer(name)
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.33, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=bridge_complexity)
                )
            # Fallback for any unhandled style
            case _:
                return (
                    TemplateComposer(name)
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )

    def _generate_outro(self, style: str, complexity: float) -> Pattern:
        """Outro pattern - winding down with a final hit."""
        name = f"funk_{style}_outro"
        outro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(FunkGhostNotes(density=0.3, emphasize_one=False))
            .add(TomFill(pattern="descending", start_position=0.0))
            # AD2: CRASH_SPLASH for bright funk outro endings
            .add(
                CrashAccents(
                    positions=[3.75], intensity=1.0, crash_type="splash"
                )
            )
            .build(bars=1, complexity=outro_complexity)
        )

    def _apply_ride_hihat_logic(
        self,
        pattern: Pattern,
        section: str,
        parameters: GenerationParameters,
    ) -> Pattern:
        """Apply tight hi-hat variants per funk style, plus base ride promotion.

        Tight HH is the core of funk pocket depth - every style gets a specific
        AD2 tight hi-hat variant (A/B/C) that replaces standard closed HH beats.
        """
        # First: apply the base ride promotion logic from GenrePlugin
        result = super()._apply_ride_hihat_logic(pattern, section, parameters)

        # Second: override hi-hat instrument with tight HH variant based on style
        style = parameters.style
        tight_key = _FUNK_TIGHT_HH_BY_STYLE.get(style)
        if not tight_key:
            return result

        tight_map = {
            "tight_a": DrumInstrument.TIGHT_HH_A,
            "tight_b": DrumInstrument.TIGHT_HH_B,
            "tight_c": DrumInstrument.TIGHT_HH_C,
        }
        tight_instr = tight_map.get(tight_key)
        if not tight_instr:
            return result

        # Replace all closed hi-hat beats with the appropriate tight variant
        # Do NOT replace PEDAL_HH (foot pedal position markers) - those stay as-is
        tuned = result.copy()
        for beat in tuned.beats:
            if beat.instrument not in (
                DrumInstrument.CLOSED_HH,
                DrumInstrument.TIGHT_HH_EDGE,
                DrumInstrument.TIGHT_HH_TIP,
            ):
                continue
            # Don't override beats already promoted to ride/crash
            if getattr(beat, "instrument_promoted", False):
                continue
            beat.instrument = tight_instr

        return tuned


# backward-compat alias for existing test imports
FunkGenrePluginRefactored = FunkGenrePlugin
