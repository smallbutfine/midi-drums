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
        self._rng = random.Random(seed)
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

                # Ensure core instruments are present regardless of drummer modifier.
                # Drummer plugins (e.g., Weckl's linear coordination) may remove kicks,
                # but every bar needs at least one kick and one snare to sound musical.
                has_kick = any(
                    b.instrument == DrumInstrument.KICK
                    for b in drummed_pattern.beats
                )
                has_snare = any(
                    b.instrument == DrumInstrument.SNARE
                    for b in drummed_pattern.beats
                )
                if not has_kick:
                    from midi_drums.config import VELOCITY

                    drummed_pattern.beats.append(
                        Beat(
                            position=0.0,
                            instrument=DrumInstrument.KICK,
                            velocity=int(VELOCITY.KICK_HEAVY),
                        )
                    )
                if not has_snare:
                    from midi_drums.config import VELOCITY

                    drummed_pattern.beats.append(
                        Beat(
                            position=2.0,
                            instrument=DrumInstrument.SNARE,
                            velocity=int(VELOCITY.SNARE_ACCENT),
                        )
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

        Uses randomness (rather than pure cycling) to produce varied patterns
        across bars. Ensures the same flavor isn't used on two consecutive bars.
        """
        if len(available) <= 1:
            return available[0]

        # Filter out flavors used on the immediately previous bar(s)
        recent = set(previous_indices[-2:]) if previous_indices else set()
        candidates = [i for i in range(len(available)) if i not in recent]
        if not candidates:
            candidates = list(range(len(available)))

        # Random selection from valid candidates (not deterministic cycling)
        idx = self._rng.choice(candidates)
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

        # Ensure core instruments are always present — a pattern without at least
        # one snare hit on the backbeat will sound hollow/empty regardless of other hits.
        from midi_drums.config import VELOCITY

        has_kick = any(b.instrument == DrumInstrument.KICK for b in built.beats)
        has_snare_backbeat = any(
            b.instrument == DrumInstrument.SNARE
            and abs(b.position - beats_per_bar / 2) < 0.1
            for b in built.beats
        )

        if not has_kick:
            built.beats.append(
                Beat(
                    position=0.0,
                    instrument=DrumInstrument.KICK,
                    velocity=int(VELOCITY.KICK_HEAVY),
                )
            )
        if not has_snare_backbeat:
            built.beats.append(
                Beat(
                    position=beats_per_bar / 2,
                    instrument=DrumInstrument.SNARE,
                    velocity=int(VELOCITY.SNARE_ACCENT),
                )
            )

        # If this bar slice is completely empty, fall back to a minimal default pattern.
        # The fallback must always produce beats — a section with an empty bar would
        # leave a gap in the combined song that sounds like silence.
        if not built.beats:
            logger.warning(
                f"Empty bar slice for {section_name} bar {bar_index}; "
                "creating a minimal default pattern."
            )
            from midi_drums.config import VELOCITY

            # Use the first available flavor that has beats, or fall back to defaults
            if all_flavors:
                available = [
                    f for f in all_flavors if f is not None and f.beats
                ]
                if available:
                    source = available[0]
                    builder2 = PatternBuilder(
                        f"{section_name}_bar{bar_index}_fallback"
                    )
                    for beat in source.beats[:16]:  # cap at first bar's hits
                        if beat.position < beats_per_bar:
                            builder2.pattern.add_beat(
                                beat.position,
                                beat.instrument,
                                max(1, min(127, beat.velocity)),
                            )
                    built = builder2.build()

            # Ultimate fallback: kick on 1 + snare on 3
            if not built.beats:
                from midi_drums.config import VELOCITY

                built = Pattern(f"{section_name}_bar{bar_index}_minimal")
                built.beats.append(
                    Beat(
                        position=0.0,
                        instrument=DrumInstrument.KICK,
                        velocity=int(VELOCITY.KICK_HEAVY),
                    )
                )
                built.beats.append(
                    Beat(
                        position=2.0,
                        instrument=DrumInstrument.SNARE,
                        velocity=int(VELOCITY.SNARE_ACCENT),
                    )
                )
                built.time_signature = (
                    base_pattern.time_signature
                    if base_pattern
                    else TimeSignature()
                )

        return built

    def _combine_bar_patterns(
        self, bars: list[Pattern], genre_plugin, global_params
    ) -> Pattern:
        """Combine individual bar patterns into a single section pattern.

        The result is the union of all beats across bars. Bars already have
        section-relative positions from BarSelector.generate_for_bar(), so no
        additional offset is applied — we just collect and deduplicate them.
        """

        combined = Pattern(f"{bars[0].name.replace('_bar*', '')}_combined")
        total_beats = 0
        beats_per_bar = (
            global_params.time_signature.beats_per_bar
            if hasattr(global_params, "time_signature")
            and global_params.time_signature
            else 4
        )

        # Validate bars — warn but don't skip empty ones (they are filled in-place below)
        for i, bar in enumerate(bars):
            if not bar.beats:
                logger.warning(
                    f"Bar {i} has zero beats — filling with a basic kick/snare pattern."
                )

        # Use a set to deduplicate hits at the same (position, instrument)
        seen: set[tuple[float, str]] = set()

        for bar_idx, bar in enumerate(bars):
            if not bar.beats:
                # Fill empty bars with a minimal kick/snare pattern at this position
                fill_pos = bar_idx * beats_per_bar + 0.0
                combined.beats.append(
                    Beat(
                        position=fill_pos,
                        instrument=DrumInstrument.KICK,
                        velocity=80,
                    )
                )
                combined.beats.append(
                    Beat(
                        position=fill_pos + beats_per_bar / 2,
                        instrument=DrumInstrument.SNARE,
                        velocity=100,
                    )
                )
                continue

            for beat in bar.beats:
                key = (round(beat.position, 4), beat.instrument.name)
                if key in seen:
                    continue  # deduplicate same instrument at same position
                seen.add(key)
                combined.beats.append(
                    Beat(
                        position=beat.position,
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
                Beat(
                    position=0,
                    instrument=DrumInstrument.KICK,
                    velocity=int(VELOCITY.KICK_HEAVY),
                )
            )
            combined.beats.append(
                Beat(
                    position=2,
                    instrument=DrumInstrument.SNARE,
                    velocity=int(VELOCITY.SNARE_ACCENT),
                )
            )

        # Ensure minimum velocity for snare hits — ghost notes at vel < 40
        # become nearly inaudible and defeat the purpose of pattern generation.
        from midi_drums.config import VELOCITY

        min_snare_vel = int(VELOCITY.SNARE_NORMAL * 0.5)  # ~57 (half of normal)
        for beat in combined.beats:
            if (
                beat.instrument == DrumInstrument.SNARE
                and beat.velocity < min_snare_vel
            ):
                beat.velocity = max(
                    min_snare_vel, beat.velocity + 15
                )  # boost gently

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
