# PLAN 01 — Bar-by-Bar Pattern Evolution

**Status**: Design phase  
**Started**: 2025-08-13  
**Target**: Replace static pattern reuse with bar-level evolution

## Problem Statement

Currently, when a song has `verse: 8 bars`, the code does:
```python
pattern = generate_pattern(style="death", section="verse")
for i in range(8):
    song.add_section("verse", bars=8)  # same pattern looped 8 times
```

Result: every bar sounds identical (just velocity jitter). This is the primary reason drums sound "boring" and "similar".

## Design Goals

1. **No repeated bar patterns** in any single section
2. **Natural progression**: verse builds → chorus hits harder → bridge drops → outro fades
3. **Drummer personality shines**: different drummers should produce completely different parts for the same pattern skeleton
4. **Musical coherence**: patterns still fit together (no jarring jumps, fills land on beats, etc.)
5. **Backward compatible**: existing code (`--engine v1` or default) still works

## Architecture

### New Files

```
midi_drums/generation/
├── bar_selector.py        # NEW: selects a different pattern per bar
├── intensity_curve.py     # NEW: defines section arcs (buildup, drop, plateau)
└── composer_v2.py         # NEW: uses BarSelector + IntensityCurve + PatternLibrary
```

### BarSelector Interface

```python
class BarSelector:
    """Selects a distinct pattern for each bar within a section."""
    
    def select_bar_pattern(
        self,
        base_pattern: Pattern,       # The "skeleton" pattern for this section
        bar_index: int,              # 0-based position within the section
        section_length: int,         # Total bars in this section
        complexity: float,           # Section complexity (0-1)
        previous_bars: list[Pattern],# Patterns generated for bars before this one
    ) -> Pattern:
        """Return a pattern unique to this bar position.
        
        The returned pattern should:
        - Be musically coherent with the base_pattern
        - Differ from every entry in previous_bars
        - Reflect the section's intensity curve at bar_index / section_length
        - Apply the drummer's style distinctly per-bar
        """
        ...
```

### IntensityCurve Data Structure

```python
@dataclass(frozen=True)
class IntensityPoint:
    position: float  # 0.0 to 1.0 within the section
    complexity: float  # 0.0 to 1.0
    density_factor: float  # multiplier on pattern hit count
    velocity_bias: int  # add/subtract to all velocities
    
class IntensityCurve(Enum):
    ASCENDING = [IntensityPoint(0, 0.3), IntensityPoint(0.5, 0.6), IntensityPoint(1.0, 0.9)]
    DESCENDING = [IntensityPoint(0, 0.8), IntensityPoint(0.5, 0.5), IntensityPoint(1.0, 0.2)]
    PLATEAU = [IntensityPoint(0, 0.7), IntensityPoint(0.5, 0.8), IntensityPoint(1.0, 0.7)]
    DIP_RISE = [IntensityPoint(0, 0.6), IntensityPoint(0.3, 0.3), IntensityPoint(0.7, 0.9), IntensityPoint(1.0, 0.8)]
```

### PatternLibrary Registry

Each (genre, style, section) key gets a library of 3+ pattern flavors:

```python
class PatternLibrary:
    """Registry of alternative patterns per section type."""
    
    _libraries: dict[tuple[str, str, str], list[Pattern]] = { ... }
    
    def get_flavors(self, genre: str, style: str, section: str) -> list[Pattern]:
        ...
```

For **death metal verse**, flavors include:
1. `sparse_blast` — half the blast-beat hits (bars 0-2 of a section)
2. `full_blast` — complete blast beats (bars 3-5)
3. `syncopated_kick` — blast on snare + syncopated kick (bars 6-7, buildup to chorus)

### ComposerV2 Pipeline

```python
def compose_song_v2(...):
    # For each section in the song structure:
    curve = resolve_intensity_curve(section_type)
    
    for bar_idx in range(section.bars):
        intensity_at_bar = curve.evaluate(bar_idx / section.bars)
        
        flavors = pattern_library.get_flavors(genre, style, section.name)
        candidate_flavor = select_best_flavor(
            flavors=flavors,
            previous_bars=generated_bars[:],
            intensity=intensity_at_bar,
        )
        
        base_pattern = candidate_flavor.apply_intensity(intensity_at_bar)
        drummed_pattern = drummer_plugin.apply_style(base_pattern)
        
        groove_engine.apply_groove(drummed_pattern, drummer_name)
        
        fill_candidate = fill_picker.maybe_select_fill(
            position=bar_idx,
            section_end=(bar_idx == section.bars - 1),
            drummer=drummer_plugin,
        )
        
        song.add_bar(section.name, drummed_pattern, fill_candidate)
```

## Flavor Design by Genre

