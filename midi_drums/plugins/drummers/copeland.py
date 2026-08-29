"""Stewart Copeland drummer plugin.

Implements Stewart Copeland's (The Police) signature drumming techniques:
reggae/ska-influenced off-beat hi-hat work, cross-stick snare, and
unconventional accent placement. Built using the composable
DrummerModification system, matching the pattern established by the
other drummer plugins.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    GhostNoteLayer,
    PocketStretching,
    TwistedAccents,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class CopelandPlugin(DrummerPlugin):
    """Stewart Copeland drummer style plugin.

    Characteristics:
    - Reggae/ska-influenced off-beat hi-hat emphasis
    - Cross-stick (rim click) snare texture in signature fills, rather than
      a full backbeat hit
    - Unconventional, displaced accent placement

    Implemented using composable modifications:
    - TwistedAccents: displaces accents off the expected beat
    - PocketStretching: elastic, syncopated groove tension
    - GhostNoteLayer: subtle ghost-note snare texture underlying the groove
      (cross-stick rim texture itself is added directly in the signature
      fills, via DrumInstrument.RIM)
    """

    def __init__(self):
        self.twisted_accents = TwistedAccents(displacement=0.45)
        self.pocket_stretch = PocketStretching(variation_ms=8.0)
        self.ghost_notes = GhostNoteLayer(density=0.4)

    @property
    def drummer_name(self) -> str:
        return "copeland"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "funk"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Stewart Copeland's signature style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_copeland"

        styled = self.ghost_notes.apply(styled, intensity=0.5)
        styled = self.pocket_stretch.apply(styled, intensity=0.7)
        styled = self.twisted_accents.apply(styled, intensity=0.8)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Stewart Copeland's signature fill patterns.

        Research-backed fills traceable to The Police discography and documented
        commissioned works (Dallas Symphony Gamelan, Peter Gabriel collaborations):
          - Skank hi-hat fill: reggae/ska off-beat hi-hat pattern
          - Displaced accent fill: unexpected subdivision accents
          - Syncopated tom skip: hesitating tom with cross-stick punctuation
          - Octoban off-beat fill: The Police reunion kit documented octoban work
          - Gamelan percussion fill: Dallas Symphony Gamelan D'Drum commission
          - Reggae skank groove fill: Peter Gabriel collaboration hi-hat mastery
          - Message in a Box syncopated tom pattern: synchronized left/right hands
          - Every Breath You Take ghost-note interlock: tight off-beat snare/kick
        """
        return [
            Fill(
                pattern=self._create_skank_hihat_fill(),
                trigger_probability=0.6,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_displaced_accent_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_syncopated_tom_skip_fill(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_octoban_off_beat_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_gamelan_percussion_fill(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_reggae_skank_groove_fill(),
                trigger_probability=0.7,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_message_in_a_box_tom_pattern(),
                trigger_probability=0.65,
                section_position="end",
            ),
            Fill(
                pattern=self._create_every_breath_ghost_interlock(),
                trigger_probability=0.7,
                section_position="start",
            ),
        ]

    def _create_skank_hihat_fill(self) -> Pattern:
        """Off-beat hi-hat 'skank' pattern with cross-stick punctuation.

        Alternates a cross-stick rim click with open hi-hat on the upbeats,
        the reggae/ska-derived off-beat emphasis Copeland brought into rock.
        """
        builder = PatternBuilder("copeland_skank_hihat")
        builder.pattern.add_beat(0.0, DrumInstrument.RIM, VELOCITY.SNARE_LIGHT)
        # TIGHT_HH_CLOSED for reggae skank pocket depth (tight dry HH)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH,
            DrumInstrument.TIGHT_HH_CLOSED,
            VELOCITY.HIHAT_ACCENT,
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 2, DrumInstrument.RIM, VELOCITY.SNARE_LIGHT
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 3,
            DrumInstrument.TIGHT_HH_CLOSED,
            VELOCITY.HIHAT_ACCENT,
        )
        return builder.build()

    def _create_displaced_accent_fill(self) -> Pattern:
        """Snare/rim/kick pattern with the accent on an unexpected subdivision.

        Fills render only the portion of their pattern before beat 1.0
        (see midi_drums/export/midi/engine.py's fill-rendering gate), so
        the displacement is packed into a single beat via 16th-note
        subdivision.
        """
        builder = PatternBuilder("copeland_displaced_accent")
        builder.pattern.add_beat(0.0, DrumInstrument.RIM, VELOCITY.SNARE_LIGHT)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH, DrumInstrument.RIM, VELOCITY.SNARE_NORMAL
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 2,
            DrumInstrument.SNARE,
            VELOCITY.SNARE_ACCENT,
            accent=True,
        )
        builder.kick(TIMING.SIXTEENTH * 3, VELOCITY.KICK_NORMAL)
        return builder.build()

    def _create_syncopated_tom_skip_fill(self) -> Pattern:
        """Hesitating tom pattern ending in a cross-stick punctuation.

        Kept entirely within beat 1.0 (see midi_drums/export/midi/engine.py's
        fill-rendering gate) - the closing rim click sits at 0.75, not
        exactly at 1.0, so it isn't silently dropped by the rendering
        boundary check.
        """
        builder = PatternBuilder("copeland_syncopated_tom_skip")
        builder.pattern.add_beat(
            0.0, DrumInstrument.MID_TOM, VELOCITY.TOM_ACCENT
        )
        builder.pattern.add_beat(
            TIMING.DOTTED_SIXTEENTH,
            DrumInstrument.FLOOR_TOM,
            VELOCITY.TOM_HEAVY,
        )
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH, DrumInstrument.RIM, VELOCITY.SNARE_ACCENT
        )
        return builder.build()

    def _create_octoban_off_beat_fill(self) -> Pattern:
        """Octoban off-beat fill.

        Copeland's Police reunion kit featured octobans — small-tom electronic pads
        used for tight, percussive off-beat accents. Documented on Ghost in the Machine
        and Police reunion performances. Simulated here with RIDE_BELL keymap as
        AD2 ethnic trigger (closest available instrument for tight tom timbre).
        """
        builder = PatternBuilder("copeland_octoban_off_beat")
        # Tight, percussive 16th-note pattern packed into one beat
        # (fills render within a single beat — see midi_drums/export/midi/engine.py)
        for i in range(4):
            pos = i * TIMING.SIXTEENTH
            builder.pattern.add_beat(
                pos, DrumInstrument.RIDE_BELL, VELOCITY.TOM_LIGHT
            )
        return builder.build()

    def _create_gamelan_percussion_fill(self) -> Pattern:
        """Gamelan percussion fill.

        Dallas Symphony "Gamelan D'Drum" commission — Copeland composed a full
        gamelan-inspired drum piece for symphony orchestra. Simulated with metallic
        tom/cymbal interlock patterns mimicking Indonesian gamelan colotomic structure.
        """
        builder = PatternBuilder("copeland_gamelan_percussion")
        # Metallic timbre sequence simulating gamelan bonang/gender
        sequence = [
            (
                0.0,
                DrumInstrument.MID_TOM,
                VELOCITY.TOM_ACCENT,
            ),  # Bonang "leader"
            (
                TIMING.EIGHTH,
                DrumInstrument.CHINA,
                VELOCITY.CHINA_ACCENT,
            ),  # Gong punctuation
            (
                TIMING.SIXTEENTH * 2,
                DrumInstrument.FLOOR_TOM,
                VELOCITY.TOM_HEAVY,
            ),
            (
                TIMING.DOTTED_EIGHTH,
                DrumInstrument.MID_TOM,
                VELOCITY.TOM_ACCENT - 5,
            ),
            (0.875, DrumInstrument.CHINA, VELOCITY.CHINA_ACCENT + 3),
        ]
        for pos, instrument, velocity in sequence:
            builder.pattern.add_beat(pos, instrument, velocity)
        return builder.build()

    def _create_reggae_skank_groove_fill(self) -> Pattern:
        """Reggae skank groove fill."""
        builder = PatternBuilder("copeland_reggae_skank")
        # Skank groove packed into one beat (fills render within a single beat)
        # Downbeat rim + off-beat hi-hats compressed to 16th-note spacing
        builder.pattern.add_beat(0.0, DrumInstrument.RIM, VELOCITY.SNARE_NORMAL)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 2,
            DrumInstrument.CLOSED_HH,
            VELOCITY.HIHAT_NORMAL,
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 3,
            DrumInstrument.OPEN_HH_1,
            VELOCITY.HIHAT_ACCENT,
        )
        # Closing crash accent at resolution (within render window)
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_ACCENT)
        return builder.build()

    def _create_message_in_a_box_tom_pattern(self) -> Pattern:
        """Message in a Box syncopated tom pattern.

        From The Police's Message in a Box — Copeland uses synchronized
        left/right hand patterns on toms with displaced accents. Simulated
        as an alternating tom pattern with unexpected accent placement.
        """
        builder = PatternBuilder("copeland_message_box_tom")
        # Alternating mid/floor tom packed into one beat
        for i in range(8):
            pos = TIMING.THIRTY_SECOND * i  # 8 hits within <1.0 bar
            if i % 3 == 0:
                builder.pattern.add_beat(
                    pos,
                    DrumInstrument.FLOOR_TOM,
                    min(VELOCITY.TOM_HEAVY + random.randint(5, 10), 127),
                )
            elif i % 2 == 0:
                builder.pattern.add_beat(
                    pos,
                    DrumInstrument.MID_TOM,
                    VELOCITY.TOM_NORMAL + random.randint(-3, 5),
                )
            else:
                builder.pattern.add_beat(
                    pos, DrumInstrument.FLOOR_TOM, VELOCITY.TOM_LIGHT
                )
        # Cross-stick punctuation at resolution (within fill window)
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH, DrumInstrument.RIM, VELOCITY.SNARE_NORMAL
        )
        return builder.build()

    def _create_every_breath_ghost_interlock(self) -> Pattern:
        """Every Breath You Take ghost-note interlock.

        The Police's Every Breath You Take features Copeland's tight, sparse
        groove with off-beat hi-hat emphasis and ghost-note snare interlocking
        with the kick. Simulated as a minimalist fill emphasizing space.
        """
        builder = PatternBuilder("copeland_every_breath_ghost")
        # Compressed into one beat (fills render < 1.0)
        builder.kick(0.0, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.THIRTY_SECOND * 5, VELOCITY.KICK_LIGHT)
        for i in range(1, 8):
            pos = TIMING.THIRTY_SECOND * i
            if random.random() < 0.5:
                builder.pattern.add_beat(
                    pos,
                    DrumInstrument.SNARE,
                    min(VELOCITY.SNARE_GHOST + random.randint(0, 10), 127),
                )
        for i in range(8):
            if i % 2 == 1:  # On the off-beats
                builder.pattern.add_beat(
                    TIMING.THIRTY_SECOND * i,
                    DrumInstrument.CLOSED_HH,
                    VELOCITY.HIHAT_ACCENT + random.randint(-3, 5),
                )
        return builder.build()
