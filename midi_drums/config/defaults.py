"""Central configuration defaults for MIDI Drums Generator."""

from __future__ import annotations

# ── Default MIDI note mapping preset ────────────────────────────────
DEFAULT_MAPPING = "gm_drums"

# ── Valid mapping presets (sorted by preference, gm_drums is default) ───
VALID_MAPPINGS: tuple[str, ...] = (
    "gm_drums",
    "ezdrummer3",
    "addictive_drums",
    "bfd3",
    "ml_drums",
    "modo_drums",
    "studio_drummer3",
)  # gm_drums is DEFAULT_MAPPING

# ── Default CLI values ─────────────────────────────────────────────
DEFAULT_TEMPO: int = 120
DEFAULT_GENRE: str = "metal"
DEFAULT_STYLE: str = "doom"
DEFAULT_SECTION: str = "verse"
DEFAULT_COMPLEXITY: float = 0.5

# ── Reaper Lua default values (mirrors create_song_sections.lua) ───
REAPER_DEFAULTS = {
    "genre": DEFAULT_GENRE,
    "style": DEFAULT_STYLE,
    "mapping": DEFAULT_MAPPING,
}


__all__ = [
    "DEFAULT_MAPPING",
    "DEFAULT_TEMPO",
    "DEFAULT_GENRE",
    "DEFAULT_STYLE",
    "DEFAULT_SECTION",
    "DEFAULT_COMPLEXITY",
    "VALID_MAPPINGS",
    "REAPER_DEFAULTS",
]
