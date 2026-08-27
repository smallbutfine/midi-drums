"""Macro-composer for purposeful bar-by-bar pattern selection.

Instead of repeating the same static skeleton across all bars, this module
understands section context (establish/maintain/build/turnaround phases) and
selects from genre-specific groove libraries to create musically coherent
progression within each section.

This fixes the "polka" effect where every bar sounds identical by giving each
bar a purposeful role in the section's arc.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from midi_drums.core.models.pattern import Pattern


@dataclass
class MacroComposerPhase:
    """Represents a phase of the section's intensity arc.

    Phases determine what structural approach is musically appropriate:
    - ESTABLISH (0-25%): Clear downbeat, strong backbeat, unambiguous groove
    - MAINTAIN (25-60%): Slight variation on established groove to avoid monotony
    - BUILD (60-85%): Add density/energy — more kicks, syncopation, accents
    - TURNAROUND (85-100%): Closure, tension release, or dynamic shift
    """

    name: str
    start_pct: float  # inclusive
    end_pct: float  # exclusive
    description: str


# Standard section arc phases (75% of sections)
PHASE_ESTABLISH = MacroComposerPhase(
    name="establish",
    start_pct=0.0,
    end_pct=0.25,
    description="First quarter: establish groove with clear downbeat and backbeat",
)

PHASE_MAINTAIN = MacroComposerPhase(
    name="maintain",
    start_pct=0.25,
    end_pct=0.60,
    description="Middle: maintain groove with slight structural variation",
)

PHASE_BUILD = MacroComposerPhase(
    name="build",
    start_pct=0.60,
    end_pct=0.85,
    description="Late section: add density/energy for transition to next section",
)

PHASE_TURNAROUND = MacroComposerPhase(
    name="turnaround",
    start_pct=0.85,
    end_pct=1.0,
    description="Final bars: closure/tension release before next section",
)

# Short sections (< 4 bars) use simplified arcs
SHORT_PHASE_ESTABLISH = MacroComposerPhase(
    name="establish",
    start_pct=0.0,
    end_pct=0.5,
    description="Short section: establish groove (first half only)",
)

SHORT_PHASE_TURNAROUND = MacroComposerPhase(
    name="turnaround",
    start_pct=0.5,
    end_pct=1.0,
    description="Short section: turnaround/closure (second half only)",
)


class GrooveLibraryManager:
    """Manages per-genre/section groove libraries for multi-bar variety."""

    def __init__(self):
        self._groove_libs: dict[str, list[Pattern]] = (
            {}
        )  # key: genre:section -> grooves

    def register_groove_library(
        self,
        genre: str,
        section: str,
        grooves: list[Pattern],
    ) -> None:
        """Register a library of grooves for a specific genre/section combo.

        Each groove should be a complete 1-bar pattern with distinct structural
        approach (not just timing/velocity differences). The library should
        contain 4-8 grooves covering different approaches the drummer might use.
        """
        key = f"{genre}:{section}"
        if len(grooves) < 2:
            raise ValueError(
                f"Groove library must have at least 2 grooves, got {len(grooves)} "
                f"(for {key})"
            )
        self._groove_libs[key] = grooves

    def get_grooves(self, genre: str, section: str) -> list[Pattern]:
        """Get the groove library for a genre/section combo."""
        key = f"{genre}:{section}"
        if key not in self._groove_libs:
            return []
        return list(self._groove_libs[key])

    def select_groove(
        self,
        genre: str,
        section: str,
        phase: MacroComposerPhase | None = None,
        rng: random.Random | None = None,
        previous_indices: list[int] | None = None,
    ) -> Pattern | None:
        """Select a groove from the library based on section context.

        Args:
            genre: Genre name (e.g., 'rock', 'metal')
            section: Section name (e.g., 'verse', 'chorus')
            phase: Current macro-composer phase (establish/maintain/build/turnaround)
                If None, picks randomly (useful for short sections)
            rng: Random number generator for reproducible selection
            previous_indices: Previously selected indices to avoid repeat patterns

        Returns:
            A groove Pattern from the library, or None if no library exists
        """
        grooves = self.get_grooves(genre, section)
        if not grooves:
            return None

        rng = rng or random.Random()
        previous_indices = previous_indices or []

        # Filter grooves by phase appropriateness (if phase specified)
        if phase is not None:
            compatible = [
                g
                for i, g in enumerate(grooves)
                if self._is_compatible_with_phase(i, phase, len(grooves))
            ]
            if compatible:
                grooves = compatible

        # Avoid immediate repeat of previously used groove from this library
        candidates = [
            i for i in range(len(grooves)) if i not in previous_indices[-2:]
        ]
        if not candidates:
            candidates = list(range(len(grooves)))

        idx = rng.choice(candidates)
        previous_indices.append(idx)
        return grooves[idx]

    @staticmethod
    def _is_compatible_with_phase(
        index: int, phase: MacroComposerPhase, total: int
    ) -> bool:
        """Determine if a groove index is appropriate for the given phase.

        Convention: first 25% of grooves = establish types, last 25% = turnaround.
        Middle grooves are flexible (maintain/build).
        """
        early_ratio = int(total * 0.25)
        late_start = total - int(total * 0.25)

        if phase.name == "establish":
            return index < max(early_ratio, 1)
        elif phase.name == "turnaround":
            return index >= late_start
        else:
            # maintain/build can use any groove except extreme establish/turnaround only
            return True


class MacroComposer:
    """Determines purposeful bar-by-bar structure based on section position.

    Instead of random pattern selection, this module understands that sections
    have an arc: they start by establishing a groove, develop through variation,
    build energy or tension, and resolve/turnaround before the next section.

    Each phase maps to different structural approaches within the genre's groove
    library (defined by get_section_grooves() on genre plugins).
    """

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self.groove_manager = GrooveLibraryManager()

    def determine_phase(
        self, bar_index: int, total_bars: int
    ) -> MacroComposerPhase:
        """Determine which macro-composer phase a bar belongs to.

        Args:
            bar_index: 0-based position within the section
            total_bars: Total number of bars in the section

        Returns:
            The appropriate phase for this bar position
        """
        if total_bars <= 4:
            # Short sections: simplified arc (establish/turnaround only)
            progress = bar_index / max(1, total_bars - 1)
            if progress < SHORT_PHASE_ESTABLISH.end_pct:
                return SHORT_PHASE_ESTABLISH
            else:
                return SHORT_PHASE_TURNAROUND

        # Standard section arc
        progress = bar_index / max(1, total_bars - 1)

        if progress < PHASE_ESTABLISH.end_pct:
            return PHASE_ESTABLISH
        elif progress < PHASE_BUILD.end_pct:
            return (
                PHASE_MAINTAIN
                if progress < PHASE_MAINTAIN.end_pct
                else PHASE_BUILD
            )
        elif progress < PHASE_TURNAROUND.end_pct:
            return PHASE_TURNAROUND

        # Fallback to establish (shouldn't happen but safety)
        return PHASE_ESTABLISH


def get_section_grooves(
    genre_plugin, section_name: str, complexity: float, style: str = "default"
) -> list[Pattern]:
    """Get the groove library for a genre/section/style combo from the plugin.

    Falls back to generate_pattern() if the plugin doesn't implement
    get_section_grooves(), returning [single_pattern] (no variety).
    """
    try:
        return genre_plugin.get_section_grooves(section_name, complexity, style)
    except (TypeError, AttributeError):
        # Plugin doesn't support multi-bar grooves yet — use generate_pattern
        from midi_drums.core.value_objects.generation_parameters import (
            GenerationParameters,
        )

        params = GenerationParameters(
            genre=genre_plugin.genre_name, style="default"
        )
        pattern = genre_plugin.generate_pattern(section_name, params)
        return [pattern] if pattern else []
