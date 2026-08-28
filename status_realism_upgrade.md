# MIDI-DRUMS — REALISM UPGRADE STATUS

## Current State
Batch `regen_all.bat` is generating all songs (14 drummers × 28 styles = 392 combos) to `reaper_test/`. Each combo produces:
- `*_gm.mid` (GM mapping)
- `*_ad2.mid` (Addictive Drums 2 keymap)  
- `*.rpp` (REAPER project with markers)

Output is still being generated — metal genre in progress.

---

## COMPLETED WORK (commit `af5d5d0`)

### Problem: Songs sounded boring and not quite right for genres/drummers
Root causes identified:
1. Humanization default was 0.3 — barely activates the sophisticated humanizer
2. Swing ratio was 0.0 for all genres — Jazz/Funk had zero swing feel
3. GrooveEngine existed with drummer-specific profiles but was **never wired up**
4. Templates didn't use complexity for actual structural variation

### Changes Made

**1. `midi_drums/core/value_objects/generation_parameters.py`**
   - `complexity`: 0.5 → 0.5 (unchanged)
   - `dynamics`: 0.5 → **0.6** (wider volume range)
   - `humanization`: 0.3 → **0.5** (main fix — activates humanizer properly)
   - `fill_frequency`: 0.2 → **0.35** (more natural phrasing)
   - `swing_ratio`: 0.0 → **0.12** (light swing base; genres override higher)

**2. `midi_drums/generation/composer_v2.py` — GrooveEngine wiring**
   - Added `GrooveEngine` import and instance
   - Wired groove offsets into each bar during song creation
   - Each bar now gets drummer-specific timing displacement (swing feel)
   - Result: Bonham = heavy swing (~21ms), Hoglan = mechanical (~0.9ms), Porcaro = shuffle (~10ms)

**3. Restored `midi_drums/generation/macro_composer.py` (262 lines)**
   - This file was missing from commit `41c18b2` (untracked/uncommitted)
   - Restored from remote — it implements bar-by-bar pattern selection via `GrooveLibraryManager`

---

## KNOWN ISSUE

**Snare is much too penetrant in all songs.** Needs velocity adjustment or mapping fix.

---

## TEST STATUS
575 passed, 10 skipped (commit verified before batch generation)

---

## NEXT STEPS (pending snare issue fix)
- [ ] Identify why snare velocity is too high — check GM mapping + AD2 mapping velocity curves
- [ ] Apply genre-specific velocity adjustments if needed
- [ ] Re-generate affected songs with fixed mappings
- [ ] Add Electronic genre plugin (Phase 3 task)
