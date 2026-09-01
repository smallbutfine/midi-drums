# Codebase Analysis — midi-drums

> Functional analysis of the Chameleon Drummer MIDI generation system, based on direct code inspection only. No documentation was consulted.

---

## What This Codebase Does

Chameleon Drummer generates instrumentally-accurate MIDI drum files for **5 genres** across **32 styles**, rendered as `.mid` files. It takes high-level prompts like "death metal verse with Hoglan style" and produces a DAW-ready MIDI file using configurable drum kit mappings (GM, EZDrummer 3, Addictive Drums 2, BFD3, MODO Drums, Studio Drummer 3, ML Drums). The **default** mapping preset is `"gm_drums"`.

---

## Architecture: How Generation Works

### Entry Points

1. **`DrumGeneratorAPI`** (high-level API in `api/python_api.py`) — simplified interface for typical use
2. **`DrumGenerator`** (engine in `generation/engines/drum_generator.py`) — full control, both V1 and V2 engines
3. **CLI** (`api/cli.py`) — command-line access with subcommands: `generate`, `pattern`, `list`, `prompt`, `reaper`, `ardour`

### Generation Pipeline

1. **Plugin discovery** scans `plugins/genres/` and `plugins/drummers/` via `pkgutil`, instantiates anything subclassing `GenrePlugin` or `DrummerPlugin`, registers them in `PluginRegistry`.

2. **Song creation** flows through two engines:
   - **V1 (legacy)**: generates one pattern per section, repeats for N bars with velocity jitter (`DrumGenerator._extend_pattern_to_bars()`).
   - **V2 (default/composer)**: `ComposerV2` iterates bar-by-bar, using `MacroComposer` to assign phase context (establish/maintain/build/turnaround), selecting from genre-specific groove libraries (`get_section_grooves()`).

3. **Drummer styling** applies 2–4 composable `DrummerModification` objects per drummer. Each modification is a pure function returning a new pattern:
   ```python
   styled = self.behind_beat.apply(pattern, intensity=0.7)
   styled = self.triplets.apply(styled, intensity=0.8)
   ```

4. **BarSelector** modulates velocity per bar using intensity curves and drummer-specific seeding. Enforces a minimum velocity floor for kick/snare.

5. **Export** writes SMF Format 0 MIDI files via `mido`. The MIDI engine (`export/midi/engine.py`) creates `mido.Message` and `mido.MidiFile` objects directly, using 960 ticks per beat.

### Default Kit & Mapping Configuration

- **Default mapping preset**: `"gm_drums"` (from `config/defaults.py:DEFAULT_MAPPING`)
- **CLI default mapping**: `"gm_drums"` (`api/cli.py` — all commands use DEFAULT_MAPPING)
- **`DrumGenerator` internal default**: `DrumKit.create_ezdrummer3_kit()` when no explicit drum_kit is passed
- **`DrumGeneratorAPI.create_song(mapping=...)`** resolves its mapping parameter to a DrumKit via `DrumKit.from_preset(mapping)`, defaulting to `"gm_drums"`

When `DrumGeneratorAPI` is used (the typical entry point), the output uses GM. When raw `DrumGenerator` or `MIDIEngine` are used without specifying a drum_kit, the internal MIDI engine defaults to EZD3 kit. These two paths diverge on which preset gets applied — the high-level API defaults to GM, the low-level engine defaults to EZD3.

---

## Kit Mapping Coverage (Verified)

