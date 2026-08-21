"""ComposerV2 — bar-by-bar song composition engine.

Replaces the static "generate once, repeat N bars" loop in DrumGenerator.create_song()
with per-bar pattern generation using BarSelector and IntensityCurve.

Compatible with v1 (static patterns) — call via create_song_v2() or set
composer_engine="v2" in DrumGenerator().
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.models.song import Fill, Section, Song
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.core.value_objects.time_signature import TimeSignature
from midi_drums.generation.bar_selector import BarSelector
from midi_drums.generation.fill_library.picker import FillContext, FillPicker
from midi_drums.generation.intensity_curve import (
    IntensityCurve,
    interpolate_curve,
)

if TYPE_CHECKING:
    from midi_drums.plugins.registry.plugin_registry import PluginManager

logger = logging.getLogger(__name__)


class ComposerV2:
    """Bar-by-bar song composition engine."""

    def __init__(self, plugin_manager: PluginManager, seed: int | None = None):
        self.plugin_manager = plugin_manager
        self.bar_selector = BarSelector(seed=seed)
        self.fill_picker = FillPicker(seed=seed)

    def create_song(
        self,
        genre: str,
        style: str,
        tempo: int,
        structure: list[tuple[str, int]],
        **kwargs,
    ) -> Song:
        """Create a complete song with bar-by-bar pattern evolution.

        Args:
            genre: Genre name (e.g., 'metal', 'rock').
            style: Style within genre (e.g., 'death', 'power').
            tempo: Tempo in BPM.
            structure: List of (section_name, bars) tuples.
            **kwargs: Additional parameters for GenerationParameters
                (complexity, drummer, humanization, dynamics, etc.).

        Returns:
            Complete Song object with unique patterns per bar.
        """
        params = GenerationParameters(genre=genre, style=style, **kwargs)

        # Auto-select a random preferred drummer when none is specified
        if not params.drummer:
            all_drummers = self.plugin_manager.get_available_drummers()
            preferred_for_genre: list[str] = []
            for name in all_drummers:
                plugin = self.plugin_manager.registry.get_drummer_plugin(name)
                if plugin and genre in plugin.preferred_genres:
                    preferred_for_genre.append(name)

            if preferred_for_genre:
                params.drummer = random.choice(preferred_for_genre)
                logger.info(
                    f"Auto-selected drummer '{params.drummer}' for {genre}"
                )
            else:
                # If no drummer prefers this genre, pick any at random
                params.drummer = random.choice(all_drummers)
                logger.info(
                    f"No preferred drummer for {genre}; randomly picked '{params.drummer}'"
                )

        song = Song(
            name=f"{genre}_{style}_song",
            tempo=tempo,
            global_parameters=params,
        )

        # Determine section-specific intensity curves
        curve_map = self._get_section_curve_map(structure)

        for section_name, bars in structure:
            # Generate a unique pattern for each bar
            generated_bars: list[Pattern] = []

            genre_plugin = self.plugin_manager.registry.get_genre_plugin(genre)
            if not genre_plugin:
                logger.warning(f"No genre plugin found for {genre}")
                continue

            for bar_index in range(bars):
                # Get intensity point for this bar position
                curve = curve_map.get(section_name, IntensityCurve.PLATEAU)
                # Flatten tuple of lists from enum value into single list
                all_points = [pt for pts in curve.value for pt in pts]
                intensity_pt = interpolate_curve(
                    all_points, bar_index / max(1, bars - 1)
                )

                # Generate base pattern from genre plugin (skeleton)
                # We'll modify it per-bar in the selector
                # Generate base pattern directly - no separate params needed for skeleton

                # Generate a unique beat-by-beat skeleton for this bar
                base_bar_pattern = self._generate_base_bar(
                    genre_plugin, section_name, params, bar_index, intensity_pt
                )

                if not base_bar_pattern:
                    continue

                # Apply drummer style to this specific bar's skeleton
                drummed_pattern = base_bar_pattern
                if params.drummer:
                    drummer_plugin = (
                        self.plugin_manager.registry.get_drummer_plugin(
                            params.drummer
                        )
                    )
                    if drummer_plugin:
                        drummed_pattern = drummer_plugin.apply_style(
                            base_bar_pattern
                        )

                # Final bar-level modulation (density, complexity, etc.)
                final_pattern = self.bar_selector.generate_for_bar(
                    drummed_pattern,
                    bar_index,
                    bars,
                    intensity_pt,
                    drummer_name=params.drummer,
                    previous_bars=generated_bars,
                )

                generated_bars.append(final_pattern)

            # If we have individual bar patterns, combine them into a section
            if generated_bars:
                combined = self._combine_bar_patterns(
                    generated_bars, genre_plugin, params
                )

                # Determine fill placement based on section context
                fills = self._generate_context_aware_fills(genre, params, bars)

                section = Section(section_name, combined, bars, fills=fills)
                song.add_section(section)

        return song

    def _get_section_curve_map(
        self, structure: list[tuple[str, int]]
    ) -> dict[str, IntensityCurve]:
        """Assign intensity curves based on section names and neighbors."""
        curve_map = {}
        section_names = [name for name, _ in structure]

        # Find chorus positions for post-chorus dips
        # _chorus_indices used for future pre-chorus curve adjustments

        for i, (section_name, _bars) in enumerate(structure):
            prev_section = section_names[i - 1] if i > 0 else None
            next_section = (
                section_names[i + 1] if i < len(structure) - 1 else None
            )

            # Assign curves based on musical context
            if section_name == "intro":
                curve_map[section_name] = IntensityCurve.ASCENDING
            elif section_name == "verse" and prev_section == "chorus":
                # Post-chorus verse: start lower then build
                curve_map[section_name] = IntensityCurve.DIP_RISE
            elif section_name == "verse" and (
                prev_section == "bridge" or i < 2
            ):
                # First verse after bridge: build up
                curve_map[section_name] = IntensityCurve.STEPS
            elif section_name == "chorus":
                # Choruses maintain energy with a plateau
                curve_map[section_name] = IntensityCurve.PLATEAU
            elif section_name == "bridge":
                # Bridge: dip then rise (setup for final chorus)
                if next_section == "chorus":
                    curve_map[section_name] = IntensityCurve.DIP_RISE
                else:
                    curve_map[section_name] = IntensityCurve.DESCENDING
            elif section_name == "breakdown":
                # Breakdown: drop to sparse, then build back
                curve_map[section_name] = IntensityCurve.DIP_RISE
            elif section_name == "outro":
                curve_map[section_name] = IntensityCurve.DESCENDING
            else:
                curve_map[section_name] = IntensityCurve.PLATEAU

        return curve_map

    def _select_flavor(
        self,
        available: list[Pattern],
        bar_index: int,
        previous_indices: list[int],
    ) -> Pattern:
        """Pick a flavor for this bar, avoiding immediate repeats.

        Tries to pick a different flavor than the last bar; falls back
        to the first (default) if all others were just used.
        """
        if len(available) <= 1:
            return available[0]

        # Filter out flavors used on the immediately previous bar(s)
        recent = set(previous_indices[-2:]) if previous_indices else set()
        candidates = [i for i in range(len(available)) if i not in recent]
        if not candidates:
            candidates = list(range(len(available)))

        idx = candidates[bar_index % len(candidates)]
        previous_indices.append(idx)
        return available[idx]

    def _generate_base_bar(
        self,
        genre_plugin,
        section_name: str,
        global_params: GenerationParameters,
        bar_index: int,
        intensity_pt,
    ) -> Pattern | None:
        """Generate the raw beat skeleton for this specific bar (before drummer style).

        For sections that are one-bar loops (most common), returns a single-bar slice
        of the genre plugin's pattern. For multi-bar patterns, cycles through bars.

        Returns a one-bar pattern with intensity-appropriate density and velocities.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        beats_per_bar = (
            global_params.time_signature.beats_per_bar
            if hasattr(global_params, "time_signature")
            and global_params.time_signature
            else 4
        )

        builder = PatternBuilder(f"{section_name}_bar{bar_index}")

        # Use the genre plugin to generate a base pattern for this section
        base_params_dict = {
            k: v
            for k, v in vars(global_params).items()
            if not (k == "genre" or k == "style")
        }
        params_for_base = GenerationParameters(
            genre=global_params.genre,
            style=global_params.style,
            **base_params_dict,
        )

        # Try to get available flavors; fall back to generate_pattern()
        try:
            all_flavors = genre_plugin.get_section_flavors(
                section_name, params_for_base
            )
        except TypeError:
            # Older plugins without get_section_flavors — skip flavor rotation
            all_flavors = []

        if all_flavors:
            # Filter out None entries (e.g. style-specific flavors only for some styles)
            available = [f for f in all_flavors if f is not None]
            if available:
                key = (global_params.genre, section_name)
                indices = getattr(self, "_prev_indices", {})
                idx_list = indices.setdefault(key, [])
                base_pattern = self._select_flavor(
                    available, bar_index, idx_list
                )
            else:
                base_pattern = genre_plugin.generate_pattern(
                    section_name, params_for_base
                )
        else:
            base_pattern = genre_plugin.generate_pattern(
                section_name, params_for_base
            )

        if not base_pattern:
            return None

        # If the pattern spans multiple bars, cycle through them based on bar_index.
        # This ensures each bar gets a different subset of the multi-bar skeleton.
        if base_pattern.beats:
            max_pos = max(b.position for b in base_pattern.beats)
            num_bars_in_pattern = int(max_pos / beats_per_bar) + 1
        else:
            num_bars_in_pattern = 1

        target_bar = bar_index % num_bars_in_pattern

        start_pos = target_bar * beats_per_bar
        end_pos = start_pos + beats_per_bar

        for beat in base_pattern.beats:
            if start_pos <= beat.position < end_pos:
                bar_pos = beat.position - start_pos
                builder.pattern.add_beat(
                    bar_pos,
                    beat.instrument,
                    max(1, min(127, beat.velocity)),
                )

        built = builder.build()

        # If this bar slice is completely empty, fall back to the original full pattern
        if not built.beats:
            logger.warning(
                f"Empty bar slice for {section_name} bar {bar_index}; "
                "reusing the full base pattern instead."
            )
            # Create a one-bar slice from the first bar of the base pattern
            fallback_builder = PatternBuilder(f"{section_name}_bar{bar_index}_fallback")
            for beat in base_pattern.beats:
                if beat.position < beats_per_bar:
                    fallback_builder.pattern.add_beat(
                        beat.position,
                        beat.instrument,
                        max(1, min(127, beat.velocity)),
                    )
            built = fallback_builder.build()

        return built

    def _combine_bar_patterns(
        self, bars: list[Pattern], genre_plugin, global_params
    ) -> Pattern:
        """Combine individual bar patterns into a single section pattern.

        The result is the union of all beats across bars, with proper offset
        (each bar's beats start at its correct beat position).
        Skips empty bars but ensures the final pattern always has beats.
        """

        combined = Pattern(f"{bars[0].name.replace('_bar*', '')}_combined")
        total_beats = 0
        beats_per_bar = (
            global_params.time_signature.beats_per_bar
            if hasattr(global_params, "time_signature")
            and global_params.time_signature
            else 4
        )

        # Validate: reject bars with zero beats (should not happen after fix)
        for i, bar in enumerate(bars):
            if not bar.beats:
                logger.warning(
                    f"Bar {i} has zero beats — this bar will be skipped "
                    f"in the combined pattern. Check _generate_base_bar fallback logic."
                )

        for bar_idx, bar in enumerate(bars):
            if not bar.beats:
                continue  # skip empty bars
            offset = bar_idx * beats_per_bar
            for beat in bar.beats:
                combined.beats.append(
                    Beat(
                        position=beat.position + offset,
                        instrument=beat.instrument,
                        velocity=beat.velocity,
                        duration=beat.duration,
                        ghost_note=beat.ghost_note,
                        accent=beat.accent,
                        instrument_promoted=beat.instrument_promoted,
                    )
                )
            total_beats += len(bar.beats)

        # If nothing was combined, use a basic default pattern
        if not combined.beats:
            logger.warning(
                "No beats were combined for section — creating a basic kick/snare pattern."
            )
            from midi_drums.config import VELOCITY

            combined.beats.append(
                Beat(position=0, instrument=DrumInstrument.KICK, velocity=int(VELOCITY.KICK_HEAVY))
            )
            combined.beats.append(
                Beat(position=2, instrument=DrumInstrument.SNARE, velocity=int(VELOCITY.SNARE_ACCENT))
            )

        # Set time signature from first bar
        combined.time_signature = (
            bars[0].time_signature if bars else TimeSignature()
        )
        return combined

    def _generate_context_aware_fills(
        self, genre: str, params: GenerationParameters, section_bars: int
    ) -> list[Fill]:
        """Generate fills based on section context and drummer.

        Drummer signature fills are wrapped in FillContext so that
        FillPicker can apply position-aware weighting later.  Genre
        common fills remain as bare Fill objects (they have no context).
        """
        # If drummer has signature fills, use those preferentially
        if params.drummer:
            drummer_plugin = self.plugin_manager.registry.get_drummer_plugin(
                params.drummer
            )
            if drummer_plugin:
                raw_fills = drummer_plugin.get_signature_fills()
                if raw_fills:
                    # Wrap each Fill in a FillContext so picker can weight by
                    # section preference, trigger probability, etc.
                    context_fills: list[FillContext] = []
                    for fill in raw_fills:
                        ctx = FillContext(
                            name=fill.pattern.name,
                            pattern=fill.pattern,
                            trigger_probability=fill.trigger_probability,
                            section_position=fill.section_position,
                            preferred_sections=getattr(
                                fill, "preferred_sections", set()
                            ),
                            weight=1.0,
                        )
                        context_fills.append(ctx)
                    # Return the FillContexts wrapped as Fill objects
                    # (FillContext._pattern_name provides legacy accessor)
                    return [self._fill_from_context(f) for f in context_fills]

        # Fallback to genre common fills
        genre_plugin = self.plugin_manager.registry.get_genre_plugin(genre)
        if genre_plugin:
            return genre_plugin.get_common_fills()

        return []

    def _fill_from_context(self, ctx: FillContext) -> Fill:
        """Convert a FillContext back to a Fill for API compatibility.

        The returned Fill delegates _pattern_name / pattern.name to the
        context so existing code that reads fill.pattern.name still works.
        """
        return Fill(
            pattern=ctx.pattern,
            trigger_probability=ctx.trigger_probability,
            section_position=ctx.section_position,
        )
