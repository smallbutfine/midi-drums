"""Main drum generation engine and composition system."""

import logging
from pathlib import Path

from midi_drums.config.bpm_ranges import get_default_bpm
from midi_drums.core.models.kit import DrumKit
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Section, Song
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.export.midi.engine import MIDIEngine
from midi_drums.plugins.registry.plugin_registry import PluginManager

# Genre-specific default structures (replaces hardcoded pop formula)
# Section names use the canonical set that genre plugins recognize:
#   intro, verse, chorus, bridge, breakdown, outro
GENRE_ARCHETYPES: dict[str, list[tuple[str, int]]] = {
    "metal": [
        ("intro", 8),
        ("verse", 8),
        ("chorus", 8),
        ("verse", 8),
        ("breakdown", 8),
        ("chorus", 8),
        ("bridge", 4),
        ("solo", 8),
        ("outro", 8),
    ],
    "rock": [
        ("intro", 4),
        ("verse", 8),
        ("chorus", 8),
        ("verse", 8),
        ("chorus", 8),
        ("bridge", 4),
        ("solo", 8),
        ("outro", 4),
    ],
    "jazz": [
        ("intro", 8),
        ("verse", 16),
        ("chorus", 16),
        ("bridge", 8),
        ("chorus", 16),
        ("outro", 8),
    ],
    "funk": [
        ("intro", 4),
        ("verse", 8),
        ("chorus", 8),
        ("verse", 8),
        ("breakdown", 8),
        ("bridge", 4),
        ("outro", 8),
    ],
    "electronic": [
        ("intro", 8),
        ("verse", 16),
        ("chorus", 16),
        ("breakdown", 8),
        ("chorus", 16),
        ("outro", 8),
    ],
}


def _get_genre_default_structure(genre: str) -> list[tuple[str, int]]:
    """Return a genre-appropriate default structure."""
    return GENRE_ARCHETYPES.get(
        genre.lower(),
        [
            ("intro", 4),
            ("verse", 8),
            ("chorus", 8),
            ("verse", 8),
            ("chorus", 8),
            ("bridge", 4),
            ("outro", 8),
        ],
    )


def _apply_groove_restraints(song: Song) -> None:
    """Apply genre-aware restraint to improve musicality.

    Per-genre adjustments that target the *right* problem:
    - Jazz  : attenuate snare, lower crash cymbals (ride should dominate)
    - Funk   : tighten main snare, preserve ghost-note lows
    - Metal  : ensure snares stay punchy (no dampening)
    - Rock   : keep standard energy, no heavy attenuation
    """
    genre = song.global_parameters.genre if song.global_parameters else "rock"

    from midi_drums.config import VELOCITY

    for section in song.sections:
        for beat in section.pattern.beats:
            name = beat.instrument.name

            # --- Jazz: ride-centric, sparse kick, gentle snares ---
            if genre in ("jazz",):
                if name == "snare_rimshot_open_hit":
                    # Bring heavy snares down to a controlled level;
                    # leave ghost notes untouched.
                    if not getattr(beat, "ghost_note", False):
                        beat.velocity = min(
                            beat.velocity, int(VELOCITY.SNARE_LIGHT)
                        )
                elif (
                    name.startswith("cymbal_")
                    or "crash" in name
                    or "ride" in name
                ):
                    beat.velocity = min(
                        beat.velocity, int(VELOCITY.CRASH_LIGHT)
                    )

            # --- Funk: tight backbeat, ghost notes stay quiet ---
            elif genre in ("funk",):
                if name == "snare_rimshot_open_hit":
                    if not getattr(beat, "ghost_note", False):
                        beat.velocity = max(
                            int(VELOCITY.SNARE_NORMAL),
                            min(beat.velocity, int(VELOCITY.SNARE_ACCENT)),
                        )

            # --- Metal: ensure snares are loud and clear ---
            elif genre == "metal":
                if name == "snare_rimshot_open_hit" and beat.velocity < 100:
                    beat.velocity = min(beat.velocity + 25, 127)


logger = logging.getLogger(__name__)


