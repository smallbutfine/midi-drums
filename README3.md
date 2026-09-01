# MIDI Drums Generator — User Guide

Generate realistic drum tracks in **metal, rock, jazz, funk**, and **electronic** genres. Choose from **17 drummer styles**, apply genre-specific patterns, and export directly to **REAPER** or **Ardour/Mixbus**.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
  - [Generate a Song](#generate-a-song)
  - [Generate a Single Pattern](#generate-a-single-pattern)
  - [AI-Powered Generation](#ai-powered-generation)
  - [List Available Options](#list-available-options)
  - [Riff-Locked Beats](#riff-locked-beats)
- [DAW Integration](#daw-integration)
  - [REAPER Integration](#reaper-integration)
  - [Ardour / Mixbus Integration](#ardour--mixbus-integration)
- [Available Genres & Styles](#available-genres--styles)
- [Available Drummers](#available-drummers)
- [MIDI Mapping Presets](#midi-mapping-presets)

---

## Installation

### Prerequisites

- **Python 3.10+** installed and on your PATH
- **uv** (for dependency management)

### Setup

```bash
# Clone or copy the project into your working directory, then:
cd midi-drums

# Create and activate a virtual environment
uv venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS

# Install core dependencies (mido for MIDI generation)
uv pip install -r core_requirements.in

# (Optional) AI support for `prompt` command
uv pip install -r ai_requirements.in

# (Optional) Dev tools for riff-lock audio analysis
uv pip install -r dev_requirements.in
```

### Confirm Installation

```bash
python -m midi_drums.api.cli info
```

Expected output:

```
MIDI Drums Generator
========================================
Genres: 5
Drummers: 17
Plugin system: Active

Available genres:
  electronic (4 styles)
  funk (7 styles)
  jazz (7 styles)
  metal (7 styles)
  rock (7 styles)
```

---

## Quick Start

Generate a complete song in one command — defaults to **rock / classic** at genre-aware tempo:

```bash
python -m midi_drums.api.cli --song --output my_song.mid
```

Or use the `generate` subcommand with explicit genre and style:

```bash
python -m midi_drums.api/cli generate --genre metal --style death --tempo 180 --output death_metal.mid
```

---

## CLI Reference

The CLI is invoked via `python -m midi_drums.api.cli`. All commands shown below use this form. You may also create an alias (`alias midi-drums='python -m midi_drums.api.cli'` on Linux/macOS, or a batch/cmd wrapper on Windows).

### Generate a Song

```bash
python -m midi_drums.api.cli generate --genre GENRE --style STYLE --output OUTPUT.mid [options]
```

**Required:** `--genre`, `--output`

| Option | Default | Description |
|--------|---------|-------------|
| `--genre GENRE` | *(required)* | Genre: `metal`, `rock`, `jazz`, `funk`, `electronic` |
| `--style STYLE` | `"default"` | Style within genre. Run `list styles --genre <name>` to see options. |
| `--tempo BPM` | Genre/style default | Tempo in BPM. When omitted, a **genre-style-aware default** is used (e.g. doom = 70 BPM, death = 195 BPM). |
| `--output -o PATH` | *(required)* | Output `.mid` file path |
| `--name NAME` | Auto-generated | Song name (stored in MIDI metadata) |
| `--complexity F` | 0.5 | Pattern complexity, 0.0 (sparse) to 1.0 (dense). Affects fill density and variation. |
| `--humanization F` | 0.3 | Humanization amount, 0.0 (robotic) to 1.0 (noticeable timing/velocity drift). |
| `--drummer NAME` | Auto-selected | Drummer style (see [Available Drummers](#available-drummers)). When omitted, a drummer preferred for the genre is chosen at random. |
| `--mapping NAME` | `"gm_drums"` | MIDI note mapping preset. See [MIDI Mapping Presets](#midi-mapping-presets). Also accessible as `--vst`. |
| `--mapping-file PATH` | *(none)* | Path to a custom MIDI mapping JSON file. Takes precedence over `--mapping`. |
| `--sidecar JSON` | *(none)* | Path to a `midi_drums_sections.json` sidecar file. When provided, the song's section structure (section names and bar counts) is read from this file instead of using the genre's default structure. The sidecar's tempo is used unless you also specify `--tempo`. |
| `--song-map JSON` | *(none)* | Path to a song_creator-shaped song-map JSON file (regions containing segments, each with its own bars / bpm / num / denom). When provided, the section structure **and** any per-segment tempo or time-signature overrides come from the song map. Mutually exclusive with `--sidecar`. The song map's tempo is used unless you also specify `--tempo`. |
| `--write-timeline JSON` | *(none)* | Write a flat, resolved timeline JSON (tempo points + regions + color groups) to this path after generation. Useful together with `--song-map` for REAPER/Ardour song-map mode. |

**Example: Full song with drummer and mapping**

```bash
python -m midi_drums.api.cli generate \
  --genre rock --style classic --tempo 110 \
  --drummer bonham --mapping ezdrummer3 \
  --complexity 0.7 --humanization 0.4 \
  --output classic_rock.mid
```

### Generate a Single Pattern

```bash
python -m midi_drums.api.cli pattern --genre GENRE --section SECTION --style STYLE --output OUTPUT.mid [options]
```

**Required:** `--genre`, `--output`

| Option | Default | Description |
|--------|---------|-------------|
| `--genre GENRE` | *(required)* | Genre |
| `--section SECTION` | `"verse"` | Section type: `intro`, `verse`, `chorus`, `bridge`, `breakdown`, `outro` |
| `--style STYLE` | `"default"` | Style within genre |
| `--bars N` | 4 | Number of bars in the pattern |
| `--tempo BPM` | 120 | Tempo in BPM for this pattern |
| `--complexity F` | 0.5 | Pattern complexity, 0.0–1.0 |
| `--mapping NAME` | `"gm_drums"` | MIDI mapping preset |

**Example: A verse pattern with a funk groove**

```bash
python -m midi_drums.api.cli pattern \
  --genre funk --style classic --section verse \
  --bars 4 --tempo 105 --drummer chambers \
  --mapping addictive_drums \
  --output funk_groove.mid
```

### AI-Powered Generation

Generate patterns or full songs from natural language descriptions. Requires the optional AI dependencies (`ai_requirements.in`) and an API key for one of the supported providers (see below).

```bash
python -m midi_drums.api.cli prompt "DESCRIBE YOUR GROOVE" [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `text` | *(none)* | Natural language description in quotes. When omitted, a simple default groove is generated. |
| `-o --output PATH` | Auto-generated | Output MIDI file path |
| `--tempo BPM` | 120 | Tempo in BPM |
| `--section SECTION` | `"verse"` | Song section type |
| `--bars N` | 4 | Number of bars (single pattern mode) |
| `--complexity F` | 0.5 | Pattern complexity, 0.0–1.0 |
| `--drummer NAME` | *(none)* | Drummer style to apply |
| `--song` | Off | Compose a **full multi-section song** via the AI agent (default: single pattern) |
| `--rpp FILE.rpp` | *(none)* | Also create a REAPER project file with tempo, meter, and section markers |
| `--ardour DIR` | *(none)* | Create an Ardour session directory with sidecar + MIDI alongside the AI output (same as `--rpp` but for the Ardour workflow) |
| `--save-metadata` | Off | Save a JSON metadata file at `output/<slug>/metadata.json` alongside the MIDI. When `--song` is also used, per-section part files are written to `output/<slug>/parts/`. |
| `--write-sidecar JSON` | *(none)* | Write a `midi_drums_sections.json` sidecar at this path after generation. Used by REAPER / Ardour scripts for region creation. |
| `--mapping NAME` | `"gm_drums"` | MIDI mapping preset (choices: `ezdrummer3`, `gm_drums`, `addictive_drums`, `bfd3`, `modo_drums`, `ml_drums`, `studio_drummer3`) |

**AI Backend Setup**

AI generation reads configuration from environment variables or a `.env` file in the project root. Set these to choose your provider:

| Environment Variable | Description | Example |
|---------------------|-------------|---------|
| `AI_PROVIDER` | Provider: `anthropic`, `openai`, `groq`, `cohere`, `ollama` (default: `anthropic`) | `export AI_PROVIDER=openai` |
| `AI_MODEL` | Model identifier for the provider. Defaults per provider:<br>- anthropic: `claude-sonnet-5`<br>- openai: `gpt-4o`<br>- groq: `llama-3.3-70b-versatile`<br>- cohere: `command-r-plus`<br>- ollama: `qwen3.6` | `export AI_MODEL=gpt-4o` |
| `ANTHROPIC_API_KEY` | Anthropic API key | (set your key) |
| `OPENAI_API_KEY` | OpenAI API key | (set your key) |
| `GROQ_API_KEY` | Groq API key | (set your key) |
| `COHERE_API_KEY` | Cohere API key | (set your key) |
| `AI_TEMPERATURE` | Sampling temperature, 0.0–2.0 (default: 0.7) | `export AI_TEMPERATURE=0.5` |
| `AI_MAX_TOKENS` | Maximum output tokens (default: 4096) | `export AI_MAX_TOKENS=8192` |

For **local / offline** generation, use `ollama`: set `AI_PROVIDER=ollama`, install [Ollama](https://ollama.com), pull a model (e.g. `ollama pull qwen3.6`), and ensure the Ollama server is running at `http://127.0.0.1:11434`. No API key is needed.

**Example: Generate from a prompt**

```bash
python -m midi_drums.api.cli prompt "aggressive death metal with blast beats" \
  --tempo 180 --drummer hoglan --mapping gm_drums \
  --output breakdown.mid
```

**Example: Full song via AI + REAPER project**

```bash
python -m midi_drums.api/cli prompt "groovy funk bridge with ghost notes" \
  --song --tempo 105 --drummer porcaro \
  --rpp bridge.rpp --save-metadata --mapping ezdrummer3
```

### List Available Options

| Command | Description |
|---------|-------------|
| `list genres` | List all available genres |
| `list styles --genre NAME` | List styles for a genre |
| `list drummers` | List all available drummer styles |
| `list mappings` | List all MIDI mapping presets with descriptions |

### Riff-Locked Beats

Generate kick patterns locked to the rhythmic accents detected from an audio riff (guitar or bass). This requires the optional `dev_requirements.in` dependencies (`librosa`, `numpy`).

```bash
python -m midi_drums.api/cli riff AUDIO_FILE [options] --output OUTPUT.mid
```

| Option | Default | Description |
|--------|---------|-------------|
| `audio_path` | *(required)* | Path to an audio riff file (WAV or MP3) |
| `--genre GENRE` | `"rock"` | Genre for the base drum pattern |
| `--style STYLE` | `"classic"` | Style within genre |
| `--drummer NAME` | *(none)* | Drummer style to apply |
| `--bpm BPM` | 120 | Tempo in BPM (used to convert audio timings to beat positions) |
| `--section SECTION` | `"verse"` | Section type for the base pattern |
| `--bars N` | 4 | Number of bars |
| `--grid GRID` | `"16th"` | Grid resolution: `"16th"`, `"eighth"`, etc. |
| `--lock-strength F` | 1.0 | How strictly kicks follow riff accents, 0.0 (no locking) to 1.0 (exact match). Intermediate values interpolate between the original kick position and the accent. |
| `--mapping NAME` | *(none)* | MIDI mapping preset |
| `--snare-mode MODE` | `"off"` | Snare reaction mode: `"off"` (no snare modification), `"reinforce"` (boost velocity of snare hits near accents), `"stab"` (insert a new snare hit at strong accent positions where none exists). |
| `--snare-threshold F` | 0.85 | Minimum accent strength for snare reaction to activate, 0.0–1.0. Only relevant when `--snare-mode` is `"reinforce"` or `"stab"`. |
| `-o --output PATH` | *(none)* | Output MIDI file path |

**Example: Lock kicks to a guitar riff**

```bash
python -m midi_drums.api/cli riff my_guitar_riff.mp3 \
  --genre metal --style death --bpm 195 \
  --lock-strength 0.8 --snare-mode stab \
  --output riff_locked.mid
```

---

## DAW Integration

### REAPER Integration

The `reaper/create_song_sections.lua` script provides a **bi-directional bridge** between MIDI Drums Generator and REAPER. It communicates with Python via file sidecars — no server or network needed.

#### Installation (One-Time)

1. Open `reaper/create_song_sections.lua` in a text editor.
2. Edit the first configurable line to point to your Python executable:
   ```lua
   local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"
   ```
   Use `pythonw.exe` on Windows to suppress the console window. On Linux/macOS use `python`.
3. In REAPER: **Actions → Load ReaScript →** select `create_song_sections.lua`.
4. Assign a keyboard shortcut for quick access. (Optional: run `reaper/midi_drums_help.lua` as an action to display usage help inside REAPER.)

#### Usage — Four Modes

Each time you run the script, you choose one of four modes via dialogs.

**Mode 1 — REAPER Mode (default)**

You define the section structure in the Lua script's `REAPER_SECTIONS` table at the top of the file, then run the script:

```lua
local REAPER_SECTIONS = {
    {"Intro",  8},
    {"Verse", 16},
    {"Chorus",16},
    {"Bridge", 8},
    {"Outro",  4},
}
```

What happens:
- Timeline regions are created in REAPER from the table.
- A `midi_drums_sections.json` sidecar is written to your project folder.
- You can optionally generate matching drums right now: a dialog prompts for genre, style, mapping, and tempo → a MIDI file (`drums.mid`) is generated (~1–2 s) and auto-imported onto a new track.

To use the sidecar later in Python instead of generating inline:

```python
from midi_drums.api.python_api import DrumGeneratorAPI
api = DrumGeneratorAPI()
song = api.create_song_from_sections_json(
    r"<project_dir>/midi_drums_sections.json",
    genre="metal", style="doom"
)
api.save_as_midi(song, "drums.mid")
```

**Mode 2 — Python Sidecar Mode**

You have already generated a song in Python with an exported sidecar. The Lua script reads the sidecar and creates matching regions:

- Reads `midi_drums_sections.json` (written by `api.save_as_midi_with_sidecar()` or `api.export_sections_json()`).
- Creates REAPER regions matching the structure.
- Offers to sync the project tempo from the sidecar's BPM value.
- Import the MIDI file manually via Media Explorer.

**Mode 3 — AI Agent Mode**

Describe a song in natural language and let the AI compose it:

- Prompts for a text description and tempo.
- Runs `python -m midi_drums prompt "..." --song --write-sidecar`.
- The AI composes the song (~20–45 s).
- Writes `drums.mid` + sidecar → auto-imported on a new track.
- REAPER project tempo is synced to the BPM chosen by the AI.

Requires an API key for the configured provider (see [AI Backend Setup](#ai-backend-setup) above).

**Mode 4 — Song Map Mode (per-section tempo / meter)**

Useful when different sections have different tempos or time signatures:

- Prompts for a song_creator-shaped song-map JSON path and genre/style.
- Runs `python -m midi_drums generate --song-map ... --write-timeline`.
- Reads the flat timeline JSON back from Python (tempo points, regions, color groups).
- Places one `SetTempoTimeSigMarker` per tempo/meter change point in REAPER.
- Creates one colored region per song-map region.
- Imports `drums.mid` on a new track.

#### CLI Alternative: `reaper export`

You can also generate from the command line without opening the Lua script:

```bash
# Full generation + markers (MIDI generated)
python -m midi_drums.api/cli reaper export \
  --genre metal --style doom --tempo 70 \
  --output doom.rpp --midi

# Preset-only mode (markers only, no MIDI — faster)
python -m midi_drums.api/reaper export \
  --genre jazz --style swing --tempo 160 \
  --output jazz.rpp --preset-only

# List genre structure presets
python -m midi_drums.api/cli reaper presets
python -m midi_drums.api/cli reaper presets --genre metal

# Add markers to an existing REAPER project from a MIDI file
python -m midi_drums.api/cli reaper add-markers \
  --song doom.mid --output project.rpp
```

**`reaper export` options**

| Option | Default | Description |
|--------|---------|-------------|
| `--genre GENRE` | *(required)* | Genre |
| `--style STYLE` | `"default"` | Style within genre |
| `--tempo BPM` | Preset default | Tempo (uses genre preset default when omitted) |
| `--output -o PATH` | *(required)* | Output `.rpp` file path |
| `--name NAME` | Auto-generated | Song name |
| `--complexity F` | 0.5 | Complexity, 0.0–1.0 |
| `--humanization F` | 0.3 | Humanization, 0.0–1.0 |
| `--drummer NAME` | *(none)* | Drummer style |
| `--mapping NAME` | *(none)* | MIDI mapping preset (defaults to genre default when omitted) |
| `--template FILE.rpp` | *(none)* | Input REAPER template file to use as a base |
| `--midi [FILE]` | *(none)* | Also export a MIDI file. Auto-generates filename from the `.rpp` name, or specify a custom path |
| `--marker-color HEX` | `"#FF5733"` | Hex color for markers (ignored in `--preset-only` mode) |
| `--preset-only` | Off | Create the `.rpp` with genre-smart structure markers **without** generating any MIDI audio. Faster, does not require the drum plugin system |
| `--list-presets` | Off | List available genre structure presets and exit |

#### CLI Alternative: `reaper add-markers`

Add markers to an existing project from a metadata file or manual structure definition:

```bash
# From a metadata.json file (auto-detected if in the same directory as --song)
python -m midi_drums.api/cli reaper add-markers --song song.mid --output project.rpp

# Manually specify structure
python -m midi_drums.api/cli reaper add-markers \
  --structure "intro:4,verse:8,chorus:8,outro:4" \
  --tempo 120 --time-signature "3/4" \
  --output project.rpp

# Options: --metadata PATH, --song PATH (for auto-detecting metadata),
#          --structure "section:bars,...", --tempo BPM,
#          --time-signature "N/M", --template FILE.rpp,
#          --marker-color HEX
```

### Ardour / Mixbus Integration

The `ardour/create_song_sections.lua` script provides the same bi-directional bridge for **Ardour** and **Mixbus** users. It is a port of the REAPER script with Ardour-specific session handling.

#### Installation (One-Time)

1. Open `ardour/create_song_sections.lua` in a text editor.
2. Edit the first configurable line to point to your Python executable:
   ```lua
   local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"
   ```
   Use `pythonw.exe` on Windows. On Linux/macOS use `python`.
3. In Ardour/Mixbus: **Tools → Scripts → Load Script →** select `create_song_sections.lua`.
4. Assign a keyboard shortcut for quick access.

The script reads the current session folder and writes the sidecar (`midi_drums_sections.json`) and timeline file (`midi_drums_timeline.json`) there.

#### Usage — Four Modes (Same as REAPER)

| Mode | What It Does |
|------|-------------|
| **Ardour Mode** (default) | Creates timeline regions from an `ARDOUR_SECTIONS` table in the Lua script, writes a sidecar, optionally generates MIDI and auto-imports it |
| **Python Sidecar** | Reads an existing `midi_drums_sections.json` written by Python API calls and creates matching regions |
| **AI Agent** | Prompts for a natural-language description, runs the AI generator, creates regions from the AI-composed structure, auto-imports MIDI |
| **Song Map** | Reads a song_creator-shaped song-map JSON, places per-section tempo/meter markers, creates colored regions, imports MIDI |

#### CLI Alternative: `ardour create`

```bash
# Full generation + sidecar (with MIDI)
python -m midi_drums.api/cli ardour create \
  --genre metal --style doom --tempo 70 \
  --output project.ardourproj --midi

# Preset-only mode (markers only, no MIDI)
python -m midi_drums.api/cli ardour create \
  --genre rock --style classic \
  --output project.ardourproj --preset-only

# List genre presets
python -m midi_drums.api/cli ardour create --list-presets
```

**`ardour create` options**

| Option | Default | Description |
|--------|---------|-------------|
| `--genre GENRE` | *(required)* | Genre |
| `--style STYLE` | `"default"` | Style within genre |
| `--tempo BPM` | Preset default | Tempo (uses genre preset default when omitted) |
| `--output -o PATH` | *(required)* | Output Ardour session path (`.ardourproj`) or directory name |
| `--name NAME` | Auto-generated | Song name |
| `--complexity F` | 0.5 | Complexity, 0.0–1.0 |
| `--humanization F` | 0.3 | Humanization, 0.0–1.0 |
| `--drummer NAME` | *(none)* | Drummer style |
| `--mapping NAME` | *(none)* | MIDI mapping preset (defaults to `"gm_drums"` when omitted) |
| `--midi [FILE]` | *(none)* | Also export a MIDI file. Auto-generates filename from the output name, or specify a custom path. Ignored in `--preset-only` mode. |
| `--marker-color HEX` | `"#FF5733"` | Hex color for markers (ignored in `--preset-only`) |
| `--preset-only` | Off | Create the Ardour project with genre-smart structure markers **without** generating MIDI. Faster, does not require the drum plugin system |
| `--write-sidecar JSON` | *(none)* | Write a `midi_drums_sections.json` sidecar at this path (used by the Lua script). When omitted, defaults to `<output_parent>/midi_drums_sections.json`. |
| `--list-presets` | Off | List available genre structure presets and exit. |

---

## Available Genres & Styles

### Metal (7 styles)

| Style | Default Tempo | Description |
|-------|--------------|-------------|
| `heavy` | 140 BPM | Classic heavy metal patterns (Sabbath, Iron Maiden style) |
| `death` | 195 BPM | Blast beats, double bass, intense patterns |
| `power` | 160 BPM | Anthemic, driving patterns with melodic elements |
| `progressive` | 140 BPM | Complex time signatures and syncopation |
| `thrash` | 200 BPM | Fast, aggressive patterns with emphasis on precision |
| `doom` | 70 BPM | Slow, heavy, powerful patterns |
| `breakdown` | 100 BPM | Syncopated patterns for breakdown sections |

### Rock (7 styles)

| Style | Default Tempo | Description |
|-------|--------------|-------------|
| `classic` | 110 BPM | 70s classic rock (Led Zeppelin, Deep Purple) |
| `blues` | 100 BPM | Blues rock with shuffles and triplets |
| `alternative` | 115 BPM | 90s alternative rock syncopation |
| `progressive` | 120 BPM | Complex progressive rock patterns |
| `punk` | 180 BPM | Fast, aggressive punk rock |
| `hard` | 125 BPM | Hard rock with heavy emphasis |
| `pop` | 110 BPM | Pop rock with clean patterns |

### Jazz (7 styles)

| Style | Default Tempo | Description |
|-------|--------------|-------------|
| `swing` | 150 BPM | Traditional swing with ride patterns |
| `bebop` | 210 BPM | Fast, complex bebop rhythms |
| `fusion` | 130 BPM | Jazz fusion with electric energy |
| `latin` | 125 BPM | Latin jazz with clave patterns |
| `ballad` | 70 BPM | Soft, brushed ballad patterns |
| `hard_bop` | 200 BPM | Aggressive hard bop rhythms |
| `contemporary` | 140 BPM | Modern contemporary jazz |

### Funk (7 styles)

| Style | Default Tempo | Description |
|-------|--------------|-------------|
| `classic` | 105 BPM | James Brown "the one" emphasis |
| `pfunk` | 100 BPM | Parliament-Funkadelic grooves |
| `shuffle` | 110 BPM | Bernard Purdie shuffle patterns |
| `new_orleans` | 110 BPM | Second line funk patterns |
| `fusion` | 120 BPM | Jazz-funk fusion styles |
| `minimal` | 100 BPM | Stripped-down pocket grooves |
| `heavy` | — | Heavy funk with rock influence (no default tempo) |

### Electronic (4 styles)

| Style | Default Tempo | Description |
|-------|--------------|-------------|
| `house` | 124 BPM | Four-on-the-floor house patterns |
| `techno` | 136 BPM | Driving techno grooves |
| `drum_and_bass` | 174 BPM | Amen-break-inspired breakbeats |
| `dubstep` | 140 BPM | Half-time dubstep wobble patterns |

Run `python -m midi_drums.api.cli list styles --genre <name>` to see the full list for any genre.

---

## Available Drummers

| Drummer | Key Characteristics | Preferred Genres |
|---------|---------------------|-----------------|
| `bonham` | Triplet vocabulary, behind-the-beat timing, heavy kick emphasis | rock, metal, blues |
| `porcaro` | Half-time shuffle mastery, ghost notes, studio precision | funk, jazz, rock |
| `weckl` | Linear playing (no simultaneous limbs), technical precision | jazz, funk, fusion |
| `chambers` | Funk pocket mastery, ghost notes, fast triplet chops | funk, jazz |
| `roeder` | Atmospheric sludge, sparse minimal approach, crushing weight | metal (doom) |
| `dee` | Speed and precision, twisted displaced backbeats | rock, metal |
| `hoglan` | Mechanical precision, blast beats, extreme consistency | metal |
| `peart` | Extreme timing precision, linear limb independence, polyrhythmic fills | rock, progressive, metal |
| `rich` | Virtuosic single-stroke speed, full-kit fills | rock, jazz |
| `carey` | Polyrhythmic quintuplets, deep tom cascades, ethnic percussion textures | rock, progressive, metal |
| `copeland` | Off-beat hi-hat emphasis, cross-stick snare, displaced accents | funk, jazz, rock |
| `chadsmith` | Pocket groove, syncopated kick patterns, behind-the-beat feel | funk, rock |
| `haake` | Polyrhythmic layering, machine-like precision, odd-time adaptation | metal (progressive/djent) |
| `halpern` | Odd time signatures, polyrhythmic fills, technical precision | metal (progressive), funk |
| `moon` | Crash-heavy chaos, tom fills on every chord, loose timing | rock |
| `watts` | Minimalist swing/shuffle feel, sparse hits, elegant simplicity | jazz |

**Composite Drummer:**

| Drummer | Key Characteristics | Preferred Genres |
|---------|---------------------|-----------------|
| `composite_doom_blues` | Layered Roeder → Porcaro → Chambers styles for doom/blues fusion | metal, rock, blues |

Run `python -m midi_drums.api/cli list drummers` to see the full list.

---

## MIDI Mapping Presets

The `--mapping` / `--vst` flag selects which instrument-to-MIDI-note mapping is used. Run `python -m midi_drums.api/cli list mappings` for the current full list. Available presets:

| Preset | Description | Notes |
|--------|-------------|-------|
| `gm_drums` **(default)** | General MIDI standard drum mapping | Universally compatible; extended instruments fall back to their enum defaults |
| `ezdrummer3` | EZDrummer 3 keymap | ~25 custom mappings including extended hi-hats, tom edges, crash chokes |
| `addictive_drums` / `addictive_drums_2` | Addictive Drums 2 vendor-documented keymap | **~40 custom mappings** — brush sweeps (A–F), tight HH zones, crash variants, flexi triggers. Most extensive mapping available. Source: XLN Audio "Addictive Drums 2 Keymap" PDF (June 2021). |
| `bfd3` | BFD3 (FXpansion) compatible | Uses GM baseline for compatibility |
| `studio_drummer3` / `studio_drummer_3` | Studio Drummer 3 (Native Instruments) compatible | Uses GM baseline for compatibility |
| `modo_drums` | MODO Drums (IK Multimedia) compatible | Uses GM baseline for compatibility |
| `ml_drums` | ML Drums (ML Sound Lab) compatible | Uses GM baseline for compatibility |
| `metal` | Metal-optimized kit | Velocity ranges tuned for heavy music; same note mapping as default |
| `jazz` | Jazz-optimized kit | Velocity ranges tuned for jazz; same note mapping as default |

To use a custom mapping, create a JSON file with the following shape and pass it via `--mapping-file`:

```json
{
    "name": "My Kit",
    "channel": 9,
    "mappings": {
        "KICK": 36,
        "SNARE": 38,
        "CLOSED_HH": 42
    }
}
```

Instruments not listed in `"mappings"` fall back to their `DrumInstrument` enum default values.
