-- midi_drums_help.lua (Ardour / Mixbus)
-- Displays usage instructions in the Ardour console.
-- Load via Tools → Scripts → Load Script, or run from command line.
--
-- This is the Ardour/Mixbus equivalent of reaper/midi_drums_help.lua.

io.stderr:write([=[
================================================================================
midi_drums × Ardour / Mixbus Integration — Help
https://github.com/fsecada01/midi-drums
================================================================================

INSTALLATION
  1. Edit create_song_sections.lua → set PYTHON_EXE to your midi_drums .venv pythonw.exe
  2. Tools → Scripts → Load Script → select create_song_sections.lua
  3. (Optional) Assign a keyboard shortcut via Options → Customize...

USAGE
  Run: Tools → Scripts → midi_drums (or your shortcut)
  A dialog will ask you to choose a generation mode:

  MODES:
    YES = Ardour mode (default)
      - Creates regions from ARDOUR_SECTIONS table
      - Writes midi_drums_sections.json sidecar
      - Optionally generates MIDI via Python template engine (~1-2s)

    NO → "sidecar"   Python sidecar mode
      - Reads midi_drums_sections.json
      - Creates regions matching that structure
      - Offers to sync project tempo from sidecar

    NO → "ai"        AI agent mode
      - Prompts for natural-language drum description + tempo
      - Calls: python -m midi_drums prompt "..." --song --write-sidecar ...
      - Imports generated MIDI on a new track (~20-45s)

    NO → "songmap"   Song-map mode (per-section tempo/meter)
      - Prompts for song_creator-shaped JSON path + genre/style
      - Calls: python -m midi_drums generate --song-map ... --write-timeline ...
      - Places tempo/time-sig markers per change point
      - Creates colored regions per region

PYTHON API EQUIVALENTS
  api.export_sections_json(song, "midi_drums_sections.json")
    Write sidecar from a Song object

  song = api.create_song_from_sections_json("midi_drums_sections.json", genre)
    Read sidecar → generate a matching Song

  api.save_as_midi_with_sidecar(song, "drums.mid")
    Export MIDI + write sidecar in one call

SIDE CAR FORMAT (midi_drums_sections.json)
  {
    "source": "ardour",
    "tempo": 120,
    "time_signature": [4, 4],
    "sections": [
      {"name": "Intro",  "bars": 8},
      {"name": "Verse",  "bars": 16}
    ]
  }

TROUBLESHOOTING
  • "No Session available"  → Open a session in Ardour/Mixbus first
  • "Generation Failed"     → Check PYTHON_EXE path + Ardour console (F12)
  • "Sidecar Not Found"     → Run save_as_midi_with_sidecar in Python first
  • "MIDI Import Failed"    → Check Ardour console for error details
  • AI API key error         → Set ANTHROPIC_API_KEY / OPENAI_API_KEY in .env
  • AI too slow             → Try Groq: set GROQ_API_KEY, AI_PROVIDER=groq

RECOMMENDED PYTHON CLI USAGE
  # Template generation (fast, no AI key needed)
  python -m midi_drums generate --genre metal --style doom \
    --sidecar midi_drums_sections.json --output drums.mid

  # AI generation (requires API key)
  python -m midi_drums prompt "heavy doom riff" --song --write-sidecar sc.json -o drums.mid

================================================================================
]=])
