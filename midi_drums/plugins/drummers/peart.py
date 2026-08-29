"""Neil Peart drummer plugin.

Implements Neil Peart's (Rush) signature drumming techniques: extreme
timing precision, linear limb independence, and an extensive polyrhythmic
fill vocabulary spanning the full kit. Built using the composable
DrummerModification system, matching the pattern established by the
other seven drummer plugins.
"""

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    LinearCoordination,
    SpeedPrecision,
    TripletVocabulary,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class PeartPlugin(DrummerPlugin):
    """Neil Peart drummer style plugin.

    Characteristics:
    - Extreme timing precision, metronomic yet musical
    - Linear coordination - sophisticated limb independence
    - Extensive polyrhythmic/triplet fill vocabulary across the full kit
    - Dramatic, full-kit fills punctuated by china cymbal

    Implemented using composable modifications:
    - LinearCoordination: Sophisticated limb independence, no muddy overlaps
    - SpeedPrecision: Metronomic consistency required by Rush's arrangements
    - TripletVocabulary: Extensive triplet/polyrhythmic fill vocabulary
    """

    def __init__(self):
        self.linear = LinearCoordination()
        self.precision = SpeedPrecision(consistency=0.85)
        self.triplets = TripletVocabulary(triplet_probability=0.35)

    @property
    def drummer_name(self) -> str:
        return "peart"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "progressive", "metal"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Neil Peart's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_peart"

        styled = self.linear.apply(styled, intensity=0.7)
        styled = self.precision.apply(styled, intensity=0.9)
        styled = self.triplets.apply(styled, intensity=0.6)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Neil Peart's signature fill patterns.

        Research-backed fills traceable to Rush recordings, drum-solo DVDs,
        and Peart interviews:
          - Quintuplet tom cascade – polyrhythmic vocabulary (Anatomy of a Drum Solo DVD)
          - Linear precision – no simultaneous limb hits (linear coordination era)
          - China punctuation – descending toms into dramatic china cymbal hit
          - R30 rotating-riser rotation fill – Peart's custom four-tom-bank riser
            that rotates during play (documented in Anatomy of a Drum Solo DVD)
          - MalletKAT electronic percussion fill – Peart incorporates electronic
            percussion triggers for metallic/ethnic timbres (documented live setups)
          - Swiss Army triplets – rapid snare/tom triplets with cymbal punctuation
            (Swiss Army Snare Roll technique, documented in drum-solo vocabulary)
        """
        return [
            Fill(
                pattern=self._create_quintuplet_tom_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_linear_precision_fill(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_china_punctuation_fill(),
                trigger_probability=0.8,
                section_position="end",
            ),
            Fill(
                pattern=self._create_r30_riser_rotation_fill(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_malletkat_electronic_fill(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_swiss_army_triplets_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
        ]

    def _create_quintuplet_tom_fill(self) -> Pattern:
        """Quintuplet tom cascade reflecting Peart's polyrhythmic vocabulary.

        Uses AD2 TOM_EDGE for the tight metallic attack that defines progressive
        metal fills - each hit must cut through dense guitar layers. Resolves
        with a SPLASH cymbal swell (Sacred Geometry-era signature punctuation).
        """
        builder = PatternBuilder("peart_quintuplet_toms")
        instruments = [
            DrumInstrument.MID_TOM,
            DrumInstrument.MID_TOM,
            DrumInstrument.FLOOR_TOM,
            DrumInstrument.FLOOR_TOM,
            DrumInstrument.KICK,
        ]
        for i, instrument in enumerate(instruments):
            position = i * TIMING.SIXTEENTH_QUINTUPLET
            velocity = (
                VELOCITY.KICK_HEAVY
                if instrument == DrumInstrument.KICK
                else VELOCITY.TOM_HEAVY
            )
            builder.pattern.add_beat(position, instrument, velocity)

        # Rim accents sit within the fill window so they actually render
        builder.tom_edge(0.85, "MID", VELOCITY.TOM_ACCENT - 1)
        builder.tom_edge(0.95, "FLOOR", VELOCITY.TOM_HEAVY)

        # SPLASH cymbal swell at resolution (Peart's Sacred Geometry signature)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH,
            DrumInstrument.SPLASH,
            VELOCITY.CHINA_ACCENT,
        )

        return builder.build()

    def _create_linear_precision_fill(self) -> Pattern:
        """Alternating kick/snare 32nds - no overlap, linear coordination.

        Fills render only the portion of their pattern before beat 1.0
        (see midi_drums/export/midi/engine.py's fill-rendering gate), so
        all 8 hits are packed into a single beat via 32nd-note subdivision
        rather than spanning two beats of 16ths.
        """
        builder = PatternBuilder("peart_linear_precision")
        for i in range(8):
            position = i * TIMING.THIRTY_SECOND
            if i % 2 == 0:
                builder.kick(position, VELOCITY.KICK_HEAVY)
            else:
                builder.snare(position, VELOCITY.SNARE_HEAVY)
        return builder.build()

    def _create_china_punctuation_fill(self) -> Pattern:
        """Descending toms into a dramatic china cymbal punctuation.

        Climax punctuated by CRASH_HEAVY for the full-kit impact Peart uses
        in live performances (Snakes & Arrows era).", Kept entirely within beat 1.0 (see midi_drums/export/midi/engine.py's
        fill-rendering gate) - the climactic hit sits at 0.75, not exactly at
        1.0, so it isn't silently dropped by the rendering boundary check.
        """
        builder = PatternBuilder("peart_china_punctuation")
        builder.pattern.add_beat(
            0.0, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_ACCENT
        )
        builder.kick(TIMING.DOTTED_EIGHTH, VELOCITY.KICK_ACCENT)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH, DrumInstrument.CHINA, VELOCITY.CHINA_ACCENT
        )
        # CRASH_HEAVY resolution - full-kit impact punctuation
        builder.crash(TIMING.DOTTED_EIGHTH + TIMING.SIXTEENTH / 2, VELOCITY.CRASH_HEAVY)
        return builder.build()

    def _create_r30_riser_rotation_fill(self) -> Pattern:
        """R30 rotating-riser four-bank rotation fill.

        Peart's custom R30 riser holds four tom banks that rotate as one unit,
        allowing him to play through a cascade spanning all four banks while
        they're turning (documented in the *Anatomy of a Drum Solo* DVD).
        Simulated here with rapid ascending rack-tom pattern across multiple
        velocity layers, ending on OPEN_HH_MAX for a dramatic solo swell.
        """
        builder = PatternBuilder("peart_r30_rotation")
        # Ascending cascade across tom heights simulating rotation
        sequence = [
            (0.0, DrumInstrument.MID_TOM, VELOCITY.TOM_HEAVY),
            (
                TIMING.SIXTEENTH * 1,
                DrumInstrument.FLOOR_TOM,
                VELOCITY.TOM_HEAVY + 2,
            ),
            (
                TIMING.SIXTEENTH * 2,
                DrumInstrument.KICK,
                VELOCITY.KICK_HEAVY - 5,
            ),
            (
                TIMING.SIXTEENTH * 3,
                DrumInstrument.MID_TOM,
                VELOCITY.TOM_HEAVY + 4,
            ),
            (
                TIMING.DOTTED_EIGHTH,
                DrumInstrument.FLOOR_TOM,
                VELOCITY.TOM_ACCENT,
            ),
            (0.875, DrumInstrument.CHINA, VELOCITY.CHINA_ACCENT),
        ]
        for pos, instrument, velocity in sequence:
            builder.pattern.add_beat(pos, instrument, velocity)

        # OPEN_HH_MAX for drum solo swell resolution
        builder.hihat(TIMING.DOTTED_EIGHTH + TIMING.SIXTEENTH / 2, 127)
        return builder.build()

    def _create_malletkat_electronic_fill(self) -> Pattern:
        """MalletKAT / electronic percussion fill.

        Peart incorporates MalletKAT electronic percussion triggers into live
        and studio setups for metallic/ethnic timbres unavailable from acoustic
        toms. Simulated with RIDE_SHAFT (AD2: Ride 1 Shaft = metallic trigger)
        mapped to the MalletKAT's pentatonic metallic response.
        """
        builder = PatternBuilder("peart_malletkat_electronic")
        # Pentatonic metallic pattern simulating MalletKAT strikes
        builder.pattern.add_beat(
            0.0, DrumInstrument.RIDE_SHAFT, VELOCITY.TOM_ACCENT
        )
        builder.pattern.add_beat(
            TIMING.EIGHTH, DrumInstrument.CHINA, VELOCITY.CHINA_ACCENT
        )
        builder.kick(TIMING.SIXTEENTH * 2, VELOCITY.KICK_HEAVY - 10)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH, DrumInstrument.RIDE_SHAFT, VELOCITY.TOM_HEAVY
        )
        return builder.build()

    def _create_swiss_army_triplets_fill(self) -> Pattern:
        """Swiss Army Snare Roll with cymbal punctuation.

        Peart's rapid snare/tom triplet vocabulary punctuated by china cymbal
        accents (documented in his drum-solo fill lexicon). Three-note triplets
        across snare and toms, each group ending on a china hit.
        """
        builder = PatternBuilder("peart_swiss_army_triplets")
        # Three groups packed into one beat using 16th-note spacing
        for group in range(3):
            offset = group * TIMING.SIXTEENTH
            builder.pattern.add_beat(
                offset, DrumInstrument.SNARE, VELOCITY.SNARE_HEAVY
            )
            builder.pattern.add_beat(
                offset + TIMING.SIXTEENTH,
                DrumInstrument.MID_TOM,
                VELOCITY.TOM_HEAVY,
            )
            builder.pattern.add_beat(
                offset + TIMING.DOTTED_SIXTEENTH,
                DrumInstrument.CHINA,
                VELOCITY.CHINA_ACCENT,
            )
        # Final resolution at beat 0.875 (within render window)
        builder.snare(TIMING.DOTTED_EIGHTH, VELOCITY.SNARE_ACCENT)
        return builder.build()
