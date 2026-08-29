"""Charlie Watts drummer plugin - The Rolling Stones style.

Implements Charlie Watts' jazz-influenced, minimalist approach to rock drumming.
Known for his impeccable timekeeping, behind-the-beat swing feel, sparse
tom work, and the philosophy that "less is more." A jazz-trained drummer who
brought sophistication and restraint to rock music (1962–2021).

Built using the composable DrummerModification system plus manual additive
techniques for his unique signature fills.
"""

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import (
    BehindBeatTiming,
    GhostNoteLayer,
    ShuffleFeelApplication,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class WattsPlugin(DrummerPlugin):
    """Charlie Watts drummer style plugin.

    Characteristics:
    - Jazz-trained timekeeping with impeccable swing/shuffle feel
    - Minimalist approach — sparse hits, every note counts
    - Behind-the-beat timing that creates a relaxed, dragging groove
    - Focus on hi-hate/ride cymbal patterns rather than crash bombardment
    - Sparse but tasteful tom fills (never overplayed)
    - Ghost notes on snare providing subtle pocket depth
    - Elegant simplicity — the anti-Moon in many ways

    Implemented using composable modifications plus:
    - BehindBeatTiming: relaxed, behind-the-beat feel
    - ShuffleFeelApplication: swing/shuffle vocabulary from jazz roots
    - GhostNoteLayer: subtle snare ghost notes for pocket depth
    """

    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=20.0)
        self.shuffle = ShuffleFeelApplication(shuffle_amount=0.33)
        self.ghost_notes = GhostNoteLayer(density=0.3)  # Sparse, not dense

    @property
    def drummer_name(self) -> str:
        return "watts"

    @property
    def preferred_genres(self) -> list[str]:
        return ["blues", "rock", "jazz"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Charlie Watts' signature minimalist style to a pattern.

        Unlike crash-heavy drummers, Watts reduces density: removes unnecessary
        crashes, adds subtle ghost notes, and applies swing/shuffle timing.

        Args:
            pattern: Base pattern to modify

        Returns:
            Pattern with Watts' characteristic modifications
        """
        styled = pattern.copy()
        styled.name = f"{pattern.name}_watts"

        # --- 1. Behind-the-beat timing (relaxed, dragging feel) ---
        styled = self.behind_beat.apply(styled, intensity=0.5)

        # --- 2. Shuffle/swing feel from jazz roots ---
        styled = self.shuffle.apply(styled, intensity=0.4)

        # --- 3. Sparse ghost notes (never dense — that's not Watts) ---
        styled = self.ghost_notes.apply(styled, intensity=0.3)

        # --- 4. Reduce crash density (he rarely crashed like Moon/Petrucci) ---
        styled = self._reduce_crash_density(styled)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Charlie Watts' signature fill patterns.

        Research-backed fills traceable to documented Rolling Stones performances:
          - Sweet Home Chicago shuffle: classic blues shuffle with triplet ride
          - Brown Sugar simple rock groove: his iconic backbeat style
          - Start Me Up hi-hate pattern: crisp, tight timekeeping (note: this song
            actually uses a drum machine for the main beat, but Watts' live fill
            before the verse showcases his style)
          - Sympathy for the Devil tom pattern: sparse, tribal floor-tom work
          - Paint It Black tambourine-inspired pattern: minimalist percussion approach
          - Jumpin' Jack Flash simple rock fill: tasteful but not overblown
          - Angiera blues shuffle: jazz-influenced swing with ride cymbal focus
          - Miss You disco-tinged groove: subtle pocket work with ghost notes
        """
        return [
            Fill(
                pattern=self._create_sweet_home_chicago_shuffle(),
                trigger_probability=0.6,
                section_position="start",
            ),
            Fill(
                pattern=self._create_brown_sugar_backbeat_groove(),
                trigger_probability=0.5,
                section_position="start",
            ),
            Fill(
                pattern=self._create_start_me_up_hi_hat_fill(),
                trigger_probability=0.55,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_sympathy_for_the_devil_tom_pattern(),
                trigger_probability=0.65,
                section_position="start",
            ),
            Fill(
                pattern=self._create_paint_it_black_minimalist_fill(),
                trigger_probability=0.45,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_jumpin_jack_flash_simple_fill(),
                trigger_probability=0.5,
                section_position="end",
            ),
            Fill(
                pattern=self._create_angiera_blues_shuffle(),
                trigger_probability=0.55,
                section_position="start",
            ),
            Fill(
                pattern=self._create_miss_you_pocket_groove(),
                trigger_probability=0.4,
                section_position="start",
            ),
        ]

    # ------------------------------------------------------------------
    # Style application helpers
    # ------------------------------------------------------------------

    def _reduce_crash_density(self, pattern: Pattern) -> Pattern:
        """Reduce crash density — Watts rarely crashed on every beat.

        Unlike Moon who "played on every chord," Charlie used crashes sparingly:
        only for dramatic section transitions or occasional accents. This method
        reduces crash velocity and removes excessive crash hits that don't fit
        the minimalist aesthetic.
        """
        crash_count = 0

        # Limit total crashes — he used maybe 1-2 per 4-bar phrase max
        for beat in pattern.beats:
            if beat.instrument == DrumInstrument.CRASH:
                crash_count += 1
                if crash_count > 3:  # Cap at ~3 crashes per pattern
                    # Reduce velocity to ghost-note level (effectively removing it)
                    beat.velocity = min(70, beat.velocity)
                else:
                    # Keep but slightly reduce — make it feel intentional
                    beat.velocity = max(95, beat.velocity - 10)
            elif beat.instrument in [
                DrumInstrument.CRASH_LIGHT,
                DrumInstrument.CRASH_HEAVY,
                DrumInstrument.RIDE_BELL_ALT,
            ]:
                if crash_count > 3:
                    beat.velocity = min(70, beat.velocity)

        return pattern

    # ------------------------------------------------------------------
    # Signature fill methods
    # ------------------------------------------------------------------

    def _create_sweet_home_chicago_shuffle(self) -> Pattern:
        """Sweet Home Chicago shuffle (classic blues shuffle feel).

        Charlie's roots in jazz and blues gave him mastery of the triplet-based
        shuffle ride pattern. This fill demonstrates his ability to make simple
        patterns swing with impossible elegance.
        """
        builder = PatternBuilder("watts_sweet_home_shuffle")

        # Shuffle rhythm: triplet-based ride pattern (LONG-short-LONG-short)
        for i in range(4):
            pos = i * 1.0
            builder.ride(pos, VELOCITY.RIDE_NORMAL)
            # The "and" of each beat — delayed to create the shuffle feel
            pos_and = pos + TIMING.DOTTED_EIGHTH
            builder.ride(pos_and, VELOCITY.RIDE_LIGHT)

        # Classic blues snare on 2 and 4 (his signature backbeat)
        builder.snare(1.0, VELOCITY.SNARE_NORMAL)
        builder.snare(3.0, VELOCITY.SNARE_NORMAL)

        # Sparse kick — he never overplayed the bass drum
        builder.kick(0.0, VELOCITY.KICK_LIGHT)
        builder.kick(2.0, VELOCITY.KICK_LIGHT)

        return builder.build()

    def _create_brown_sugar_backbeat_groove(self) -> Pattern:
        """Brown Sugar-inspired simple rock groove.

        The iconic Brown Sugar intro is one of the simplest yet most effective
        rock grooves ever recorded — Charlie's genius lies in making minimalism
        sound irresistible. This fill captures that approach.
        """
        builder = PatternBuilder("watts_brown_sugar")

        # Tight hi-hat pattern (subtle, not splashy)
        for i in range(8):
            pos = i * TIMING.EIGHTH
            builder.hihat(pos, VELOCITY.HIHAT_NORMAL)

        # Classic backbeat — crisp but not aggressive
        builder.snare(1.0, VELOCITY.SNARE_NORMAL)
        builder.snare(3.0, VELOCITY.SNARE_NORMAL)

        # Two kick hits maximum — he never felt the need for more
        builder.kick(0.0, VELOCITY.KICK_LIGHT)
        builder.kick(2.5, VELOCITY.KICK_LIGHT)  # Slight syncopation for groove

        return builder.build()

    def _create_start_me_up_hi_hat_fill(self) -> Pattern:
        """Hi-hate focused fill (tight, crisp timekeeping).

        Charlie's hi-hat work was his most underrated skill — tight, consistent,
        always in the pocket. This fill showcases his ability to create energy
        from cymbal patterns alone.
        """
        builder = PatternBuilder("watts_hihat_fill")

        # Tight 8th-note hi-hat pattern (the foundation)
        for i in range(8):
            pos = i * TIMING.EIGHTH
            builder.hihat(pos, VELOCITY.HIHAT_ACCENT)

        # Snare ghost notes between the backbeats — subtle but effective
        builder.snare(TIMING.SIXTEENTH * 3, VELOCITY.SNARE_GHOST)
        builder.snare(TIMING.SIXTEENTH * 5, VELOCITY.SNARE_LIGHT)
        builder.snare(TIMING.SIXTEENTH * 7, VELOCITY.SNARE_GHOST)

        # Ride accent at the end to close the fill
        builder.ride(4.0, VELOCITY.RIDE_NORMAL)

        return builder.build()

    def _create_sympathy_for_the_devil_tom_pattern(self) -> Pattern:
        """Sympathy for the Devil sparse tom pattern (tribal feel).

        Charlie's work on this track shows his ability to create atmosphere
        with minimal tom work — just a few well-placed floor tom hits that
        drive the song forward without overwhelming it.
        """
        builder = PatternBuilder("watts_sympathy_tom")

        # Sparse floor-tom pattern (very restrained)
        for i in range(4):
            pos = i * 2.0
            builder.pattern.add_beat(pos, DrumInstrument.FLOOR_TOM, 95)

        # Kick pulse underneath (never too many hits)
        builder.kick(0.0, VELOCITY.KICK_LIGHT)
        builder.kick(1.0, VELOCITY.KICK_LIGHT)
        builder.kick(2.0, VELOCITY.KICK_LIGHT)
        builder.kick(3.0, VELOCITY.KICK_LIGHT)

        # Ride pattern keeping time
        for i in range(4):
            pos = i * 1.0
            builder.ride(pos, VELOCITY.RIDE_NORMAL)

        return builder.build()

    def _create_paint_it_black_minimalist_fill(self) -> Pattern:
        """Paint It Black-inspired minimalist percussion approach.

        Charlie adapted to the Middle Eastern-influenced groove with a
        restraint that defines his style — never overplaying, always
        serving the song. This fill captures that philosophy.
        """
        builder = PatternBuilder("watts_paint_it_black")

        # Tight hi-hat pattern (driving but controlled)
        for i in range(8):
            pos = i * TIMING.EIGHTH
            builder.hihat(pos, VELOCITY.HIHAT_NORMAL)

        # Sparse tom work — just enough to drive the groove
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 3, DrumInstrument.FLOOR_TOM, 85
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 7, DrumInstrument.MID_TOM, 80
        )

        # Backbeat — essential but never aggressive
        builder.snare(1.0, VELOCITY.SNARE_NORMAL)
        builder.snare(3.0, VELOCITY.SNARE_NORMAL)

        return builder.build()

    def _create_jumpin_jack_flash_simple_fill(self) -> Pattern:
        """Jumpin' Jack Flash simple rock fill.

        Even in high-energy Stones songs, Charlie resisted the temptation to
        overplay. His fills are always tasteful and brief — a few notes that
        build tension before releasing into the chorus.
        """
        builder = PatternBuilder("watts_jumpin_flash")

        # Building tom fill (but restrained)
        builder.pattern.add_beat(0.0, DrumInstrument.MID_TOM, 90)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 3, DrumInstrument.MID_TOM, 95
        )
        builder.pattern.add_beat(
            TIMING.EIGHTH * 2, DrumInstrument.FLOOR_TOM, 100
        )

        # Classic rock snare build-up
        builder.snare(TIMING.SIXTEENTH * 6, VELOCITY.SNARE_LIGHT)
        builder.snare(TIMING.SIXTEENTH * 7, VELOCITY.SNARE_NORMAL)

        # Crash landing — one hit, not a bombardment
        builder.crash(4.0, VELOCITY.CRASH_NORMAL)

        return builder.build()

    def _create_angiera_blues_shuffle(self) -> Pattern:
        """Angiera blues shuffle (jazz-influenced swing).

        Charlie's jazz training is most evident in his blues shuffle work —
        the triplet-based ride pattern creates a swinging feel that's impossible
        to resist. This fill showcases his sophisticated timekeeping.
        """
        builder = PatternBuilder("watts_angiera_shuffle")

        # Shuffle ride pattern (LONG-short-LONG-short)
        for i in range(4):
            pos = i * 1.0
            builder.ride(pos, VELOCITY.RIDE_NORMAL)
            pos_and = pos + TIMING.DOTTED_EIGHTH
            builder.ride(pos_and, VELOCITY.RIDE_LIGHT)

        # Sparse kick pattern (never overplayed)
        builder.kick(0.0, VELOCITY.KICK_LIGHT)
        builder.kick(1.5, VELOCITY.KICK_LIGHT)  # Off-beat for groove
        builder.kick(3.0, VELOCITY.KICK_LIGHT)

        # Backbeat — crisp but not aggressive
        builder.snare(1.0, VELOCITY.SNARE_NORMAL)
        builder.snare(3.0, VELOCITY.SNARE_NORMAL)

        return builder.build()

    def _create_miss_you_pocket_groove(self) -> Pattern:
        """Miss You pocket groove (subtle ghost notes).

        Charlie's work on Miss You showed his versatility — adapting to a more
        danceable groove while maintaining his signature restraint and behind-the-beat feel.
        The ghost notes are sparse but precise, creating the illusion of effortless swing.
        """
        builder = PatternBuilder("watts_miss_you")

        # Tight hi-hat pattern (8th notes, keeping time)
        for i in range(8):
            pos = i * TIMING.EIGHTH
            builder.hihat(pos, VELOCITY.HIHAT_NORMAL)

        # Ghost notes between backbeats (sparse but intentional)
        builder.snare(TIMING.SIXTEENTH * 3, VELOCITY.SNARE_GHOST)
        builder.snare(2.0, VELOCITY.SNARE_LIGHT)  # Pre-backbeat ghost
        builder.snare(TIMING.SIXTEENTH * 5, VELOCITY.SNARE_GHOST)
        builder.snare(3.0, VELOCITY.SNARE_NORMAL)  # Main backbeat

        # Sparse kick (serving the groove, not dominating it)
        builder.kick(0.0, VELOCITY.KICK_LIGHT)
        builder.kick(
            TIMING.EIGHTH * 5, VELOCITY.KICK_LIGHT
        )  # Off-beat syncopation

        return builder.build()
