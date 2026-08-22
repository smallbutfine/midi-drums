"""Rock genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~35% while maintaining
full functional equivalence with the original rock.py plugin.
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
    JazzRidePattern,
    TemplateComposer,
    TomFill,
)
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin

# Styles that crash-ride through high-energy sections instead of using
# ride cymbal, per issue #18's research: hard rock/punk drummers (e.g.
# Phil Rudd) favor a big, washy crash over a controlled ride for this
# role.
_CRASH_TIMEKEEPER_STYLES = frozenset({"hard", "punk"})


class RockGenrePlugin(GenrePlugin):
    """Rock genre plugin using template composition.

    Refactored version that uses declarative pattern templates instead of
    manual PatternBuilder construction. Supports all 7 original rock styles
    with identical output characteristics.
    """

    @property
    def genre_name(self) -> str:
        return "rock"

    @property
    def supported_styles(self) -> list[str]:
        return [
            "classic",
            "blues",
            "alternative",
            "progressive",
            "punk",
            "hard",
            "pop",
        ]

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Rock genre intensity characteristics."""
        return {
            "aggression": 0.6,
            "speed": 0.6,
            "density": 0.6,
            "power": 0.75,
            "complexity": 0.5,
            "darkness": 0.5,
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate rock pattern based on section and style."""
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
        """Get common rock fill patterns using TomFill template."""
        fills = []

        # Classic rock tom fill
        tom_fill_pattern = (
            TemplateComposer("rock_tom_fill")
            .add(
                TomFill(
                    pattern="descending",
                    subdivision=TIMING.SIXTEENTH,
                    start_position=2.0,
                )
            )
            .build(bars=1, complexity=0.6)
        )
        fills.append(
            Fill(
                tom_fill_pattern,
                trigger_probability=0.8,
                section_position="end",
            )
        )

        # Ascending fill
        ascending_pattern = (
            TemplateComposer("rock_snare_fill")
            .add(
                TomFill(
                    pattern="ascending",
                    subdivision=TIMING.SIXTEENTH,
                    start_position=2.0,
                )
            )
            .build(bars=1, complexity=0.6)
        )
        fills.append(
            Fill(
                ascending_pattern,
                trigger_probability=0.7,
                section_position="middle",
            )
        )

        # Crash accent fill
        crash_pattern = (
            TemplateComposer("rock_crash_fill")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
            .build(bars=1, complexity=0.5)
        )
        fills.append(
            Fill(
                crash_pattern, trigger_probability=0.6, section_position="start"
            )
        )

        return fills

    def get_section_flavors(
        self, section: str, parameters: GenerationParameters
    ) -> list[Pattern]:
        """Return 3 distinct rock flavors for this (section, style)."""
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
        name = f"rock_{style}_intro"
        c = max(0.0, complexity - 0.3)
        # 1: sparse quarter-hat with single crash (use bright splash for dramatic intro)
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=1.0, crash_type="splash"))
            .build(bars=1, complexity=c)
        )
        # 2: double-kick build with crash at bar end
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(CrashAccents(positions=[3.0], intensity=1.0, crash_type="splash"))
            .build(bars=1, complexity=c)
        )
        # 3: crash-sparse with tom fill at end (use light crash to keep intro gentle)
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(CrashAccents(positions=[0.0, 1.5, 3.0], intensity=0.7, crash_type="light"))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_verse(self, style: str, complexity: float) -> list[Pattern]:
        name = f"rock_{style}_verse"
        # 1: classic backbeat groove (use CRASH_LIGHT for verses — softer timbre)
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .build(bars=1, complexity=complexity)
        )
        # 2: syncopated kick with tight hi-hat
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.75, 2.0, 2.75],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.SIXTEENTH,
                )
            )
            .build(bars=1, complexity=complexity)
        )
        # 3: half-time feel with heavy snare
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 3.0],
                    snare_positions=[1.5],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .build(bars=1, complexity=max(0.0, complexity - 0.1))
        )
        return [f1, f2, f3]

    def _flavors_chorus(self, style: str, complexity: float) -> list[Pattern]:
        name = f"rock_{style}_chorus"
        c = min(1.0, complexity + 0.2)
        # 1: stomp on every beat (use CRASH_HEAVY for choruses — more power/cut-through)
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.0, 2.0, 3.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"))
            .build(bars=1, complexity=c)
        )
        # 2: gallop kick pattern
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 0.75, 1.0, 1.75, 2.0, 2.75, 3.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy"))
            .build(bars=1, complexity=c)
        )
        # 3: crash-rich with ride-like cymbal timekeeping
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(CrashAccents(positions=[0.0, 1.0, 2.0, 3.0], intensity=0.8, crash_type="heavy"))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_breakdown(
        self, style: str, complexity: float
    ) -> list[Pattern]:
        name = f"rock_{style}_breakdown"
        # 1: sparse syncopated groove with tom fill (use EDGE for sharper attack)
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.5],
                    snare_positions=[1.5],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(TomFill(pattern="descending", start_position=3.0, use_edge=True))
            .build(bars=1, complexity=complexity)
        )
        # 2: heavy stomp on every beat
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.0, 2.0, 3.0],
                    snare_positions=[2.0],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=1.0))
            .build(bars=1, complexity=complexity)
        )
        # 3: half-time slow groove
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 3.0],
                    snare_positions=[1.5],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(TomFill(pattern="around", start_position=0.0))
            .build(bars=1, complexity=max(0.0, complexity - 0.15))
        )
        return [f1, f2, f3]

    def _flavors_bridge(self, style: str, complexity: float) -> list[Pattern]:
        name = f"rock_{style}_bridge"
        c = max(0.0, complexity - 0.1)
        # 1: tom-heavy bridge
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.HALF,
                )
            )
            .add(TomFill(pattern="descending", start_position=0.0))
            .build(bars=1, complexity=c)
        )
        # 2: sparse groove with fill
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.5],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(TomFill(pattern="around", start_position=3.0))
            .build(bars=1, complexity=c)
        )
        # 3: ride/crash-based
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 1.5, 3.0],
                    snare_positions=[1.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[3.5], intensity=0.8))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _flavors_outro(self, style: str, complexity: float) -> list[Pattern]:
        name = f"rock_{style}_outro"
        c = max(0.0, complexity - 0.3)
        # 1: descending tom + crash
        f1 = (
            TemplateComposer(f"{name}_f1")
            .add(TomFill(pattern="descending", start_position=0.0))
            .add(CrashAccents(positions=[3.75], intensity=1.0))
            .build(bars=1, complexity=c)
        )
        # 2: sparse hits fading out
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0],
                    snare_positions=[],
                    hihat_subdivision=TIMING.QUARTER,
                )
            )
            .add(CrashAccents(positions=[3.5], intensity=0.6))
            .build(bars=1, complexity=c)
        )
        # 3: ascending tom finale
        f3 = (
            TemplateComposer(f"{name}_f3")
            .add(TomFill(pattern="ascending", start_position=0.0))
            .add(CrashAccents(positions=[3.5], intensity=1.0))
            .build(bars=1, complexity=c)
        )
        return [f1, f2, f3]

    def _high_energy_timekeeper(
        self, section: str, parameters: GenerationParameters
    ) -> DrumInstrument:
        """Crash-ride for hard/punk styles, ride cymbal otherwise.

        See _CRASH_TIMEKEEPER_STYLES.

        Near-identical in shape to MetalGenrePlugin's override of this
        method (fixed style set -> fixed DrumInstrument, else defer to
        super()). This is a deliberate rule-of-three call, not an
        oversight: with only 2 instances, a shared declarative
        abstraction on the base GenrePlugin isn't yet justified - see
        issue #36 item 3.
        """
        if parameters.style in _CRASH_TIMEKEEPER_STYLES:
            return DrumInstrument.CRASH
        return super()._high_energy_timekeeper(section, parameters)

    # -------------------------------------------------------------------------
    # Section generators
    # -------------------------------------------------------------------------

    def _generate_intro(self, style: str, complexity: float) -> Pattern:
        """Intro pattern - typically builds energy."""
        name = f"rock_{style}_intro"
        intro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.0],
                    snare_positions=[1.0, 3.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=0.9))
            .build(bars=1, complexity=intro_complexity)
        )

    def _generate_verse(self, style: str, complexity: float) -> Pattern:
        """Verse pattern based on style."""
        name = f"rock_{style}_verse"

        if style == "classic":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "blues":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(
                        swing_ratio=0.58,
                        accent_positions=[0.0, 0.75, 1.5, 2.25, 3.0],
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.5, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "alternative":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(TomFill(pattern="around", start_position=3.0))
                .build(bars=1, complexity=complexity)
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
                .build(bars=1, complexity=complexity)
            )
        elif style == "punk":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .add(CrashAccents(positions=[0.0], intensity=0.9))
                .build(bars=1, complexity=max(0.0, complexity + 0.1))
            )
        elif style == "hard":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(CrashAccents(positions=[0.0], intensity=0.9))
                .build(bars=1, complexity=max(0.0, complexity + 0.1))
            )
        else:  # pop
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 2.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=max(0.0, complexity - 0.1))
            )

    def _generate_chorus(self, style: str, complexity: float) -> Pattern:
        """Chorus pattern - more intense than verse."""
        name = f"rock_{style}_chorus"
        c = min(1.0, complexity + 0.2)

        if style == "classic":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(CrashAccents(positions=[0.0, 2.0], intensity=1.0))
                .build(bars=1, complexity=c)
            )
        elif style == "blues":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(
                        swing_ratio=0.6,
                        accent_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                    )
                )
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=c)
            )
        elif style == "alternative":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.5, 2.0, 2.5],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(CrashAccents(positions=[0.0], intensity=1.0))
                .build(bars=1, complexity=c)
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
                .add(CrashAccents(positions=[0.0], intensity=1.0))
                .build(bars=1, complexity=c)
            )
        elif style == "punk":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.HALF,
                    )
                )
                .add(
                    CrashAccents(positions=[0.0, 1.0, 2.0, 3.0], intensity=0.9)
                )
                .build(bars=1, complexity=c)
            )
        elif style == "hard":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .add(CrashAccents(positions=[0.0, 2.0], intensity=1.0))
                .build(bars=1, complexity=c)
            )
        else:  # pop
            return (
                TemplateComposer(name)
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
        """Breakdown pattern - syncopated, heavy."""
        name = f"rock_{style}_breakdown"
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

    def _generate_bridge(self, style: str, complexity: float) -> Pattern:
        """Bridge pattern - often simpler, with added tom fills."""
        name = f"rock_{style}_bridge"
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
            .add(TomFill(pattern="around", start_position=3.0))
            .build(bars=1, complexity=bridge_complexity)
        )

    def _generate_outro(self, style: str, complexity: float) -> Pattern:
        """Outro pattern - descending tom fill with final crash."""
        name = f"rock_{style}_outro"
        outro_complexity = max(0.0, complexity - 0.3)

        return (
            TemplateComposer(name)
            .add(TomFill(pattern="descending", start_position=0.0))
            .add(CrashAccents(positions=[3.75], intensity=1.0))
            .build(bars=1, complexity=outro_complexity)
        )


# backward-compat alias for existing test imports
RockGenrePluginRefactored = RockGenrePlugin
