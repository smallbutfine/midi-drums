"""
Danny Carey drummer plugin - Tool style.

Implements Danny Carey's signature polyrhythmic, odd-meter, tom-heavy approach
to progressive and alternative metal. Known for his deep tom work, complex
polyrhythms (3 vs 2 quintuplets), custom electronic drum pad influences,
and the spacious, heavy "Tool groove" that defines albums like Lateralus and
Fear Inoculum.
"""

import random

from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class CareyPlugin(DrummerPlugin):
    """Danny Carey (Tool) drummer style plugin.

    Characteristics:
    - Polyrhythmic complexity (3 vs 2 quintuplets, odd meters)
    - Deep tom-focused patterns with cascading fills
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
        """Apply Danny Carey's signature style to a pattern.

        NOTE: Max new-beats is capped at 12 to prevent density explosion
        when combined with ComposerV2's bar-by-bar loop.
        Args:
            pattern: Base pattern to modify

        Returns:
            Pattern with Carey's characteristic modifications
        """
        styled_pattern = pattern.copy()
        styled_pattern.name = f"{pattern.name}_carey"

        # Scale additive density inversely to input pattern density.
        # Sparse base patterns get MORE layers to fill out the groove;
        # dense base patterns get FEWER layers so structural differences
        # between flavors aren't drowned out by uniform additive beats.
        beat_count = len(pattern.beats)
        max_new_beats = 12
        if beat_count <= 4:
            scale_factor = 1.0      # Very sparse → full density
        elif beat_count <= 8:
            scale_factor = 0.75     # Medium sparse → slightly reduced
        elif beat_count <= 16:
            scale_factor = 0.5      # Dense → half density to preserve structure
        else:
            scale_factor = 0.3      # Very dense → minimal additions

        max_new_beats = int(max_new_beats * scale_factor)
        current_count = [0]  # Use list for mutability in closures

        def _track(n):
            """Track and cap added beat count."""
            if n > max(0, max_new_beats - current_count[0]):
                return max(0, max_new_beats - current_count[0])
            current_count[0] += n
            return n

        # 1. Add polyrhythmic quintuplet kick counterpoint (3 vs 2)
        styled_pattern = self._add_polyrhythmic_kick(styled_pattern, _track)

        # 2. Deep tom-heavy accent patterns and cascading fills
        styled_pattern = self._add_deep_tom_patterns(styled_pattern, _track)

        # 3. Apply the "Tool groove" - spaciousness with intentional space
        styled_pattern = self._apply_tool_groove_space(styled_pattern)

        # 4. Complex pentatonic/quintuplet accent fills between beats
        styled_pattern = self._add_pentatonic_accent_fills(
            styled_pattern, _track
        )

        # 5. Cymbal swells and effects (simulated with long sustain)
        styled_pattern = self._add_cymbal_swell_effects(styled_pattern, _track)

        return styled_pattern

    def get_signature_fills(self) -> list[Fill]:
        """Return Danny Carey's signature fill patterns."""
        fills = []

        # Quintuplet tom cascade (his most recognizable fill)
        quintuplet_fill = Fill(
            pattern=self._create_quintuplet_tom_cascade(),
            trigger_probability=0.85,
            section_position="end",
        )
        fills.append(quintuplet_fill)

        # Polyrhythmic floor tom build-up
        polyrhythmic_fill = Fill(
            pattern=self._create_polyrhythmic_buildup(),
            trigger_probability=0.75,
            section_position="middle",
        )
        fills.append(polyrhythmic_fill)

        # Custom Mandala pad / tabla-sample fill (replaces prior "ethnic/taiko")
        mandala_tabla_fill = Fill(
            pattern=self._create_mandala_tabla_fill(),
            trigger_probability=0.7,
            section_position="middle",
        )
        fills.append(mandala_tabla_fill)

        # Odd-meter kick counterpoint fill (Tool-era signature technique)
        odd_meter_kick_fill = Fill(
            pattern=self._create_odd_meter_kick_counterpoint(),
            trigger_probability=0.65,
            section_position="middle",
        )
        fills.append(odd_meter_kick_fill)

        # Deep sacred-geometry tom pattern (pentatonic tom cascades)
        sacred_geometry_fill = Fill(
            pattern=self._create_sacred_geometry_tom_fill(),
            trigger_probability=0.6,
            section_position="end",
        )
        fills.append(sacred_geometry_fill)

        # Pentatonic kick accent fill (Tool-era polyrhythmic approach)
        pentatonic_kick_fill = Fill(
            pattern=self._create_pentatonic_kick_accent(),
            trigger_probability=0.55,
            section_position="middle",
        )
        fills.append(pentatonic_kick_fill)

        # Cymbal swell pattern for atmospheric transition
        cymbal_fill = Fill(
            pattern=self._create_cymbal_swell_pattern(),
            trigger_probability=0.60,
            section_position="start",
        )
        fills.append(cymbal_fill)

        return fills

    def _apply_tool_groove_space(self, pattern: Pattern) -> Pattern:
        """Apply the "Tool groove" - spaciousness with intentional space."""
        for beat in pattern.beats:
            if beat.instrument == DrumInstrument.KICK:
                beat.velocity = min(127, beat.velocity + 15)
                beat.duration = max(0.3, beat.duration * 1.4)
            elif beat.instrument == DrumInstrument.SNARE:
                beat.velocity = min(127, beat.velocity + 10)
            elif beat.instrument in [
                DrumInstrument.FLOOR_TOM,
                DrumInstrument.MID_TOM,
            ]:
                beat.duration = max(0.4, beat.duration * 2.0)
        return pattern

    # --- Style application methods ---

    def _add_polyrhythmic_kick(self, pattern: Pattern, track_fn) -> Pattern:
        """Add polyrhythmic kick counterpoint (3 vs 2 quintuplets)."""
        new_beats = list(pattern.beats)

        for beat in pattern.beats:
            if beat.instrument == DrumInstrument.KICK:
                pos = beat.position
                for i in range(1, 4):  # At most 3 extra kicks per original
                    added = track_fn(1)  # Check/track before adding
                    if added <= 0:
                        break
                    poly_pos = pos + (i * 0.267)
                    new_beats.append(
                        Beat(
                            position=poly_pos,
                            instrument=beat.instrument,
                            velocity=min(
                                127, beat.velocity + random.randint(-8, 8)
                            ),
                            duration=beat.duration * 0.9,
                        )
                    )

        pattern.beats = new_beats
        return pattern

    def _add_deep_tom_patterns(self, pattern: Pattern, track_fn) -> Pattern:
        """Add deep tom-focused accents and cascades."""
        new_beats = list(pattern.beats)

        for i in range(8):
            pos = i * 0.5
            if track_fn(1) <= 0:
                break
            if random.random() < 0.2:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=DrumInstrument.FLOOR_TOM,
                        velocity=90 + random.randint(-10, 25),
                        duration=0.8,
                    )
                )

        for i in range(4):
            pos = i + 0.5
            if track_fn(1) <= 0:
                break
            if random.random() < 0.15:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=DrumInstrument.MID_TOM,
                        velocity=80 + random.randint(-5, 20),
                        duration=0.4,
                    )
                )

        pattern.beats = new_beats
        return pattern

    def _add_pentatonic_accent_fills(
        self, pattern: Pattern, track_fn
    ) -> Pattern:
        """Add pentatonic/quintuplet accent fills between beats."""
        new_beats = list(pattern.beats)

        for i in range(5):
            pos = i * 0.8
            if track_fn(1) <= 0:
                break
            if random.random() < 0.3:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=DrumInstrument.SNARE,
                        velocity=100 + random.randint(-10, 25),
                        duration=0.1,
                    )
                )

        for i in range(3):
            pos = i * 1.2
            if track_fn(1) <= 0:
                break
            if random.random() < 0.15:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=(
                            DrumInstrument.FLOOR_TOM
                            if i < 2
                            else DrumInstrument.MID_TOM
                        ),
                        velocity=95 + random.randint(-5, 20),
                        duration=0.3,
                    )
                )

        pattern.beats = new_beats
        return pattern

    def _add_cymbal_swell_effects(self, pattern: Pattern, track_fn) -> Pattern:
        """Add cymbal swells and effects (simulated)."""
        new_beats = list(pattern.beats)

        for pos in [0.0, 2.0]:
            if track_fn(1) <= 0:
                break
            if random.random() < 0.35:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=DrumInstrument.CRASH,
                        velocity=100 + random.randint(-10, 20),
                        duration=2.0,
                    )
                )

        for i in range(8):
            pos = i * 0.5
            if track_fn(1) <= 0:
                break
            if random.random() < 0.1:
                eth_inst = random.choice(
                    [DrumInstrument.CHINA, DrumInstrument.RIDE_BELL]
                )
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=eth_inst,
                        velocity=85 + random.randint(-10, 15),
                        duration=0.6,
                    )
                )

        pattern.beats = new_beats
        return pattern

    # --- Signature fill methods ---

    def _create_quintuplet_tom_cascade(self) -> Pattern:
        """Create signature quintuplet tom cascade fill.

        The quintuplet pattern is Carey's most recognizable fill technique,
        often starting from floor tom and cascading up to mid/toms.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_quintuplet_tom_cascade")

        # Signature Quintuplet Tom Cascade (5 notes in 4/4 space)
        sequence = [
            # Floor tom foundation building upward
            (0.0, DrumInstrument.FLOOR_TOM, 120),
            (0.8, DrumInstrument.FLOOR_TOM, 115),
            # Mid tom cascade building intensity
            (1.6, DrumInstrument.MID_TOM, 110),
            (2.4, DrumInstrument.MID_TOM, 105),
            # Kick transition with crash accent
            (3.2, DrumInstrument.KICK, 100),
            (4.0, DrumInstrument.FLOOR_TOM, 125),
            (4.8, DrumInstrument.CHINA, 110),
        ]

        for pos, instrument, velocity in sequence:
            builder.pattern.add_beat(pos, instrument, velocity)

        # Add pent-uplet kick counterpoint
        for i in range(5):
            pos = i * 0.8
            builder.kick(pos, 90 + random.randint(-10, 20))

        return builder.build()

    def _create_polyrhythmic_buildup(self) -> Pattern:
        """Create polyrhythmic floor tom build-up pattern.

        A layered buildup using multiple drum elements in overlapping rhythms.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_polyrhythmic_buildup")

        # Layer 1: Floor tom quintuplet pattern
        for i in range(5):
            pos = i * 0.8
            builder.pattern.add_beat(pos, DrumInstrument.FLOOR_TOM, 85 + i * 4)

        # Layer 2: Kick drum on quarter notes (creates 3 vs 2 feel)
        for i in range(5):
            pos = i * 1.6
            builder.kick(pos, 100)

        # Layer 3: Snare accents building intensity
        for i in [2, 4]:
            pos = i * 0.8
            builder.snare(pos + 0.4, 80 + i * 6)

        # Signature crash accent at the end
        builder.crash(4.0, 120)

        return builder.build()

    def _create_mandala_tabla_fill(self) -> Pattern:
        """Custom Mandala pad / tabla-sample fill.

        Carey incorporates custom electronic drum pads (Mandala, etc.) to trigger
        samples such as prerecorded tabla and octoban sounds during live performances
        — documented in Tool interview material. Simulated here with RIDE_BELL / CHINA
        mapped to the Addictive Drums 2 ethnic keymap (midi_drums/core/value_objects/drum_instrument.py)
        where Ride 1 Bell corresponds to AD2 Key D3 (ethnic percussion trigger).
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_mandala_tabla")

        # Mimic tabla-like rhythmic phrasing across the Mandala pad's pentatonic timbre
        sequence = [
            (0.0, DrumInstrument.RIDE_BELL, 95),  # Mandala pad — "daya" (right)
            (0.375, DrumInstrument.FLOOR_TOM, 100),  # Deep tom underneath
            (0.75, DrumInstrument.RIDE_BELL, 90),  # Mandala pad — "baya" (left)
            (1.125, DrumInstrument.CHINA, 85),  # Ethnic accent
            (1.5, DrumInstrument.FLOOR_TOM, 95),  # Deep tom resonance
            (
                2.0,
                DrumInstrument.RIDE_BELL,
                92,
            ),  # Mandala pad phrase resolution
            (
                2.75,
                DrumInstrument.KICK,
                105,
            ),  # Kick on off-beat for Tool groove
        ]

        for pos, instrument, velocity in sequence:
            builder.pattern.add_beat(pos, instrument, velocity)

        return builder.build()

    def _create_odd_meter_kick_counterpoint(self) -> Pattern:
        """Odd-meter kick counterpoint fill.

        Carey frequently layers a kick drum pattern in one meter (e.g. 5 or 7)
        against the main groove's time signature — creating an independent rhythmic
        counterpoint that resolves when both meters align. Documented in Tool-era
        analyses of Lateralus and Fear Inoculum arrangements.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_odd_meter_kick")

        # 7-note kick pattern over a 4/4 bar (resolves on bar boundary)
        for i in range(7):
            pos = i * (4.0 / 7)  # 7 equal divisions of the bar
            velocity = 90 + random.randint(-5, 15)
            builder.kick(pos, velocity)

        # Floor tom accents aligning with kick on beats 2 and 4
        for beat in [1.6, 3.6]:
            builder.pattern.add_beat(beat, DrumInstrument.FLOOR_TOM, 98)

        return builder.build()

    def _create_sacred_geometry_tom_fill(self) -> Pattern:
        """Sacred-geometry tom pattern (pentatonic cascade).

        Carey's tom work often follows pentatonic pitch sequences — ascending and
        descending through toms in intervals that create a "sacred geometry"
        feel. This fill maps to his characteristic pentatonic tom cascades found
        across Tool discography.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_sacred_geometry_tom")

        # Ascending pentatonic tom cascade (floor → mid → rack pitch mapping)
        sequence = [
            (0.0, DrumInstrument.FLOOR_TOM, 115),  # Deepest tone
            (0.8, DrumInstrument.FLOOR_TOM, 110),
            (1.6, DrumInstrument.MID_TOM, 105),
            (2.4, DrumInstrument.MID_TOM, 100),
            (3.2, DrumInstrument.KICK, 95),  # Kick transition
        ]

        for pos, instrument, velocity in sequence:
            builder.pattern.add_beat(pos, instrument, velocity)

        # Return to floor tom on bar boundary with China accent
        builder.pattern.add_beat(4.0, DrumInstrument.FLOOR_TOM, 125)
        builder.pattern.add_beat(4.0, DrumInstrument.CHINA, 110)

        return builder.build()

    def _create_pentatonic_kick_accent(self) -> Pattern:
        """Pentatonic kick accent fill.

        Carey often accents the kick drum with pentatonic pitch sequences
        that mirror his tom work. This fill layers a pentatonic kick pattern
        over deep floor-tom sustenance.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_pentatonic_kick")

        # Pentatonic kick sequence (root, third, fourth, fifth, octave)
        pentatonic_intervals = [0.0, 1.2, 2.0, 3.2, 4.0]
        for i, pos in enumerate(pentatonic_intervals):
            velocity = 95 + (i % 3) * 10
            builder.kick(pos, min(127, velocity))

        # Floor tom underpinning
        for beat in [1.0, 3.0]:
            builder.pattern.add_beat(beat, DrumInstrument.FLOOR_TOM, 105)

        return builder.build()

    def _create_ethnic_inspired_fill(self) -> Pattern:
        """Ethnically-inspired fill pattern (superseded by mandala_tabla_fill).

        Carey incorporates ethnic percussion elements via custom electronic drum
        pads (Mandala, etc.) triggering tabla/octoban samples — see _create_mandala_tabla_fill.
        Kept here for backward compatibility but new compositions should use
        the dedicated mandala/tabla fill instead.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_ethnic_fill")

        # Deep taiko-style foundation (floor tom + kick)
        builder.kick(0.0, 115)
        builder.pattern.add_beat(0.0, DrumInstrument.FLOOR_TOM, 120)

        builder.kick(1.0, 110)
        builder.pattern.add_beat(1.0, DrumInstrument.FLOOR_TOM, 115)

        # Ethnic percussion simulation (china/cymbal accents on off-beats)
        for i in [0.5, 1.5]:
            pos = i
            builder.pattern.add_beat(
                pos, DrumInstrument.CHINA, 90 + random.randint(-5, 15)
            )

        # Timpani-like rolls on toms (deep, resonant tones)
        for i in range(8):
            pos = i * 0.25
            if i % 3 == 0:
                builder.pattern.add_beat(pos, DrumInstrument.MID_TOM, 80)
            elif i % 3 == 1:
                builder.pattern.add_beat(pos, DrumInstrument.FLOOR_TOM, 85)

        return builder.build()

    def _create_cymbal_swell_pattern(self) -> Pattern:
        """Create cymbal swell pattern for atmospheric effect.

        Simulates Carey's use of pedal-driven cymbal swells and ethnic percussion textures.
        """
        from midi_drums.generation.builders.pattern_builder import (
            PatternBuilder,
        )

        builder = PatternBuilder("carey_cymbal_swell")

        # Cymbal swell pattern with extended sustain
        for i in range(4):
            pos = i * 2.0
            builder.crash(pos, 100)

            # Extended sustain creates the "swell" effect (simulated)
            if random.random() < 0.7:
                builder.pattern.add_beat(
                    pos + 0.25, DrumInstrument.RIDE_BELL, 85
                )

        # Chinese cymbal accents for ethnic texture
        for i in [1.0, 3.0]:
            pos = i
            builder.pattern.add_beat(
                pos, DrumInstrument.CHINA, 95 + random.randint(-5, 10)
            )

        return builder.build()
