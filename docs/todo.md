# MIDI Drums Generator — Project TODO List

This file tracks the master development roadmap. Priorities are ordered by impact on the user experience (live, varied, inspiring drum parts). Updated regularly.

---

## 🔥 HIGH PRIORITY — Making Drums Sound Alive

### [ ] Bar-by-bar pattern evolution (PLAN #1 — STARTED)
**Goal**: No two bars should sound identical. Patterns evolve within sections instead of looping static loops.

- [x] Design the `BarSelector` interface (see `midi_drums/generation/bar_selector.py`)
- [x] Implement `BarSelector.generate_for_bar(section, bar_index, section_length, complexity, previous_bars)` that returns a different pattern per bar
- [ ] Wire into `SongComposer.compose_song()` — replace the current "generate once, repeat N times" loop
- [ ] Add 3+ distinct pattern "flavors" per section type per style (e.g., death verse has: sparse blast, full blast, syncopated variant)
- [ ] Test: verify no bar-to-bar repetition in a full song generation

**Impact**: ★★★★★ — This single change addresses the #1 complaint ("boring and similar sounding")

### [ ] Section intensity curves (PLAN #2)
**Goal**: Each section should have an internal arc — not flat from start to finish.

- [x] Design `IntensityCurve` data structure (ascending, descending, plateau, dip-rise)
- [ ] Implement curve-aware pattern generation that adjusts complexity, density, and dynamics per bar
- [ ] Wire into the BarSelector so curve + bar_index determine pattern "energy"
- [ ] Test: verse builds → chorus hits hard → bridge drops → outro fades

**Impact**: ★★★★☆ — Creates natural flow and energy

### [ ] Pattern swapping / flavor selection (PLAN #3)
**Goal**: Even within a single section type, alternate between distinct patterns to avoid monotony.

- [x] Design `PatternLibrary` registry that holds multiple flavors per (genre, style, section) key
- [ ] Implement swap logic: after N bars, switch to a different flavor if one is available
- [ ] Ensure transitions are musically coherent (no jarring pattern jumps)
- [ ] Test: full song with no repeated bar patterns

**Impact**: ★★★★☆ — Eliminates the "same loop forever" problem

### [ ] Drummer fill library expansion (PLAN #4)
**Goal**: Each drummer needs 8-12 signature fills, not 1-2. Fills should be context-aware ("tom roll after verse", "cymbal swell before chorus").

- [ ] Expand each of the 10 drummer plugins to include 8+ unique fills (target: 80+ total new fills)
- [ ] Add `FillContext` metadata: which sections trigger this fill, what bar positions work, which genres are compatible
- [ ] Implement a `FillPicker` that selects fills based on section context, recent fill history, and drummer personality
- [ ] Test: full song with appropriate fills in the right places

**Impact**: ★★★☆☆ — Fills are the "voice" of each drummer - crucial for life-like performance

### [ ] Groove engine & swing (PLAN #5)
**Goal**: Per-bar swing ratio + timing micro-shifts, not individual note jitter. Creates a unified "feel" per bar.

- [x] Design `GrooveEngine` that applies per-bar swing/swing-ratio and timing push-pull
- [ ] Implement post-processing pass that shifts all notes in a bar slightly together (not independently)
- [ ] Add drummer-specific groove profiles: Bonham = 60% swing behind beat, Weckl = straight with micro-grooves, etc.
- [ ] Test: same pattern with different drummers should feel completely different

**Impact**: ★★★★☆ — Timing is the #1 factor in "human" vs "robotic" perception

---

## 🎸 MID PRIORITY — Feature Completeness & Quality of Life

### AD2 keymap integration
- [x] Parse and validate the AD2 MIDI keymap PDF
- [x] Wire tight HH, crash_choked, ride_bell, tom_edge into metal patterns
- [ ] Wire AD2 zones into rock, jazz, funk patterns (lower priority)
- [ ] Add AD2-specific drummer fills for all 10 drummers

### Danny Carey (Tool) drummer plugin
- [x] Implement polyrhythmic kick, deep tom patterns, Tool groove space
- [x] Add 4 signature fills (quintuplet cascade, poly buildup, ethnic fill, cymbal swell)
- [ ] Wire AD2 extended instruments into carey's fills

### Rock genre improvements
- [ ] Add tight HH + ride_bell to rock patterns (currently only metal has these)
- [ ] Add crash_choked variants for punk/hard rock styles
- [ ] Implement 3+ pattern flavors per section style

### Jazz/Funk groove templates
- [ ] Create jazz-specific swing templates (traditional, heavy, ballad)
- [ ] Create funk ghost-note density presets
- [ ] Export these as pre-configured GrooveEngine profiles