| Preset | Custom Mappings Count | Extended Instruments | Notes |
|--------|----------------------|---------------------|-------|
| **Addictive Drums 2** (`addictive_drums`) | **~40 entries** (`_AD2_FULL_MAP`) | Brush sweeps (A–F), rim variants, tight HH, extended open HH, tom edges, crash chokes | Vendor-documented from XLN Audio keymap PDF. Not all 50+ enum members are mapped — unmapped ones fall back to their enum defaults. |
| **EZDrummer 3** (`ezdrummer3`) | **~25 entries** (`create_ezdrummer3_kit()`) | Extended HH (open variants, tight HH), tom edges, crash chokes | Core drums on GM notes; EZD3 auto-detects mapping. Comment claims "all 35 AD2-zone instruments" but actual code has fewer. |
| **GM Baseline** (`gm_drums`) | **13 entries** (`_GM_BASELINE`) + **16 hi-hat collapses** (`_GM_HIHAT_COLLAPSE`) | None — extended/articulated instruments fall back to enum defaults (safe but unmapped) | GM-compliant; extended hi-hats collapsed to closed/open HH equivalents. |
| **Metal Kit** (`metal`) | 0 custom mappings | Velocity ranges only (no note mapping changes) | Default kit name is "Standard Kit"; velocity tuned for heavy music. |
| **Jazz Kit** (`jazz`) | 0 custom mappings | Velocity ranges only | Default kit name is "Standard Kit"; softer velocity ranges. |
| Other presets (bfd3, studio_drummer3, modo_drums, ml_drums) | `_GM_BASELINE` + `_GM_HIHAT_COLLAPSE` | None | All use GM baseline for safety. |

**Addictive Drums 2 has the most extensive mapping by far** — 40 custom mappings covering brush sweeps, rim variants, tight HH zones, extended open HH positions, tom edges, and crash chokes, sourced from XLN Audio's vendor-documented keymap PDF.

---

## Plugin System

### Genre Plugins (5 total, 32 styles)

| Genre | Styles (count) | DEFAULT_TEMPO_MAP entries |
|-------|---------------|---------------------------|
| `metal` | heavy, death, power, progressive, thrash, doom, breakdown | 7 |
| `rock` | classic, blues, alternative, progressive, punk, hard, pop | 7 |
| `jazz` | swing, bebop, fusion, latin, ballad, hard_bop, contemporary | 7 |
| `funk` | classic, pfunk, shuffle, new_orleans, fusion, minimal, heavy | 7 |
| `electronic` | house, techno, drum_and_bass, dubstep | 4 |

### Drummer Plugins (17 total: 16 named + 1 composite)

| # | Plugin | Lines | Core Modifications Used |
|---|--------|-------|------------------------|
| 1 | BonhamPlugin | ~291 | BehindBeatTiming, TripletVocabulary, HeavyAccents |
| 2 | CareyPlugin | ~586 | PolyrhythmApplication, FastChopsTriplets, SpeedPrecision |
| 3 | ChambersPlugin | ~340 | GhostNoteLayer, PocketStretching, ShuffleFeelApplication |
| 4 | CopelandPlugin | ~325 | TwistedAccents, LinearCoordination, MinimalCreativity |
| 5 | DeePlugin | ~304 | SpeedPrecision, TwistedAccents |
| 6 | HaakePlugin | ~395 | PolyrhythmApplication, MechanicalPrecision, OddTimeAdaptation |
| 7 | HalpernPlugin | ~442 | PolyrhythmApplication, OddTimeAdaptation, SpeedPrecision |
| 8 | HoglanPlugin | ~307 | MechanicalPrecision, HeavyAccents, FastChopsTriplets |
| 9 | MoonPlugin | ~547 | TwistedAccents, BehindBeatTiming, HeavyAccents |
| 10 | PeartPlugin | ~280 | LinearCoordination, SpeedPrecision, TripletVocabulary |
| 11 | PorcaroPlugin | ~340 | ShuffleFeelApplication, GhostNoteLayer, PocketStretching |
| 12 | RichPlugin | ~302 | FastChopsTriplets, HeavyAccents, SpeedPrecision |
| 13 | RoederPlugin | ~298 | MinimalCreativity, HeavyAccents, SpeedPrecision |
| 14 | SmithPlugin | ~515 | BehindBeatTiming, GhostNoteLayer, PocketStretching |
| 15 | WattsPlugin | ~392 | BehindBeatTiming, ShuffleFeelApplication, GhostNoteLayer |
| 16 | WecklPlugin | ~360 | LinearCoordination, SpeedPrecision, PocketStretching |
| 17 | CompositeDoomBluesPlugin | ~114 | Layers Roeder → Porcaro → Chambers sequentially with auto-validation/fix |

