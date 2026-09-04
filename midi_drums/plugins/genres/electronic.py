"""Electronic genre plugin - house, techno, drum & bass, dubstep.

Uses pattern templates from midi_drums.patterns (same infrastructure as
the rock/jazz/funk plugins) via declarative TemplateComposer composition -
no manual PatternBuilder construction. BasicGroove's kick_positions already
express a four-on-the-floor kick (one every quarter note), so no new
pattern template was needed for this genre; see issue #30.
"""

from midi_drums.config import TIMING
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.patterns import (
    BasicGroove,
    CrashAccents,
    TemplateComposer,
    TomFill,
)
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin

# Four-on-the-floor: kick on every quarter note. Shared by house and
# techno verses/choruses/intros.
_FOUR_ON_THE_FLOOR = [0.0, 1.0, 2.0, 3.0]

# Drum & bass breakbeat kick: syncopated, off the plain quarter-note grid.
_BREAKBEAT_KICK = [0.0, 0.75, 2.5]

# Drum & bass syncopated snare: one hit off the standard 2-and-4 backbeat.
_BREAKBEAT_SNARE = [1.0, 2.75]

# Dubstep half-time kick/snare: sparse, with the single snare hit landing
# on beat 3 rather than the usual 2-and-4 backbeat.
_HALF_TIME_KICK = [0.0, 2.5]
_HALF_TIME_SNARE = [2.0]


