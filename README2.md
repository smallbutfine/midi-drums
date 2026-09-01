# MIDI Drums — User Guide

Chameleon Drummer is a Python system for generating realistic MIDI drum tracks. It covers **5 genres**, **32 styles**, and **17 drummer personalities** with genre-aware default tempos, humanization, pattern templates, natural-language AI generation, Additive Drums 2 (AD2) keymap support, and direct REAPER + Ardour DAW integration.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
  - [Top-Level Flags (No Subcommand)](#top-level-flags-no-subcommand)
  - [generate — Full Song](#generate--full-song)
  - [pattern — Single Pattern](#pattern--single-pattern)
  - [prompt — AI Generation](#prompt--ai-generation)
  - [riff — Riff-Locked Beats](#riff--riff-locked-beats)
  - [list — Browse Options](#list--browse-options)
  - [info — System Status](#info--system-status)
- [MIDI Mappings](#midi-mappings)
- [Genres, Styles & Default Tempos](#genres-styles--default-tempos)
- [Drummer Personalities](#drummer-personalities)
- [REAPER Integration](#reaper-integration)
- [Ardour / Mixbus Integration](#ardour--mixbus-integration)
- [AI Setup](#ai-setup)
- [File Layout (Generated Output)](#file-layout-generated-output)

---

## Installation

The project uses `uv` for dependency management.

```bash
# Install uv if you don't have it
# https://docs.astral.sh/uv/getting-started/installation/

# Create virtualenv and install core deps
uv sync

# (Optional) AI features — large extras group
uv sync --group ai

# (Optional) Riff-lock audio analysis
uv sync --group rfi
```

**Core dependency:** `midiutil` is listed in `core_requirements.in` but **the codebase no longer uses it**. MIDI export uses the [`mido`](https://mido.github.io/) library (`import mido` inside `midi_drums/export/midi/engine.py`). Install mido if you plan to generate MIDI manually:

```bash
pip install mido
```

---

## Quick Start

Generate a complete rock song with defaults — no subcommand needed:

```bash
python -m midi_drums --song --tempo 140
# → saves "rock_classic.mid" in the current directory
```

Or generate a metal song via the `generate` subcommand:

```bash
python -m midi_drums generate --genre metal --style death --tempo 195 --output song.mid
```

---

## CLI Reference

### Top-Level Flags (No Subcommand)

Run these flags **without** any subcommand to generate a quick song using the default genre (`rock`) and style (`classic`):

| Flag | Default | Description |
|------|---------|-------------|
| `--song` | (off) | Enable full-song generation |
| `--genre` | `rock` | Genre override (only meaningful with `--song`) |
| `--style` | `classic` | Style override (only meaningful with `--song`) |
| `--tempo` | *(none)* | BPM. Omit to use genre-aware default |
| `-o, --output` | auto | Output MIDI filename |
| `--name` | *(none)* | Song name (shown in metadata) |
| `--complexity` | `0.5` | Pattern complexity 0.0–1.0 |
| `--humanization` | `0.3` | Human feel 0.0–1.0 |
| `--drummer` | *(none)* | Drummer personality (see below) |
| `--mapping` / `--vst` | `gm_drums` | MIDI note mapping preset (see [Mappings](#midi-mappings)) |
| `--mapping-file` | *(none)* | Path to a custom JSON mapping file (overrides `--mapping`) |

**Example:**

```bash
python -m midi_drums --song --genre metal --style doom --tempo 70 -o doom.mid
```

### `generate` — Full Song

Generates a multi-section song based on genre defaults and saves it as MIDI. The `--output` flag is **required**.

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--genre` | **Yes** | — | Genre name (metal, rock, jazz, funk) |
| `--style` | No | `default` | Style name; use `default` to pick genre-style default structure |
| `--tempo` | No | genre-aware or 120 | BPM |
| `-o, --output` | **Yes** | — | Output `.mid` path |
| `--name` | No | — | Song name |
| `--complexity` | No | `0.5` | Complexity 0.0–1.0 |
| `--humanization` | No | `0.3` | Human feel 0.0–1.0 |
| `--drummer` | No | — | Drummer personality |
| `--sidecar` | No | — | Path to a `midi_drums_sections.json` file. Overrides the genre's default song structure. The sidecar tempo is used unless `--tempo` is also given. |
| `--song-map` | No | — | Path to a song-map JSON (regions → segments with per-segment tempo/meter). Takes precedence over `--sidecar`. |
| `--write-timeline` | No | — | Write a flat timeline JSON after generation. Best used with `--song-map`. |

**Examples:**

```bash
# Standard generation — uses genre/style default structure
python -m midi_drums generate --genre rock --style classic -o song.mid

# Use a REAPER-produced sidecar for custom structure
python -m midi_drums generate --genre metal --sidecar midi_drums_sections.json -o song.mid

# Song-map mode — per-segment tempo/meter
python -m midi_drums generate --genre metal --song-map map.json --write-timeline timeline.json -o song.mid
```

### `pattern` — Single Pattern

Generates a single 4-bar pattern.

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--genre` | **Yes** | — | Genre name |
| `--section` | No | `verse` | Section type (verse, chorus, bridge, etc.) |
| `--style` | No | `default` | Style within genre |
| `--bars` | No | `4` | Number of bars |
| `--tempo` | No | `120` | BPM |
| `-o, --output` | **Yes** | — | Output `.mid` path |
| `--complexity` | No | `0.5` | Complexity 0.0–1.0 |
| `--mapping` / `--vst` | No | `gm_drums` | MIDI mapping preset |
| `--mapping-file` | No | — | Custom JSON mapping file path |

**Example:**

```bash
python -m midi_drums pattern --genre jazz --section bridge --style fusion --tempo 160 -o bridge.mid
```

### `prompt` — AI Generation

Generates drums from a natural-language description using an LLM backend.

| Flag | Default | Description |
|------|---------|-------------|
| `text` | *(optional)* | Natural-language prompt (in quotes). Omit for a simple groove. |
| `-o, --output` | auto | Output MIDI path |
| `--tempo` | `120` | Target BPM |
| `--section` | `verse` | Section type |
| `--bars` | `4` | Number of bars |
| `--complexity` | `0.5` | Complexity 0.0–1.0 |
| `--drummer` | *(none)* | Drummer personality |
| `--song` | off | Compose a full multi-section song via agent (default: single pattern) |
| `--rpp FILE.rpp` | none | Also create a REAPER project with markers and tempo/meter |
| `--ardour DIR` | none | Create an Ardour session dir with sidecar + MIDI |
| `--save-metadata` | off | Save a `metadata.json` alongside the output |
| `--write-sidecar JSON` | none | Write a `midi_drums_sections.json` sidecar for REAPER Lua integration |
| `--mapping` | `gm_drums` | MIDI mapping preset. Use `addictive_drums` for AD2 native keymap. |

**Examples:**

```bash
# Single pattern from text
python -m midi_drums prompt "funky groove with ghost notes and syncopation" -o funky.mid

# Full AI-composed song → REAPER project + MIDI
python -m midi_drums prompt "aggressive death metal breakdown" --song --rpp doom.rpp -o doom.mid

# AI single pattern → Ardour session dir
python -m midi_drums prompt "jazzy swing with brush snare" --ardour ardour_output/ -o swing.mid
```

### `riff` — Riff-Locked Beats

Analyzes an audio riff and generates drums that lock to its onsets. Requires the `rfi` extras group (`uv sync --group rfi`).

| Flag | Default | Description |
|------|---------|-------------|
| `audio_path` | **positional** | Path to WAV/MP3 audio riff |
| `--genre` | `rock` | Base genre for the pattern template |
| `--style` | `classic` | Base style within genre |
| `--drummer` | *(none)* | Drummer personality |
| `--bpm` | `120` | Estimated BPM of the source riff |
| `--section` | `verse` | Section type |
| `--bars` | `4` | Number of bars |
| `--grid` | `16th` | Beat grid resolution |
| `--lock-strength` | `1.0` | How tightly kicks lock to riff onsets (0.0–1.0) |
| `--mapping` | *(none)* | MIDI mapping preset |
| `--snare-mode` | `off` | One of: `off`, `reinforce`, `stab` |
| `--snare-threshold` | `0.85` | Min accent threshold for snare reaction |
| `--offset-beats` | `0` | Beat offset for alignment |
| `--audio-offset` | `0` | Audio start offset (seconds) |
| `--audio-duration` | *(none)* | Max audio length to analyze |
| `-o, --output` | `riff_output.mid` | Output path |

**Example:**

```bash
python -m midi_drums riff guitar_riff.wav --genre metal --bpm 140 --lock-strength 0.85 -o locked.mid
```

### `list` — Browse Options

| Subcommand | Required Flag | Description |
|------------|--------------|-------------|
| `list genres` | — | List all 5 available genres |
| `list drummers` | — | List all 17 drummer personalities |
| `list styles --genre <name>` | `--genre` | List styles within a genre |
| `list mappings` | — | List all 9 MIDI mapping presets + descriptions |

**Examples:**

```bash
python -m midi_drums list genres
python -m midi_drums list drummers
python -m midi_drums list styles --genre metal
python -m midi_drums list mappings
```

### `info` — System Status

Prints a summary of available genres, drummers, plugin status, and style counts.

```bash
python -m midi_drums info
```

---

## MIDI Mappings

The default mapping is **`gm_drums`** (General MIDI Standard). This ensures compatibility with any GM-compliant sampler or VST.

| Preset | Description | Mapped Instruments |
|--------|-------------|-------------------|
| `gm_drums` / `gm` / `general_midi` | **Default.** GM Level 1 standard notes. Broadest compatibility. | 12 core instruments (kick, snare, rim, HH closed/open/pedal, mid/floor tom, crash, ride, ride bell, splash, china) |
| `ezdrummer3` / `ez_drummer_3` | EZDrummer 3 keymap with extended hi-hat and cymbal choke variants. | ~30+ instruments including tight HH, crash choked A-D, tom edges, closed/hh tip |
| `addictive_drums` / `addictive_drums_2` | **AD2 native keymap.** Most extensive mapping (~40 entries) from XLN Audio's vendor PDF. Covers core drums, brush sweeps (6 zones), rim/shot, tight HH (5 velocity-tunable zones), crash chokes, tom edges, extended cymbals. | ~40+ instruments — full AD2 zone coverage |
| `bfd3` | BFD3 preset (uses GM baseline). | 12 core instruments |
| `studio_drummer3` / `studio_drummer_3` | Studio Drummer 3 preset (uses GM baseline). | 12 core instruments |
| `modo_drums` | MODO Drums preset (uses GM baseline). | 12 core instruments |
| `ml_drums` | ML Drums preset (uses GM baseline). | 12 core instruments |
| `metal` | Metal-optimized velocity ranges (powerful kicks/snares, loud crashes). | 12 core instruments with custom velocity ranges |
| `jazz` | Jazz-optimized velocity ranges (softer kicks, dynamic snares, subtle HH). | 12 core instruments with custom velocity ranges |

To use a custom mapping file:

```bash
python -m midi_drums generate --genre rock --mapping-file my_kit.json -o song.mid
```

---

## Genres, Styles & Default Tempos

Each genre/style combo has a research-based default tempo. Omit `--tempo` to use it.

### Metal (7 styles)

| Style | Default BPM | Description |
|-------|-------------|-------------|
| `heavy` | 140 | Classic heavy metal (Sabbath, Iron Maiden style) |
| `death` | 195 | Blast beats, double bass, intense patterns |
| `power` | 160 | Anthemic, driving patterns with melodic elements |
| `progressive` | 140 | Complex time signatures and syncopation |
| `thrash` | 200 | Fast, aggressive patterns with precision emphasis |
| `doom` | 70 | Slow, heavy, powerful patterns |
| `breakdown` | 100 | Syncopated patterns for breakdown sections |

### Rock (7 styles)

| Style | Default BPM | Description |
|-------|-------------|-------------|
| `classic` | 110 | 70s classic rock (Led Zeppelin, Deep Purple) |
| `blues` | 100 | Blues rock with shuffles and triplets |
| `alternative` | 115 | 90s alternative rock syncopation |
| `progressive` | 120 | Complex progressive rock patterns |
| `punk` | 180 | Fast, aggressive punk rock |
| `hard` | 125 | Hard rock with heavy emphasis |
| `pop` | 110 | Pop rock with clean patterns |

### Jazz (7 styles)

| Style | Default BPM | Description |
|-------|-------------|-------------|
| `swing` | 150 | Traditional swing with ride patterns |
| `bebop` | 210 | Fast, complex bebop rhythms |
| `fusion` | 130 | Jazz fusion with electric energy |
| `latin` | 125 | Latin jazz with clave patterns |
| `ballad` | 70 | Soft, brushed ballad patterns |
| `hard_bop` | 200 | Aggressive hard bop rhythms |
| `contemporary` | 140 | Modern contemporary jazz |

### Funk (7 styles)

| Style | Default BPM | Description |
|-------|-------------|-------------|
| `classic` | 105 | James Brown "the one" emphasis |
| `pfunk` | 100 | Parliament-Funkadelic grooves |
| `shuffle` | 110 | Bernard Purdie shuffle patterns |
| `new_orleans` | 110 | Second line funk patterns |
| `fusion` | 120 | Jazz-funk fusion styles |
| `minimal` | 100 | Stripped-down pocket grooves |
| `heavy` | — (uses pattern default) | Heavy funk with rock influence |

### Electronic (4 styles)

| Style | Default BPM | Description |
|-------|-------------|-------------|
| `house` | 124 | Four-on-the-floor house groove |
| `techno` | 136 | Driving techno beat |
| `drum_and_bass` | 174 | Breakbeat-driven D&B |
| `dubstep` | 140 | Half-time dubstep groove |

---

## Drummer Personalities

**17 total:** 16 named drummers + 1 composite. Each modifies the base pattern with characteristic timing, velocity, and textural traits.

| ID | Drummer | Style Description | Preferred Genres |
|----|---------|-------------------|-----------------|
| `bonham` | John Bonham | Triplet vocabulary, behind-the-beat timing, heavy kick emphasis, dramatic dynamic contrast | rock, metal, blues, hard_rock |
| `chambers` | Dennis Chambers | Funk mastery, ghost notes, pocket stretching, fast triplet chops, laid-back feel | funk, jazz, fusion, rock, r&b |
| `porcaro` | Jeff Porcaro | Half-time shuffle (Rosanna), ghost notes, studio precision | rock, pop, blues, funk, jazz |
| `weckl` | Dave Weckl | Linear playing (no simultaneous limbs), ghost notes, sophisticated coordination | jazz, fusion, funk, rock |
| `carey` | Danny Carey | Polyrhythmic quintuplets, deep tom cascades, odd meters, electronic pad textures | metal, rock, progressive, alternative, hard_rock, post_metal, psychedelic |
| `roeder` | Jason Roeder | Atmospheric sludge, minimal sparse cymbal work, crushing accents | metal, sludge, post_metal, doom, atmospheric |
| `dee` | Mikkey Dee | Speed and precision, twisted backbeats, Motorhead/King Diamond style | metal, speed_metal, punk, hard_rock, horror_metal |
| `hoglan` | Gene Hoglan | Mechanical precision, blast beats, extreme metal power, machine-like quantization | metal, death, thrash, progressive |
| `peart` | Neil Peart | Extreme timing precision, linear limb independence, polyrhythmic fills | rock, progressive, metal |
| `rich` | Buddy Rich | Virtuosic single-stroke speed, dramatic dynamic contrast (ghost → thunder), fast triplet chops | jazz, rock |
| `copeland` | Stewart Copeland | Reggae/ska off-beat HH, displaced accents, cross-stick snare fills | rock, funk |
| `chadsmith` | Chad Smith | Funk-rock fusion, heavy ghost notes, behind-the-beat pocket, syncopated kick patterns | *(see code)* |
| `haake` | Thomas Haake | Polyrhythmic layering (7-over-5-over-4), mechanical precision, sparse devastating hits | metal, progressive, djent, experimental |
| `halpern` | Matt Halpern | Odd time signatures (7/8, 11/8) in grooves, dense polyrhythmic fills, atmospheric builds | metal, progressive, djent, experimental |
| `moon` | Keith Moon | Explosive tom fills, crash bombardment on every chord, loose behind-the-beat timing, chaotic energy | rock, punk, hard_rock |
| `watts` | Charlie Watts | Jazz-trained timekeeping, behind-the-beat swing, minimalist sparse hits, subtle ghost notes | blues, rock, jazz |
| `composite_doom_blues` | DoomBlues Composite | Layered combination of Roeder + Porcaro + Chambers techniques (minimal sludge × shuffle pocket × funk depth) | *(see code)* |

**Note:** The drummer plugins are auto-discovered via the plugin registry. Use `python -m midi_drums list drummers` to get the live, discovered list from your installation.

---

## REAPER Integration

### Setup

1. Copy `reaper/create_song_sections.lua` and `reaper/midi_drums_help.lua` into your REAPER `Scripts/` folder.
2. Open `create_song_sections.lua` in a text editor and set `PYTHON_EXE` to point at your virtualenv's Python (use `pythonw.exe` on Windows to suppress the console window).

```lua
local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"
```

3. Assign a keyboard shortcut in REAPER → load the script.

### Four Modes (chosen via dialog each run)

| Mode | Trigger | What it does |
|------|---------|-------------|
| **REAPER** (default) | Press YES at first dialog | Uses `REAPER_SECTIONS` table to create timeline regions, writes `midi_drums_sections.json` sidecar, optionally generates a drum track via Python template engine (~1–2 s, no AI key needed). |
| **Python sidecar** | NO → type "sidecar" | Reads an existing `midi_drums_sections.json` (from Python's `save_as_midi_with_sidecar()`), creates matching regions, offers to sync project tempo. Import the MIDI file manually via Media Explorer. |
| **AI agent** | NO → type "ai" | Prompts for a natural-language description + BPM, calls `midi_drums prompt --song`, AI composes a full song (~20–45 s), creates regions from AI-chosen structure, auto-imports MIDI onto a new track. Requires an AI API key in `.env`. |
| **Song-map** | NO → type "songmap" | Prompts for a song_creator-shaped JSON path + genre/style, calls `midi_drums generate --song-map`, reads back the flat timeline JSON, places per-section tempo/meter time-sig markers and colored regions, auto-imports MIDI. |

### CLI Side of REAPER Integration

```bash
# Full generation: create REAPER project with markers AND export MIDI
python -m midi_drums reaper export --genre metal --style doom --tempo 70 -o project.rpp --midi

# Preset-only mode: create .rpp with genre-smart markers, no MIDI (fastest)
python -m midi_drums reaper export --genre jazz --style swing --tempo 160 -o jazz.rpp --preset-only

# Add markers to an existing Reaper project from metadata or manual structure
python -m midi_drums reaper add-markers --song song.mid --output project.rpp
# Or provide structure inline:
python -m midi_drums reaper add-markers --structure "intro:4,verse:8,chorus:8,outro:4" --tempo 120 -o project.rpp

# List available genre structure presets
python -m midi_drums reaper presets --genre metal
```

### Sidecar File Format (`midi_drums_sections.json`)

Written by the Lua script or Python API. Consumed by both tools for synchronization:

```json
{
  "source": "reaper",
  "tempo": 70,
  "time_signature": [4, 4],
  "sections": [
    {"name": "Intro",  "bars": 8},
    {"name": "Verse",  "bars": 16},
    {"name": "Chorus", "bars": 8}
  ]
}
```

### REAPER Help Script

Run `reaper/midi_drums_help.lua` (as a REAPER action) at any time to display usage instructions inside the REAPER Console.

---

## Ardour / Mixbus Integration

### Setup

1. Copy `ardour/create_song_sections.lua` and `ardour/midi_drums_help.lua` into your Ardour/Mixbus `Scripts/` folder.
2. Open `create_song_sections.lua` in a text editor and set `PYTHON_EXE`.

```lua
local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"
```

3. Tools → Scripts → Load Script in Ardour/Mixbus. Assign a shortcut.

### Four Modes (same structure as REAPER)

| Mode | Trigger | What it does |
|------|---------|-------------|
| **Ardour** (default) | Press YES at first dialog | Uses `ARDOUR_SECTIONS` table to create timeline regions, writes `midi_drums_sections.json` sidecar to the session folder, optionally generates a drum track via Python. |
| **Python sidecar** | NO → "sidecar" | Reads existing sidecar, creates matching regions, syncs project tempo. |
| **AI agent** | NO → "ai" | Same as REAPER AI mode — natural-language prompt, full song composition. |
| **Song-map** | NO → "songmap" | Same as REAPER song-map mode — per-section tempo/meter markers. |

### CLI for Ardour

```bash
# Full generation: create Ardour session dir with markers + sidecar + MIDI
python -m midi_drums ardour create --genre metal --style doom --tempo 70 -o ardour_output/ --midi

# Preset-only (markers only, no MIDI generated — fastest)
python -m midi_drums ardour create --genre rock --style classic --output ardour_output/ --preset-only

# List available genre structure presets from Ardour
python -m midi_drums ardour create --list-presets
```

**Note:** The `--output` path for Ardour is a **session directory**, not a `.ardourproj` file. The script will create the session structure inside it.

---

## AI Setup

Install extras: `uv sync --group ai`

The default provider is **Anthropic (Claude Sonnet 5)**. Set environment variables in a `.env` file at the project root or in your shell:

```bash
# Provider selection (default: anthropic)
AI_PROVIDER=anthropic          # or openai, groq, cohere, ollama

# API key for your provider
ANTHROPIC_API_KEY=sk-ant-...
# OR  OPENAI_API_KEY=sk-proj-...
# OR  GROQ_API_KEY=gsk_...
# OR  COHERE_API_KEY=...
# OLLAMA has no API key — it runs locally

# Optional tuning
AI_MODEL=claude-sonnet-5       # Default per provider: see table below
AI_TEMPERATURE=0.7             # Range: 0.0 – 2.0
AI_MAX_TOKENS=4096
```

### Provider → Model Defaults

| Provider | Default Model | API Key Env Var | Notes |
|----------|--------------|-----------------|-------|
| `anthropic` | `claude-sonnet-5` | `ANTHROPIC_API_KEY` | Cloud-based, highest quality |
| `openai` | `gpt-4o` | `OPENAI_API_KEY` | Cloud-based |
| `groq` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | Fastest inference (cloud) |
| `cohere` | `command-r-plus` | `COHERE_API_KEY` | Cloud-based |
| `ollama` | `qwen3.6` | *(none)* | Runs locally on `127.0.0.1:11434` |

---

## File Layout (Generated Output)

### Standard CLI (`--output song.mid`)

```
song.mid                          ← Single MIDI file with full song patterns
```

### AI `prompt --save-metadata` (organized layout)

```
output/
  <slug>/                         ← slug derived from prompt or --output name
    <slug>.mid                    ← Generated MIDI
    metadata.json                 ← Metadata (prompt, provider, tempo, structure)
    parts/                        ← Per-section MIDI files (--song only)
      00_intro.mid
      01_verse.mid
      02_chorus.mid
      ...
```

### AI `--rpp` or `--ardour` (DAW integration)

The generated `.mid` file is placed alongside the sidecar or in the output directory. The REAPER project (`.rpp`) or Ardour session dir contains markers/regions aligned to the generated structure.

---

## Pattern Templates

Internally, genre plugins compose patterns from **10 reusable templates**: BasicGroove, DoubleBassPedal, BlastBeat, SteadyRidePattern, JazzRidePattern, FunkGhostNotes, CrashAccents, TomFill, BrushGroove, and RimshotGroove. These are not exposed as CLI flags — they drive all genre/style generation automatically based on the selected genre and style.

## Drummer Modifications

Each drummer personality uses **17 `DrummerModification` classes** internally (BehindBeatTiming, TripletVocabulary, GhostNoteLayer, LinearCoordination, HeavyAccents, ShuffleFeelApplication, FastChopsTriplets, PocketStretching, MinimalCreativity, SpeedPrecision, TwistedAccents, MechanicalPrecision, PolyrhythmApplication, OddTimeAdaptation, plus 2 riff-lock transforms) to reshape the base pattern. You do not configure individual modifications — just select a drummer ID and all their traits are applied automatically.
