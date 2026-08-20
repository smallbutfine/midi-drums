# MIDI Drums Generator — Project TODO List

This file tracks the master development roadmap. Priorities are ordered by impact on the user experience (live, varied, inspiring drum parts). Updated regularly.

---

## ✅ COMPLETED

### Engine V2 — Bar-by-Bar Pattern Evolution ([PLAN #1](docs/plan_01_bar_by_bar.md))
- [x] `IntensityCurve` enum + interpolation (`midi_drums/generation/intensity_curve.py`)
- [x] `BarSelector.generate_for_bar()` with intensity modulation
- [x] `ComposerV2` orchestrating BarSelector + IntensityCurve per section
- [x] `DrumGenerator(composer_engine="v2")` as default — every bar unique
- [x] Drummer personality per bar (Bonham fills later in sections, Porcaro ghost notes every 4th bar)

### Song Composition Engine V2
- [x] ComposerV2 replaces static loop with bar-by-bar generation
- [x] `DrumGenerator.create_song()` delegates to V2 by default
- [x] V1 preserved via `composer_engine="v1"` for backward compat
- [x] All code paths use V2: CLI, API, AI agent

### AD2 Keymap Wiring (Metal)
- [x] 35 zones mapped in `_AD2_FULL_MAP`
- [x] tight HH, crash_choked, ride_bell, tom_edge wired into all metal patterns
- [x] AD2 fills in Dee, Hoglan, Peart drummer plugins

### AD2 Keymap Wiring (Rock/Jazz/Funk)
- [x] tight HH used for punk/hard rock verse comping (dry pencil attack)
- [x] ride_bell accents added to jazz swing/bebop/fusion/hard_bop patterns
- [x] tom_edge accents on funk backbeats and shuffle grooves
- [x] crash_choked punctuation for punk, alt-rock, fusion, new_orleans styles
- [x] All 4 genres now use AD2 zones — tight HH, crash_choked, ride_bell, tom_edge

### Danny Carey (Tool) Drummer Plugin
- [x] 11th drummer: polyrhythmic kick, deep tom patterns, Tool groove space
- [x] 4 signature fills + composer V2 integration

---

## 🔥 NEXT — HIGH PRIORITY

### [x] Pattern Swapping / Flavors (PLAN #3) ✅
**Goal**: 3+ distinct pattern "flavors" per section type per style. Instead of one skeleton per bar, each bar picks from a pool.

- [ ] Create `PatternLibrary` registry: `{(genre, style, section): [pattern_flavor_1, pattern_flavor_2, pattern_flavor_3]}`
- [ ] Death metal verse flavors: sparse_blast → full_blast → syncopated_kick (crescendo)
- [ ] Rock chorus flavors: classic_groove → double_kick → crash_rich
- [ ] Add `ComposerV2._select_flavor()` method that picks based on bar position + previous bars
- [ ] Ensure transitions are musically coherent

**Where to start**: `midi_drums/plugins/genres/metal.py` — add `_death_metal_verse_flavors()` returning a list of 3+ patterns, wire into ComposerV2.

### [ ] Drummer Fill Library Expansion (PLAN #4)
**Goal**: Each drummer gets 8-12 signature fills with context-aware selection.

Current state: most drummers have 0-2 fills. Carey has 4. Peart has 3.
Target: 8+ fills each × 11 drummers = 88+ total fills.

- [ ] Add `FillContext` metadata: which sections/bar positions trigger this fill
- [ ] Implement `FillPicker` that selects based on section context + recent fill history
- [ ] Example for Hoglan: blast_cascade, chicken_lights, snare_solo, floor_tom_roll, tom_edge_run, double_kick_breakdown, ride_crash_buildup, full_kit_finale
- [ ] Context rules: "use tom roll after verse", "crash swell before chorus", "never two fills within 2 bars of each other"

### [ ] Groove Engine & Swing (PLAN #5)
**Goal**: Per-bar swing ratio + timing push/pull. Creates unified "feel" per bar instead of independent note jitter.

- [x] Design `GrooveEngine` that applies per-bar swing/swing-ratio and timing push-pull
- [ ] Implement post-processing pass: shift all notes in a bar together (not independently)
- [ ] Drummer-specific groove profiles: Bonham = 60% swing behind beat, Weckl = straight with micro-grooves, Chambers = pocket stretching
- [ ] Test: same pattern with different drummers should feel completely different

### [ ] AD2 Zones for Rock/Jazz/Funk — ✅ DONE
**Status**: Completed. All 4 genres now use tight HH, crash_choked, ride_bell, tom_edge.
- [x] Add `PatternBuilder.tight_hh()` usage to rock verse/chorus (tighter attack for punk/hard)
- [x] Add ride_bell accents to jazz swing patterns
- [x] Add crash_choked variants to funk breakdown sections
- [x] Wire into Carey drummer fills too

---

## 🎸 MID PRIORITY — Feature Completeness & Quality of Life

### Rock Genre Improvements
- [ ] tight HH + ride_bell in rock patterns (currently only metal)
- [ ] crash_choked variants for punk/hard rock styles
- [ ] 3+ pattern flavors per section style

### Jazz/Funk Groove Templates
- [ ] Jazz swing templates: traditional, heavy, ballad
- [ ] Funk ghost-note density presets
- [ ] Export as pre-configured GrooveEngine profiles

---

## 🛠️ MEDIUM PRIORITY — Infrastructure & DX

### Pattern Template Expansion
- [x] Basic groove templates (8 done)
- [ ] "Buildup" templates (1-bar → 4-bar intensity ramps)
- [ ] "Transition" templates (fill-less bars that set up next section)
- [ ] "Drop" templates (sudden silence or sparse pattern into heavy chorus)

### MIDI Export Enhancements
- [ ] CC controller mapping for expression in EZDrummer/AD2 playback
- [ ] Export drum kit config metadata in GM2 header
- [ ] Per-track velocity maps for EZDrummer/AD2 expression

### Testing Improvements
- [ ] Musicality test: verify no repeated bar patterns in a full song
- [ ] Timbre diversity test: count unique instrument articulations per generation
- [ ] Load testing: generate 100 songs, measure variety score

---

## 📊 Current Status Summary

| Category | Done | In Progress | Todo | Total |
|----------|------|-------------|------|-------|
| Genre plugins | 5 (Metal, Rock, Jazz, Funk, Electronic) | 0 | 0 | 5 |
| Drummer plugins | 11 (+ 1 composite) | 0 | 0 | 12 |
| AD2 keymap | Mapped + wired into metal | **All 4 genres done** ✅ | 0 | 3 |
| Pattern diversity | Engine V2 (bars unique) | Flavors, fills, groove engine | 3 items | 5+ |
| Pattern diversity | Engine V2 (bars unique) | Flavors, fills, groove engine | 3 items | 5+ |
| Fill library | ~4 per drummer | Expanding to 8-12 each | 10 drummers | ~88 fills |
| Song composition | v2 default (bar-by-bar) | Flavor selection next | 1 item | 2 total |
| MIDI export | Sidecar, song map, timeline | CC controllers | 3 items | 5 total |

---

## 📝 How to Use This TODO

1. **Priority order matters** — work through the NEXT section first.
2. Each item includes a "Where to start" pointer.
3. Check off items as you complete them.
4. Add new items here before implementing.

---

_Last updated: 2026-08-20 (AD2 zones wired into all 4 genres ✅)._
