"""Metal genre plugin with various metal substyles."""

import random

from midi_drums.config import VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.core.value_objects.generation_parameters import (
    GenerationParameters,
)
from midi_drums.core.value_objects.time_signature import TimeSignature
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.plugins.interfaces.genre_plugin import GenrePlugin


class MetalGenrePlugin(GenrePlugin):
    """Plugin for generating metal drum patterns."""

    @property
    def genre_name(self) -> str:
        return "metal"

    @property
    def supported_styles(self) -> list[str]:
        return [
            "heavy",
            "death",
            "power",
            "progressive",
            "thrash",
            "doom",
            "breakdown",
        ]

    @property
    def intensity_profile(self) -> dict[str, float]:
        """Metal genre intensity characteristics.

        Metal is characterized by high aggression, power, and darkness with
        fast tempos and dense patterns. Complexity varies by subgenre.
        """
        return {
            "aggression": 0.9,  # Very aggressive and heavy
            "speed": 0.8,  # Generally fast tempos (140-200+ BPM)
            "density": 0.8,  # Dense double bass and cymbal work
            "power": 1.0,  # Maximum power in hits
            "complexity": 0.6,  # Moderate complexity (prog metal higher)
            "darkness": 0.9,  # Dark, heavy tonal quality
        }

    def generate_pattern(
        self, section: str, parameters: GenerationParameters
    ) -> Pattern:
        """Generate metal pattern based on section and style."""
        style = parameters.style
        time_sig = TimeSignature(4, 4)  # Most metal is 4/4

        if section == "intro":
            return self._generate_intro_pattern(style, parameters, time_sig)
        elif section == "verse":
            return self._generate_verse_pattern(style, parameters, time_sig)
        elif section == "chorus":
            return self._generate_chorus_pattern(style, parameters, time_sig)
        elif section == "breakdown":
            return self._generate_breakdown_pattern(style, parameters, time_sig)
        elif section in ["bridge", "pre_chorus"]:
            return self._generate_bridge_pattern(style, parameters, time_sig)
        elif section in ["outro", "ending"]:
            return self._generate_outro_pattern(style, parameters, time_sig)
        else:
            # Default to verse pattern
            return self._generate_verse_pattern(style, parameters, time_sig)

    def get_common_fills(self) -> list[Fill]:
        """Get common metal fill patterns."""
        fills = []

        # Tom roll fill
        tom_roll = PatternBuilder("metal_tom_roll")
        for i in range(16):  # 16th notes
            pos = i * 0.25
            instrument = (
                DrumInstrument.SNARE
                if i % 3 == 0
                else (
                    DrumInstrument.MID_TOM
                    if i % 2 == 0
                    else DrumInstrument.FLOOR_TOM
                )
            )
            velocity = 100 + random.randint(-10, 15)
            tom_roll.pattern.add_beat(pos, instrument, velocity)
        fills.append(Fill(tom_roll.build(), 0.8))

        # Blast beat fill
        blast_fill = PatternBuilder("metal_blast_fill")
        for i in range(8):  # 8th notes
            pos = i * 0.5
            blast_fill.kick(pos, 110).snare(pos + 0.25, 115)
        fills.append(Fill(blast_fill.build(), 0.6))

        return fills

    # ------------------------------------------------------------------
    # Pattern Flavors (PLAN #3)
    # ------------------------------------------------------------------

    def get_section_flavors(
        self, section: str, parameters: GenerationParameters
    ) -> list[Pattern]:
        """Return 3+ distinct patterns for every (section, style) combo.

        Flavor 1 is always the base ``generate_pattern()`` result; flavors
        2 and 3 give ComposerV2 real alternatives to rotate bar-by-bar.
        """
        style = parameters.style
        time_sig = TimeSignature(4, 4)

        if section == "verse":
            return [
                self._generate_verse_pattern(style, parameters, time_sig),
                self._death_metal_verse_v2(time_sig) if style == "death" else None,
                self._death_metal_verse_v3(time_sig) if style == "death" else None,
            ]
        elif section == "chorus":
            return [
                self._generate_chorus_pattern(style, parameters, time_sig),
                self._death_metal_chorus_v2(time_sig)
                if style == "death"
                else None,
                self._death_metal_chorus_v3(time_sig)
                if style == "death"
                else None,
            ]
        elif section == "bridge":
            return [
                self._generate_bridge_pattern(style, parameters, time_sig),
                self._bridge_half_time(time_sig),
                self._bridge_tom_buildup(time_sig),
            ]
        elif section == "breakdown":
            return [
                self._generate_breakdown_pattern(style, parameters, time_sig),
                self._breakdown_syncopated(time_sig),
                self._breakdown_half_time(time_sig),
            ]
        elif section in ("intro", "outro"):
            # Intro/outro already vary by style — just return a single variant
            return [
                self._generate_intro_pattern(style, parameters, time_sig)
                if section == "intro"
                else self._generate_outro_pattern(style, parameters, time_sig),
            ]
        # For any other section return a single flavor (no swap needed)
        return [self._generate_verse_pattern(style, parameters, time_sig)]

    def _generate_intro_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate intro pattern - typically builds energy."""
        builder = PatternBuilder(f"metal_{style}_intro", time_sig)

        # Crash on beat 1
        builder.crash(0.0, 115)

        if style == "death":
            # Double kick quarters with snare on 2 and 4
            for i in [0.0, 1.0, 2.0, 3.0]:
                builder.kick(i, 110)
                builder.kick(i + 0.5, 105)  # Double kick
            builder.snare(1.0, 120).snare(3.0, 120)

        else:
            # Standard heavy intro - kick quarters, snare on 3
            for i in [0.0, 1.0, 2.0, 3.0]:
                builder.kick(i, 110)
            builder.snare(2.0, 115)  # Rimshot effect

        return builder.build()

    def _generate_verse_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate verse pattern based on style."""
        builder = PatternBuilder(f"metal_{style}_verse", time_sig)

        if style == "death":
            return self._death_metal_verse(builder, params)
        elif style == "power":
            return self._power_metal_verse(builder, params)
        elif style == "doom":
            return self._doom_metal_verse(builder, params)
        elif style == "progressive":
            return self._progressive_metal_verse(builder, params)
        elif style == "thrash":
            return self._thrash_metal_verse(builder, params)
        else:
            return self._heavy_metal_verse(builder, params)

    def _generate_chorus_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate chorus pattern - typically more intense than verse."""
        builder = PatternBuilder(f"metal_{style}_chorus", time_sig)

        if style == "death":
            return self._death_metal_chorus(builder, params)
        elif style == "power":
            return self._power_metal_chorus(builder, params)
        elif style == "doom":
            return self._doom_metal_chorus(builder, params)
        elif style == "thrash":
            return self._thrash_metal_chorus(builder, params)
        else:
            return self._heavy_metal_chorus(builder, params)

    def _generate_breakdown_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate breakdown pattern - syncopated, heavy."""
        builder = PatternBuilder(f"metal_{style}_breakdown", time_sig)

        # Breakdown pattern: kick on 1, 2.5, 3.5
        builder.kick(0.0, 120)
        builder.kick(1.5, 115)
        builder.kick(2.5, 115)

        # Rimshot on 2
        builder.pattern.add_beat(2.0, DrumInstrument.RIM, 115)

        return builder.build()
        # Toms for groove
        builder.tom(1.0, "MID", VELOCITY.TOM_HEAVY - 10)
        builder.tom(3.0, "FLOOR", VELOCITY.TOM_HEAVY - 10)

        # Choked crash accents on downbeat (sharp cutoff "chick")
        builder.crash_choked(0.0, "A", VELOCITY.CRASH_ACCENT)

        return builder.build()

    def _generate_bridge_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate bridge pattern - often simpler or different from
        verse/chorus."""
        # For simplicity, use a modified verse pattern
        pattern = self._generate_verse_pattern(style, params, time_sig)
        pattern.name = f"metal_{style}_bridge"

        # Reduce complexity slightly
        reduced_beats = []
        hihat_instruments = {
            DrumInstrument.CLOSED_HH,
            DrumInstrument.CLOSED_HH_EDGE,
            DrumInstrument.CLOSED_HH_TIP,
            DrumInstrument.TIGHT_HH_EDGE,
            DrumInstrument.TIGHT_HH_TIP,
            DrumInstrument.OPEN_HH,
            DrumInstrument.OPEN_HH_1,
            DrumInstrument.OPEN_HH_2,
            DrumInstrument.OPEN_HH_3,
            DrumInstrument.OPEN_HH_MAX,
        }
        for beat in pattern.beats:
            if beat.instrument in hihat_instruments:
                # Reduce hi-hat density
                if beat.position % 1.0 == 0:  # Keep only quarter notes
                    reduced_beats.append(beat)
            else:
                reduced_beats.append(beat)

        # Safety: Ensure pattern never empty (prevents downstream plugin errors)
        if not reduced_beats:
            return pattern  # Return original unfiltered pattern

        pattern.beats = reduced_beats
        return pattern

    def _generate_outro_pattern(
        self, style: str, params: GenerationParameters, time_sig: TimeSignature
    ) -> Pattern:
        """Generate outro pattern.

        Uses ride bell accents and choked crashes for dramatic ending.
        """
        builder = PatternBuilder(f"metal_{style}_outro", time_sig)

        # Descending tom fill pattern
        builder.tom(0.0, "FLOOR", VELOCITY.TOM_HEAVY + 5)
        builder.tom(1.0, "MID", VELOCITY.TOM_HEAVY)
        builder.snare(2.0, VELOCITY.SNARE_ACCENT)
        builder.tom(3.0, "FLOOR", VELOCITY.TOM_HEAVY + 5)

        # Choked crash for dramatic ending cutoff (sharp "chick")
        builder.crash_choked(3.75, "A", VELOCITY.CRASH_HEAVY)

        return builder.build()

    def _thrash_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Thrash metal verse - fast, aggressive, driving."""
        # Driving kick pattern with double-time feel
        for i in [0.0, 0.5, 1.5, 2.0, 2.5, 3.5]:
            builder.kick(i, VELOCITY.KICK_HEAVY + random.randint(-8, 8))

        # Snare on 2 and 4
        builder.snare(1.0, VELOCITY.SNARE_HEAVY)
        builder.snare(3.0, VELOCITY.SNARE_HEAVY)

        # Tight HH driving pattern (AD2 zone 91) - crisp no wash for fast sections
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)

        return builder.build()

    def _heavy_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Classic heavy metal verse pattern."""
        # Kick on 1, 1.75, 3
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(0.75, VELOCITY.KICK_NORMAL)
        builder.kick(2.0, VELOCITY.KICK_HEAVY)

        # Snare on 2 and 4
        builder.snare(1.0, VELOCITY.SNARE_HEAVY)
        builder.snare(3.0, VELOCITY.SNARE_HEAVY)

        return builder.build()

    def _death_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Death metal verse with blast beats."""
        # Blast beat pattern - alternating kick/snare on 16ths
        for i in range(8):
            pos = i * 0.5
            builder.kick(pos, 110 + random.randint(-5, 10))
            builder.snare(pos + 0.25, 115 + random.randint(-5, 10))

        # Tight HH (AD2 zone 91) — dry pencil attack for blast-beat sections
        # where wash from standard hi-hat would muddy the texture
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)

        # Sparse crashed cymbal for textural punctuation
        builder.crash_choked(2.0, "B", VELOCITY.CRASH_ACCENT)

        return builder.build()

    def _power_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Power metal verse - driving and melodic."""
        # Steady kick quarters
        for i in [0.0, 1.0, 2.0, 3.0]:
            builder.kick(i, VELOCITY.KICK_NORMAL)

        # Snare on 2 and 4 with some ghost notes
        builder.snare(1.0, VELOCITY.SNARE_HEAVY)
        builder.snare(3.0, VELOCITY.SNARE_HEAVY)
        builder.snare(1.5, VELOCITY.SNARE_GHOST)  # Ghost note

        return builder.build()

    def _doom_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Doom metal verse - slow and heavy."""
        # Simple but heavy kick pattern
        builder.kick(0.0, 120)
        builder.kick(2.0, 120)

        # Powerful snare on 2 and 4
        builder.snare(1.0, 125)
        builder.snare(3.0, 125)

        # Tight HH (AD2 zone 91) — dry pencil attack for crushing precision at slow tempos
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)

        # Ride bell accents on off-beats for textural atmosphere
        builder.ride_bell(1.5, VELOCITY.RIDE_BELL + random.randint(-2, 4))
        builder.ride_bell(3.5, VELOCITY.RIDE_BELL + random.randint(-2, 4))

        return builder.build()

    def _doom_metal_chorus(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Doom metal chorus - heavier and more intense than verse."""
        # More aggressive kick pattern
        builder.kick(0.0, 125)
        builder.kick(1.5, 115)
        builder.kick(2.0, 125)
        builder.kick(3.5, 115)

        # Powerful snare on 2 and 4
        builder.snare(1.0, 127)
        builder.snare(3.0, 127)

        # Crash on 1 for emphasis
        builder.crash(0.0, 115)

        # Tight HH (AD2 zone 91) — dry pencil attack suits the crushing weight of doom
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)

        return builder.build()

    def _progressive_metal_verse(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Progressive metal verse - complex timing."""
        # Complex kick pattern
        for pos in [0.0, 0.75, 1.5, 2.25, 3.0]:
            builder.kick(pos, 105 + random.randint(-5, 10))

        # Snare on traditional beats plus syncopation
        builder.snare(1.0, 115)
        builder.snare(2.75, 100)  # Syncopated
        builder.snare(3.0, 115)

        # Ride bell accents on off-beats (progressive/metalcore texture)
        builder.ride_bell(
            1.5,
            VELOCITY.RIDE_BELL_ACCENT + random.randint(-2, 4),
        )
        builder.ride_bell(
            3.5,
            VELOCITY.RIDE_BELL_ACCENT + random.randint(-2, 4),
        )

        # Choked crash on major downbeats (sharp "chick" cutoff)
        builder.crash_choked(0.0, "A", VELOCITY.CRASH_HEAVY)
        builder.crash_choked(2.5, "C", VELOCITY.CRASH_ACCENT)

        return builder.build()

    def _thrash_metal_chorus(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Thrash metal chorus - even more aggressive than verse.

        Uses tight HH on fast comping, ride bell accents for texture,
        and choked crashes on major beats for punchy cutoff.
        """
        # Fast kick double-time pattern
        for i in range(8):
            builder.kick(i * 0.5, VELOCITY.KICK_HEAVY + random.randint(-10, 8))

        # Snare on 2 and 4 with rimshot accents
        builder.snare(1.0, VELOCITY.SNARE_HEAVY)
        builder.snare_rimshot(3.0, min(VELOCITY.SNARE_RIMSHOT + 5, 127))

        # Tight HH rapid comping (AD2 zone 91) on every 8th note
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)

        # Ride bell accents on off-beats for aggressive textural variety
        builder.pattern.add_beat(
            1.5,
            DrumInstrument.RIDE_BELL,
            VELOCITY.RIDE_BELL_ACCENT + random.randint(-3, 4),
        )
        builder.pattern.add_beat(
            3.5,
            DrumInstrument.RIDE_BELL,
            VELOCITY.RIDE_BELL_ACCENT + random.randint(-3, 4),
        )

        # Choked crash on major downbeats (sharp "chick" cutoff)
        builder.crash_choked(0.0, "A", VELOCITY.CRASH_HEAVY)
        builder.crash_choked(2.0, "B", VELOCITY.CRASH_ACCENT)

        return builder.build()

    def _heavy_metal_chorus(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Heavy metal chorus - double kick shuffle."""
        # Double kick pattern
        for beat in range(4):
            base_pos = beat * 1.0
            builder.kick(base_pos, 110)
            builder.kick(base_pos + 0.5, 105)

        # Snare on 2 and 4
        builder.snare(1.0, 120)
        builder.snare(3.0, 120)

        # Choked crash on downbeats (sharp "chick" cutoff)
        builder.crash_choked(0.0, "A", VELOCITY.CRASH_HEAVY)
        builder.crash_choked(2.0, "B", VELOCITY.CRASH_ACCENT)

        # Ride bell accents on off-beats (progressive/metalcore texture)
        builder.ride_bell(
            1.5,
            VELOCITY.RIDE_BELL + random.randint(-2, 4),
        )
        builder.ride_bell(
            3.5,
            VELOCITY.RIDE_BELL + random.randint(-2, 4),
        )

        return builder.build()

    def _death_metal_chorus(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Death metal chorus - intense blast beats."""
        # Faster blast beat for chorus intensity
        for i in range(16):
            pos = i * 0.25
            if i % 2 == 0:
                builder.kick(pos, 115)
            else:
                builder.snare(pos + 0.25, 120)

        # Choked crash accents on major downbeats (sharp "chick" cutoff)
        builder.crash_choked(0.0, "A", VELOCITY.CRASH_HEAVY)
        builder.crash_choked(
            4.0 if params.complexity > 0.7 else 2.0, "B", VELOCITY.CRASH_ACCENT
        )

        return builder.build()

    def _power_metal_chorus(
        self, builder: PatternBuilder, params: GenerationParameters
    ) -> Pattern:
        """Power metal chorus - anthemic and driving."""
        # Driving double kick
        for beat in range(4):
            builder.kick(beat, 110)
            if beat < 3:  # Don't double the last beat
                builder.kick(beat + 0.5, 100)

        # Strong snare backbeat
        builder.snare(1.0, 120)
        builder.snare(3.0, 120)

        # Crash on 1 and 3 for power
        builder.crash(0.0, 115)
        builder.crash(2.0, 110)

        # Ride bell accents for texture (progressive/metalcore) + tom_edge for attack clarity
        builder.ride_bell(1.5, 90)
        builder.ride_bell(3.5, 90)
        builder.tom_edge(0.5, "MID", VELOCITY.TOM_HEAVY - 5)
        builder.tom_edge(2.5, "FLOOR", VELOCITY.TOM_ACCENT)

        return builder.build()

    # ------------------------------------------------------------------
    # Flavor v2/v3 helpers for death metal verse + chorus
    # ------------------------------------------------------------------

    def _death_metal_verse_v2(self, time_sig: TimeSignature) -> Pattern:
        """Flavor 2 — sparse blast (fewer blast-beat hits)."""
        builder = PatternBuilder("death_metal_verse_sparse", time_sig)
        # Only every other 8th note gets a blast hit
        for i in [0.0, 1.0, 2.0, 3.0]:
            builder.kick(i, 110)
            builder.snare(i + 0.5, 110)
        # Tight HH on quarters only (much sparser than base)
        for i in range(4):
            builder.tight_hh(i * 1.0, open=False)
        return builder.build()

    def _death_metal_verse_v3(self, time_sig: TimeSignature) -> Pattern:
        """Flavor 3 — syncopated kick with lighter snare."""
        builder = PatternBuilder("death_metal_verse_syncopated", time_sig)
        for pos in [0.0, 0.75, 1.5, 2.25, 3.0]:
            builder.kick(pos, 115)
        # Lighter snare on off-beats
        builder.snare(0.5, 100).snare(2.0, 100).snare(3.5, 100)
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)
        return builder.build()

    def _death_metal_chorus_v2(self, time_sig: TimeSignature) -> Pattern:
        """Flavor 2 — double-kick heavy, fewer blasts."""
        builder = PatternBuilder("death_metal_chorus_dk", time_sig)
        for beat in range(4):
            base = beat * 1.0
            builder.kick(base, 120).kick(base + 0.5, 115)
        builder.snare(1.0, 120).snare(3.0, 120)
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)
        return builder.build()

    def _death_metal_chorus_v3(self, time_sig: TimeSignature) -> Pattern:
        """Flavor 3 — blast on off-beats with tom accents."""
        builder = PatternBuilder("death_metal_chorus_tom", time_sig)
        for i in range(8):
            pos = i * 0.5
            builder.kick(pos, 115)
            if i % 2 == 0:
                builder.snare(pos + 0.25, 120)
        # Tom edge accents
        builder.tom_edge(0.25, "MID", VELOCITY.TOM_HEAVY)
        builder.tom_edge(1.25, "FLOOR", VELOCITY.TOM_ACCENT)
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)
        return builder.build()

    def _bridge_half_time(self, time_sig: TimeSignature) -> Pattern:
        """Bridge flavor — half-time groove."""
        builder = PatternBuilder("bridge_half_time", time_sig)
        builder.kick(0.0, 120).kick(2.5, 115)
        builder.snare(1.5, 125)
        for i in range(4):
            builder.tight_hh(i * 1.0, open=False)
        return builder.build()

    def _bridge_tom_buildup(self, time_sig: TimeSignature) -> Pattern:
        """Bridge flavor — tom build-up toward next section."""
        builder = PatternBuilder("bridge_tom_build", time_sig)
        for i in range(4):
            pos = i * 0.5
            builder.snare(pos, 100 + i * 8)
        # Sparse kick on off-beats
        builder.kick(0.25, 95).kick(1.75, 100).kick(3.25, 105)
        for i in range(8):
            builder.tight_hh(i * 0.5, open=False)
        return builder.build()

    def _breakdown_syncopated(self, time_sig: TimeSignature) -> Pattern:
        """Breakdown flavor — heavily syncopated kick."""
        builder = PatternBuilder("breakdown_syncopated", time_sig)
        for pos in [0.0, 0.75, 1.5, 2.0, 2.75, 3.5]:
            builder.kick(pos, 125)
        # Snare ghost notes + rimshot
        builder.snare(1.0, 95).snare_rimshot(3.0, 115)
        for i in range(4):
            builder.tight_hh(i * 1.0, open=False)
        return builder.build()

    def _breakdown_half_time(self, time_sig: TimeSignature) -> Pattern:
        """Breakdown flavor — half-time with heavy tom accents."""
        builder = PatternBuilder("breakdown_half_time", time_sig)
        builder.kick(0.0, 130).kick(2.5, 120)
        for beat in range(4):
            if beat % 2 == 1:
                builder.tom_edge(beat + 0.25, "MID" if beat == 1 else "FLOOR", VELOCITY.TOM_HEAVY - 10)
        builder.snare(1.5, 130)
        for i in range(4):
            builder.tight_hh(i * 1.0, open=False)
        return builder.build()
