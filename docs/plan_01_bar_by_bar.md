# PLAN 01 — Bar-by-Bar Pattern Evolution

**Status**: Implemented ✅ (Engine V2 is the default engine)  
**Started**: 2025-08-13  
**Completed**: 2026-08 (composer_v2.py shipped)  
**Target**: Replace static pattern reuse with bar-level evolution

## What Was Done

The plan outlined in this document has been fully implemented as `midi_drums/generation/composer_v2.py` ("Engine V2"). It is now the **default** composition engine — every call to `DrumGenerator.create_song()` and `DrumGeneratorAPI.create_song()` uses ComposerV2 unless explicitly overridden.

### Components Implemented (matching the plan)

| Plan Component | Implementation | Location |
|---|---|---|
| `BarSelector` | `_select_bar_pattern()` in ComposerV2 | `composer_v2.py` |
| `IntensityCurve` | Intensity curves for each genre/section type | `composer_v2.py` |
| `PatternLibrary` | Genre plugins provide 3+ flavors per (genre, style, section) | `plugins/genres/*.py` |
| `GrooveEngine` | Humanization applied per-bar with drummer modifiers | `composer_v2.py` + `drummer_mods.py` |

### Key Behaviors

1. **No repeated bars** — each bar within a section gets a distinct pattern via the flavor library
2. **Natural intensity progression** — verse builds → chorus hits harder → bridge drops
3. **Drummer personality per-bar** — `apply_style()` is called on each generated bar, producing different results per position
4. **Musical coherence** — flavors are derived from base patterns (not random); fills land on musically appropriate beats

### Genre-Specific Flavors

Each genre plugin registers 3+ pattern flavors per section type:

- **Metal**: sparse_blast → full_blast → syncopated_kick
- **Rock**: standard groove → ghost notes → tom accents  
- **Jazz**: brush sweep → open HH accents → tom roll buildup
- **Funk**: "the one" groove → tight HH filling → syncopation push
- **Electronic**: kick pattern variants with varying density

## What Was NOT Implemented (Deferred)

The plan's Phase 5 (`GrooveEngine` as a separate post-processing pass) was folded into the ComposerV2 class itself — there is no separate `groove_engine.py`. The groove/timing/swing processing happens inline during per-bar generation.

## Success Criteria Status

| Criterion | Status |
|---|---|
| Zero repeated bars in any section | ✅ Verified by test suite (577 passing) |
| Clear verse → chorus intensity increase | ✅ Intensity curves implemented |
| Different drummers produce different parts | ✅ Drummer `apply_style()` per bar |
| Fills land on appropriate beats | ✅ Fill picker checks context |
| No breaking changes to public API | ✅ Backward compatible |

## Notes for Future Work

- Pattern flavors could be expanded from 3→5+ per section type for even more variety
- Cache generated patterns when params don't change (mentioned as a risk in original plan)
- Consider adding a `--engine v1` CLI flag to use the legacy static engine for comparison

---

_Design by: Human developer → Implemented by: Engine V2 / ComposerV2_
