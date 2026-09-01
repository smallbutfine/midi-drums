"""Funk genre plugin - refactored using template composition.

Uses pattern templates from midi_drums.patterns to eliminate manual
PatternBuilder construction, reducing code by ~41% while maintaining
full functional equivalence with the original funk.py plugin.
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

    DEFAULT_TEMPO_MAP: dict[str, int] = {
        "classic": 105,
        "pfunk": 100,
        "shuffle": 110,
        "new_orleans": 110,
        "fusion": 120,
        "minimal": 100,
        "heavy": 118,
    }

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

    def get_section_grooves(
        self, section: str, complexity: float, style: str = "default"
    ) -> list[Pattern]:
        """Return 6+ structurally distinct grooves for this section.

        Funk groove variation comes from:
        - RIMSHOT vs snare backbeats (rimshots = classic funk)
        - One-drop (kick on 1 only) vs two-drop (kick on 1+3) bass patterns
        - Ghost note density as PRIMARY differentiator (0.3 to 0.9)
        - Hi-hat timekeeping: eighth vs sixteenth vs open hat
        - Crash placement: sparse verses vs accent-heavy choruses
        """
        c = complexity

        if section == "intro":
            # === CLASSIC FUNK INTRO: sparse kick build — James Brown era ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_intro_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_classic_intro_g2")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_classic_intro_g3")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=2.5))
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === P-FUNK INTRO: deep pocket sparse build — Mose Allison feel ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_intro_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_pfunk_intro_g2")
                    .add(FunkGhostNotes(density=0.4, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === SHUFFLE INTRO: Purdie shuffle sparse — behind-beat feel ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_intro_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_shuffle_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === NEW ORLEANS INTRO: second line sparse build — clave syncopation ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_intro_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_no_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === FUSION INTRO: sparse straight comping — jazz-funk minimalism ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_intro_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_fusion_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === MINIMAL INTRO: extremely sparse — bass alone intro ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_intro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_minimal_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HEAVY INTRO: rock-funk sparse build — aggressive energy ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_intro_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_heavy_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
            # === HEAVY INTRO: rock-funk sparse build — aggressive energy ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_intro_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_heavy_intro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                ]
        elif section == "verse":
            # === CLASSIC FUNK VERSE: one-drop (kick on 1) + heavy ghost notes — James Brown foundation ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_verse_g1")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_classic_verse_g2")
                    .add(FunkGhostNotes(density=0.85, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_classic_verse_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === P-FUNK VERSE: complex syncopated bass patterns — Parliament-Funkadelic deep pocket ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_verse_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.75, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_pfunk_verse_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_pfunk_verse_g3")
                    .add(FunkGhostNotes(density=0.75, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === SHUFFLE VERSE: Purdie shuffle triplet timekeeping — behind-beat pocket ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_verse_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_shuffle_verse_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_shuffle_verse_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.75, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === NEW ORLEANS VERSE: second line clave syncopation — brass-driven groove ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_verse_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.75, 2.0, 2.75],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_no_verse_g2")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_no_verse_g3")
                    .add(FunkGhostNotes(density=0.65, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === FUSION VERSE: tight straight-eighth comping — jazz-funk groove ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_verse_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_fusion_verse_g2")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_fusion_verse_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.65, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === MINIMAL VERSE: sparse minimalist funk — maximum room for bass/guitar ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_verse_g1")
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_minimal_verse_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_minimal_verse_g3")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === HEAVY VERSE: rock-funk hybrid — four-on-floor drive with ghost notes ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_verse_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_heavy_verse_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                    TemplateComposer("funk_heavy_verse_g3")
                    .add(FunkGhostNotes(density=0.75, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c),
                ]
            # === FUNK (default): generic funk groove fallback — balanced style ===
            grooves = [
                # g1: Classic James Brown one-drop (kick on 1 only) + heavy ghost notes
                # One-drop = foundation of funk; kick ON THE ONE lets bass carry walking
                (
                    TemplateComposer("funk_verse_g1_onedrop")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g2: Rimshot groove + moderate ghosting (tighter pocket — Meters/Cream style)
                # Rimshots replace snare for the classic funk sound
                (
                    TemplateComposer("funk_verse_g_rimshot")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g3: Sixteen-hat pulse + light ghosting (parlay-style verse — busy hats)
                # Busy hats create energy without volume; kick follows bassline syncopation
                (
                    TemplateComposer("funk_verse_g_sixteen")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.75, 2.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g4: Two-drop (kick on 2) + moderate ghosting (driving funk verse)
                # Kick displaced to create forward momentum; great for building energy
                (
                    TemplateComposer("funk_verse_g_twoDrop")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=c)
                ),
                # g5: Heavy ghost notes + sparse kick (minimalist funk verse — space for guitars)
                # Ghost note density drives the pocket; kick only on 1 leaves room
                (
                    TemplateComposer("funk_verse_g_minimal")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1))
                ),
            ]
        elif section == "chorus":
            # === CLASSIC FUNK CHORUS: four-on-floor + heavy ghost notes — maximum energy ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_chorus_g1")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_classic_chorus_g2")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.85, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="splash"
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_classic_chorus_g3")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.95))
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === P-FUNK CHORUS: deep pocket crash-heavy — Parliament energy ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_chorus_g1")
                    .add(FunkGhostNotes(density=0.85, emphasize_one=True))
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
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_pfunk_chorus_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=1.0, crash_type="heavy"
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_pfunk_chorus_g3")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 1.5, 2.0, 3.5], intensity=0.95
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === SHUFFLE CHORUS: drive-forward shuffle — Purdie energy builds ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_chorus_g1")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.85,
                            crash_type="light",
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_shuffle_chorus_g2")
                    .add(FunkGhostNotes(density=0.85, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0], intensity=0.9, crash_type="light"
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                    TemplateComposer("funk_shuffle_chorus_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .add(
                        CrashAccents(
                            positions=[0.0, 2.0],
                            intensity=0.85,
                            crash_type="light",
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === NEW ORLEANS CHORUS: second line syncopation — brass-heavy energy ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_chorus_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_no_chorus_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 0.75, 1.5, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === FUSION CHORUS: tight straight comping — jazz-funk power ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_chorus_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.95))
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_fusion_chorus_g2")
                    .add(FunkGhostNotes(density=0.75, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                    TemplateComposer("funk_fusion_chorus_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.7, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 1.0, 2.0, 3.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0, 2.0], intensity=0.95))
                    .build(bars=1, complexity=min(1.0, c + 0.15)),
                ]
            # === MINIMAL CHORUS: sparse but driving — controlled energy ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_chorus_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                    TemplateComposer("funk_minimal_chorus_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
            # === HEAVY CHORUS: four-on-floor rock-funk — maximum energy ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_chorus_g1")
                    .add(FunkGhostNotes(density=0.85, emphasize_one=True))
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
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_heavy_chorus_g2")
                    .add(FunkGhostNotes(density=0.9, emphasize_one=True))
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
                    .build(bars=1, complexity=min(1.0, c + 0.2)),
                    TemplateComposer("funk_heavy_chorus_g3")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
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
                            intensity=0.95,
                            crash_type="heavy",
                        )
                    )
                    .build(bars=1, complexity=min(1.0, c + 0.1)),
                ]
        elif section == "breakdown":
            # === CLASSIC FUNK BREAKDOWN: one-drop minimal — leave room for bass ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_breakdown_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_classic_breakdown_g2")
                    .add(FunkGhostNotes(density=0.8, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_classic_breakdown_g3")
                    .add(RimshotGroove())
                    .add(FunkGhostNotes(density=0.65, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === P-FUNK BREAKDOWN: sparse deep pocket — bass carries groove ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_breakdown_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_pfunk_breakdown_g2")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === SHUFFLE BREAKDOWN: sparse shuffle feel — minimal timekeeping ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_breakdown_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_shuffle_breakdown_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === NEW ORLEANS BREAKDOWN: sparse second line syncopation ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_breakdown_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_no_breakdown_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === FUSION BREAKDOWN: sparse straight comping — minimal jazz-funk ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_breakdown_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_fusion_breakdown_g2")
                    .add(FunkGhostNotes(density=0.45, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === MINIMAL BREAKDOWN: extremely sparse — bass/guitar alone ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_breakdown_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_minimal_breakdown_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HEAVY BREAKDOWN: sparse rock-funk stomp — building tension ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_breakdown_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=max(0.0, c - 0.2)),
                    TemplateComposer("funk_heavy_breakdown_g2")
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
            # === CLASSIC FUNK BRIDGE: one-drop sparse — leave room for horns ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_bridge_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_classic_bridge_g2")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_classic_bridge_g3")
                    .add(FunkGhostNotes(density=0.65, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === P-FUNK BRIDGE: sparse deep pocket — bass and drums converse ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_bridge_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_pfunk_bridge_g2")
                    .add(FunkGhostNotes(density=0.55, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === SHUFFLE BRIDGE: sparse shuffle timekeeping — behind-beat tension ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_bridge_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_shuffle_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === NEW ORLEANS BRIDGE: syncopated clave patterns — second line tension ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_bridge_g1")
                    .add(FunkGhostNotes(density=0.7, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_no_bridge_g2")
                    .add(FunkGhostNotes(density=0.65, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === FUSION BRIDGE: ride timekeeper + tight comping — jazz-funk conversational ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_bridge_g1")
                    .add(FunkGhostNotes(density=0.6, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.5],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_fusion_bridge_g2")
                    .add(FunkGhostNotes(density=0.55, emphasize_one=True))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === MINIMAL BRIDGE: sparse minimal funk — leave room for horns ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_minimal_bridge_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                ]
            # === HEAVY BRIDGE: sparse rock-funk build — building tension ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_bridge_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.1)),
                    TemplateComposer("funk_heavy_bridge_g2")
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
            # === CLASSIC FUNK OUTRO: ghost notes fade — pocket fades with bass ===
            if style == "classic":
                return [
                    TemplateComposer("funk_classic_outro_g1")
                    .add(FunkGhostNotes(density=0.5, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_classic_outro_g2")
                    .add(FunkGhostNotes(density=0.45, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_classic_outro_g3")
                    .add(RimshotGroove())
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === P-FUNK OUTRO: sparse deep pocket fade — slow dissolution ===
            if style == "pfunk":
                return [
                    TemplateComposer("funk_pfunk_outro_g1")
                    .add(FunkGhostNotes(density=0.45, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_pfunk_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === SHUFFLE OUTRO: sparse shuffle fade — gradual dissolution ===
            if style == "shuffle":
                return [
                    TemplateComposer("funk_shuffle_outro_g1")
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_shuffle_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH_TRIPLET,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === NEW ORLEANS OUTRO: sparse second line fade — gradual resolution ===
            if style == "new_orleans":
                return [
                    TemplateComposer("funk_no_outro_g1")
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_no_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === FUSION OUTRO: sparse straight comping fade — jazz-funk dissolution ===
            if style == "fusion":
                return [
                    TemplateComposer("funk_fusion_outro_g1")
                    .add(FunkGhostNotes(density=0.45, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_fusion_outro_g2")
                    .add(FunkGhostNotes(density=0.4, emphasize_one=False))
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === MINIMAL OUTRO: extremely sparse fade — bass fades alone ===
            if style == "minimal":
                return [
                    TemplateComposer("funk_minimal_outro_g1")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                    TemplateComposer("funk_minimal_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=max(0.0, c - 0.3)),
                ]
            # === HEAVY OUTRO: sparse rock-funk fade — crash finish ===
            if style == "heavy":
                return [
                    TemplateComposer("funk_heavy_outro_g1")
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
                    TemplateComposer("funk_heavy_outro_g2")
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.HALF,
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
        """Filter/swap grooves based on funk style."""
        if style not in ("pfunk", "shuffle", "new_orleans", "minimal"):
            return grooves  # classic/fusion/heavy use default

        result = []
        for g in grooves:
            name_lower = g.name.lower()
            skip = False
            if style == "pfunk" and section == "verse":
                # pfunk: remove one-drop patterns, keep syncopated ghost notes
                if "onedrop" in name_lower or "twoDrop" in name_lower:
                    skip = True
            elif style == "shuffle" and section == "chorus":
                # shuffle chorus: need Purdie shuffle feel (not fusion)
                if "ride" in name_lower or "rimshot" not in name_lower:
                    skip = True
            elif style == "new_orleans" and section == "bridge":
                # new orleans: keep syncopated kick patterns, remove sparse ones
                if "minimal" in name_lower or "oneDrop" in name_lower:
                    skip = True
            elif style == "minimal" and section in ("verse", "chorus"):
                # minimal funk: only keep sparse patterns with light ghosting
                if "four-on-floor" in name_lower or "heavy" in name_lower:
                    skip = True
            if not skip:
                result.append(g)

        return result

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
            "tight_a": InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit"),
            "tight_b": InstrumentRegistry.get("hihat_closed_1_shaft_closed_1_hit_dbl"),
            "tight_c": InstrumentRegistry.get("hihat_closed_bell"),
        }
        tight_instr = tight_map.get(tight_key)
        if not tight_instr:
            return result

        # Replace all closed hi-hat beats with the appropriate tight variant
        # Do NOT replace PEDAL_HH (foot pedal position markers) - those stay as-is
        tuned = result.copy()
        for beat in tuned.beats:
            if beat.instrument not in (
                InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit"),
                InstrumentRegistry.get("hihat_closed_bell"),
                InstrumentRegistry.get("hihat_closed_2_tip_closed_2_hit"),
            ):
                continue
            # Don't override beats already promoted to ride/crash
            if getattr(beat, "instrument_promoted", False):
                continue
            beat.instrument = tight_instr

        return tuned


# backward-compat alias for existing test imports
FunkGenrePluginRefactored = FunkGenrePlugin