---

## Core Domain Models

### Value Objects
- **`DrumInstrument`** — enum with **50+ members** covering core drums (GM notes), extended hi-hats (AD2/EZD3 zones), tom edges, crash chokes, ride variants, brush sweeps, flexi triggers. Comment in source: "All MIDI values taken from the AD2 keymap PDF (Addictive Drums 2 Keymap.pdf)"
- **`TimeSignature`** — numerator/denominator dataclass with validation (denominator must be power of 2)
- **`GenerationParameters`** — controls complexity, dynamics, humanization, fill_frequency, swing_ratio, ride_threshold, and genre context blending
- **`RiffAccent`** / **`RiffAccentMap`** — frozen dataclasses for audio-onset-derived accent positions (used by riff-lock feature)

### Domain Models
- **`Beat`** — position/instrument/velocity/duration with ghost_note/accent flags. Contains `instrument_promoted: bool` to distinguish promoted timekeeping cymbals from genuinely-placed ones
- **`Pattern`** — named collection of beats with subdivision, swing_ratio, metadata. Has `.copy()` and `.humanize()`
- **`SongSegment`** — tempo/time-signature overrides within a section (for mid-section meter/tempo changes)
- **`Section`** — name + pattern + bars + variations + fills + segments + groove_offsets_ms. Validates that segment bars sum to section bars
- **`Song`** — name + tempo + time_signature + sections + metadata

### MIDI Note Resolution Chain

1. `DrumKit.get_midi_note(instrument)` returns `custom_mappings[instrument]` if present, else `instrument.value` (enum default)
2. `MIDIEngine._resolve_note(instrument)` delegates to the engine's `drum_kit.get_midi_note()`
3. Legacy `_mid_note()` fallback in `engine.py` uses a hardcoded `_INSTR_NOTE` dict for non-drum_kit contexts

---

## Pattern Template System (`midi_drums/patterns/`)

10 concrete `PatternTemplate` implementations:
1. **BasicGroove** — kick + snare + hihat with configurable positions/subdivisions
2. **DoubleBassPedal** — continuous/gallop/triplet patterns for metal
3. **BlastBeat** — traditional/hammer/gravity blast beats
4. **SteadyRidePattern** — quarter/eighth ride pulse with velocity variation
5. **JazzRidePattern** — swing ride with accent patterns (standard/elvin/tony)
6. **FunkGhostNotes** — snare ghost notes with "the one" emphasis
7. **CrashAccents** — crash placement with AD2 crash type variants (light/heavy/splash)
8. **TomFill** — descending/ascending/around fills, supports tom edge hits
9. **BrushGroove** — jazz brush sweeps cycling through 6 AD2 presets
10. **RimshotGroove** — funk R&B with rimshots instead of snare

**TemplateComposer** combines multiple templates via fluent API:
```python
TemplateComposer("metal_verse")
    .add(BasicGroove(kick_positions=[0.0, 2.0]))
    .add(DoubleBassPedal(intensity=0.8))
    .add(CrashAccents(positions=[0.0]))
    .build(bars=1, complexity=0.7)
```

---

## Drummer Modifications (`midi_drums/modifications/`)

### Core Modifications (14 in `drummer_mods.py`):
1. **BehindBeatTiming** — delays snare/kick by max_delay_ms (Bonham, Chambers style)
2. **TripletVocabulary** — converts straight-eighth to triplet feel (Bonham style)
3. **GhostNoteLayer** — adds ghost notes on snare between main hits (Porcaro, Chambers)
4. **LinearCoordination** — removes simultaneous limb hits for linear playing (Weckl)
5. **HeavyAccents** — increases dynamic contrast for metal
6. **ShuffleFeelApplication** — converts 16ths to shuffle/swing feel (Porcaro)
7. **FastChopsTriplets** — rapid triplet fills and embellishments (Chambers)
8. **PocketStretching** — subtle timing variations on timekeeping beats (Chambers)
9. **MinimalCreativity** — removes non-essential cymbals for sparse feel (Roeder)
10. **SpeedPrecision** — normalizes velocities/timing for precision (Dee)
11. **TwistedAccents** — displaces accents off-beat (Dee)
12. **MechanicalPrecision** — extreme quantization (Hoglan)
13. **PolyrhythmApplication** — cross-metric patterns (Haake/Meshuggah style)
14. **OddTimeAdaptation** — maps 4/4 onto odd-meter grids (Halpern/Periphery)

