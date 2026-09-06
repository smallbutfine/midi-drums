# Ardour / Mixbus Integration

This directory contains the **Ardour/Mixbus** integration scripts for `midi_drums`.

## Files

| File | Purpose |
|------|---------|
| `create_song_sections.lua` | Bi-directional bridge (4 modes: Ardour, sidecar, AI, song-map) |
| `midi_drums_help.lua` | Help script — displays usage instructions in the Ardour console |

## How it works

The Python CLI generates MIDI + writes a `midi_drums_sections.json` sidecar.
The Lua script reads that sidecar (or uses built-in template sections) and creates
timeline regions/marker markers inside the **open** Ardour/Mixbus session.
This is the reverse of REAPER: Python is the engine, Lua is the viewer/consumer.

### Workflow 1 — Python-first (recommended)

```bash
# Generate drums and write sidecar
python -m midi_drums generate --genre metal --style doom --tempo 70 \
    --output drums.mid --write-sidecar project_dir/midi_drums_sections.json

# Open Ardour/Mixbus, open your session, then run the Lua script
# It reads the sidecar and creates matching regions automatically.
```

### Workflow 2 — Lua-first (interactive)

1. Set `PYTHON_EXE` in `create_song_sections.lua` to your midi_drums `.venv` pythonw.exe.
2. Open Ardour/Mixbus with a session active.
3. Run the script (Ardour: **Edit → Scripts…**, Mixbus: **Tools → Scripts…**).
4. Choose **YES** for template sections or **NO → sidecar/ai/songmap**.

## Modes

| Mode | Trigger | What it does |
|------|---------|-------------|
| **Ardour** (default) | YES | Creates regions from `ARDOUR_SECTIONS`, writes sidecar, optionally calls Python |
| **Sidecar** | NO → `sidecar` | Reads existing sidecar, creates matching regions, syncs project tempo |
| **AI Agent** | NO → `ai` | Natural-language prompt → Python AI → imports generated MIDI (~20-45s) |
| **Song-map** | NO → `songmap` | Per-section tempo/meter from a song_creator-shaped JSON file |

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

## CLI Commands (Python side)

```bash
# Generate and write sidecar + MIDI
python -m midi_drums generate --genre rock --style classic \
    --output drums.mid --write-sidecar project_dir/midi_drums_sections.json

# AI generation with Ardour output directory
python -m midi_drums prompt "funky groove" --song --ardour ardour_output/
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No Session available" | Ensure a session is open in Ardour/Mixbus before running the Lua script |
| Python generation failed | Check PYTHON_EXE path; verify .venv exists and has dependencies installed |
| MIDI import failed | Check Ardour console (F12) for details |
| AI too slow / API key error | Try Groq: set `GROQ_API_KEY`, `AI_PROVIDER=groq` in `.env` |

## Notes

- The Lua script uses `pcall()` on all Ardour/Mixbus API calls — failures are silently skipped so the script never crashes.
- MIDI import relies on Ardour's media system; if auto-import fails, manually import `drums.mid` from the session directory.
- The sidecar JSON is the single source of truth shared between Python and Lua.
