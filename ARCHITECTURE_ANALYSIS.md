# Architecture Analysis — midi-drums

## Song Creation Flow

```
┌──────────────────────────────────────────────────────────────┐
│  DrumGeneratorAPI.create_song()                              │
│    ├── DrumKit.from_preset(mapping) → resolves MIDI notes   │
│    └── DrumGenerator.create_song_v2(genre, style, tempo..)  │
│         ├── GenerationParameters (complexity/humanization)   │
│         └── ComposerV2.create_song()                          │
│              ├── Auto-select drummer from preferred_genres   │
│              └── For each section:                            │
│                    ├── get_section_grooves(genre_plugin, ..) │
│                    │   └── GenrePlugin.get_section_grooves() │
│                    │       └── Returns list[Pattern] from    │
│                    │           PatternTemplate subclasses     │
│                    └── Per bar:                               │
│                          ├── GrooveManager.select_groove()   │
│                          │   └── Phase-aware (establish/     │
│                          │       maintain/build/turnaround)   │
│                          ├── DrummerPlugin.apply_style(pat)  │
│                          │   └── 15+ drummer modifications   │
│                          └── BarSelector.generate_for_bar()  │
│                               └── Velocity + position jitter │
├──────────────────────────────────────────────────────────────┤
│  MIDI Export Path:                                            │
│    DrumGenerator.export_midi(song) → MIDIExporter            │
│      └── MIDIEngine.save_song_midi()                         │
│           └── _resolve_note(instrument, drum_kit)           │
│                └── KeymapLoader.get_midi_note(inst,keymap)  │
│                     └── JSON lookup (gm.json, ad2.json, ..) │
├──────────────────────────────────────────────────────────────┤
│  REAPER/Ardour Export:                                        │
│    ReaperExporter.export_with_markers() → .rpp               │
│      ├── MIDIEngine.save_song_midi()                        │
│      └── ReaperEngine.calculate_marker_positions(song)      │
│    ReaperExporter.create_reaper_project() → .rpp             │
│    Ardour: same Python + Lua bridge pattern                  │
└──────────────────────────────────────────────────────────────┘
```

## Architecture Overview

| Layer | Components | Purpose |
|-------|-----------|---------|
| **API** | `DrumGeneratorAPI` (`api/python_api.py`) | High-level API with convenience methods (metal_song, quick_export) |
| **CLI** | `cli.py` | Subcommands: generate, pattern, list, prompt, reaper, ardour |
| **Core** | Song/Section/Beat/Pattern models, DrumInstrument registry | Data layer — no generation logic |
| **Generation** | ComposerV2 (bar-by-bar evolution), PatternBuilder, GrooveEngine | Composition engine with per-bar pattern selection |
| **Plugin System** | GenrePlugin interface (5 genres), DrummerPlugin interface (17 drummers) | Strategy pattern for genre/drummer personality |
| **Templates** | BasicGroove, BlastBeat, DoubleBassPedal, JazzRidePattern, etc. | Declarative pattern composition to eliminate duplication |
| **Modifications** | BehindBeatTiming, GhostNoteLayer, LinearCoordination, etc. (12 mods) | Composable drummer techniques |
| **Export** | MIDIExporter/MIDIEngine (mido), ReaperEngine/ReaperExporter, Ardour path | Output: .mid files, REAPER .rpp projects, Ardour sessions |
| **Keymaps** | template.json, gm.json, ad2.json, ezdrummer.json + custom loader | Dynamic MIDI note resolution — no hardcoded values |

## Good Design Points

1. **Dynamic mapping system** — JSON keymaps completely replace hardcoded MIDI notes. New drumkits just need a new JSON file. The InstrumentRegistry loads from template at startup, and KeymapLoader discovers all mapping files by filename stem.

2. **Template-based patterns** — PatternTemplate subclasses (BasicGroove, BlastBeat, etc.) allow declarative composition via TemplateComposer instead of manual beat-by-beat construction. Eliminates duplication across genre plugins.

3. **Composable modifications** — Drummer modifications implement a common interface and can be layered (behind-beat + ghost notes + heavy accents = Bonham). Each modification is independently testable.

4. **Bar-by-bar evolution** — ComposerV2 avoids the "polka effect" by selecting different groove patterns per bar based on section phase (establish/maintain/build/turnaround), not just velocity jitter.

5. **GrooveEngine for timing displacement** — Each bar gets a unique timing offset (positive/negative ms) based on drummer's groove profile, creating authentic swing feel without modifying beat positions within the skeleton.

