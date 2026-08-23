# REAPER Integration

## New UI Panel (ReaImGui) — **RECOMMENDED**

`reaper/midi_drums_panel.lua` replaces all legacy scripts with a dockable ReaImGui window.

### Setup

1. **Install ReaImGui** (one-time):
   - Extensions > ReaPack > Browse packages...
   - Search "ReaImGui", install, restart REAPER

2. **Copy the `midi_drums/` subfolder** into your REAPER Scripts folder:
   ```
   cp -r reaper/midi_drums "C:/REAPER/Scripts/"
   ```

3. **Load the panel**:
   - Extensions > midi_drums Panel (or assign a shortcut via Actions)

4. **Configure Python path** in the Settings tab → the panel will prompt on first use

### Features

- **Four modes** — REAPER sections, Sidecar JSON, AI prompt, Song Map
- **Riff-Lock Beat** — lock kicks to guitar/bass riff accents (requires `midi_drums[rff]` extras)
- **Real-time log** with colorized output and auto-scroll
- **Persistent settings** via ExtState (survives REAPER restarts)
- **Non-blocking generation** — REAPER stays usable during AI runs (20-45s)

---

## Legacy Scripts (Retired)

These are replaced by the panel above. They remain for backward compatibility:

- `create_song_sections.lua` — original sidecar bridge script
- `midi_drums_help.lua` — help screen (replaced by Settings tab)

**Do not use these unless you specifically need dialog-based interaction.**

---

## Python CLI Reference

All panel modes call our midi-drums CLI:

| Panel Mode | CLI Equivalent |
|------------|----------------|
| REAPER Sections | `midi-drums generate --genre X --style Y --sidecar sidecar.json -o drums.mid` |
| Sidecar | (no Python call — reads existing JSON) |
| AI Prompt | `midi-drums prompt "description" --song --tempo N --write-sidecar sc.json -o drums.mid` |
| Song Map | `midi-drums generate --genre X --style Y --song-map map.json --write-timeline tl.json -o drums.mid` |
| Riff-Lock Beat | `midi-drums riff audio.wav --genre X --style Y ... -o drums.mid` |

## Riff Lock (requires `midi_drums[rfi]`)

Enable with `pip install "midi-drums[rfi]"` to add librosa-based onset detection.

Usage:
```bash
midi-drums riff path/to/guitar.wav --genre rock --style classic --drummer bonham -o riff.mid
# Snare modes: off, reinforce (boost existing hits), stab (insert unison hits)
midi-drums riff riff.wav --snare-mode stab --snare-threshold 0.85
```

The panel handles audio rendering, bar alignment correction, and Python CLI invocation automatically.
