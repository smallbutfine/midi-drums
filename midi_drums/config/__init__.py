"""Configuration module for MIDI Drums Generator.

This module provides centralized constants and configuration values used
throughout the system, eliminating magic numbers and improving maintainability.

Quick Start:
    from midi_drums.config import VELOCITY, TIMING, DEFAULTS, DEFAULT_MAPPING

    # Use velocity constants
    builder.kick(0.0, VELOCITY.KICK_NORMAL)
    builder.snare(1.0, VELOCITY.SNARE_HEAVY)

    # Use timing constants
    for i in range(8):
        builder.hihat(i * TIMING.EIGHTH, VELOCITY.HIHAT_NORMAL)

    # Use generation defaults
    if complexity is None:
        complexity = DEFAULTS.COMPLEXITY_DEFAULT
"""

from midi_drums.config.constants import (
    DEFAULTS,
    TIMING,
    VELOCITY,
    GenerationDefaults,
    TimingConstants,
    VelocityPresets,
    VelocityRanges,
)

# ── Top-level defaults (imported for convenience) ──────────────────
from midi_drums.config.defaults import (
    DEFAULT_MAPPING,
    VALID_MAPPINGS,
    DEFAULT_TEMPO,
    DEFAULT_GENRE,
    DEFAULT_STYLE,
    DEFAULT_SECTION,
    DEFAULT_COMPLEXITY,
)

__all__ = [
    # Singleton instances (most commonly used)
    "VELOCITY",
    "TIMING",
    "DEFAULTS",
    # Classes (for type hints and advanced usage)
    "VelocityRanges",
    "TimingConstants",
    "GenerationDefaults",
    "VelocityPresets",
    # Defaults
    "DEFAULT_MAPPING",
    "VALID_MAPPINGS",
    "DEFAULT_TEMPO",
    "DEFAULT_GENRE",
    "DEFAULT_STYLE",
    "DEFAULT_SECTION",
    "DEFAULT_COMPLEXITY",
]