class ElectronicGenrePlugin(GenrePlugin):
    """Electronic genre plugin using template composition.

    Supports house, techno, drum_and_bass, and dubstep styles, following
    the same declarative TemplateComposer approach as the refactored
    rock/jazz/funk genre plugins.
    """

    @property
    def genre_name(self) -> str:
        return "electronic"

    @property
    def supported_styles(self) -> list[str]:
        return ["house", "techno", "drum_and_bass", "dubstep"]

    DEFAULT_TEMPO_MAP: dict[str, int] = {
        "house": 124,
        "techno": 136,
        "drum_and_bass": 174,
        "dubstep": 140,
    }

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Electronic genre intensity characteristics."""
        return {
            "aggression": 0.4,
            "speed": 0.7,
            "density": 0.6,
            "power": 0.55,
            "complexity": 0.45,
            "darkness": 0.4,
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate electronic pattern based on section and style."""
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

        return pattern

    def get_common_fills(self) -> list[Fill]:
        """Get common electronic fill patterns using templates."""
        fills = []

        # Hi-hat roll building into a crash - typical build-up/drop fill.
        roll_pattern = (
            TemplateComposer("electronic_hihat_roll_fill")
            .add(
                BasicGroove(
                    kick_positions=_FOUR_ON_THE_FLOOR,
                    snare_positions=[],
                    hihat_subdivision=TIMING.SIXTEENTH,
                )
            )
            .add(CrashAccents(positions=[0.0], intensity=0.9))
            .build(bars=1, complexity=0.7)
        )
        fills.append(
            Fill(roll_pattern, trigger_probability=0.7, section_position="end")
        )

        # Tom fill transition into the next section.
        tom_fill_pattern = (
            TemplateComposer("electronic_tom_fill")
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
                trigger_probability=0.5,
                section_position="middle",
            )
        )

        return fills

    def get_section_grooves(
        self, section: str, complexity: float, style: str = "default"
    ) -> list[Pattern]:
        """Return 3 structurally distinct grooves for this section.

        Electronic music has less natural variation than acoustic genres,
        but each style receives genuinely different kick/snare/hat patterns
        researched from real drumming practice:

        - **house** (124 BPM): Four-on-floor timekeeping, crash accents on
          downbeats, tight 8th-note hats, open-hat off-beat fills.
        - **techno** (136 BPM): Driving minimal patterns, tighter 16th-note
          hats, no washy crashes — mechanical precision.
        - **drum_and_bass** (174 BPM): Breakbeat-based patterns only
          (_BREAKBEAT_KICK/_BREAKBEAT_SNARE), frantic 16th-note hat energy,
          no four-on-floor timekeeping.
        - **dubstep** (140 BPM): Half-time feel with sparse kicks,
          single heavy snare on beat 3, deep space between hits,
          tom builds for tension.

        No shared groove pool — each style has its own patterns per section.
        """
        c = complexity
        low = max(0.0, c - 0.3)
        mid = c
        high = min(1.0, c + 0.2)

        if section == "intro":
            grooves = self._intro_grooves(style, low)
        elif section == "verse":
            grooves = self._verse_grooves(style, mid)
        elif section == "chorus":
            grooves = self._chorus_grooves(style, high)
        elif section == "breakdown":
            grooves = self._breakdown_grooves(style, low)
        elif section in ("bridge", "pre_chorus"):
            grooves = self._bridge_grooves(style, max(0.0, c - 0.1))
        elif section == "outro":
            grooves = self._outro_grooves(style, low)
        else:
            # Fallback: style-appropriate pattern
            grooves = [self._fallback(section, style, c)]

        return grooves

    # -------------------------------------------------------------------
    # Per-style groove constructors (genuine patterns, not filters)
    # -------------------------------------------------------------------

    def _intro_grooves(self, style: str, complexity: float) -> list[Pattern]:
        """Intro grooves — each style gets its own timekeeper."""
        match style:
            case "house":
                return [
                    # G1: Classic house intro — four-on-floor + open hats
                    (
                        TemplateComposer("electronic_intro_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse two-kick with driving hats
                    (
                        TemplateComposer("electronic_intro_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Half-time house feel for tension
                    (
                        TemplateComposer("electronic_intro_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "techno":
                return [
                    # G1: Minimal driving — sparse kick + tight 16th hats
                    (
                        TemplateComposer("electronic_intro_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Two-kick mechanical pulse
                    (
                        TemplateComposer("electronic_intro_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 1.5, 2.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Sparse with subtle rimshot on 3
                    (
                        TemplateComposer("electronic_intro_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.5],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Amen-break-inspired kick
                    (
                        TemplateComposer("electronic_intro_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_BREAKBEAT_KICK,
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse two-kick + syncopated snare
                    (
                        TemplateComposer("electronic_intro_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.0],
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Build-up feel — escalating kick density
                    (
                        TemplateComposer("electronic_intro_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.5, 2.0],
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Sparse single kick with deep space
                    (
                        TemplateComposer("electronic_intro_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Half-time with ghost snare
                    (
                        TemplateComposer("electronic_intro_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[1.5, 2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Minimal tom + sparse hat
                    (
                        TemplateComposer("electronic_intro_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]

    def _verse_grooves(self, style: str, complexity: float) -> list[Pattern]:
        """Verse grooves — main groove per style."""
        match style:
            case "house":
                return [
                    # G1: Four-on-floor + standard backbeat
                    (
                        TemplateComposer("electronic_verse_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Open-hat variation on off-beats
                    (
                        TemplateComposer("electronic_verse_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.5, 1.5, 2.5, 3.5]))
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Sparse snare — focus on kick energy
                    (
                        TemplateComposer("electronic_verse_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "techno":
                return [
                    # G1: Driving four-on-floor + single clap on 2
                    (
                        TemplateComposer("electronic_verse_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Syncopated kick pattern (minimal techno style)
                    (
                        TemplateComposer("electronic_verse_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 1.0, 2.5],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Two-kick + offbeat rimshot
                    (
                        TemplateComposer("electronic_verse_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.0],
                                snare_positions=[1.5, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Amen break pattern — the signature D&B groove
                    (
                        TemplateComposer("electronic_verse_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_BREAKBEAT_KICK,
                                snare_positions=_BREAKBEAT_SNARE,
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Syncopated kick + displaced snare
                    (
                        TemplateComposer("electronic_verse_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.5, 2.0, 2.75],
                                snare_positions=[1.0, 3.5],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Classic D&B — syncopated bassline + tom fills
                    (
                        TemplateComposer("electronic_verse_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_BREAKBEAT_KICK,
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .add(TomFill(pattern="descending", start_position=3.5))
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Half-time with sparse kick + heavy snare on beat 3
                    (
                        TemplateComposer("electronic_verse_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=_HALF_TIME_SNARE,
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse kick + ghost snare on 3
                    (
                        TemplateComposer("electronic_verse_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[1.5, 2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Minimal — single kick + rimshot ghost
                    (
                        TemplateComposer("electronic_verse_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.5],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]

    def _chorus_grooves(self, style: str, complexity: float) -> list[Pattern]:
        """Chorus grooves — maximum energy per style."""
        match style:
            case "house":
                return [
                    # G1: Classic house chorus — four-on-floor + crash accents
                    (
                        TemplateComposer("electronic_chorus_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.0], intensity=0.9))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G2: Open hat fills between crashes
                    (
                        TemplateComposer("electronic_chorus_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.0, 2.0], intensity=0.95))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G3: Four-on-floor with tom accent build
                    (
                        TemplateComposer("electronic_chorus_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(TomFill(pattern="around", start_position=3.5))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                ]
            case "techno":
                return [
                    # G1: Driving four-on-floor — minimal but powerful
                    (
                        TemplateComposer("electronic_chorus_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G2: Tight hats only — no washy crashes for techno
                    (
                        TemplateComposer("electronic_chorus_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.0], intensity=0.7))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G3: Syncopated kick for driving energy
                    (
                        TemplateComposer("electronic_chorus_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.5, 1.0, 2.0, 2.5, 3.0],
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Full D&B chorus — breakbeat + tom fills + crash
                    (
                        TemplateComposer("electronic_chorus_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_BREAKBEAT_KICK,
                                snare_positions=_BREAKBEAT_SNARE,
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .add(TomFill(pattern="around", start_position=3.5))
                        .add(CrashAccents(positions=[0.0], intensity=0.9))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G2: Accelerated breakbeat — more kick hits
                    (
                        TemplateComposer("electronic_chorus_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.5, 1.0, 2.0, 2.5],
                                snare_positions=_BREAKBEAT_SNARE,
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G3: Classic D&B drop — syncopated bassline kick
                    (
                        TemplateComposer("electronic_chorus_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.25, 1.0, 2.0, 2.75],
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.0], intensity=0.85))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Half-time with heavy crash — the drop
                    (
                        TemplateComposer("electronic_chorus_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=_HALF_TIME_SNARE,
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(CrashAccents(positions=[0.0], intensity=1.0))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G2: Sparse kick + tom cascade build
                    (
                        TemplateComposer("electronic_chorus_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[1.5, 2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(TomFill(pattern="descending", start_position=3.0))
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                    # G3: Minimal half-time — maximum space
                    (
                        TemplateComposer("electronic_chorus_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=min(1.0, complexity + 0.2))
                    ),
                ]

    def _breakdown_grooves(
        self, style: str, complexity: float
    ) -> list[Pattern]:
        """Breakdown grooves — stripped back, spacious."""
        match style:
            case "house":
                return [
                    # G1: Sparse two-kick with quarter hats (tension build)
                    (
                        TemplateComposer("electronic_breakdown_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Single kick + open hat swells
                    (
                        TemplateComposer("electronic_breakdown_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Half-time with subtle snare tap
                    (
                        TemplateComposer("electronic_breakdown_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "techno":
                return [
                    # G1: Minimal — single kick, sparse hats
                    (
                        TemplateComposer("electronic_breakdown_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Very sparse — kick every other bar
                    (
                        TemplateComposer("electronic_breakdown_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Rimshot ghost on 3 + sparse kick
                    (
                        TemplateComposer("electronic_breakdown_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.5],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Sparse syncopated kick + single snare
                    (
                        TemplateComposer("electronic_breakdown_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.5],
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Minimal half-time D&B feel
                    (
                        TemplateComposer("electronic_breakdown_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[1.5, 2.5],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Build-up — escalating kick pattern
                    (
                        TemplateComposer("electronic_breakdown_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 1.0, 2.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Sparse single kick — maximum space
                    (
                        TemplateComposer("electronic_breakdown_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Half-time with deep space between hits
                    (
                        TemplateComposer("electronic_breakdown_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Minimal — single kick + rimshot ghost
                    (
                        TemplateComposer("electronic_breakdown_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.5],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]

    def _bridge_grooves(self, style: str, complexity: float) -> list[Pattern]:
        """Bridge grooves — transition/contrast per style."""
        match style:
            case "house":
                return [
                    # G1: Four-on-floor + ascending tom (build tension)
                    (
                        TemplateComposer("electronic_bridge_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .add(TomFill(pattern="ascending", start_position=3.0))
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse kick + open hats
                    (
                        TemplateComposer("electronic_bridge_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Half-time bridge for contrast
                    (
                        TemplateComposer("electronic_bridge_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "techno":
                return [
                    # G1: Minimal four-on-floor + build (tension to drop)
                    (
                        TemplateComposer("electronic_bridge_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .add(TomFill(pattern="ascending", start_position=3.0))
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse syncopated kick pattern
                    (
                        TemplateComposer("electronic_bridge_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 1.5, 3.0],
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Rimshot + sparse kick — minimal build
                    (
                        TemplateComposer("electronic_bridge_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.5],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Breakbeat + tom fill (build to drop)
                    (
                        TemplateComposer("electronic_bridge_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_BREAKBEAT_KICK,
                                snare_positions=_BREAKBEAT_SNARE,
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .add(TomFill(pattern="around", start_position=3.0))
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                    # G2: Escalating kick density
                    (
                        TemplateComposer("electronic_bridge_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 0.5, 2.0, 2.5],
                                snare_positions=[1.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                    # G3: Syncopated kick + ghost snare
                    (
                        TemplateComposer("electronic_bridge_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 1.5, 2.75],
                                snare_positions=[1.0, 3.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Half-time + ascending tom (build to heavy drop)
                    (
                        TemplateComposer("electronic_bridge_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=_HALF_TIME_SNARE,
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(TomFill(pattern="ascending", start_position=3.0))
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                    # G2: Sparse kick + deep space
                    (
                        TemplateComposer("electronic_bridge_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                    # G3: Minimal half-time + tom fill
                    (
                        TemplateComposer("electronic_bridge_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .add(TomFill(pattern="descending", start_position=3.5))
                        .build(bars=1, complexity=max(0.0, complexity - 0.1))
                    ),
                ]

    def _outro_grooves(self, style: str, complexity: float) -> list[Pattern]:
        """Outro grooves — wind down per style."""
        match style:
            case "house":
                return [
                    # G1: Four-on-floor with quarter hats (fade)
                    (
                        TemplateComposer("electronic_outro_house_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Two-kick fade — removing backbeat
                    (
                        TemplateComposer("electronic_outro_house_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0, 2.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Single kick + sparse hats
                    (
                        TemplateComposer("electronic_outro_house_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "techno":
                return [
                    # G1: Sparse four-on-floor fade
                    (
                        TemplateComposer("electronic_outro_techno_g1")
                        .add(
                            BasicGroove(
                                kick_positions=_FOUR_ON_THE_FLOOR,
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Single kick with quarter hats
                    (
                        TemplateComposer("electronic_outro_techno_g2")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.QUARTER,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Minimal — single hit per bar
                    (
                        TemplateComposer("electronic_outro_techno_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case "drum_and_bass":
                return [
                    # G1: Breakout from breakbeat — sparse + quiet
                    (
                        TemplateComposer("electronic_outro_dnb_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Half-time + sparse hat
                    (
                        TemplateComposer("electronic_outro_dnb_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[2.0],
                                hihat_subdivision=TIMING.SIXTEENTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Single hit — fade to nothing
                    (
                        TemplateComposer("electronic_outro_dnb_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]
            case _:  # dubstep
                return [
                    # G1: Minimal single kick fade
                    (
                        TemplateComposer("electronic_outro_dub_g1")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G2: Sparse half-time with space
                    (
                        TemplateComposer("electronic_outro_dub_g2")
                        .add(
                            BasicGroove(
                                kick_positions=_HALF_TIME_KICK,
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                    # G3: Single hit — fade to silence
                    (
                        TemplateComposer("electronic_outro_dub_g3")
                        .add(
                            BasicGroove(
                                kick_positions=[0.0],
                                snare_positions=[],
                                hihat_subdivision=TIMING.EIGHTH,
                            )
                        )
                        .build(bars=1, complexity=complexity)
                    ),
                ]

    def _fallback(self, section: str, style: str, complexity: float) -> Pattern:
        """Fallback groove when section not recognized — still style-specific."""
        match style:
            case "house":
                return (
                    TemplateComposer(f"electronic_{section}_fallback")
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "techno":
                return (
                    TemplateComposer(f"electronic_{section}_fallback")
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "drum_and_bass":
                return (
                    TemplateComposer(f"electronic_{section}_fallback")
                    .add(
                        BasicGroove(
                            kick_positions=_BREAKBEAT_KICK,
                            snare_positions=_BREAKBEAT_SNARE,
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case _:  # dubstep
                return (
                    TemplateComposer(f"electronic_{section}_fallback")
                    .add(
                        BasicGroove(
                            kick_positions=_HALF_TIME_KICK,
                            snare_positions=_HALF_TIME_SNARE,
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )

    # -------------------------------------------------------------------------
    # Section generators (used by DrumGenerator.generate_pattern for single
    # pattern fallback when no grooves are registered for a section)
    # -------------------------------------------------------------------------

    def _generate_intro(self, style: str, complexity: float) -> Pattern:
        """Intro pattern - establishes the groove, builds energy."""
        name = f"electronic_{style}_intro"
        intro_complexity = max(0.0, complexity - 0.3)

        match style:
            case "house" | "techno":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=intro_complexity)
                )
            case "drum_and_bass":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=intro_complexity)
                )
            case _:  # dubstep
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .build(bars=1, complexity=intro_complexity)
                )

    def _generate_verse(self, style: str, complexity: float) -> Pattern:
        """Verse pattern based on style."""
        name = f"electronic_{style}_verse"

        match style:
            case "house":
                # Four-on-the-floor kick, backbeat snare/clap, steady
                # off-beat-filling 8th note hi-hat groove.
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "techno":
                # Driving, minimal, mechanical precision: four-on-the-floor
                # kick, a single sparse clap accent, dense 16th-note hats.
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case "drum_and_bass":
                # Fast breakbeat kick, syncopated snare placement off the
                # standard backbeat grid, fast 16th-note hats.
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_BREAKBEAT_KICK,
                            snare_positions=_BREAKBEAT_SNARE,
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )
            case _:  # dubstep
                # Half-time feel: sparse kick, single heavy snare on beat 3.
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_HALF_TIME_KICK,
                            snare_positions=_HALF_TIME_SNARE,
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=complexity)
                )

    def _generate_chorus(self, style: str, complexity: float) -> Pattern:
        """Chorus pattern - more intense/energetic than verse."""
        name = f"electronic_{style}_chorus"
        chorus_complexity = min(1.0, complexity + 0.2)

        match style:
            case "house":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=chorus_complexity)
                )
            case "techno":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=0.85))
                    .build(bars=1, complexity=chorus_complexity)
                )
            case "drum_and_bass":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_BREAKBEAT_KICK,
                            snare_positions=_BREAKBEAT_SNARE,
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.5))
                    .add(CrashAccents(positions=[0.0], intensity=0.9))
                    .build(bars=1, complexity=chorus_complexity)
                )
            case _:  # dubstep
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_HALF_TIME_KICK,
                            snare_positions=_HALF_TIME_SNARE,
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(CrashAccents(positions=[0.0], intensity=1.0))
                    .build(bars=1, complexity=chorus_complexity)
                )

    def _generate_breakdown(self, style: str, complexity: float) -> Pattern:
        """Breakdown pattern - stripped back, spacious."""
        name = f"electronic_{style}_breakdown"
        breakdown_complexity = max(0.0, complexity - 0.2)

        match style:
            case "house" | "techno":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0, 2.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .build(bars=1, complexity=breakdown_complexity)
                )
            case _:  # drum_and_bass, dubstep
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[2.0],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=breakdown_complexity)
                )

    def _generate_bridge(self, style: str, complexity: float) -> Pattern:
        """Bridge pattern - transition or contrasting section."""
        name = f"electronic_{style}_bridge"
        bridge_complexity = max(0.0, complexity - 0.1)

        match style:
            case "drum_and_bass":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_BREAKBEAT_KICK,
                            snare_positions=_BREAKBEAT_SNARE,
                            hihat_subdivision=TIMING.SIXTEENTH,
                        )
                    )
                    .add(TomFill(pattern="around", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )
            case "dubstep":
                # Half-time feel: sparse kick, single heavy snare on beat 3,
                # matching every other dubstep section (intro/verse/chorus/
                # breakdown/outro) instead of house/techno's four-on-the-floor.
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_HALF_TIME_KICK,
                            snare_positions=_HALF_TIME_SNARE,
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )
            case _:  # house, techno
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[1.0, 3.0],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .add(TomFill(pattern="ascending", start_position=3.0))
                    .build(bars=1, complexity=bridge_complexity)
                )

    def _generate_outro(self, style: str, complexity: float) -> Pattern:
        """Outro pattern - winds down."""
        name = f"electronic_{style}_outro"
        outro_complexity = max(0.0, complexity - 0.3)

        match style:
            case "house" | "techno":
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=_FOUR_ON_THE_FLOOR,
                            snare_positions=[],
                            hihat_subdivision=TIMING.QUARTER,
                        )
                    )
                    .build(bars=1, complexity=outro_complexity)
                )
            case _:  # drum_and_bass, dubstep
                return (
                    TemplateComposer(name)
                    .add(
                        BasicGroove(
                            kick_positions=[0.0],
                            snare_positions=[],
                            hihat_subdivision=TIMING.EIGHTH,
                        )
                    )
                    .build(bars=1, complexity=outro_complexity)
                )
