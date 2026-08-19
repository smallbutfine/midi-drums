"""
Danny Carey drummer plugin - Tool style.

Implements Danny Carey's signature polyrhythmic, odd-meter, tom-heavy approach 
to progressive and alternative metal. Known for his deep tom work, complex 
polyrhythms (3 vs 2 quintuplets), ethnic percussion influences, and the 
spacious, heavy "Tool groove" that defines albums like Lateralus and Fear Inoculum.
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
    - Ethnically-inspired percussion textures (taiko/timpani/hang)
    - Spacious grooves with intentional space between hits
    - Complex pentatonic/quintuplet accent fills
    - Long-sustain cymbal swells and effects
    """

    @property
    def drummer_name(self) -> str:
        return "carey"

    @property
    def compatible_genres(self) -> list[str]:
        return [
            "progressive",
            "alternative",
            "hard_rock",
            "post_metal",
            "psychedelic",
        ]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Danny Carey's signature style to a pattern.

        Args:
            pattern: Base pattern to modify

        Returns:
            Pattern with Carey's characteristic modifications
        """
        styled_pattern = pattern.copy()
        styled_pattern.name = f"{pattern.name}_carey"

        # 1. Add polyrhythmic quintuplet kick counterpoint (3 vs 2)
        styled_pattern = self._add_polyrhythmic_kick(styled_pattern)

        # 2. Deep tom-heavy accent patterns and cascading fills
        styled_pattern = self._add_deep_tom_patterns(styled_pattern)

        # 3. Apply the "Tool groove" - spaciousness with intentional space
        styled_pattern = self._apply_tool_groove_space(styled_pattern)

        # 4. Complex pentatonic/quintuplet accent fills between beats
        styled_pattern = self._add_pentatonic_accent_fills(styled_pattern)

        # 5. Cymbal swells and effects (simulated with long sustain)
        styled_pattern = self._add_cymbal_swell_effects(styled_pattern)

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

        # Deep ethnic-inspired fill (taiko/timpani/hang feel)
        ethnic_fill = Fill(
            pattern=self._create_ethnic_inspired_fill(),
            trigger_probability=0.65,
            section_position="end",
        )
        fills.append(ethnic_fill)

        # Cymbal swell pattern for atmospheric transition
        cymbal_fill = Fill(
            pattern=self._create_cymbal_swell_pattern(),
            trigger_probability=0.60,
            section_position="start",
        )
        fills.append(cymbal_fill)

        return fills

    # --- Style application methods ---

    def _add_polyrhythmic_kick(self, pattern: Pattern) -> Pattern:
        """Add polyrhythmic kick counterpoint (3 vs 2 quintuplets).

        Carey constantly layers pent-uplet kicks against the main meter,
        creating the characteristic tension/release of the "Tool groove".
        """
        new_beats = list(pattern.beats)

        # Identify existing kicks and add quintuplet counterpoint around them
        for beat in pattern.beats:
            if beat.instrument == DrumInstrument.KICK:
                original_pos = beat.position

                # Quintuplet counter-kick notes spaced at 0.8 intervals (3 vs 2)
                quintuplet_spacing = 0.8
                num_notes = max(4, int(4.0 / quintuplet_spacing))

                for i in range(1, num_notes):
                    pos = original_pos + (i * quintuplet_spacing / 3)

                    if random.random() < 0.5:  # 50% chance to add poly-kick
                        poly_kick = Beat(
                            position=pos,
                            instrument=beat.instrument,
                            velocity=min(127, beat.velocity + random.randint(-8, 8)),
                            duration=beat.duration * 0.9,
                        )
                        new_beats.append(poly_kick)

        pattern.beats = new_beats
        return pattern

    def _add_deep_tom_patterns(self, pattern: Pattern) -> Pattern:
        """Add deep tom-focused accents and cascades.

        Carey's toms are incredibly deep-tuned with long sustain. Floor tom
        cascades (starting low and going up) are his signature fill element.
        """
        new_beats = list(pattern.beats)

        # Deep floor tom accents on off-beats for the "Tool" depth
        for i in range(8):
            pos = i * 0.5
            if random.random() < 0.2:
                deep_tom = Beat(
                    position=pos,
                    instrument=DrumInstrument.FLOOR_TOM,
                    velocity=90 + random.randint(-10, 25),
                    duration=0.8,  # Long sustain for deep tuning effect
                )
                new_beats.append(deep_tom)

        # Mid tom accents between main beats
        for i in range(4):
            pos = i + 0.5
            if random.random() < 0.15:
                mid_tom = Beat(
                    position=pos,
                    instrument=DrumInstrument.MID_TOM,
                    velocity=80 + random.randint(-5, 20),
                    duration=0.4,
                )
                new_beats.append(mid_tom)

        pattern.beats = new_beats
        return pattern

    def _apply_tool_groove_space(self, pattern: Pattern) -> Pattern:
        """Apply the "Tool groove" - spaciousness with intentional space.

        Carey's grooves are characterized by deep, powerful hits separated by
        silence, creating a hypnotic, heavy feel. Long-sustain drums amplify this.
        """
        for beat in pattern.beats:
            if beat.instrument == DrumInstrument.KICK:
                # Deep, resonant kicks with longer sustain
                beat.velocity = min(127, beat.velocity + 15)
                beat.duration = max(0.3, beat.duration * 1.4)

            elif beat.instrument == DrumInstrument.SNARE:
                # Powerful but spacious snares (less ghost notes, more space)
                beat.velocity = min(127, beat.velocity + 10)

            elif beat.instrument in [
                DrumInstrument.FLOOR_TOM,
                DrumInstrument.MID_TOM,
            ]:
                # Deep tom sustain is key to Carey's sound
                beat.duration = max(0.4, beat.duration * 2.0)

        return pattern

    def _add_pentatonic_accent_fills(self, pattern: Pattern) -> Pattern:
        """Add pentatonic/quintuplet accent fills between beats.

        Carey frequently weaves pentatonic melodic patterns and quintuplet fills
        into his grooves as transitional elements.
        """
        new_beats = list(pattern.beats)

        # Pentatonic snare accents (5-note pattern across bar)
        for i in range(5):
            pos = i * 0.8
            if random.random() < 0.3:
                pent_snare = Beat(
                    position=pos,
                    instrument=DrumInstrument.SNARE,
                    velocity=100 + random.randint(-10, 25),
                    duration=0.1,
                )
                new_beats.append(pent_snare)

        # Floor tom cascade pattern (floor -> mid -> high toms upward)
        for i in range(3):
            pos = i * 1.2
            if random.random() < 0.15:
                casc_tom = Beat(
                    position=pos,
                    instrument=DrumInstrument.FLOOR_TOM if i < 2 else DrumInstrument.MID_TOM,
                    velocity=95 + random.randint(-5, 20),
                    duration=0.3,
                )
                new_beats.append(casc_tom)

        pattern.beats = new_beats
        return pattern

    def _add_cymbal_swell_effects(self, pattern: Pattern) -> Pattern:
        """Add cymbal swells and effects (simulated).

        Carey extensively uses pedal-driven cymbal swells and ethnic percussion
        elements. Simulated here with long-sustain crashes and ride bell accents.
        """
        new_beats = list(pattern.beats)

        # Cymbal swells on strong beats
        for pos in [0.0, 2.0]:
            if random.random() < 0.35:
                swell = Beat(
                    position=pos,
                    instrument=DrumInstrument.CRASH,
                    velocity=100 + random.randint(-10, 20),
                    duration=2.0,  # Very long sustain for "swell" effect
                )
                new_beats.append(swell)

        # Ethnically-inspired percussion accents (simulated with china/ride bell)
        for i in range(8):
            pos = i * 0.5
            if random.random() < 0.1:
                eth_inst = random.choice([DrumInstrument.CHINA, DrumInstrument.RIDE_BELL])
                ethnic = Beat(
                    position=pos,
                    instrument=eth_inst,
                    velocity=85 + random.randint(-10, 15),
                    duration=0.6,
                )
                new_beats.append(ethnic)

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

    def _create_ethnic_inspired_fill(self) -> Pattern:
        """Create ethnically-inspired fill pattern.

        Carey incorporates ethnic percussion elements (taiko, timpani, hang drum
        feel). Simulated here with unique tom/china combinations and long sustain.
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
            builder.pattern.add_beat(pos, DrumInstrument.CHINA, 90 + random.randint(-5, 15))

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
                builder.pattern.add_beat(pos + 0.25, DrumInstrument.RIDE_BELL, 85)

        # Chinese cymbal accents for ethnic texture
        for i in [1.0, 3.0]:
            pos = i
            builder.pattern.add_beat(pos, DrumInstrument.CHINA, 95 + random.randint(-5, 10))

        return builder.build()
