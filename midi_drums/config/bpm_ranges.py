"""Genre/style default BPM lookup.

Data lives in the genre plugins' ``DEFAULT_TEMPO_MAP`` class attributes.
This module is a thin adapter that queries loaded plugins so callers don't
need to know about plugin internals.
"""

from __future__ import annotations

from midi_drums.plugins.registry.plugin_registry import PluginManager


def get_default_bpm(genre: str, style: str) -> int | None:
    """Return the preferred default BPM for a genre/style combo.

    Looks up ``DEFAULT_TEMPO_MAP`` on the loaded genre plugin.  Returns
    ``None`` when no data exists (the caller should fall back to
    TEMPO_DEFAULT).
    """
    pm = PluginManager()
    pm.discover_plugins()
    entry = pm.get_default_tempo_map(genre, style)
    if isinstance(entry, int):
        return entry
    return None  # no map or unknown style