### Riff-Lock Modifications (2 in separate files):
15. **RiffLockTransform** (`riff_lock.py`) — locks kick beats to audio-onset positions from `audio_analysis.analyze_onsets()`
16. **SnareAccentReaction** (`snare_accent_reaction.py`) — reinforces/stabs snare at riff accent positions

---

## Generation Engines

### ComposerV2 (bar-by-bar, default)
Located in `generation/composer_v2.py`. Implements the bar-by-bar evolution loop:
```python
for section_name, bars in structure:
    macro_composer = MacroComposer(seed=...)
    grooves = get_section_grooves(genre_plugin, section_name, complexity, style)
    
    for bar_index in range(bars):
        phase = macro_composer.determine_phase(bar_index, bars)  # establish/maintain/build/turnaround
        base_pattern = macro_composer.groove_manager.select_groove(...)
        
        if not base_pattern:
            # Fallback chain: groove library → flavors → generate_pattern() → hardcoded default
            base_pattern = genre_plugin.get_section_flavors(section_name, params)[:6]
            base_pattern = genre_plugin.generate_pattern(section_name, params)  # fallback
        
        drummed_pattern = drummer_plugin.apply_style(base_pattern)
        final_pattern = bar_selector.generate_for_bar(drummed_pattern, bar_index, bars, intensity_pt, drummer_name)
        
        generated_bars.append(final_pattern)
    
    combined = composer._combine_bar_patterns(generated_bars, genre_plugin, params)
```

### DrumGenerator (V1 static, legacy)
Located in `generation/engines/drum_generator.py`. Generates one pattern per section and repeats for all bars.

### GrooveEngine (timing displacement per bar)
Located in `generation/groove_engine.py`. Defines `DrummerGrooveProfile` dataclass per drummer: swing ratio, timing bias (ms), range (ms). Applied as `groove_offsets_ms` on each Section:
- Bonham: swing=0.60, bias=-20ms (behind beat)
- Weckl: swing=0.15, bias=0ms (centered)
- Chambers: swing=0.40, bias=-5ms (slight drag)

---

## REAPER Integration (`export/reaper/`)

### Bidirectional Bridge via `create_song_sections.lua`
The Lua script at `reaper/create_song_sections.lua` communicates with Python via file sidecars + `io.popen` subprocess calls. Four modes:

| Mode | Trigger | Python Command | Regions Source |
|------|---------|---------------|----------------|
| **REAPER** (default) | YES on first dialog | `generate --sidecar` | REAPER regions table |
| **Python sidecar** | NO → "sidecar" | *(none)* | JSON from `export_sections_json()` |
| **AI agent** | NO → "ai" | `prompt --song --write-sidecar` | AI-chosen structure |
| **Song map** | NO → "songmap" | `generate --song-map --write-timeline` | Per-segment tempo/meter JSON |

### Sidecar Format (`midi_drums_sections.json`)
```json
{
  "source": "reaper",
  "tempo": 70,
  "time_signature": [4, 4],
  "sections": [
    {"name": "Intro", "bars": 8, "color": [200, 120, 40]},
    {"name": "Verse", "bars": 16, "color": [180, 40, 40]}
  ]
}
```

### Song Map Format (issue #53)
```json
{
  "title": "Song Name",
  "color_groups": {"groove": [200, 120, 40]},
  "regions": [
    {
      "name": "Verse 1",
      "color_group": "groove",
      "segments": [
        {"bars": 8, "bpm": 144, "num": 4, "denom": 4},
        {"bars": 2, "bpm": 144, "num": 7, "denom": 8}
      ]
    }
  ]
}
```