---

## 🛠️ MEDIUM PRIORITY — Infrastructure & DX

### Song composition engine rewrite
- [ ] Current `SongComposer.compose_song()` is a flat loop that: generate pattern → copy N bars → next section
- [ ] Design new `SongComposer` that uses BarSelector, IntensityCurve, PatternLibrary, FillPicker
- [ ] Implement the new pipeline in `midi_drums/generation/composer_v2.py` (keep old for compatibility)
- [ ] Add a CLI flag `--engine v2` to test without breaking existing users

### MIDI export enhancements
- [x] Song map per-segment tempo/meter support (already done)
- [x] Timeline export (already done)
- [ ] CC controller mapping for expressive playback (expression, volume, sostenuto per-bar)
- [ ] Export drum kit configuration metadata in the MIDI file's GM2 header
- [ ] Per-track velocity maps for EZDrummer/AD2 expression

### Pattern template system expansion
- [x] Basic groove templates (done, 8 templates)
- [ ] Add "buildup" templates (1-bar → 2-bar → 4-bar intensity ramps)
- [ ] Add "transition" templates (fill-less bars that set up the next section)
- [ ] Add "drop" templates (sudden silence or sparse pattern into heavy chorus)

### Testing improvements
- [ ] Add musicality tests: verify no repeated bar patterns in a full song
- [ ] Add timbre diversity test: count unique instrument articulations per generation
- [ ] Load testing: generate 100 songs with different seeds, measure variety score
- [ ] Audio preview tests (optional): render to WAV and run ML "human vs machine" classifier

### Documentation improvements
- [x] Update README.md with AD2 keymap info
- [x] Update CLAUDE.md with all drummer plugins
- [x] Update CHANGELOG.md with recent changes
- [ ] Add a "Patterns That Sound Alive" guide (user-facing, explains how to use the new features)
- [ ] Add a "Drummer Style Guide" explaining each drummer's personality and best-use genres

---

## 🔮 LOWER PRIORITY — Nice-to-Have

### AI-driven pattern variations
- [ ] Train a small model on real drum transcriptions to generate natural variations
- [ ] Or: prompt-based variation engine ("more ghost notes", "simplify the verse", "make it funkier")
- [ ] Keep as optional AI backend so users don't need it

### Real-time audio synthesis
- [ ] Phase 1: Add a VST host or AU wrapper for live playback of MIDI patterns
- [ ] Phase 2: Integrate with EZDrummer/AD2 via the official SDKs if available
- [ ] Phase 3: Build-in lightweight drum synth as fallback

### Pattern marketplace / community sharing
- [ ] Export/import pattern bundles (JSON format)
- [ ] GitHub Discussions or a simple web gallery for user submissions
- [ ] Rate and tag patterns ("metal", "heavy", "groovy", "simple")

### GUI / visual editor
- [ ] Web-based MIDI piano roll with genre/drummer selection sidebar
- [ ] VS Code extension? (overkill, but possible)
- [ ] Standalone Electron app?

### World music genres
- [ ] Latin (salsa, bossa nova, cumbia)
- [ ] Reggae / Dub
- [ ] Afrobeat
- [ ] Country / Folk
- [ ] Bluegrass

---

## 📊 Current Status Summary

| Category | Done | In Progress | Todo | Total |
|----------|------|-------------|------|-------|
| Genre plugins | 5 (Metal, Rock, Jazz, Funk, Electronic) | 0 | 0 | 5 |
| Drummer plugins | 11 (+ 1 composite) | 0 | 0 | 12 |
| AD2 keymap | Mapped + wired into metal | Wiring rock/jazz/funk | 2 | 3 |
| Pattern diversity | Foundation designs | Implementation started (#1) | 4 more phases | 5+ |
| Fill library | ~4 per drummer (base) | Expanding | 8-12 each | 10 drummers |
| Song composition | v1 (static, looping) | v2 design phase | Rewrite + tests | 2 |
| MIDI export features | Sidecar, song map, timeline | CC controllers | 2 | 3 |
| Documentation | ✅ Up to date with all changes | Adding "Alive Patterns" guide | 2 items | 4 |

---

## 📝 How to Use This TODO

1. **Priority order matters** - work through HIGH PRIORITY first. Items inside are numbered by plan priority.
2. **Each high-priority item is a plan** - the detailed design for PLAN #1 (bar-by-bar) is in `docs/plan_01_bar_by_bar.md`.
3. **Check off items as you complete them** - use the `- [x]` syntax.
4. **Add new items here first** - then implement them. Don't just "add features" without documenting the intent.

---

_Last updated: 2025-08-13 (this file was created now)._
