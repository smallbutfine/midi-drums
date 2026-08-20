"""Generation domain - composition engine, pattern builder, and the
strategy interfaces/service orchestrator that sit above them.

Engine v2 (bar-by-bar evolution):
    BarSelector: produces different patterns per bar using intensity curves
    IntensityCurve: defines section energy arcs (ASCENDING, PLATEAU, etc.)
    ComposerV2: new composition engine using BarSelector + intensity curves
"""

from midi_drums.generation.bar_selector import BarSelector
from midi_drums.generation.composer_v2 import ComposerV2
from midi_drums.generation.intensity_curve import IntensityCurve

__all__ = [
    "BarSelector",
    "ComposerV2",
    "IntensityCurve",
]
