"""Danny Carey drummer plugin - Tool style using full AD2 kit vocabulary.

Fills now cascade through ALL toms (HIGH→MID→LOW→FLOOR), use deep floor
toms for sacred geometry patterns, and layer cymbal_4/5 crashes for the
heavy Tool-era sound. Also uses tom_edge rimshots for textured fills and
cymbal_choke for tight transitions.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class CareyPlugin(DrummerPlugin):
    """Danny Carey (Tool) drummer style plugin.

    Characteristics:
    - Polyrhythmic complexity (3 vs 2 quintuplets, odd meters)
    - Deep tom-focused patterns with cascading fills through ALL toms
    - Custom electronic drum pad textures (Mandala pads triggering tabla/octoban samples)
    - Spacious grooves with intentional space between hits
    - Complex pentatonic/quintuplet accent fills
    - Long-sustain cymbal swells and effects
    """

    @property
    def drummer_name(self) -> str:
        return "carey"

    @property
    def preferred_genres(self) -> list[str]:
        return [
            "metal",
            "rock",
            "progressive",
            "alternative",
            "hard_rock",
            "post_metal",
            "psychedelic",
        ]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Danny Carey's signature style to a pattern."""
        styled_pattern = pattern.copy()
        styled_pattern.name = f"{pattern.name}_carey"

        beat_count = len(pattern.beats)
        max_new_beats = 12
        if beat_count <= 4:
            scale_factor = 1.0
        elif beat_count <= 8:
            scale_factor = 0.75
        elif beat_count <= 16:
            scale_factor = 0.5
        else:
            scale_factor = 0.3

        max_new_beats = int(max_new_beats * scale_factor)
        current_count = [0]

        def _track(n):
            if n > max(0, max_new_beats - current_count[0]):
                return max(0, max_new_beats - current_count[0])
            current_count[0] += n
            return n

        styled_pattern = self._add_polyrhythmic_kick(styled_pattern, _track)
        styled_pattern = self._add_deep_tom_patterns(styled_pattern, _track)
        styled_pattern = self._apply_tool_groove_space(styled_pattern)
        styled_pattern = self._add_pentatonic_accent_fills(
            styled_pattern, _track
        )
        styled_pattern = self._add_cymbal_swell_effects(styled_pattern, _track)

        return styled_pattern

    # Helper methods for apply_style
    def _add_polyrhythmic_kick(self, pattern: Pattern, track) -> Pattern:
        """Add Danny Carey's signature polyrhythmic kick counterpoint.

        Tool-style kicks often cycle in groups of 5 (quintuplets) or
        odd meters against the genre's primary grid.
        """
        from midi_drums.config import TIMING, VELOCITY

        beat_count = track(6)
        if beat_count == 0:
            return pattern

        # Poly Kick A: quintuplet cycle (5 hits spread across bar)
        for i in range(beat_count):
            pos = (i * TIMING.QUARTER) / 2 + (i % 2) * TIMING.SIXTEENTH
            if pos < 4.0:
                pattern.add_beat(
                    pos,
                    InstrumentRegistry.get("kick"),
                    VELOCITY.KICK_HEAVY - 10,
                )

        return pattern

    def _add_deep_tom_patterns(self, pattern, track):
        """Add Danny Carey's deep tom layering across ALL toms.

        Tool-style grooves often place a secondary tom pulse that cycles
        HIGH→MID→LOW→FLOOR, creating a melodic undercurrent beneath the
        genre's primary kick/snare skeleton.
        """
        beat_budget = track(4)
        if beat_budget == 0:
            return pattern

        for i in range(beat_budget):
            pos = TIMING.EIGHTH_TRIPLET * (1 + i * 2)
            if pos < 4.0:
                pattern.add_beat(
                    pos,
                    InstrumentRegistry.get(f"tom_{i % 4 + 1}_open_hit"),
                    VELOCITY.TOM_NORMAL + random.randint(-5, 10),
                )

        return pattern

    def _apply_tool_groove_space(self, pattern):
        """Apply Tool-era groove spacing.

        Carey often shifts a hit by a few ms to create intentional space,
        or removes redundant hits when the kit is overcrowded. Here we
        nudged the first tom beat from _add_deep_tom_patterns slightly
        ahead (play it "in front") for a pushy, propulsive feel.
        """
        n = len(pattern.beats)
        if n < 2:
            return pattern

        # Find the first tom beat added by _add_deep_tom_patterns and nudge
        # it ahead by ~12 ms for that Carey "in-your-face" groove push.
        first_tom_hit = None
        for beat in pattern.beats:
            inst_name = str(beat.instrument)
            if "tom_" in inst_name and first_tom_hit is None:
                first_tom_hit = beat
                break

        if first_tom_hit is not None and first_tom_hit.position > 0.01:
            first_tom_hit.position -= 0.012  # ~12 ms ahead

        return pattern

    def _add_pentatonic_accent_fills(self, pattern, track):
        """Add pentatonic accent fills across ALL toms.

        Carey frequently uses pentatonic sequences (5 notes = 5 toms,
        cycling) as accent patterns. We use the 4-tom cycle and pick
        a pentatonic rhythm offset so it doesn't double as the base groove.
        """
        beat_budget = track(3)
        if beat_budget == 0:
            return pattern

        for i in range(beat_budget):
            pos = TIMING.QUARTER * (1 + i) + TIMING.EIGHTH_TRIPLET
            if pos < 4.0:
                pattern.add_beat(
                    pos,
                    InstrumentRegistry.get(f"tom_{i % 4 + 1}_open_hit"),
                    VELOCITY.TOM_ACCENT,
                )

        return pattern

    def _add_cymbal_swell_effects(self, pattern, track):
        """Add long-sustain cymbal swell / texture hits.

        Carey layers crash_5/6 swells at the edges of phrases for the
        heavy Tool-era sound.  We add a single large-cym swell near bar end.
        """
        beat_budget = track(1)
        if beat_budget == 0:
            return pattern

        # Place at the very end of the bar for a phrase-ending swell
        pattern.add_beat(
            3.875,  # just before bar-line
            InstrumentRegistry.get("cymbal_6_hit"),
            VELOCITY.CRASH_ACCENT - 10,
        )

        return pattern

    def get_signature_fills(self) -> list[Fill]:
        """Return Danny Carey's signature fill patterns using full AD2 kit.

        All fills cascade through ALL toms (HIGH→MID→LOW→FLOOR), use deep
        floor toms for sacred geometry, and layer cymbal_4/5 crashes for
        the heavy Tool-era sound. tom_edge rimshots add texture.
        """
        fills = []

        # Quintuplet tom cascade — ALL toms (HIGH→MID→LOW→FLOOR cycling)
        quintuplet_fill = Fill(
            pattern=self._create_quintuplet_tom_cascade(),
            trigger_probability=0.85,
            section_position="end",
        )
        fills.append(quintuplet_fill)

        # Polyrhythmic floor tom build-up — deep FLOOR focus
        polyrhythmic_fill = Fill(
            pattern=self._create_polyrhythmic_buildup(),
            trigger_probability=0.75,
            section_position="middle",
        )
        fills.append(polyrhythmic_fill)

        # Mandala pad / tabla-sample fill — tom_edge rimshots + cymbal_choke
        mandala_tabla_fill = Fill(
            pattern=self._create_mandala_tabla_fill(),
            trigger_probability=0.7,
            section_position="middle",
        )
        fills.append(mandala_tabla_fill)

        # Odd-meter kick counterpoint — full kit with crash_5 punctuation
        odd_meter_kick_fill = Fill(
            pattern=self._create_odd_meter_kick_counterpoint(),
            trigger_probability=0.65,
            section_position="middle",
        )
        fills.append(odd_meter_kick_fill)

        # Sacred-geometry tom pattern — pentatonic cascade through ALL toms
        sacred_geometry_fill = Fill(
            pattern=self._create_sacred_geometry_tom_fill(),
            trigger_probability=0.6,
            section_position="end",
        )
        fills.append(sacred_geometry_fill)

        # Pentatonic kick accent — full kit with cymbal_4 crash
        pentatonic_kick_fill = Fill(
            pattern=self._create_pentatonic_kick_accent(),
            trigger_probability=0.55,
            section_position="end",
        )
        fills.append(pentatonic_kick_fill)

        # Deep tom-to-floor cascade — FLOOR emphasis with crash_6 resolution
        deep_cascade_fill = Fill(
            pattern=self._create_deep_tom_floor_cascade(),
            trigger_probability=0.7,
            section_position="end",
        )
        fills.append(deep_cascade_fill)

        # Polyrhythmic rimshot excursion — tom_edge across all toms
        polyrhythm_rimshot_fill = Fill(
            pattern=self._create_polyrhythm_rimshot_excursion(),
            trigger_probability=0.65,
            section_position="middle",
        )
        fills.append(polyrhythm_rimshot_fill)

        return fills

    def _create_quintuplet_tom_cascade(self) -> Pattern:
        """Quintuplet cascade through ALL toms (HIGH→MID→LOW→FLOOR cycling)."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_quintuplet_cascade")
        toms = ["HIGH", "MID", "LOW", "FLOOR"]
        for i in range(8):
            pos = i * TIMING.SIXTEENTH_QUINTUPLET
            variant = toms[i % 4]
            builder.tom(
                pos, variant, min(VELOCITY.TOM_HEAVY + (i % 3) * 5, 127)
            )
        # Heavy crash_5 resolution
        builder.crash(4.0, "5")
        return builder.build()

    def _create_polyrhythmic_buildup(self) -> Pattern:
        """Polyrhythmic floor tom build-up with FOCUS on deep FLOOR toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_polyrhythmic_floor")
        # Alternating HIGH and FLOOR (Tool's signature low-to-deep sound)
        for i in range(8):
            pos = i * TIMING.EIGHTH_TRIPLET
            variant = "FLOOR" if i % 2 == 0 else "MID"
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 15), 127),
            )
        # Deep FLOOR tom final hit + cymbal_4 crash
        builder.tom(
            TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET,
            "FLOOR",
            min(VELOCITY.TOM_ACCENT, 127),
        )
        builder.crash(4.0, "4")
        return builder.build()

    def _create_mandala_tabla_fill(self) -> Pattern:
        """Mandala pad / tabla-sample fill using tom_edge rimshots + cymbal_choke."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_mandala_tabla")
        # Rimshot-based texture across toms (simulating Mandala pad)
        for i in range(6):
            pos = i * TIMING.EIGHTH_TRIPLET
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-8, 10), 127),
            )
        # Tight cymbal_choke for percussive punctuation
        builder.crash_choked(3.5, "2", VELOCITY.CRASH_ACCENT - 10)
        return builder.build()

    def _create_odd_meter_kick_counterpoint(self) -> Pattern:
        """Odd-meter kick counterpoint with full-kit crash_5 punctuation."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_odd_meter_kick")
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.EIGHTH_TRIPLET * 2, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF + TIMING.EIGHTH_TRIPLET, VELOCITY.KICK_HEAVY)
        # Descending toms with FLOOR emphasis
        for i in range(4):
            pos = TIMING.QUARTER * 2 + i * TIMING.SIXTEENTH
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i]
            builder.tom(pos, variant, VELOCITY.TOM_HEAVY - (i * 5))
        # Heavy crash_5 punctuation
        builder.crash(TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "5")
        return builder.build()

    def _create_sacred_geometry_tom_fill(self) -> Pattern:
        """Sacred geometry pentatonic cascade through ALL toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_sacred_geometry")
        # Pentatonic sequence across all 4 toms
        for i in range(8):
            pos = i * TIMING.EIGHTH_TRIPLET
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos, variant, min(VELOCITY.TOM_HEAVY + (i % 5) * 3, 127)
            )
        # Resolve with cymbal_6 (largest/deepest crash)
        builder.crash(4.0, "6")
        return builder.build()

    def _create_pentatonic_kick_accent(self) -> Pattern:
        """Pentatonic kick accent pattern with full-kit crash_4/5 layering."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_pentatonic_kick")
        # Complex kick counterpoint across the bar
        for i in range(10):
            pos = TIMING.EIGHTH_TRIPLET * (i // 2)
            if i % 3 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                # Tom accents between kicks using varied toms
                variant = ["HIGH", "MID"][i % 2]
                builder.tom(
                    pos + TIMING.SIXTEENTH / 2, variant, VELOCITY.TOM_NORMAL
                )
        # Double crash layering (Tool-era signature)
        builder.crash(3.875, "4")
        builder.crash_choked(3.95, "5")
        return builder.build()

    def _create_deep_tom_floor_cascade(self) -> Pattern:
        """Deep tom-to-floor cascade — ALL toms resolving to FLOOR + cymbal_6."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_deep_floor_cascade")
        # Full descending cascade through ALL toms (HIGH→FLOOR)
        for i in range(5):
            pos = i * TIMING.EIGHTH_TRIPLET
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 15), 127),
            )
        # Deep FLOOR tom final hit with massive crash_6
        builder.tom(TIMING.HALF * 3, "FLOOR", min(VELOCITY.TOM_ACCENT, 127))
        builder.crash(TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, "6")
        return builder.build()

    def _create_polyrhythm_rimshot_excursion(self) -> Pattern:
        """Polyrhythmic rimshot excursion — tom_edge across all toms."""
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_polyrhythm_rimshot")
        # Tom edge rimshots across ALL toms (rimshot-based polyrhythms)
        for i in range(8):
            pos = i * TIMING.EIGHTH_TRIPLET
            variant = ["HIGH", "MID", "LOW", "FLOOR"][i % 4]
            builder.tom_edge(
                pos,
                variant,
                min(VELOCITY.TOM_HEAVY + random.randint(-10, 15), 127),
            )
        # Heavy crash_5 resolution
        builder.crash(4.0, "5")
        return builder.build()
