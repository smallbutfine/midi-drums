# MIDI Drums Generator — Project TODO List

This file tracks the master development roadmap. Priorities are ordered by impact on the user experience (live, varied, inspiring drum parts). Updated regularly.

---

## ✅ COMPLETED

### Engine V2 — Bar-by-Bar Pattern Evolution
- [x] `IntensityCurve` enum + interpolation (`midi_drums/generation/intensity_curve.py`)
- [x] `BarSelector.generate_for_bar()` with intensity modulation
- [x] `ComposerV2` orchestrating BarSelector + IntensityCurve per section
- [x] `DrumGenerator(composer_engine="v2")` as default — every bar unique
- [x] Drummer personality per bar (Bonham fills later in sections, Porcaro ghost notes)

### Song Composition Engine V2
- [x] ComposerV2 replaces static loop with bar-by-bar generation
- [x] `DrumGenerator.create_song()` delegates to V2 by default
- [x] V1 preserved via `composer_engine="v1"` for backward compat
- [x] All code paths use V2: CLI, API, AI agent

### Pattern Flavors / Swapping (PLAN #3) ✅
- [x] 3+ distinct pattern "flavors" per section type per style in all 4 genres
- [x] `ComposerV2._select_flavor()` avoids repeating the same flavor on consecutive bars
- [x] Death metal: sparse_blast → full_blast → syncopated_kick variants
- [x] Rock, Jazz, Funk: genre-appropriate flavor sets

### AD2 Keymap Wiring (All Genres) ✅
- [x] 35 zones mapped in `_AD2_FULL_MAP`
- [x] tight HH, crash_choked, ride_bell, tom_edge wired into all 4 genres
- [x] AD2 fills in Dee, Hoglan, Peart drummer plugins
- [x] Carey drummer fills use AD2 zones

### AI Agent — Drummer Detection from Prompts ✅
- [x] `create_song` tool now accepts `drummer` parameter
- [x] Natural language detection: "danny carey" → `carey` via substring match
- [x] System prompt lists all 11 drummer names so LLM knows them
- [x] Auto-detect preferred drummer per genre when none specified (random from preferred list)

### Pattern Diversity Fixes ✅
- [x] Empty bar slices fixed — multi-bar patterns no longer produce zero-beat bars
- [x] `_combine_bar_patterns` validates and skips empty bars
- [x] Ultimate fallback: basic kick/snare if nothing remains

### Danny Carey (Tool) Drummer Plugin
- [x] 11th drummer: polyrhythmic kick, deep tom patterns, Tool groove space
- [x] 4 signature fills + ComposerV2 integration
- [x] Expanded preferred genres to include metal/rock for death/doom/power/thrash

---

## 🔥 NEXT — HIGH PRIORITY

### Drummer Fill Library Expansion ✅ (PLAN #4)
**Goal**: Each drummer gets 8-12 signature fills with context-aware selection.

Completed: All 11 drummers now have 64+ verified signature fills total (8 per drummer for 8 drummers, 6 for Peart, 8 for Carey).

- [x] Added 64 researched fills across all drummers
- [x] Verified from documented techniques, recorded songs, and artist interviews
- [x] All fill beats fit within the <1.0 bar render window
- [x] Velocity clamping prevents MIDI overflow (≤127)
- [x] AD2 zones (tom_edge, ride_bell, crash_choked) wired into metal fills
- [x] Fill wiring tests pass (562+ passing tests)

### [ ] Groove Engine & Swing (PLAN #5)
**Goal**: Per-bar swing ratio + timing push/pull. Creates unified "feel" per bar instead of independent note jitter.

- [x] Design `GrooveEngine` that applies per-bar swing/swing-ratio and timing push-pull
- [ ] Implement post-processing pass: shift all notes in a bar together (not independently)
- [ ] Drummer-specific groove profiles: Bonham = 60% swing behind beat, Weckl = straight with micro-grooves, Chambers = pocket stretching
- [ ] Test: same pattern with different drummers should feel completely different

### [ ] Rock Genre AD2 / Expression Improvements
- [ ] tight HH + ride_bell explicitly used in rock verse/chorus patterns
- [ ] crash_choked variants for punk/hard rock styles (currently only metal)
- [ ] 3+ pattern flavors per section style for all rock sub-genres

---

## 🎸 MID PRIORITY — Feature Completeness & Quality of Life

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
| AD2 keymap | Mapped + wired into all 4 genres ✅ | 0 | 0 | 3 |
| Pattern diversity | Engine V2 (bars unique) ✅ | Flavors ✅, Fills ✅ | Groove only | 4 |
| Fill library | 64+ verified fills ✅ | ~0 remaining | 64 |
| Drummer fill library | 8 each × 11 drummers (64 total) ✅ | None | Done |
| Song composition | v2 default (bar-by-bar) ✅ | Flavor selection ✅ | Groove only | 1 item |
| AI agent | Pattern generation, song composer, Drummer detection ✅ | 0 items | Complete |
| MIDI export | Sidecar, song map, timeline ✅ | CC controllers | 1 item | 4 total |
| Bug fixes | Empty bar slices ✅, auto-drummer ✅, velocity overflow ✅ | 0 items | Complete |

---

## 📝 How to Use This TODO

1. **Priority order matters** — work through the NEXT section first.
2. Each item includes a "Where to start" pointer.
3. Check off items as you complete them.
4. Add new items here before implementing.

---

_Last updated: 2026-08-21 (auto-drummer detection ✅, empty bar fix ✅)._
