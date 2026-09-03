"""Central configuration defaults for MIDI Drums Generator."""

from __future__ import annotations

# ── Default CLI values ─────────────────────────────────────────────
DEFAULT_TEMPO: int = 120
DEFAULT_GENRE: str = "rock"
DEFAULT_STYLE: str = "classic"
DEFAULT_SECTION: str = "verse"
DEFAULT_COMPLEXITY: float = 0.5

# No DEFAULT_MAPPING — just use 'gm' literally everywhere.

# ── Reaper Lua default values (mirrors create_song_sections.lua) ───
REAPER_DEFAULTS = {
    "genre": DEFAULT_GENRE,
    "style": DEFAULT_STYLE,
    "mapping": "gm",
}

__all__ = [
    "DEFAULT_TEMPO",
    "DEFAULT_GENRE",
    "DEFAULT_STYLE",
    "DEFAULT_SECTION",
    "DEFAULT_COMPLEXITY",
    "REAPER_DEFAULTS",
]