### Key API Methods for REAPER Integration
- `DrumGeneratorAPI.export_sections_json(song, path)` — serialize song sections to sidecar JSON
- `DrumGeneratorAPI.create_song_from_sections_json(json_path, genre, style)` — read sidecar → generate Song
- `DrumGeneratorAPI.save_as_midi_with_sidecar(song, filename)` — export MIDI + sidecar in one call
- `DrumGeneratorAPI.create_song_from_song_map(song_map, genre, style)` — read song-map JSON (per-segment tempo/meter) → generate Song with `SongSegment` overrides
- `DrumGeneratorAPI.export_song_map_json(song, path)` — serialize song back to song-map format
- `DrumGeneratorAPI.export_song_timeline_json(song, path)` — resolve to flat tempo/region timeline JSON for REAPER's `SetTempoTimeSigMarker` API

---

## Ardour Integration (`ardour/` + CLI)

Ardour integration is a separate but parallel workflow to REAPER:

### CLI Entry Point
```bash
python -m midi_drums.api.cli ardour create --genre metal --style doom \
    --tempo 70 --output project.ardourproj --midi
```

Implemented in `api/cli.py` via `handle_ardour_create_command()`. The command:
1. Generates a Song using the same genre/drummer pipeline
2. Writes a sidecar (`midi_drums_sections.json`) consumed by `ardour/create_song_sections.lua`
3. Exports MIDI (optionally, with `--midi`)
4. Creates an Ardour project directory structure

### Lua Script
Located at `ardour/create_song_sections.lua`. Nearly identical to the REAPER script but:
- Uses `ARDOUR_SECTIONS` table instead of REAPER-specific region data
- Targets Mixbus/Ardour session format (`.ardourproj`)
- Auto-imports MIDI onto a new track

### Ardour Command Subcommands
The CLI's `ardour` subparser in `api/cli.py` has:
- `ardour create` — mirrors REAPER export, targets Ardour/Mixbus sidecar + MIDI workflow
- `--preset-only` flag — creates session markers without generating MIDI
- `--write-sidecar JSON` — writes the section structure sidecar for Lua consumption

### Prompt Mode Ardour Support
The `prompt` (AI generation) command also supports Ardour output:
```python
# In handle_prompt_command() in api/cli.py:
if ardour_dir and song_obj:
    ardour_out = Path(ardour_dir)
    ardour_out.mkdir(parents=True, exist_ok=True)
    # Writes sidecar + MIDI alongside the session dir
```

### Key Difference from REAPER
The Ardour integration reuses `export/reaper/models.py` (for genre presets and section colors) but targets a different output format — `.ardourproj` session files instead of `.rpp`. The Python side writes the same JSON sidecar format; the Lua script at `ardour/create_song_sections.lua` handles Ardour-specific region creation.

---

## Design Strengths

### 1. Drummer Modifications Are Excellent
Each `DrummerModification` is a pure function taking a pattern and returning a new one. Composable, independently testable, single-responsibility. The drummer plugins are thin wrappers that wire up modifications with genre-specific constants:
```python
class BonhamPlugin(DrummerPlugin):
    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=25.0)
        self.triplets = TripletVocabulary(triplet_probability=0.4)
    
    def apply_style(self, pattern):
        styled = pattern.copy()
        styled = self.behind_beat.apply(styled, intensity=0.7)
        styled = self.triplets.apply(styled, intensity=0.8)
        return styled
```

### 2. Pattern Templates Solve Repetition Well
`BasicGroove`, `BlastBeat`, `TomFill` — each is a reusable template. `TemplateComposer` composes multi-element patterns declaratively instead of manual builder calls. AD2/EZD3 extended instrument support is baked into templates via `crash_type="heavy"`, `use_edge=True`, etc.

### 3. Plugin Registry Is Clean
Simple register-lookup pattern in `plugins/registry/plugin_registry.py`. Auto-discovery works for built-in packages and supports external plugin directories.

