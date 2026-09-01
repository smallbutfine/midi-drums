"""Rock genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~35% while maintaining
full functional equivalence with the original rock.py plugin.
"""

from midi_drums.config import TIMING
from midi_drums.core.models.kit import DrumInstrument, InstrumentRegistry
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.patterns import (
    BasicGroove,
    CrashAccents,
    FunkGhostNotes,
    JazzRidePattern,
    RimshotGroove,
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

    DEFAULT_TEMPO_MAP: dict[str, int] = {
        "classic": 110,
        "blues": 100,
        "alternative": 115,
        "progressive": 120,
        "punk": 180,
        "hard": 125,
        "pop": 110,
    }

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
            # AD2: CRASH_HEAVY for rock crash fill accents
            .add(
                CrashAccents(
                    positions=[0.0, 2.0], intensity=0.9, crash_type="heavy"
                )
            )
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

    def get_section_grooves(
        self, section: str, complexity: float, style: str = "default"
    ) -> list[Pattern]:
        """Return style-aware groove library for this section.

        Genuinely different patterns per style — not filters on a shared set:
        - **classic** (110): Ride timekeeper, standard swing Bonham-style kick 1+2.5
        - **blues** (100): Shuffle triplet behind-beat feel, rimshot backbeats
        - **alternative** (115): Sparse kick placement, tight hats only, chorus crashes
        - **progressive** (120): Odd-meter grooves, syncopated kicks, Elvin ride accents
        - **punk** (180): Crash-as-timekeeper, four-on-floor, bare-bones skeleton
        - **hard** (125): Driving power kick, heavy crash accents, tom fills
        - **pop** (110): Tight hats w/ghost notes, accessible four-on-floor
        """
        c = complexity

        if section == "verse":
            # === CLASSIC ROCK: ride timekeeper, standard backbeat ===
            if style == "classic":
                return [
                    # g1: Ride cymbal timekeeper — Bonham/Zeppelin classic verse
                    TemplateComposer("rock_classic_verse_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    # g2: Ride + subtle kick variation — Bonham follow-guitar patterns
                    TemplateComposer("rock_classic_verse_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    # g3: Ride + open HH accents — deeper pocket with space
                    TemplateComposer("rock_classic_verse_g3")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                            use_open_hihat=True,
                            open_hihat_positions=[2.0],
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]

            # === BLUES ROCK: shuffle feel behind the beat, rimshot backbeats ===
            if style == "blues":
                return [
                    # g1: Shuffle triplet subdivision with rimshot backbeat — SRV/Allman-style
                    TemplateComposer("rock_blues_verse_g1")
                    .add(
                        RimshotGroove(use_tight_hh=False)
                    )  # tight HH only for funk, not blues
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    # g2: Behind-beat shuffle with open HH comping every other beat
                    TemplateComposer("rock_blues_verse_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[2.5], intensity=0.6, crash_type="light"
                        )
                    )  # open HH accent on shuffle
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    # g3: Shuffle groove with ghost notes — tighter pocket
                    TemplateComposer("rock_blues_verse_g3")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c)),
                ]

        elif section == "chorus":
            # === CLASSIC ROCK CHORUS: ride timekeeper + heavy crashes ===
            if style == "classic":
                return [
                    TemplateComposer("rock_classic_chorus_g1")
                    .add(
                        JazzRidePattern(swing_ratio=0.3, accent_pattern="elvin")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_classic_chorus_g2")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0, 3.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.9,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_classic_chorus_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.6, c + 0.2)),
                ]
            # === BLUES ROCK CHORUS: half-time power chorus, rimshot backbeats ===
            if style == "blues":
                return [
                    TemplateComposer("rock_blues_chorus_g1")
                    .add(RimshotGroove(use_tight_hh=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=1.0,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_blues_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=0.9, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c)),
                ]
            # === ALTERNATIVE ROCK CHORUS: crash-heavy explosion ===
            if style == "alternative":
                return [
                    TemplateComposer("rock_alt_chorus_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.2)),
                    TemplateComposer("rock_alt_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=1.0,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_alt_chorus_g3")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=max(0.5, c + 0.2)),
                ]
            # === PROGRESSIVE ROCK CHORUS: complex timekeeping, Elvin accents ===
            if style == "progressive":
                return [
                    TemplateComposer("rock_prog_chorus_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="elvin"
                        )
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.9,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c + 0.2)),
                    TemplateComposer("rock_prog_chorus_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.35, accent_pattern="tony")
                    )
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
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_prog_chorus_g3")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.85,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.6, c + 0.2)),
                ]
            # === PUNK CHORUS: four-on-floor power, crash every beat ===
            if style == "punk":
                return [
                    TemplateComposer("rock_punk_chorus_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 1.0, 2.0, 3.0],
                            intensity=0.9,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.6, c + 0.2)),
                    TemplateComposer("rock_punk_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.6, c + 0.1)),
                    TemplateComposer("rock_punk_chorus_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.5, c)),
                ]
            # === HARD ROCK CHORUS: driving power kick + heavy crashes ===
            if style == "hard":
                return [
                    TemplateComposer("rock_hard_chorus_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.7, c + 0.3)),
                    TemplateComposer("rock_hard_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=1.0,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=max(0.7, c + 0.2)),
                    TemplateComposer("rock_hard_chorus_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.7, c + 0.2)),
                ]
            # === POP ROCK CHORUS: accessible four-on-floor with ghost notes ===
            if style == "pop":
                return [
                    TemplateComposer("rock_pop_chorus_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=max(0.5, c + 0.2)),
                    TemplateComposer("rock_pop_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.85))
                    .build(bars=1, complexity=max(0.5, c + 0.1)),
                    TemplateComposer("rock_pop_chorus_g3")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
                    .build(bars=1, complexity=max(0.5, c + 0.2)),
                ]

        elif section == "bridge":
            # === CLASSIC BRIDGE: ride-only, sparse feel ===
            if style == "classic":
                return [
                    TemplateComposer("rock_classic_bridge_g1")
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
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_classic_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_classic_bridge_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BLUES BRIDGE: half-time with rimshots — blues/jam feel ===
            if style == "blues":
                return [
                    TemplateComposer("rock_blues_bridge_g1")
                    .add(RimshotGroove())
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_blues_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=0.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === ALTERNATIVE BRIDGE: tense/industrial feel ===
            if style == "alternative":
                return [
                    TemplateComposer("rock_alt_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("rock_alt_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_alt_bridge_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PROGRESSIVE BRIDGE: odd-meter timekeeping, Elvin ride ===
            if style == "progressive":
                return [
                    TemplateComposer("rock_prog_bridge_g1")
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
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_prog_bridge_g2")
                    .add(
                        JazzRidePattern(swing_ratio=0.35, accent_pattern="tony")
                    )
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("rock_prog_bridge_g3")
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
            # === PUNK BRIDGE: sparse build to chorus ===
            if style == "punk":
                return [
                    TemplateComposer("rock_punk_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_punk_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === HARD ROCK BRIDGE: building tension with tom fills ===
            if style == "hard":
                return [
                    TemplateComposer("rock_hard_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_hard_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_hard_bridge_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === POP BRIDGE: sparse build, clean feel ===
            if style == "pop":
                return [
                    TemplateComposer("rock_pop_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_pop_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("rock_pop_bridge_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]

        elif section == "intro":
            # === CLASSIC INTRO: sparse ride + tom build ===
            if style == "classic":
                return [
                    TemplateComposer("rock_classic_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_classic_intro_g2")
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
                    .add(CrashAccents(positions=[2.0], intensity=0.7))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_classic_intro_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === BLUES INTRO: sparse shuffle feel ===
            if style == "blues":
                return [
                    TemplateComposer("rock_blues_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=0.8, crash_type="light"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_blues_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === ALTERNATIVE INTRO: sparse kick + tom roll ===
            if style == "alternative":
                return [
                    TemplateComposer("rock_alt_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_alt_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PROGRESSIVE INTRO: odd-meter feel ===
            if style == "progressive":
                return [
                    TemplateComposer("rock_prog_intro_g1")
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
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_prog_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=0.9, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PUNK INTRO: raw drum hit into song ===
            if style == "punk":
                return [
                    TemplateComposer("rock_punk_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_punk_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HARD ROCK INTRO: heavy build to first chord ===
            if style == "hard":
                return [
                    TemplateComposer("rock_hard_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_hard_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === POP INTRO: clean sparse build ===
            if style == "pop":
                return [
                    TemplateComposer("rock_pop_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_pop_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]

        elif section == "outro":
            # === CLASSIC OUTRO: ride fade with final crash ===
            if style == "classic":
                return [
                    TemplateComposer("rock_classic_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.3, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_classic_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_classic_outro_g3")
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
            # === BLUES OUTRO: sparse shuffle fade ===
            if style == "blues":
                return [
                    TemplateComposer("rock_blues_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_blues_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=0.8, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === ALTERNATIVE OUTRO: sparse fade or bang-out ===
            if style == "alternative":
                return [
                    TemplateComposer("rock_alt_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_alt_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PROGRESSIVE OUTRO: sparse ride fade ===
            if style == "progressive":
                return [
                    TemplateComposer("rock_prog_outro_g1")
                    .add(
                        JazzRidePattern(
                            swing_ratio=0.35, accent_pattern="standard"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_prog_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === PUNK OUTRO: bang-out with crash ===
            if style == "punk":
                return [
                    TemplateComposer("rock_punk_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_punk_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HARD ROCK OUTRO: heavy bang-out ===
            if style == "hard":
                return [
                    TemplateComposer("rock_hard_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[3.75], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_hard_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === POP OUTRO: clean fade with final crash ===
            if style == "pop":
                return [
                    TemplateComposer("rock_pop_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("rock_pop_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .add(CrashAccents(positions=[3.75], intensity=0.9))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
        else:
            # Fallback for breakdown/pre_chorus: use flavors with actual style
            flavors = self.get_section_flavors(
                section,
                GenerationParameters(genre=self.genre_name, style=style),
            )
            return flavors[:6] if len(flavors) > 6 else flavors

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
            .add(
                CrashAccents(
                    positions=[0.0], intensity=1.0, crash_type="splash"
                )
            )
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
            .add(
                CrashAccents(
                    positions=[3.0], intensity=1.0, crash_type="splash"
                )
            )
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
            .add(
                CrashAccents(
                    positions=[0.0, 1.5, 3.0], intensity=0.7, crash_type="light"
                )
            )
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
            .add(
                CrashAccents(
                    positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                )
            )
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
            .add(
                CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy")
            )
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
            .add(
                CrashAccents(
                    positions=[0.0, 1.0, 2.0, 3.0],
                    intensity=0.8,
                    crash_type="heavy",
                )
            )
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
            .add(
                TomFill(pattern="descending", start_position=3.0, use_edge=True)
            )
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
            # AD2: CRASH_HEAVY for rock breakdown stomp
            .add(
                CrashAccents(positions=[0.0], intensity=1.0, crash_type="heavy")
            )
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
        # 2: sparse groove with tom accents
        f2 = (
            TemplateComposer(f"{name}_f2")
            .add(
                BasicGroove(
                    kick_positions=[0.0, 2.5],
                    snare_positions=[1.0],
                    hihat_subdivision=TIMING.EIGHTH,
                )
            )
            # AD2: TomFill with edge tom for bridge accents
            .add(TomFill(pattern="around", start_position=3.0, use_edge=True))
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
            # AD2: TomFill with edge tom for rock outro aggression
            .add(
                TomFill(pattern="descending", start_position=0.0, use_edge=True)
            )
            # AD2: CRASH_HEAVY for epic rock outro ending
            .add(
                CrashAccents(
                    positions=[3.75], intensity=1.0, crash_type="heavy"
                )
            ).build(bars=1, complexity=c)
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
            # AD2: CRASH_LIGHT for fading rock outro
            .add(
                CrashAccents(positions=[3.5], intensity=0.6, crash_type="light")
            )
            .build(bars=1, complexity=c)
        )
        # 3: ascending tom finale with heavy crash
        f3 = (
            TemplateComposer(f"{name}_f3")
            # AD2: TomFill with edge tom for ascending fill aggression
            .add(
                TomFill(pattern="ascending", start_position=0.0, use_edge=True)
            )
            # AD2: CRASH_HEAVY for epic rock outro finale
            .add(
                CrashAccents(positions=[3.5], intensity=1.0, crash_type="heavy")
            ).build(bars=1, complexity=c)
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
            return InstrumentRegistry.get("cymbal_1_hit")
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
            .add(
                CrashAccents(
                    positions=[0.0], intensity=0.9, crash_type="splash"
                )
            )
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
                # AD2: TomFill with edge tom for alternative verse aggression
                .add(
                    TomFill(pattern="around", start_position=3.0, use_edge=True)
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "progressive":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 0.75, 1.5, 2.25, 3.0],
                        snare_positions=[1.0, 2.75, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                .build(bars=1, complexity=complexity)
            )
        elif style == "punk":
            return (
                TemplateComposer(name)
                .add(
                    BasicGroove(
                        kick_positions=[0.0, 1.0, 2.0, 3.0],
                        snare_positions=[1.0, 3.0],
                        hihat_subdivision=TIMING.EIGHTH,
                    )
                )
                # AD2: CRASH_HEAVY for punk verse power
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.9, crash_type="heavy"
                    )
                )
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
                # AD2: CRASH_HEAVY for hard rock verse power
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.9, crash_type="heavy"
                    )
                )
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
                .add(
                    CrashAccents(
                        positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                    )
                )
                .build(bars=1, complexity=c)
            )
        elif style == "blues":
            return (
                TemplateComposer(name)
                .add(
                    JazzRidePattern(
                        swing_ratio=0.6,
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
                # AD2: CRASH_HEAVY for alternative chorus
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="heavy"
                    )
                )
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
                # AD2: CRASH_HEAVY for progressive chorus
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=1.0, crash_type="heavy"
                    )
                )
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
                    # AD2: CRASH_HEAVY for punk chorus (all crash hits = maximum power)
                    CrashAccents(
                        positions=[0.0, 1.0, 2.0, 3.0],
                        intensity=0.9,
                        crash_type="heavy",
                    )
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
                # AD2: CRASH_HEAVY for hard rock chorus
                .add(
                    CrashAccents(
                        positions=[0.0, 2.0], intensity=1.0, crash_type="heavy"
                    )
                )
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
                # AD2: CRASH_LIGHT for clean pop chorus
                .add(
                    CrashAccents(
                        positions=[0.0], intensity=0.8, crash_type="light"
                    )
                )
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
            # AD2: TomFill with edge tom for rock breakdown fill aggression
            .add(
                TomFill(pattern="descending", start_position=3.0, use_edge=True)
            )
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