class DrumGenerator:
    """Main drum generation engine."""

    def __init__(
        self, config_path: Path | None = None, composer_engine: str = "v2"
    ):
        """Initialize drum generator with optional configuration.

        Args:
            config_path: Optional path to configuration file.
            composer_engine: Composition engine to use.
                - "v2" (default): Bar-by-bar evolution with intensity curves
                  and drummer per-bar variation. This is the recommended mode.
                - "v1": Static pattern reuse (original behavior, preserved for
                  backward compatibility).
        """
        self.plugin_manager = PluginManager()
        self.drum_kit = DrumKit.from_keymap_name("gm")
        self.midi_engine = MIDIEngine(self.drum_kit)

        # Load plugins
        self._load_plugins()

        # Store composer engine choice
        self.composer_engine = composer_engine

    def create_song_v2(
        self,
        genre: str,
        style: str = "default",
        tempo: int | None = None,
        structure: list[tuple[str, int]] | None = None,
        drum_kit: DrumKit | None = None,
        **kwargs,
    ) -> Song:
        """Create a complete song with bar-by-bar pattern evolution (Engine v2).

        Each bar within each section gets a unique pattern shaped by:
        - Intensity curves (section arcs like ASCENDING, PLATEAU, DIP_RISE)
        - Drummer personality (per-bar variations specific to each drummer)
        - Section context (verse after bridge vs. first verse)

        Args:
            genre: Genre name (e.g., 'metal', 'rock')
            style: Style within genre (e.g., 'death', 'power' for metal)
            tempo: Tempo in BPM. Defaults to a genre/style-aware value when
                ``None`` is passed.
            structure: List of (section_name, bars) tuples. If None, uses
                default structure.
            drum_kit: Optional DrumKit for MIDI mapping. If None, uses
                current kit.
            **kwargs: Additional parameters for GenerationParameters

        Returns:
            Complete Song object with unique patterns per bar

        Example:
            # Generate with bar-by-bar evolution (Engine v2)
            generator = DrumGenerator(composer_engine="v2")
            song = generator.create_song_v2(
                "metal", "death", tempo=180, complexity=0.8, drummer="hoglan"
            )

        See also: :meth:`create_song` (Engine v1 - original static behavior)
        """
        # Resolve genre/style-aware default when tempo not explicitly set
        if tempo is None:
            resolved = get_default_bpm(genre, style)
            tempo = resolved if resolved is not None else 120

        # Update MIDI engine if new drum kit provided
        if drum_kit:
            self.midi_engine = MIDIEngine(drum_kit)
            self.drum_kit = drum_kit

        from midi_drums.generation.composer_v2 import ComposerV2

        # Use default structure if none provided
        if structure is None:
            structure = [
                ("intro", 4),
                ("verse", 8),
                ("chorus", 8),
                ("verse", 8),
                ("chorus", 8),
                ("bridge", 4),
                ("chorus", 8),
                ("outro", 4),
            ]

        composer = ComposerV2(self.plugin_manager)
        song = composer.create_song(
            genre=genre,
            style=style,
            tempo=tempo,
            structure=structure,
            **kwargs,
        )
        return song

    def _load_plugins(self) -> None:
        """Load all available plugins."""
        try:
            self.plugin_manager.discover_plugins()
            logger.info(
                f"Loaded genres: {self.plugin_manager.get_available_genres()}"
            )
            logger.info(
                f"Loaded drummers: "
                f"{self.plugin_manager.get_available_drummers()}"
            )
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")

    def create_song(
        self,
        genre: str,
        style: str = "default",
        tempo: int | None = None,
        structure: list[tuple[str, int]] | None = None,
        drum_kit: DrumKit | None = None,
        composer_engine: str | None = None,
        **kwargs,
    ) -> Song:
        """Create a complete song structure.

        Args:
            genre: Genre name (e.g., 'metal', 'rock', 'jazz')
            style: Style within genre (e.g., 'death', 'power' for metal)
            tempo: Tempo in BPM. Defaults to a genre/style-aware value when
                ``None`` is passed.
            structure: List of (section_name, bars) tuples. If None, uses
                default structure.
            drum_kit: Optional DrumKit for MIDI mapping. If None, uses
                current kit.
            composer_engine: Override engine for this call. "v2" (default) uses
                bar-by-bar evolution; "v1" uses static pattern reuse. If None,
                uses the generator's configured engine.
            **kwargs: Additional parameters for GenerationParameters

        Returns:
            Complete Song object with generated patterns
        """
        # Resolve genre/style-aware default when tempo not explicitly set
        if tempo is None:
            resolved = get_default_bpm(genre, style)
            tempo = resolved if resolved is not None else 120

        # Update MIDI engine if new drum kit provided
        if drum_kit:
            self.midi_engine = MIDIEngine(drum_kit)
            self.drum_kit = drum_kit

        # Resolve composer engine for this call
        engine = composer_engine or self.composer_engine

        # Use Engine V2 (bar-by-bar evolution) by default
        if engine == "v2":
            from midi_drums.generation.composer_v2 import ComposerV2

            if structure is None:
                structure = _get_genre_default_structure(genre)

            composer = ComposerV2(self.plugin_manager)
            return composer.create_song(
                genre=genre,
                style=style,
                tempo=tempo,
                structure=structure,
                **kwargs,
            )

        # Use default structure if none provided
        if structure is None:
            structure = _get_genre_default_structure(genre)

        # Engine V1: original static pattern reuse
        # Create generation parameters
        params = GenerationParameters(genre=genre, style=style, **kwargs)

        if structure is None:
            structure = [
                ("intro", 4),
                ("verse", 8),
                ("chorus", 8),
                ("verse", 8),
                ("chorus", 8),
                ("bridge", 4),
                ("chorus", 8),
                ("outro", 4),
            ]

        song = Song(
            name=f"{genre}_{style}_song", tempo=tempo, global_parameters=params
        )

        # Generate patterns for each section
        for section_name, bars in structure:
            pattern = self.generate_pattern(
                genre, section_name, bars, style=style, **kwargs
            )
            if pattern:
                section = Section(section_name, pattern, bars)

                # Add variations and fills based on complexity
                if params.complexity > 0.5:
                    variations = self._generate_variations(pattern, params)
                    section.variations.extend(variations)

                fills = self._generate_fills(genre, params)
                section.fills.extend(fills)

                song.add_section(section)
            else:
                logger.warning(
                    f"Failed to generate pattern for {genre}/{section_name}"
                )

        self._apply_groove_restraints(song)

        return song

    def generate_pattern(
        self, genre: str, section: str = "verse", bars: int = 4, **kwargs
    ) -> Pattern | None:
        """Generate a single pattern with optional genre context adaptation.

        Args:
            genre: Genre name
            section: Section type
            bars: Number of bars (for multi-bar patterns)
            **kwargs: Additional generation parameters including:
                - song_genre_context: Overall song genre for adaptation
                - context_blend: Blend amount (0.0-1.0)
                - drummer: Drummer style to apply
                - humanization: Humanization amount
                - etc.

        Returns:
            Generated Pattern or None if generation failed

        Example:
            # Generate progressive pattern adapted to metal context
            pattern = generator.generate_pattern(
                genre="metal",
                style="progressive",
                section="bridge",
                song_genre_context="metal",
                context_blend=0.3
            )
        """
        # Create parameters
        params = GenerationParameters(genre=genre, **kwargs)

        # Generate base pattern
        pattern = self.plugin_manager.generate_pattern(genre, section, params)
        if not pattern:
            return None

        # Apply genre context blending if specified
        if params.song_genre_context and params.context_blend > 0:
            # Only blend if context genre is different from pattern genre
            if params.song_genre_context != genre:
                context_plugin = self.plugin_manager.get_genre_plugin(
                    params.song_genre_context
                )
                genre_plugin = self.plugin_manager.get_genre_plugin(genre)

                if context_plugin and genre_plugin:
                    context_profile = context_plugin.intensity_profile
                    pattern = genre_plugin.apply_context_blend(
                        pattern, context_profile, params.context_blend
                    )
                    logger.debug(
                        f"Applied {params.song_genre_context} context "
                        f"(blend={params.context_blend}) to {genre} pattern"
                    )

        # Apply drummer style if specified
        if params.drummer:
            styled_pattern = self.plugin_manager.apply_drummer_style(
                pattern, params.drummer
            )
            if styled_pattern:
                pattern = styled_pattern

        # Apply humanization if requested
        if params.humanization > 0:
            timing_var = params.humanization * 0.05  # Scale to reasonable range
            velocity_var = int(params.humanization * 20)
            pattern = pattern.humanize(timing_var, velocity_var)

        # Extend pattern for multiple bars if needed
        if bars > 1:
            pattern = self._extend_pattern_to_bars(pattern, bars)

        return pattern

    def apply_drummer_style(
        self, pattern: Pattern, drummer: str
    ) -> Pattern | None:
        """Apply drummer-specific style modifications to a pattern."""
        return self.plugin_manager.apply_drummer_style(pattern, drummer)

    def export_midi(self, song: Song, output_path: Path) -> None:
        """Export song as MIDI file."""
        self.midi_engine.save_song_midi(song, output_path)
        logger.info(f"Exported MIDI to: {output_path}")

    def export_pattern_midi(
        self,
        pattern: Pattern,
        output_path: Path,
        tempo: int = 120,
        drum_kit: DrumKit | None = None,
    ) -> None:
        """Export single pattern as MIDI file."""
        # Use provided drum kit or current one
        engine = self.midi_engine
        if drum_kit:
            engine = MIDIEngine(drum_kit)

        engine.save_pattern_midi(pattern, output_path, tempo)
        logger.info(f"Exported pattern MIDI to: {output_path}")

    def get_available_genres(self) -> list[str]:
        """Get list of available genres."""
        return self.plugin_manager.get_available_genres()

    def get_available_drummers(self) -> list[str]:
        """Get list of available drummers."""
        return self.plugin_manager.get_available_drummers()

    def get_styles_for_genre(self, genre: str) -> list[str]:
        """Get available styles for a genre."""
        return self.plugin_manager.get_styles_for_genre(genre)

    def get_song_info(self, song: Song) -> dict:
        """Get comprehensive information about a song."""
        info = self.midi_engine.get_midi_info(song)
        info.update(
            {
                "genre": (
                    song.global_parameters.genre
                    if song.global_parameters
                    else "unknown"
                ),
                "style": (
                    song.global_parameters.style
                    if song.global_parameters
                    else "default"
                ),
                "drummer": (
                    song.global_parameters.drummer
                    if song.global_parameters
                    else None
                ),
                "sections_count": len(song.sections),
                "unique_sections": list({s.name for s in song.sections}),
            }
        )
        return info

    def set_drum_kit(self, kit: DrumKit) -> None:
        """Set the drum kit configuration."""
        self.drum_kit = kit
        self.midi_engine = MIDIEngine(kit)

    def create_drum_kit(self, kit_type: str) -> DrumKit:
        """Create a drum kit configuration by type."""
        return DrumKit.from_keymap_name("gm")

    # Private helper methods
    def _generate_variations(
        self, base_pattern: Pattern, params: GenerationParameters
    ) -> list:
        """Generate pattern variations based on complexity."""
        from midi_drums.core.models.song import PatternVariation

        variations = []

        # Create a simplified variation
        if params.complexity > 0.7:
            simplified = base_pattern.copy()
            simplified.name = f"{base_pattern.name}_simple"

            # Remove some hi-hat hits for variation
            simplified.beats = [
                beat
                for beat in simplified.beats
                if not (
                    beat.instrument.name.endswith("HH")
                    and beat.position % 0.5 != 0
                )
            ]

            variations.append(PatternVariation(simplified, 0.3))

        return variations

    def _generate_fills(self, genre: str, params: GenerationParameters) -> list:
        """Generate fill patterns for the section.

        When a drummer is set and has signature fills (see
        DrummerPlugin.get_signature_fills()), the request is a
        drummer-inspired performance: fills are drawn exclusively from
        that drummer's candidates so the performance actually sounds
        like them, rather than being diluted by the genre's stock fills.

        Otherwise - no drummer set, or the drummer has no signature
        fills of its own (true for every drummer plugin except Peart at
        the time of writing) - fills fall back to the genre's common
        fill pool. See issue #32.
        """
        if params.drummer:
            drummer_plugin = self.plugin_manager.registry.get_drummer_plugin(
                params.drummer
            )
            if drummer_plugin:
                signature_fills = drummer_plugin.get_signature_fills()
                if signature_fills:
                    return signature_fills

        genre_plugin = self.plugin_manager.registry.get_genre_plugin(genre)
        if genre_plugin:
            return genre_plugin.get_common_fills()
        return []

    def _extend_pattern_to_bars(self, pattern: Pattern, bars: int) -> Pattern:
        """Extend a pattern to span multiple bars."""
        if bars <= 1:
            return pattern

        extended_pattern = pattern.copy()
        extended_pattern.name = f"{pattern.name}_{bars}bars"

        original_beats = pattern.beats.copy()
        beats_per_bar = pattern.time_signature.beats_per_bar

        # Repeat pattern for additional bars with slight variations
        for bar in range(1, bars):
            bar_offset = bar * beats_per_bar
            for beat in original_beats:
                import random

                from midi_drums.core.models.pattern import Beat

                new_beat = Beat(
                    position=beat.position + bar_offset,
                    instrument=beat.instrument,
                    velocity=max(
                        1, min(127, beat.velocity + random.randint(-5, 5))
                    ),  # Slight variation with clamping
                    duration=beat.duration,
                    ghost_note=beat.ghost_note,
                    accent=beat.accent,
                    instrument_promoted=beat.instrument_promoted,
                )
                extended_pattern.beats.append(new_beat)

        return extended_pattern

    def _apply_groove_restraints(self, song: Song) -> None:
        """Delegate to module-level restraint function."""
        _apply_groove_restraints(song)

    @classmethod
    def quick_generate(
        cls, genre: str = "metal", style: str = "heavy", tempo: int = 155
    ) -> Song:
        """Quick song generation with sensible defaults.

        This replicates the functionality of the original script.
        """
        generator = cls()
        return generator.create_song(
            genre=genre,
            style=style,
            tempo=tempo,
            complexity=0.7,
            dynamics=0.6,
            humanization=0.3,
        )