### Death Metal
| Section | Flavor 1 (bars 0-N/3) | Flavor 2 (bars N/3-2N/3) | Flavor 3 (bars 2N/3-end) |
|---------|------------------------|---------------------------|---------------------------|
| Verse   | Sparse blast           | Full blast                | Blast + syncopated kicks  |
| Chorus  | Double-time kick       | Blast on off-beats        | Full blast + tom accents  |
| Bridge  | Half-time groove       | Slow build to full tempo  | Rapid fire to fill transition |

### Doom Metal
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Sparse kicks, ride bell | Add tom hits on off-beats | Crash accents every bar |
| Chorus  | All elements at full volume | Subtle groove shift (swing) | Build to chorus peak |

### Thrash Metal
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Fast kicks, tight HH | Add snare ghost notes on off-beats | Blast beats start creeping in |
| Chorus  | Double-time everything | Crash accents + tom fills every 2 bars | Maximum intensity |

### Rock / Heavy Metal
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Standard verse groove | Add ghost notes on snare | Build with tom accents |
| Chorus  | All elements full volume | Syncopated crash on off-beats | Double kick shuffle |

### Progressive Metal
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Complex kick + ride bell | Add tom_edge accents | Polyrhythmic layers build |
| Chorus  | Full band groove | Time signature shift (e.g., 5/4 bar) | Return to main meter with accent changes |

### Funk
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Classic "the one" + ghost notes | Add hi-hat tight HH comping | Push syncopation forward |
| Chorus  | Full funk with crashes | Tight HH fills on off-beats | Maximum groove intensity |

### Jazz
| Section | Flavor 1 | Flavor 2 | Flavor 3 |
|---------|----------|----------|----------|
| Verse   | Brush sweep on snare + ride cymbal | Add open HH accents | Build to chorus with tom roll |
| Chorus  | Full kit, stick-on-stick | Swing ratio increase | Return to brush on verse transition |

## Drummer Personality Per-Bar

The drummer plugin's `apply_style()` method already exists. We enhance it:

```python
def apply_style_per_bar(self, pattern: Pattern, bar_index: int, total_bars: int) -> Pattern:
    """Apply drummers style with bar-aware variation."""
    
    # Ghost notes vary per bar (sometimes more, sometimes less)
    if bar_index % 3 == 0 and isinstance(self, ChambersPlugin):
        # Dennis Chambers is known for ghost note clusters every 3rd bar
        return self._apply_ghost_note_cluster(pattern)
    
    # Triplet feels appear more in later bars of a section
    if isinstance(self, BonhamPlugin) and bar_index > total_bars * 0.6:
        return self._apply_triplet_shift(pattern, intensity=0.8)
    
    # Standard apply_style for the rest
    return super().apply_style(pattern)
```

## Implementation Order

1. **Introduce `IntensityCurve`** — simple enum + dataclass, no complexity yet
2. **Build `BarSelector`** — with curve awareness but without flavor library (just velocity/density adjustments per bar)
3. **Add `PatternLibrary`** — register 3 flavors per (genre, style, section) in the genre plugins themselves
4. **Wire into ComposerV2** — new composition engine using all three components
5. **Expand fill library** — PLAN #4 fills get wired into ComposerV2's fill_picker
6. **Add `GrooveEngine`** — PLAN #5 post-processing pass for per-bar swing/timing
7. **Test and iterate** — full song generation with no repeated bars

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Patterns sound disjointed between bars | Each flavor is derived from the base pattern (not random) |
| Too many flavors to maintain | Start with 2 flavors per section, add more as needed |
| Performance impact of generating unique patterns | Cache generated patterns; only re-generate when params change |
| Fills landing on wrong beats | Fill picker checks musical context (bar position, previous fills) |
| Drummer styles get lost in variation | Drummer apply_style is applied AFTER pattern selection (not before) |

## Success Criteria

- [ ] A 16-bar verse has zero repeated bars (checked by MIDI note comparison)
- [ ] Verse → chorus transition has clear intensity increase
- [ ] Same skeleton pattern with different drummers produces noticeably different parts
- [ ] Fill patterns land on musically appropriate beats (beat 1 or bar start/end)
- [ ] No breaking changes to the existing API (`DrumGeneratorAPI` and `--engine v1` mode)

## Appendix: Flavor Example — Death Metal Verse (8 bars)

```
Bar 0 (sparse_blast, intensity=0.3):
  Kick on beat 1 only (not every eighth note)
  Snare blast on beats 2, 4 (half density)
  Tight HH (no open HH yet)

Bar 1-3 (full_blast, intensity=0.5-0.7):
  Full blast-beat pattern (kick/snare on alternating eighth notes)
  Add closed HH on quarter notes for texture
  Crash accent on bar 2 downbeat

Bar 4-6 (syncopated_kick, intensity=0.8):
  Blast beats continue but with syncopated kick accents
  Tom_edge accents added to tom fills
  Ride bell accents increase

Bar 7 (buildup to chorus, intensity=0.9):
  Rapid tom cascade (tom_edge + crash_choked)
  Build to full-chorus intensity with crescendo fill
```

---

_Design by: Human developer — committed for review_
