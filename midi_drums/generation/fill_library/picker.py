"""Fill context and picker for Drummer fill library (PLAN #4)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from midi_drums.core.models.pattern import Pattern


@dataclass(frozen=True)
class FillContext:
    """A named drummer signature fill with trigger rules."""

    name: str
    pattern: Pattern
    trigger_probability: float = 0.5
    section_position: str = "end"  # "start", "middle", "end"
    min_bars_since_fill: int = 2  # Minimum bars between fills
    preferred_sections: set[str] = field(default_factory=set)
    weight: float = 1.0

    @property
    def _pattern_name(self) -> str:
        """Legacy accessor for tests that expect .pattern.name."""
        return self.pattern.name


class FillPicker:
    """Selects fills based on section context and recent fill history."""

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def select_candidates(
        self,
        available_fills: list[FillContext],
        section_name: str,
        bar_index: int,
        total_bars: int,
        recent_fill_indices: list[int],
    ) -> list[tuple[FillContext, float]]:
        """Return [(fill, weight), ...] sorted by descending effective weight.

        Rules:
        1. Filter out fills whose section_position doesn't match bar position
        2. Weight by context (section_name, intensity of section position)
        3. Penalize recent fills to avoid rapid repeat
        """
        candidates = []

        # Determine what "position" this bar is in the section
        progress = bar_index / max(1, total_bars - 1) if total_bars > 1 else 0.5

        for i, fill in enumerate(available_fills):
            # Skip fills that don't match position (start/middle/end of section)
            if fill.section_position == "start" and progress < 0.3:
                pass  # eligible
            elif fill.section_position == "middle" and 0.2 <= progress <= 0.8:
                pass  # eligible
            elif fill.section_position == "end" and progress > 0.6:
                pass  # eligible
            else:
                continue

            weight = fill.weight

            # Section preference bonus
            if section_name in fill.preferred_sections:
                weight *= 1.5

            # Penalty for recent fills
            recent_set = set(recent_fill_indices[-3:])
            if i in recent_set:
                weight *= 0.1

            candidates.append((fill, weight))

        # Sort by weight descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def pick_one(
        self,
        available_fills: list[FillContext],
        section_name: str,
        bar_index: int,
        total_bars: int,
        recent_fill_indices: list[int],
    ) -> FillContext | None:
        """Pick one fill or return None (no fill this bar)."""
        candidates = self.select_candidates(
            available_fills,
            section_name,
            bar_index,
            total_bars,
            recent_fill_indices,
        )

        if not candidates:
            return None

        # Weighted random selection
        weights = [w for _, w in candidates]
        total = sum(weights)
        if total == 0:
            return None

        r = self._rng.uniform(0, total)
        cumulative = 0
        for fill, weight in candidates:
            cumulative += weight
            if r <= cumulative:
                # Check trigger_probability roll
                if self._rng.random() < fill.trigger_probability:
                    return fill
                # Failed probability roll — still pick it but lower confidence

        return candidates[-1][0] if candidates else None
