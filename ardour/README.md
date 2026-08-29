# Ardour / Mixbus Integration

This directory contains the **Ardour/Mixbus** integration scripts for `midi_drums`,
mirroring the REAPER integration in `../reaper/`.

## Files

| File | Purpose |
|------|---------|
| `create_song_sections.lua` | Bi-directional bridge (4 modes: Ardour, sidecar, AI, song-map) |
| `midi_drums_help.lua` | Help script — displays usage instructions in the Ardour console |

## Installation (Mixbus)

1. **Set PYTHON_EXE** in `create_song_sections.lua` to your midi_drums virtualenv pythonw.exe:
   ```lua
   local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"
   ```

2. **Load the script into Mixbus**:
   - Open Mixbus
   - Go to `Tools → Scripts → Load Script...`
   - Select `create_song_sections.lua`
   - Optionally assign a keyboard shortcut via `Options → Customize...`

3. **Run** the script from `Tools → Scripts → midi_drums` or your assigned shortcut.

## Modes (same as REAPER version)

| Mode | Description |
|------|-------------|
| **Ardour** (default) | Creates regions from `ARDOUR_SECTIONS` table, writes sidecar, optionally generates MIDI via Python template engine (~1-2s) |
| **Sidecar** | Reads `midi_drums_sections.json`, creates matching regions, offers tempo sync |
| **AI Agent** | Prompts for NL description → calls Python AI → imports generated MIDI (~20-45s) |
| **Song-map** | Per-section tempo/meter from song_creator-shaped JSON |

## Sidecar Format (`midi_drums_sections.json`)

```json
{
  "source": "ardour",
  "tempo": 120,
  "time_signature": [4, 4],
  "sections": [
    {"name": "Intro",  "bars": 8},
    {"name": "Verse",  "bars": 16}
  ]
}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No Session available" | Ensure a session is open before running the script |
| Python generation failed | Check PYTHON_EXE path; verify .venv exists |
| MIDI import failed | Check Ardour console for details |
| AI too slow | Try Groq (GROQ_API_KEY, set AI_PROVIDER=groq in .env) |

## API Equivalents

The same Python-side API used by the REAPER script also works with this Ardour version:

```python
# Write sidecar from a Song
api.export_sections_json(song, "midi_drums_sections.json")

# Read sidecar → generate Song
song = api.create_song_from_sections_json("midi_drums_sections.json", "metal", "death")

# MIDI + sidecar in one call
api.save_as_midi_with_sidecar(song, "drums.mid")
```

## Notes on Ardour/Mixbus API Differences

This script handles several Ardour/Mixbus API variations:

- **Session object**: Checked as `Session` or `SESSION` global for compatibility
- **Tempo map**: Tries multiple method signatures (`get()`, `get_tempo_at_time()`) for different Ardour versions
- **Time signature**: Handles both `numerator/denominator` and `num/denom` field names
- **Regions**: Tries `add_region()` first, falls back to `markers` table insertion
- **UI refresh**: Uses `GUI.refresh_all()` when available
- **Undo**: Wraps changes in undo blocks via `gui:undo_start()/undo_stop()`

If your Mixbus version has a different API surface, please file an issue with the error messages from the Ardour console.