6. **Clean plugin interfaces** — GenrePlugin and DrummerPlugin abstract classes with clear contracts. New genres/drummers just implement the interface.

7. **IntensityCurve system** — Section energy arcs (ASCENDING, PLATEAU, DIP_RISE) modulate complexity and velocity across section position.

8. **REAPER/Lua integration** — Sidecar JSON workflow for bidirectional sync between Python generation and REAPER marker placement via io.popen subprocesses.

## Weak Design Points

1. **Circular dependency risk** — `patterns/templates.py` imports from both `config` and `core.models.kit`, creating tight coupling between template definitions and instrument registry initialization order.

2. **GenrePlugin interface gaps** — `get_common_fills()` returns bare Fill objects, but ComposerV2 wraps them in FillContext before using FillPicker. The conversion happens inside ComposerV2 itself (line 604–636), not in the plugin. This leaks ComposerV2 internals into the plugin contract.

3. **ComposerV2 monolith** — At 648 lines, `ComposerV2.create_song()` handles: drummer selection, intensity curves, groove library registration/selection, drummer style application, bar modulation, fill placement, and groove timing offsets. Should be split into coordinator classes.

4. **GrooveManager state leak** — GrooveLibraryManager stores state in `self._groove_libs` dict, but macro_composer.py has no cleanup mechanism. Multiple create_song() calls accumulate stale libraries across invocations if genres overlap.

5. **DrumKit/KeymapLoader coupling** — `drum_kit.get_midi_note(inst_name)` delegates to KeymapLoader.get_midi_note(), which loads ALL keymaps on first call (line 190). No lazy per-keymap loading, and the load_all() is called every time no keymaps are loaded.

6. **MIDIEngine._resolve_note dead path** — Returns None for unmapped instruments (line 89–93), but this causes silent beat loss with no warning. The `_INSTR_NOTE` dict at line 26–57 has hardcoded fallback values that are never used (the comment says "no fallback").

7. **PatternBuilder.sixteenth_subdivision confusion** — hihat_subdivision accepts TIMING.EIGHTH but also accepts literal floats like 0.125 for sixteenths. The API mixes enum-based and raw-float subdivisions inconsistently across methods.

8. **Drummer auto-selection random seed** — Line 74–91 in composer_v2.py uses `random.choice()` for drummer selection when none specified, but the Random instance isn't seeded deterministically from generation parameters. Reproducing a specific genre output is impossible without knowing which drummer was randomly chosen.

9. **GenrePlugin.apply_context_blend() ghost note logic** — Line 186–192 creates Beat objects with raw float positions and hardcoded velocity formula (`50 * blend_amount`). This breaks the PatternBuilder fluent API contract and exposes internal Beat construction in the genre interface.

10. **REAPER models reexported for Ardour** — `export/reaper/models.py` (GenreStructurePreset, get_section_color) is reused by Ardour integration, but REAPER-specific terminology (markers, RPP paths) bleeds into Ardour's API surface. The Python API writes `.ardourproj` directories using the same color/section logic despite being a different DAW format.

## File Dependency Map

```
core/models/
  kit.py         → InstrumentRegistry, DrumInstrument, KeymapLoader, DrumKit (all mapping logic)
  pattern.py     → Beat, Pattern (data only)
  song.py        → Song, Section, Fill (data only)
  time_signature.py → TimeSignature

mappings/
  template.json  → Source of truth for all instrument names
  gm.json, ad2.json, ezdrummer.json → MIDI note mappings
  loader.py      → KeymapLoader (discovers JSON files by filename stem)

generation/
  composer_v2.py → ComposerV2 (bar-by-bar evolution engine) [648 lines]
  bar_selector.py → Per-bar velocity/position modulation
  macro_composer.py → Genre groove library, phase selection
  intensity_curve.py → Section energy arcs
  groove_engine.py → Timing displacement per drummer

patterns/templates.py → Declarative pattern building blocks

plugins/
  interfaces/genre_plugin.py   → GenrePlugin ABC + apply_context_blend()
  interfaces/drummer_plugin.py → DrummerPlugin ABC
  registry/plugin_registry.py  → PluginManager, auto-discovery
  genres/{metal,rock,jazz,funk,electronic}.py → 5 genre implementations
  drummers/{17+}.py → Drummer personality modifiers

export/
  midi/engine.py   → MIDIEngine (mido-based SMF output)
  midi/exporter.py → MIDIExporter (convenience wrapper)
  reaper/engine.py → ReaperEngine (.rpp manipulation)
  reaper/exporter.py → ReaperExporter
```
