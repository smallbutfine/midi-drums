"""Reusable pattern templates for drum generation.

This module provides composable pattern building blocks that can be combined
to create complex drum patterns while eliminating code duplication.

Templates follow the Strategy pattern and can be composed using TemplateComposer.
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import DrumInstrument, InstrumentRegistry
from midi_drums.core.models.pattern import Pattern
from midi_drums.generation.builders.pattern_builder import PatternBuilder

closed_hh = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
closed_hh_edge = InstrumentRegistry.get("hihat_closed_2_tip_closed_2_hit")
ride = InstrumentRegistry.get("ride_1_tip_hit_softer")
ride_bell = InstrumentRegistry.get("ride_1_bell")
ride_shaft = InstrumentRegistry.get("ride_1_shaft_hit_stronger")
crash_light = InstrumentRegistry.get("cymbal_2_hit")
crash_heavy = InstrumentRegistry.get("cymbal_4_hit")
crash_splash = InstrumentRegistry.get("cymbal_6_hit")
mid_tom = InstrumentRegistry.get("tom_3_open_hit")
floor_tom = InstrumentRegistry.get("tom_4_open_hit")
tom_edge_1 = InstrumentRegistry.get("tom_1_rimshot_open_hit_dbl")
tom_edge_floor = InstrumentRegistry.get("tom_4_rimshot_open_hit_dbl")
snare_sticks = InstrumentRegistry.get("snare_sticks")


class PatternTemplate(ABC):
    """Base class for reusable pattern structures.

    All templates implement the generate() method which receives a PatternBuilder
    and returns the same builder with added beats (fluent API).
    """

    @abstractmethod
    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        """Generate pattern beats using the provided builder.

        Args:
            builder: PatternBuilder to add beats to
            **kwargs: Additional parameters (complexity, dynamics, etc.)

        Returns:
            The same PatternBuilder instance (for method chaining)
        """
        pass


@dataclass
class BasicGroove(PatternTemplate):
    """Standard rock/metal groove: kick + snare + hihat.

    This is the most common drum pattern foundation used across
    rock, metal, and pop genres.

    Example:
        # Standard backbeat (kick on 1&3, snare on 2&4, 8th note hihats)
        BasicGroove(
            kick_positions=[0.0, 2.0],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.EIGHTH
        )
    """

    kick_positions: list[float] = field(default_factory=lambda: [0.0, 2.0])
    snare_positions: list[float] = field(default_factory=lambda: [1.0, 3.0])
    hihat_subdivision: float = TIMING.EIGHTH
    use_open_hihat: bool = False
    open_hihat_positions: list[float] = field(default_factory=list)

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        complexity = kwargs.get("complexity", 0.5)
        dynamics = kwargs.get("dynamics", 0.6)

        # Add kicks
        for pos in self.kick_positions:
            velocity = int(VELOCITY.KICK_NORMAL + (complexity * 15))
            velocity = min(127, velocity)
            builder.kick(pos, velocity)

        # Add snares with dynamics spread
        for pos in self.snare_positions:
            velocity = int(VELOCITY.SNARE_NORMAL + (dynamics * 20))
            velocity = min(127, velocity)
            builder.snare(pos, velocity)

        # Add hi-hat pattern
        bars = kwargs.get("bars", 1)
        for bar in range(bars):
            bar_offset = bar * 4.0
            beats_per_bar = int(4.0 / self.hihat_subdivision)

            for i in range(beats_per_bar):
                pos = bar_offset + (i * self.hihat_subdivision)
                relative_pos = i * self.hihat_subdivision

                # Check if this position should be open hihat
                if self.use_open_hihat and pos in self.open_hihat_positions:
                    builder.open_hihat(pos, VELOCITY.HIHAT_OPEN)
                else:
                    # Dynamic hi-hat velocity based on position for realism
                    # Downbeats (0, 1, 2, 3) are stronger
                    if relative_pos.is_integer():
                        velocity = VELOCITY.HIHAT_ACCENT
                        # Use Edge for accents (more common in rock)
                        instrument = closed_hh_edge
                    else:
                        velocity = int(
                            VELOCITY.HIHAT_NORMAL + (random.random() * 10 - 5)
                        )
                        # Use Tip for softer hits
                        instrument = closed_hh

                    # Fallback to standard if specific ones aren't available (handled by builder/kit)
                    builder.add_hit(instrument, pos, velocity)

        return builder


@dataclass
class DoubleBassPedal(PatternTemplate):
    """Fast double bass pattern for metal genres.

    Creates rapid alternating kick drum patterns typical of metal drumming.

    Example:
        # 16th note double bass
        DoubleBassPedal(subdivision=TIMING.SIXTEENTH, intensity=0.9)
    """

    subdivision: float = TIMING.SIXTEENTH
    intensity: float = 1.0
    pattern_type: str = "continuous"  # "continuous", "gallop", "triplet"

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        if self.pattern_type == "continuous":
            return self._continuous_pattern(builder, bars)
        elif self.pattern_type == "gallop":
            return self._gallop_pattern(builder, bars)
        elif self.pattern_type == "triplet":
            return self._triplet_pattern(builder, bars)
        else:
            return self._continuous_pattern(builder, bars)

    def _continuous_pattern(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Continuous alternating double bass."""
        for bar in range(bars):
            bar_offset = bar * 4.0
            beats_per_bar = int(4.0 / self.subdivision)

            for i in range(beats_per_bar):
                pos = bar_offset + (i * self.subdivision)
                # Alternate velocity for realism
                velocity = (
                    VELOCITY.KICK_NORMAL if i % 2 == 0 else VELOCITY.KICK_LIGHT
                )
                velocity = int(velocity * self.intensity)
                velocity = max(60, min(127, velocity))
                builder.kick(pos, velocity)

        return builder

    def _gallop_pattern(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Galloping rhythm (1-2-3, 1-2-3)."""
        for bar in range(bars):
            bar_offset = bar * 4.0

            # Gallop: kick on 1, 1.5, 2, then repeat
            positions = [0.0, 0.5, 1.0, 2.0, 2.5, 3.0]
            for i, pos in enumerate(positions):
                velocity = (
                    VELOCITY.KICK_HEAVY if i % 3 == 0 else VELOCITY.KICK_NORMAL
                )
                velocity = int(velocity * self.intensity)
                builder.kick(bar_offset + pos, velocity)

        return builder

    def _triplet_pattern(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Triplet-based double bass."""
        for bar in range(bars):
            bar_offset = bar * 4.0

            # 12 triplets per bar
            for i in range(12):
                pos = bar_offset + (i * TIMING.EIGHTH_TRIPLET)
                velocity = int(VELOCITY.KICK_NORMAL * self.intensity)
                builder.kick(pos, velocity)

        return builder


@dataclass
class BlastBeat(PatternTemplate):
    """Death metal blast beat patterns.

    Various blast beat styles used in extreme metal genres.

    Styles:
        - traditional: Kick + snare on every 8th note
        - hammer: Fast snare, slower kick
        - gravity: Kick emphasis, snare on ride
    """

    style: str = "traditional"  # "traditional", "hammer", "gravity"
    intensity: float = 1.0

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        if self.style == "traditional":
            return self._traditional_blast(builder, bars)
        elif self.style == "hammer":
            return self._hammer_blast(builder, bars)
        elif self.style == "gravity":
            return self._gravity_blast(builder, bars)
        else:
            return self._traditional_blast(builder, bars)

    def _traditional_blast(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Kick + snare on every 8th note."""
        for bar in range(bars):
            bar_offset = bar * 4.0

            for i in range(8):
                pos = bar_offset + (i * TIMING.EIGHTH)
                kick_vel = int(VELOCITY.KICK_HEAVY * self.intensity)
                snare_vel = int(VELOCITY.SNARE_HEAVY * self.intensity)

                builder.kick(pos, kick_vel)
                builder.snare(pos, snare_vel)
                builder.hihat(pos, VELOCITY.HIHAT_NORMAL)

        return builder

    def _hammer_blast(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Faster snare (16ths), slower kick (8ths)."""
        for bar in range(bars):
            bar_offset = bar * 4.0

            # Kicks on 8th notes
            for i in range(8):
                if i % 2 == 0:
                    pos = bar_offset + (i * TIMING.EIGHTH)
                    builder.kick(pos, int(VELOCITY.KICK_HEAVY * self.intensity))

            # Snares on 16th notes
            for i in range(16):
                pos = bar_offset + (i * TIMING.SIXTEENTH)
                builder.snare(pos, int(VELOCITY.SNARE_HEAVY * self.intensity))
                builder.hihat(pos, VELOCITY.HIHAT_LIGHT)

        return builder

    def _gravity_blast(
        self, builder: PatternBuilder, bars: int
    ) -> PatternBuilder:
        """Kick emphasis, snare on ride."""
        for bar in range(bars):
            bar_offset = bar * 4.0

            for i in range(16):
                pos = bar_offset + (i * TIMING.SIXTEENTH)

                # Every 16th: kick
                builder.kick(pos, int(VELOCITY.KICK_HEAVY * self.intensity))

                # Every 8th: snare and ride
                if i % 2 == 0:
                    builder.snare(
                        pos, int(VELOCITY.SNARE_NORMAL * self.intensity)
                    )
                    builder.ride(pos, VELOCITY.RIDE_NORMAL)

        return builder


@dataclass
class SteadyRidePattern(PatternTemplate):
    """Straight ride cymbal pattern for rock/metal.

    Provides a steady ride pulse (quarter or eighth notes) with
    natural velocity variation.
    """

    subdivision: float = TIMING.EIGHTH
    use_bell: bool = False
    use_shaft: bool = False

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0
            num_hits = int(4.0 / self.subdivision)

            for i in range(num_hits):
                pos = bar_offset + (i * self.subdivision)

                # Accents on downbeats
                if pos.is_integer():
                    velocity = VELOCITY.RIDE_NORMAL
                    instrument = ride_bell if self.use_bell else ride
                else:
                    velocity = VELOCITY.RIDE_LIGHT + random.randint(-5, 5)
                    instrument = ride
                if self.use_shaft:
                    instrument = ride_shaft

                builder.add_hit(instrument, pos, velocity)

        return builder


@dataclass
class JazzRidePattern(PatternTemplate):
    """Jazz ride cymbal pattern with swing feel.

    Creates authentic jazz ride patterns with triplet-based swing.
    Supports AD2 extended timbres:
        - use_shaft=True → RIDE_SHAFT (94) for metallic harshness (metal sections)
        - use_bell=True → RIDE_BELL (53) for fill accents
    """

    swing_ratio: float = 0.33
    accent_pattern: str = "standard"  # "standard", "elvin", "tony"
    use_bell: bool = False
    use_shaft: bool = (
        False  # AD2 ride shaft hit for metallic harshness (metal/rock)
    )

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0

            # 12 triplets per bar (3 per beat)
            for i in range(12):
                pos = bar_offset + (i * TIMING.EIGHTH_TRIPLET)

                # Swing: emphasize 1st and 3rd of each triplet
                if i % 3 in [0, 2]:
                    velocity = self._get_accent_velocity(i)

                    if self.use_bell and i % 4 == 0:
                        builder.ride_bell(pos, velocity)
                    elif self.use_shaft:
                        # AD2 ride shaft hit — metallic, bell-like timbre for metal sections
                        builder.pattern.add_beat(pos, ride_shaft, velocity)
                    else:
                        builder.ride(pos, velocity)

        return builder

    def _get_accent_velocity(self, triplet_index: int) -> int:
        """Get velocity based on accent pattern."""
        if self.accent_pattern == "elvin":
            # Elvin Jones style: accent every 4th
            return (
                VELOCITY.RIDE_NORMAL
                if triplet_index % 4 == 0
                else VELOCITY.RIDE_LIGHT
            )
        elif self.accent_pattern == "tony":
            # Tony Williams style: more accents
            return (
                VELOCITY.RIDE_ACCENT
                if triplet_index % 3 == 0
                else VELOCITY.RIDE_NORMAL
            )
        else:
            # Standard: subtle accents on downbeats
            return (
                VELOCITY.RIDE_NORMAL
                if triplet_index % 6 == 0
                else VELOCITY.RIDE_LIGHT
            )


@dataclass
class FunkGhostNotes(PatternTemplate):
    """Funk ghost note pattern for snare.

    Creates authentic funk ghost note patterns with "the one" emphasis.

    Example:
        FunkGhostNotes(density=0.7, emphasize_one=True)
    """

    density: float = 0.7  # How many 16ths get ghost notes (0.0-1.0)
    emphasize_one: bool = True  # James Brown "the one"
    main_snare_positions: list[float] = field(
        default_factory=lambda: [1.0, 3.0]
    )

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0

            # Add main snare hits
            for pos in self.main_snare_positions:
                abs_pos = bar_offset + pos
                builder.snare(abs_pos, VELOCITY.SNARE_NORMAL)

            # Add ghost notes on 16ths
            for i in range(16):
                pos = bar_offset + (i * TIMING.SIXTEENTH)

                # Skip main snare positions
                relative_pos = i * TIMING.SIXTEENTH
                if relative_pos in self.main_snare_positions:
                    continue

                # Emphasize "the one" (downbeat)
                if self.emphasize_one and i == 0:
                    builder.kick(pos, VELOCITY.KICK_HEAVY)
                    continue

                # Probabilistically add ghost notes
                if random.random() < self.density:
                    # Use add_beat directly to support ghost_note parameter
                    builder.pattern.add_beat(
                        pos,
                        snare_sticks,
                        VELOCITY.SNARE_GHOST,
                        ghost_note=True,
                    )

        return builder


@dataclass
class CrashAccents(PatternTemplate):
    """Crash cymbal accents for section emphasis.

    Adds crash cymbals at strategic positions for emphasis.
    Supports AD2 extended crash types for timbral variety:
        - "light": CRASH_LIGHT (77) — verses, softer sections
        - "heavy": CRASH_HEAVY (89) — choruses, power sections
        - "splash": CRASH_SPLASH (93) — fills, bright endings
    """

    positions: list[float] = field(default_factory=lambda: [0.0])
    use_china: bool = False
    intensity: float = 1.0
    crash_type: str | None = (
        None  # "light", "heavy", "splash" or None for standard CRASH
    )

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0

            for pos in self.positions:
                abs_pos = bar_offset + pos
                velocity = int(VELOCITY.CRASH_NORMAL * self.intensity)
                velocity = min(127, velocity)

                if self.use_china:
                    builder.china(abs_pos, velocity)
                elif self.crash_type == "light":
                    builder.pattern.add_beat(abs_pos, crash_light, velocity)
                elif self.crash_type == "heavy":
                    builder.pattern.add_beat(abs_pos, crash_heavy, velocity)
                elif self.crash_type == "splash":
                    builder.pattern.add_beat(abs_pos, crash_splash, velocity)
                else:
                    builder.crash(abs_pos, velocity)

        return builder


@dataclass
class TomFill(PatternTemplate):
    """Tom fill patterns for transitions.

    Creates descending or ascending tom fills.
    Supports AD2 edge/rim hits via use_edge=True for sharper attack in rock/metal.
    """

    pattern: str = "descending"  # "descending", "ascending", "around"
    subdivision: float = TIMING.SIXTEENTH
    start_position: float = 3.0  # Usually bar 4
    use_edge: bool = (
        False  # Use TOM_EDGE variants for sharper attack (rock/metal)
    )

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0
            fill_start = bar_offset + self.start_position

            # Calculate number of notes in fill
            duration = 4.0 - self.start_position
            num_notes = int(duration / self.subdivision)

            if self.pattern == "descending":
                self._descending_fill(builder, fill_start, num_notes)
            elif self.pattern == "ascending":
                self._ascending_fill(builder, fill_start, num_notes)
            elif self.pattern == "around":
                self._around_fill(builder, fill_start, num_notes)

        return builder

    def _get_instruments(self) -> list[DrumInstrument]:
        if not self.use_edge:
            # Standard GM toms
            return [
                mid_tom,
                mid_tom,
                floor_tom,
                floor_tom,
            ]
        else:
            return [
                tom_edge_1,
                tom_edge_1,
                tom_edge_floor,
                tom_edge_floor,
            ]

    def _descending_fill(
        self, builder: PatternBuilder, start_pos: float, num_notes: int
    ):
        """High to low tom fill."""
        instruments = self._get_instruments()

        for i in range(min(num_notes, len(instruments))):
            pos = start_pos + (i * self.subdivision)
            builder.pattern.add_beat(pos, instruments[i], VELOCITY.TOM_HEAVY)

    def _ascending_fill(
        self, builder: PatternBuilder, start_pos: float, num_notes: int
    ):
        """Low to high tom fill."""
        instruments = self._get_instruments()

        for i in range(min(num_notes, len(instruments))):
            pos = start_pos + (i * self.subdivision)
            builder.pattern.add_beat(pos, instruments[i], VELOCITY.TOM_HEAVY)

    def _around_fill(
        self, builder: PatternBuilder, start_pos: float, num_notes: int
    ):
        """Around the kit fill."""
        instruments = [
            mid_tom,
            floor_tom,
            mid_tom,
            floor_tom,
        ]

        for i in range(min(num_notes, len(instruments))):
            pos = start_pos + (i * self.subdivision)
            builder.pattern.add_beat(pos, instruments[i], VELOCITY.TOM_NORMAL)


# --- AD2 extended instrument templates ---


@dataclass
class BrushGroove(PatternTemplate):
    """Jazz ballad groove with real brush sweeps (AD2 preset zones A-F).

    Produces authentic brush shimmer across all 6 sweep presets, ideal for
    jazz ballads and slow tempo styles. Automatically alternates variants to
    prevent mechanical repetition.

    Example:
        # Ballad verse groove
        BrushGroove(density=0.8, variant_cycle="ABCD")

    Args:
        density: Fraction of 8th notes that get brush hits (0.0-1.0).
                 Higher = denser shimmer.
        variant_cycle: Pattern sweep preset cycle, e.g. "ABCDEF"
                       or "AD" for alternating bright/dark sweeps.
        use_ride: Whether to layer ride comping underneath the brushes.
    """

    density: float = 0.65
    variant_cycle: str = "ABCDEF"
    use_ride: bool = True
    ride_velocity: int = VELOCITY.RIDE_LIGHT

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)
        variants = list(self.variant_cycle)
        variant_idx = 0

        for bar in range(bars):
            bar_offset = bar * 4.0

            # Brush sweep on 8th notes (or subset per density)
            for i in range(8):
                pos = bar_offset + (i * TIMING.EIGHTH)
                if random.random() < self.density:
                    variant = variants[variant_idx % len(variants)]
                    builder.brush_sweep(
                        pos,
                        variant,
                        velocity=VELOCITY.BRUSH_NORMAL + random.randint(-6, 6),
                    )
                    variant_idx += 1

            # Layer ride comping if requested (Elvin Jones style)
            if self.use_ride:
                for i in range(0, 8, 2):
                    pos = bar_offset + (i * TIMING.EIGHTH)
                    builder.ride(
                        pos, self.ride_velocity + random.randint(-3, 5)
                    )

        return builder


@dataclass
class RimshotGroove(PatternTemplate):
    """Funk/R&B groove with rimshots instead of snare backbeats.

    Uses AD2's SNARE_RIMSHOT (side stick) zone for that crisp, muted
    backbeat characteristic of classic funk and R&B. Can combine with
    tight HH comping for an authentic James Brown vibe.

    Example:
        # Funk "the one" groove
        RimshotGroove(use_tight_hh=True)

    Args:
        use_tight_hh: Whether to comp tight HH on offbeats instead of regular
                      hihat.
        rim_variant: Which rim preset to use (A for side stick, B for brush).
    """

    use_tight_hh: bool = True
    rim_variant: str = "MID"

    def generate(self, builder: PatternBuilder, **kwargs) -> PatternBuilder:
        bars = kwargs.get("bars", 1)

        for bar in range(bars):
            bar_offset = bar * 4.0

            # Rimshot backbeat on 2 and 4
            builder.snare_rimshot(bar_offset + 1.0, VELOCITY.SNARE_RIMSHOT)
            builder.snare_rimshot(bar_offset + 3.0, VELOCITY.SNARE_NORMAL + 5)

            # Tight HH comping on offbeats (funk signature)
            if self.use_tight_hh:
                for i in range(16):
                    pos = bar_offset + (i * TIMING.SIXTEENTH)
                    is_offbeat = i % 2 == 1
                    if is_offbeat:
                        builder.tight_hh(pos, open=False)
                    elif random.random() < 0.5:
                        # Sparse tight HH on some beats for texture
                        builder.tight_hh(pos, open=False)

        return builder


class TemplateComposer:
    """Compose multiple templates into complete patterns.

    This class provides a fluent API for combining pattern templates
    to create complex drum patterns.

    Example:
        pattern = TemplateComposer("metal_verse") \\
            .add(BasicGroove(kick_positions=[0.0, 2.0, 2.5])) \\
            .add(DoubleBassPedal(intensity=0.8)) \\
            .add(CrashAccents(positions=[0.0])) \\
            .build(bars=4, complexity=0.7)
    """

    def __init__(self, name: str, time_signature=None):
        """Initialize composer with pattern name.

        Args:
            name: Name for the generated pattern
            time_signature: Optional TimeSignature (defaults to 4/4)
        """
        self.name = name
        self.time_signature = time_signature
        self.templates: list[PatternTemplate] = []

    def add(self, template: PatternTemplate) -> "TemplateComposer":
        """Add a template to the composition (fluent API).

        Args:
            template: PatternTemplate instance to add

        Returns:
            Self for method chaining
        """
        self.templates.append(template)
        return self

    def build(self, **kwargs) -> Pattern:
        """Build pattern by applying all templates.

        Args:
            **kwargs: Parameters passed to all templates
                     (bars, complexity, dynamics, etc.)

        Returns:
            Complete Pattern with all template beats combined
        """
        builder = PatternBuilder(self.name, self.time_signature)

        # Apply each template in order
        for template in self.templates:
            builder = template.generate(builder, **kwargs)

        return builder.build()


# Convenience function for common patterns
def create_basic_rock_pattern(
    name: str = "basic_rock", bars: int = 1, complexity: float = 0.5
) -> Pattern:
    """Create a basic rock pattern (kick 1&3, snare 2&4, 8th hihats).

    Args:
        name: Pattern name
        bars: Number of bars
        complexity: Pattern complexity (0.0-1.0)

    Returns:
        Complete Pattern
    """
    return (
        TemplateComposer(name)
        .add(
            BasicGroove(
                kick_positions=[0.0, 2.0],
                snare_positions=[1.0, 3.0],
                hihat_subdivision=TIMING.EIGHTH,
            )
        )
        .build(bars=bars, complexity=complexity)
    )


def create_metal_pattern(
    name: str = "metal_heavy",
    bars: int = 1,
    complexity: float = 0.8,
    use_double_bass: bool = True,
) -> Pattern:
    """Create a heavy metal pattern with optional double bass.

    Args:
        name: Pattern name
        bars: Number of bars
        complexity: Pattern complexity (0.0-1.0)
        use_double_bass: Whether to use double bass pedal

    Returns:
        Complete Pattern
    """
    composer = TemplateComposer(name).add(
        BasicGroove(
            kick_positions=[0.0, 2.0, 2.5],
            snare_positions=[1.0, 3.0],
            hihat_subdivision=TIMING.EIGHTH,
        )
    )

    if use_double_bass:
        composer.add(
            DoubleBassPedal(subdivision=TIMING.SIXTEENTH, intensity=0.9)
        )

    composer.add(CrashAccents(positions=[0.0]))

    return composer.build(bars=bars, complexity=complexity)


def create_jazz_ballad_pattern(
    name: str = "jazz_ballad",
    bars: int = 1,
    density: float = 0.65,
) -> Pattern:
    """Create a jazz ballad pattern with real brush sweeps.

    Uses AD2 brush sweep zones (A-F) for authentic shimmer rather than
    soft snare simulation.

    Args:
        name: Pattern name
        bars: Number of bars
        density: Brush hit density (0.0-1.0)

    Returns:
        Complete Pattern with brush sweeps + ride comping
    """
    return (
        TemplateComposer(name)
        .add(BrushGroove(density=density))
        .build(bars=bars)
    )


def create_funk_rimshot_pattern(
    name: str = "funk_rimshot",
    bars: int = 1,
) -> Pattern:
    """Create a funk groove with rimshots (side stick) on backbeat.

    Uses AD2's SNARE_RIMSHOT zone for crisp side stick instead of regular snare.
    Pairs well with tight HH comping.

    Args:
        name: Pattern name
        bars: Number of bars

    Returns:
        Complete Pattern with rimshot backbeat + tight HH comping
    """
    return (
        TemplateComposer(name)
        .add(RimshotGroove(use_tight_hh=True))
        .build(bars=bars)
    )