### 4. Physical Validation & Auto-Fixing Exist
`PhysicalValidator` (in `validation/physical_constraints.py`) checks patterns for impossibilities (3+ hand instruments simultaneously, ride+hihat conflicts). `PatternFixer` (in `utils/pattern_fixer.py`) auto-corrects issues: removes duplicate beats, resolves hi-hat conflicts, drops lowest-priority hand instruments when >2 are simultaneous. The composite drummer uses this validation after each layer.

### 5. Intensity Curves Enable Musical Progression
`IntensityCurve.ASCENDING`, `.DESCENDING`, `.PLATEAU`, `.DIP_RISE`, `.STEPS` — predefined arcs with control points for complexity_multiplier, velocity_bias, and density_factor. Interpolated bar-by-bar so sections have energy arcs rather than static patterns.

### 6. AD2 Has the Most Extensive Mapping
`_AD2_FULL_MAP` in `core/models/kit.py` maps **~40 instruments** using XLN Audio's vendor-documented keymap PDF (June 2021). Covers core drums, brush sweeps (A–F), rim variants, tight HH zones, extended open HH positions, tom edges, and crash chokes. This is the most comprehensive mapping of any preset — significantly more than EZD3 (~25) or GM baseline (13 + collapse rules).

### 7. Defaults Are Correctly Set to GM
`config/defaults.py:DEFAULT_MAPPING = "gm_drums"` ensures that the high-level API (`DrumGeneratorAPI.create_song(mapping=...)`) defaults to GM-compliant MIDI, which is universally compatible. The CLI also uses DEFAULT_MAPPING for all `--mapping` arguments.

---

## Design Weaknesses

### 1. Genre Plugins Are Procedural Walls of Code
The genre plugins (`funk.py` at ~2382 lines, `jazz.py` at ~2116 lines) are enormous because every section-type × style combination has hardcoded pattern generation. There's no template system that parameterizes across genres — funk's `_flavors_chorus()` is a 54-line wall of `TemplateComposer().add(...).build(bars=1, ...)` calls that should be data-driven rather than procedural.

The **refactoring narrative** ("reduced X lines") was real for individual drummer plugins but didn't scale to an architectural shift at the genre level. Every new genre/style is still a manual implementation.

### 2. ComposerV2 Has an Opaque Fallback Chain
```python
groove = groove_library.select()          # path A
if not groove: groove = flavors[0]       # path B  
if not groove: groove = generate_pattern() # path C
if not groove: fallback_default           # path D
```
You can't trace which path executes without knowing what each genre plugin implements. This makes debugging and testing harder.

### 3. Riff-Lock Is Orphaned Feature Code
`RiffLockTransform` and `SnareAccentReaction` are solid but have no clear entry point for users to trigger audio-onset-detection → riff-lock workflow. The `audio_analysis.analyze_onsets()` function exists but isn't wired into the main generation pipeline. It's a feature waiting for integration work.

### 4. Physical Validation Is Disconnected From Generation
`PhysicalValidator.validate_pattern()` and `PatternFixer.fix_pattern()` are only invoked in `CompositeDoomBluesPlugin.apply_style()`. The main generation path produces patterns that may be physically impossible (3+ simultaneous hand hits) without an explicit validation/fix pass.

### 5. Drummer Timing Offset Application Is Unclear
`GrooveEngine.get_bar_offset_ms()` calculates timing displacement per bar, stored as `groove_offsets_ms` on each Section. But it's unclear how this offset gets applied to MIDI output without reading the REAPER export code. The offset should be applied during MIDI rendering (note-on time shifts), not just stored.

### 6. Stringly-Typed Genre/Style Names
No enum or data structure guarantees that "metal/death" is valid until runtime lookup fails. All genre/style names flow through as strings with no compile-time safety.

### 7. Inconsistent `import random` Usage
Heavy use of `import random` inside methods rather than at module level. Some modules seed it properly (`random.Random(seed)`), others don't. This affects reproducibility testing.

---

## Notable Implementation Details

