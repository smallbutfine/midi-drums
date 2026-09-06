-- midi_drums_help.lua (Ardour / Mixbus)
-- Displays usage instructions in the Ardour console.
-- Load via Edit → Scripts… (Ardour) or Tools → Scripts… (Mixbus).
--
-- This is the Ardour/Mixbus equivalent of reaper/midi_drums_help.lua.

io.stderr:write([=[
================================================================================
midi_drums × Ardour / Mixbus Integration — Help
https://github.com/fsecada01/midi-drums
================================================================================

INSTALLATION
  1. Edit create_song_sections.lua → set PYTHON_EXE to your midi_drums .venv pythonw.exe
  2. Load create_song_sections.lua via:
       Ardour : Edit → Scripts…
       Mixbus : Tools → Scripts…
  3. (Optional) Assign a keyboard shortcut

USAGE
  Run the script from the menu or your shortcut.
  A dialog will ask you to choose a generation mode:

  MODES:
    YES = Ardour mode (default)
      - Creates regions from ARDOUR_SECTIONS table
      - Writes midi_drums_sections.json sidecar
      - Optionally generates MIDI via Python (~1-2s)

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

PYTHON CLI (alternative to Lua — no Ardour session needed)
  # Generate drums and write sidecar for the Lua script to consume:
  python -m midi_drums generate --genre metal --style doom \
    --tempo 70 --output drums.mid --write-sidecar project_dir/midi_drums_sections.json

  # AI generation with Ardour output directory:
  python -m midi_drums prompt "heavy doom riff" --song \
    --ardour ardour_output/ -o doom.mid

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
  • "Sidecar Not Found"     → Run the CLI command above to create the sidecar first
  • "MIDI Import Failed"    → Check Ardour console for error details; manual import works too
  • AI API key error         → Set ANTHROPIC_API_KEY / OPENAI_API_KEY in .env
  • AI too slow             → Try Groq: set GROQ_API_KEY, AI_PROVIDER=groq

================================================================================
]=])