### `beat.instrument_promoted` Provenance Flag
When a hi-hat is promoted to ride/crash/china for high-energy sections, the flag `instrument_promoted = True` distinguishes it from genuinely-placed accents of the same instrument. This lets drummer modifications (e.g., `MinimalCreativity`, `SpeedPrecision`) correctly identify "the timekeeping cymbal" without matching every beat of that instrument type — preventing unwanted removal of deliberate crash accents placed by templates.

### Default Tempo Maps Per Style
Each genre plugin has a `DEFAULT_TEMPO_MAP: dict[str, int]` with realistic tempos per style:
- Metal/death = 195 BPM, metal/doom = 70 BPM
- Jazz/swing = 150 BPM, jazz/ballad = 70 BPM
- Funk/classic = 105 BPM, funk/shuffle = 110 BPM
- House = 124 BPM, techno = 136 BPM, DnB = 174 BPM

When `tempo=None` is passed to generation, the system auto-selects from this map.

### CompositeDoomBluesPlugin Validation Loop
The composite drummer applies each layer (Roeder → Porcaro → Chambers) with a position clamp (`beat.position = max(0.0, beat.position)`) after each layer, then runs full `PatternFixer` validation + repair at the end. This is defensive programming that acknowledges layered modifications can produce physically impossible patterns.

### Section Color Coding (REAPER/Ardour)
`export/reaper/models.py:get_section_color(section_name)` assigns default colors by section type:
- intro/verse = greenish
- chorus = reddish  
- bridge = bluish
- breakdown/outro = yellowish

Overridable via `color_groups` in song-map JSON.

### GM Hi-Hat Collapse Rules
For presets that claim GM compatibility, `_GM_HIHAT_COLLAPSE` in `kit.py` maps extended hi-hat instruments to their GM equivalents: closed-hat family → CLOSED_HH (note 42), open-hat family → OPEN_HH (note 46). This prevents strict GM-compliant samplers from receiving wrong notes (e.g., note 60 = GM "Hi Bongo", not an open hi-hat).

### Hybrid Drummer Plugins (Moon, Smith)
**MoonPlugin** (Keith Moon) generates crash-heavy chaos patterns with quarter-note crash builds and floor-tom punctuation — unusual because it leans into destruction rather than pocket. **SmithPlugin** (Chad Smith) is the largest named drummer plugin (~515 lines) due to complex double-kick/tom interlock fills and RHCP-influenced slap-bass syncopated kick patterns.

---

## Dependencies

### Core Runtime
- `mido` — SMF MIDI file generation library (used in `export/midi/engine.py`)

### Optional
- `librosa` + `numpy` — riff-locked drum generation (`analysis/audio_analysis.py`)
- `pydantic-ai` — AI pattern generation backend (`ai/pattern_generator.py`)
- `loguru` — structured logging for AI module

### Dev (from dev_requirements.in)
- black, isort, pytest, pytest-cov, ruff

---

## Summary

This codebase has **excellent building blocks** — composable modifications, pattern templates, plugin registry, physical validation, intensity curves, AD2's extensive vendor-documented keymap — but they're **underutilized at the genre level**. Each genre plugin writes procedural pattern code instead of composing from shared primitives, resulting in 2000+ line walls that are hard to extend without reading through them.

The system defaults to GM-compliant MIDI output (`"gm_drums"` as DEFAULT_MAPPING) but provides rich mapping support for EZD3 (~25 instruments) and AD2 (~40 instruments). REAPER integration is sophisticated (song-map JSON, timeline export, bidirectional sidecar sync) while Ardour integration is a parallel CLI + Lua path producing `.ardourproj` sessions.

**Key opportunities for improvement:**
1. Data-driven genre templates instead of procedural pattern code
2. Automatic physical validation in the main generation pipeline
3. Wire up riff-lock as a first-class generation option, not an orphaned feature
4. Clarify how `groove_offsets_ms` timing displacement is applied to MIDI output
5. Add enum-based genre/style types for compile-time safety
6. Align `DrumGenerator` internal default kit (EZD3) with high-level API default (GM) to eliminate divergence between entry points
