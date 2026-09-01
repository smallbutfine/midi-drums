"""Keith Moon drummer plugin - The Who style.

Implements Keith Moon's chaotic, crash-heavy, tom-driven approach to rock
drumming. Known for his explosive fills across massive floor-tom arrays,
simultaneous crash cymbal bombardment on every chord, and a loose,
behind-the-beat feel that treated time as a suggestion.

Built using the composable DrummerModification system plus manual additive
techniques (similar to CareyPlugin's approach) since Moon's style requires
stripping existing elements rather than just layering new ones.
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.models.song import Fill
from midi_drums.generation.builders.pattern_builder import PatternBuilder
from midi_drums.modifications import BehindBeatTiming, HeavyAccents
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin

# Threshold below which a beat is treated as a "cymbal/timekeeping" hit
# that can be removed or replaced in Moon's chaotic style.
_CRYSTAL_VELOCITY = VELOCITY.HIHAT_NORMAL  # Cymbal timekeeping threshold


class MoonPlugin(DrummerPlugin):
    """Keith Moon drummer style plugin.

    Characteristics:
    - Explosive, unpredictable tom fills (up to 5 floor toms in his setup)
    - Crash-heavy cymbal bombardment on every chord ("I play on every chord")
    - Loose, behind-the-beat timing — time as a suggestion
    - Dramatic dynamic contrasts (whisper-to-wall-of-sound)
    - Syncopated fills that occupy space between beats rather than on them
    - Minimal hi-hat/ride timekeeping; crash ride is his primary cymbal voice

    Implemented using composable modifications plus:
    - BehindBeatTiming: loose, dragging feel
    - HeavyAccents: dramatic dynamic contrast
    - Manual additive techniques: crash layers, tom fills between beats
    """

    def __init__(self):
        self.behind_beat = BehindBeatTiming(max_delay_ms=30.0)
        self.accents = HeavyAccents(accent_boost=20)

    @property
    def drummer_name(self) -> str:
        return "moon"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "punk", "hard_rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Keith Moon's signature chaotic style to a pattern.

        Unlike Carey (who adds layers), Moon's approach is destructive-plus-creative:
        strip predictable cymbal timekeeping, then fill the gaps with crashes and toms.
        Args:
            pattern: Base pattern to modify

        Returns:
            Pattern with Moon's characteristic modifications
        """
        styled = pattern.copy()
        styled.name = f"{pattern.name}_moon"

        # --- 1. Behind-the-beat timing (even looser than Bonham) ---
        styled = self.behind_beat.apply(styled, intensity=0.85)

        # --- 2. Dramatic dynamic contrast ---
        styled = self.accents.apply(styled, intensity=0.95)

        # --- 3. Strip/flatten timekeeping cymbals, replace with crash accents ---
        styled = self._strip_timekeeping_cymbals(styled)

        # --- 4. Add syncopated tom fills between beats ---
        max_new_beats = 10
        current_count = [0]

        def _track(n):
            if n > max(0, max_new_beats - current_count[0]):
                return max(0, max_new_beats - current_count[0])
            current_count[0] += n
            return n

        styled = self._add_crash_accent_layer(styled, _track)
        styled = self._add_tom_fill_between_beats(styled, _track)

        # --- 5. Extra crash on beat downbeats (his "panic button") ---
        styled = self._add_downbeat_crash(styled)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Keith Moon's signature fill patterns.

        Research-backed fills traceable to documented performances and
        song recordings:
          - Baba O'Riley: timpani-inspired rolling intro (1971 Who's Next)
          - My Generation fuzz: chaotic crash-on-every-chord explosion
          - Won't Get Fooled Again: thunderous crash cadence (1971)
          - Magic Bus chromatic tom run: descending floor-tom cascade
          - See Way Girl fast tom cascade: 40" Paiste crash → toms → crash
          - Panic button: simultaneous multi-crash bombardment
          - Multi-bass drum fill: double-kick tom runs (late-era setups)
          - Backbeat chaos: driving quarter-note crashes into a section
        """
        return [
            Fill(
                pattern=self._create_baba_oriley_timpani_fill(),
                trigger_probability=0.7,
                section_position="start",
            ),
            Fill(
                pattern=self._create_my_generation_fuzz_exploration(),
                trigger_probability=0.9,
                section_position="end",
            ),
            Fill(
                pattern=self._create_wont_get_fooled_crash_cadence(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_magic_bus_chromatic_tom_run(),
                trigger_probability=0.65,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_see_way_girl_tom_cascade(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_panic_button_crash_bombardment(),
                trigger_probability=0.8,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_multi_bass_drum_tom_run(),
                trigger_probability=0.6,
                section_position="end",
            ),
            Fill(
                pattern=self._create_backbeat_chaos_fill(),
                trigger_probability=0.7,
                section_position="end",
            ),
        ]

    # ------------------------------------------------------------------
    # Style application helpers
    # ------------------------------------------------------------------

    def _strip_timekeeping_cymbals(self, pattern: Pattern) -> Pattern:
        """Remove predictable cymbal timekeeping and replace with crash energy.

        Moon was notorious for ignoring ride/hi-hat patterns in favor of
        crashing on every beat. We simulate this by downgrading velocity on
        timekeeping cymbals to ghost-note levels and boosting nearby crashes.
        """
        for beat in pattern.beats:
            if beat.instrument == InstrumentRegistry.get("ride_1_tip_hit_softer"):
                # Ride becomes sparse "panic button" accents only
                beat.velocity = min(127, beat.velocity - 30)
            elif beat.instrument == InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit"):
                # Hi-hat is mostly ignored — reduce to ghost notes
                beat.velocity = min(
                    80, beat.velocity
                )  # Max at ghost-note range
            elif beat.instrument in [
                InstrumentRegistry.get("hihat_closed_bell"),
                InstrumentRegistry.get("hihat_closed_2_tip_closed_2_hit"),
                InstrumentRegistry.get("hihat_closed_1_shaft_closed_1_hit_dbl"),
                InstrumentRegistry.get("hihat_closed_2_shaft_closed_2_hit_dbl"),
            ]:
                # AD2 tight HH variants — same treatment
                beat.velocity = min(80, beat.velocity)
            elif beat.instrument == InstrumentRegistry.get("hihat_open_a"):
                # Open HH only on strong accents
                if beat.velocity < 90:
                    beat.velocity = 75

        return pattern

    def _add_crash_accent_layer(self, pattern: Pattern, track_fn) -> Pattern:
        """Add crash accents at off-beat positions.

        Moon's signature move: crashing on off-beats that other drummers
        leave empty. This creates the sense of constant bombardment.
        """
        new_beats = list(pattern.beats)

        # Scan every quarter-note position for crash opportunities
        for i in range(4):
            pos = i * 1.0 + 0.5  # Off-beat positions (the "and" of each beat)
            if track_fn(1) <= 0:
                break
            # Check if something is already there — Moon's crashes are sparse but impactful
            existing_nearby = any(
                abs(b.position - pos) < 0.05
                and b.instrument == InstrumentRegistry.get("cymbal_1_hit")
                for b in pattern.beats
            )
            if not existing_nearby and random.random() < 0.4:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=InstrumentRegistry.get("cymbal_1_hit"),
                        velocity=random.randint(105, 125),
                        duration=1.5,
                    )
                )

        # Additional splash/china accents for texture
        for i in range(4):
            pos = i * 1.0 + 0.25
            if track_fn(1) <= 0:
                break
            if random.random() < 0.2:
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=InstrumentRegistry.get("cymbal_5_hit"),
                        velocity=random.randint(95, 115),
                        duration=1.0,
                    )
                )

        pattern.beats = new_beats
        return pattern

    def _add_tom_fill_between_beats(
        self, pattern: Pattern, track_fn
    ) -> Pattern:
        """Add syncopated tom fills in the gaps between beats.

        Moon didn't just fill at section boundaries — he filled between
        every beat when the moment felt right. These fills are short, fast,
        and usually floor-tom heavy (his largest toms were his signature voice).
        """
        new_beats = list(pattern.beats)

        for i in range(8):
            pos = i * 0.5  # Eighth-note scan
            if track_fn(1) <= 0:
                break
            # Only add if there's room — don't overwrite existing hits
            too_close = any(abs(b.position - pos) < 0.03 for b in pattern.beats)
            if too_close or random.random() > 0.25:
                continue

            new_beats.append(
                Beat(
                    position=pos,
                    instrument=InstrumentRegistry.get("tom_4_open_hit"),
                    velocity=random.randint(90, 120),
                    duration=0.6,
                )
            )

        # Occasional mid-tom runs (ascending/descending across his toms)
        for i in range(4):
            pos = i * 1.5 + 0.3
            if track_fn(1) <= 0:
                break
            if random.random() < 0.15:
                inst = (
                    InstrumentRegistry.get("tom_3_open_hit")
                    if i < 2
                    else InstrumentRegistry.get("tom_4_open_hit")
                )
                new_beats.append(
                    Beat(
                        position=pos,
                        instrument=inst,
                        velocity=random.randint(85, 115),
                        duration=0.4,
                    )
                )

        pattern.beats = new_beats
        return pattern

    def _add_downbeat_crash(self, pattern: Pattern) -> Pattern:
        """Add crash on every downbeat — Moon's "panic button" technique.

        He called his 40" Paiste Big Bang crash his panic button and would
        hit it at the start of every phrase for dramatic impact.
        """
        # Only add if there isn't already a crash-like element on this beat
        needs_crash = [0.0, 2.0]  # Downbeats in a 4/4 bar

        for pos in needs_crash:
            existing = any(
                abs(b.position - pos) < 0.03
                and (
                    b.instrument == InstrumentRegistry.get("cymbal_1_hit")
                    or b.instrument == InstrumentRegistry.get("ride_1_tip_hit_softer")
                )
                for b in pattern.beats
            )
            if not existing:
                pattern.beats.append(
                    Beat(
                        position=pos,
                        instrument=InstrumentRegistry.get("cymbal_4_hit"),
                        velocity=random.randint(115, 127),
                        duration=2.0,
                    )
                )

        return pattern

    # ------------------------------------------------------------------
    # Signature fill methods
    # ------------------------------------------------------------------

    def _create_baba_oriley_timpani_fill(self) -> Pattern:
        """Baba O'Riley timpani-inspired rolling intro fill (Who's Next, 1971).

        The famous Baba O'Riley opening has Moon's toms mimicking a timpani
        roll — low, resonant, building tension before the organ enters.
        Simulated with floor tom quintuplets accelerating toward an accent.
        """
        builder = PatternBuilder("moon_baba_timpani")

        # Timpani-style roll: floor toms rolling at increasing velocity
        for i in range(8):
            pos = i * TIMING.SIXTEENTH
            vel = 75 + i * 6  # Crescendo from ghost-note whisper
            builder.pattern.add_beat(pos, InstrumentRegistry.get("tom_4_open_hit"), vel)

        # Kick on the downbeat transition
        builder.kick(4.0, VELOCITY.KICK_HEAVY)
        builder.crash(3.8, VELOCITY.CRASH_ACCENT)  # Slight lead-in crash

        return builder.build()

    def _create_my_generation_fuzz_exploration(self) -> Pattern:
        """My Generation fuzz-filled chaos (1965).

        The iconic "I hope I die before I get old" track features Moon's most
        destructive playing — crashes on every chord change with tom fills
        spilling between the hits.
        """
        builder = PatternBuilder("moon_my_generation_fuzz")

        # Crash bombardment pattern across the bar
        builder.crash(0.0, VELOCITY.CRASH_HEAVY)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH, InstrumentRegistry.get("tom_4_open_hit"), 105
        )
        builder.crash(TIMING.DOTTED_EIGHTH, VELOCITY.CRASH_LIGHT)
        builder.pattern.add_beat(1.5, InstrumentRegistry.get("tom_3_open_hit"), 95)
        builder.crash(2.0, VELOCITY.CRASH_HEAVY)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH_TRIPLET * 4, InstrumentRegistry.get("tom_4_open_hit"), 110
        )
        builder.crash(TIMING.DOTTED_EIGHTH * 2, VELOCITY.CRASH_LIGHT)
        builder.pattern.add_beat(3.5, InstrumentRegistry.get("tom_3_open_hit"), 90)
        builder.crash(4.0, VELOCITY.CRASH_HEAVY)

        # Kick pulse underneath the chaos
        builder.kick(0.0, VELOCITY.KICK_NORMAL)
        builder.kick(2.0, VELOCITY.KICK_NORMAL)

        return builder.build()

    def _create_wont_get_fooled_crash_cadence(self) -> Pattern:
        """Won't Get Fooled Again thunderous crash cadence (1971).

        The outro features Moon's most deliberate crash work — a thunderous
        rhythmic pattern that drives the song to its conclusion.
        """
        builder = PatternBuilder("moon_wont_fooled_crash")

        # Thunderous crash hits building in intensity
        builder.crash(0.0, 120)
        builder.pattern.add_beat(TIMING.EIGHTH, InstrumentRegistry.get("tom_4_open_hit"), 100)
        builder.crash(TIMING.SIXTEENTH * 3, 125)
        builder.kick(1.0, VELOCITY.KICK_HEAVY)
        builder.crash(2.0, 118)
        builder.pattern.add_beat(2.5, InstrumentRegistry.get("tom_4_open_hit"), 105)
        builder.crash(TIMING.SIXTEENTH * 6, 127)  # Climactic crash
        builder.kick(3.0, VELOCITY.KICK_HEAVY)
        builder.pattern.add_beat(3.5, InstrumentRegistry.get("tom_3_open_hit"), 95)
        builder.crash(4.0, 127)  # Final thunderous crash

        return builder.build()

    def _create_magic_bus_chromatic_tom_run(self) -> Pattern:
        """Magic Bus chromatic floor-tom descent (1968).

        Moon's floor toms were his most distinctive voice. This fill simulates
        a chromatic run down across his extensive floor-tom collection.
        """
        builder = PatternBuilder("moon_magic_bus_tom_run")

        # Descending floor-tom cascade (simulating multiple floor toms)
        sequence = [
            (0.0, InstrumentRegistry.get("tom_4_open_hit"), 120),
            (TIMING.SIXTEENTH * 3, InstrumentRegistry.get("tom_4_open_hit"), 118),
            (TIMING.EIGHTH, InstrumentRegistry.get("tom_3_open_hit"), 115),
            (TIMING.SIXTEENTH * 6, InstrumentRegistry.get("tom_4_open_hit"), 112),
            (TIMING.DOTTED_EIGHTH, InstrumentRegistry.get("tom_3_open_hit"), 108),
            (TIMING.SIXTEENTH * 10, InstrumentRegistry.get("tom_4_open_hit"), 105),
            (1.625, InstrumentRegistry.get("tom_3_open_hit"), 100),
            (TIMING.DOTTED_EIGHTH * 2, InstrumentRegistry.get("tom_4_open_hit"), 95),
        ]

        for pos, inst, vel in sequence:
            builder.pattern.add_beat(pos, inst, vel)

        # Kick on the downbeat resolution
        builder.kick(2.0, VELOCITY.KICK_ACCENT)
        builder.crash(1.95, VELOCITY.CRASH_HEAVY)  # Slight lead-in

        return builder.build()

    def _create_see_way_girl_tom_cascade(self) -> Pattern:
        """See Way Girl fast tom cascade (Live at Leeds era).

        Live performances featured rapid descending runs across Moon's massive
        floor-tom array. This fill captures the energy of those fills.
        """
        builder = PatternBuilder("moon_see_way_tom_cascade")

        # Rapid 16th-note floor-to-mid tom descent with accelerando feel
        builder.pattern.add_beat(0.0, InstrumentRegistry.get("tom_4_open_hit"), 125)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 3, InstrumentRegistry.get("tom_4_open_hit"), 122
        )
        builder.pattern.add_beat(TIMING.EIGHTH, InstrumentRegistry.get("tom_3_open_hit"), 118)
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 6, InstrumentRegistry.get("tom_4_open_hit"), 115
        )
        builder.kick(0.75, VELOCITY.KICK_HEAVY)

        # Mid-tom run with crash landing
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH, InstrumentRegistry.get("tom_3_open_hit"), 110
        )
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 11, InstrumentRegistry.get("tom_4_open_hit"), 127
        )
        builder.crash(1.875, VELOCITY.CRASH_HEAVY)

        # Repeat with variation on second half of bar
        builder.pattern.add_beat(2.0, InstrumentRegistry.get("tom_4_open_hit"), 120)
        builder.pattern.add_beat(2.5, InstrumentRegistry.get("tom_3_open_hit"), 115)
        builder.kick(TIMING.SIXTEENTH * 9, VELOCITY.KICK_HEAVY)
        builder.pattern.add_beat(3.0, InstrumentRegistry.get("tom_4_open_hit"), 118)
        builder.crash(3.75, VELOCITY.CRASH_HEAVY)

        return builder.build()

    def _create_panic_button_crash_bombardment(self) -> Pattern:
        """Panic button — simultaneous multi-crash bombardment.

        Moon's 40" Paiste Big Bang (his "panic button") plus multiple crashes
        hit at once for maximum impact. This fill is pure destruction, used
        sparingly but with devastating effect.
        """
        builder = PatternBuilder("moon_panic_button")

        # The main bombardment hit on beat 1 — this is what he called his "panic button"
        builder.crash(0.0, VELOCITY.CRASH_HEAVY)
        builder.pattern.add_beat(
            0.0, InstrumentRegistry.get("ride_2_bell"), VELOCITY.CRASH_LIGHT
        )

        # Second half of the bar — another massive crash to keep tension up
        builder.crash(2.5, 127)
        builder.kick(2.5, VELOCITY.KICK_HEAVY)
        builder.pattern.add_beat(2.5, InstrumentRegistry.get("tom_4_open_hit"), 120)

        # Build-up to the final crash
        builder.pattern.add_beat(
            TIMING.SIXTEENTH * 8, InstrumentRegistry.get("tom_4_open_hit"), 110
        )
        builder.kick(TIMING.SIXTEENTH * 7, VELOCITY.KICK_ACCENT)
        builder.crash(3.5, 125)

        # Final crash — the panic button pulled with full force
        builder.crash(4.0, 127)
        builder.kick(4.0, VELOCITY.KICK_HEAVY)

        return builder.build()

    def _create_multi_bass_drum_tom_run(self) -> Pattern:
        """Multi-bass-drum fill — double-kick tom runs (late-era Moon setups).

        As Moon's setup evolved to include multiple bass drums, his fills
        incorporated driving kick patterns alongside tom cascades.
        """
        builder = PatternBuilder("moon_multi_bass_tom")

        # Driving kick/tom alternating pattern (simulating dual bass drums)
        for i in range(8):
            pos = i * TIMING.SIXTEENTH
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)
            else:
                builder.pattern.add_beat(
                    pos, InstrumentRegistry.get("tom_4_open_hit"), 110 + (i % 3) * 5
                )

        # Mid-tom bridge into the final crash
        builder.pattern.add_beat(
            TIMING.DOTTED_EIGHTH * 2, InstrumentRegistry.get("tom_3_open_hit"), 105
        )
        builder.kick(TIMING.SIXTEENTH * 14, VELOCITY.KICK_ACCENT)

        # Climactic crash landing
        builder.crash(3.875, VELOCITY.CRASH_HEAVY)

        return builder.build()

    def _create_backbeat_chaos_fill(self) -> Pattern:
        """Backbeat chaos — driving quarter-note crashes into a section change.

        Moon would sometimes abandon his kit entirely for the final chorus or
        section transition, hammering every downbeat with maximum crash intensity
        as if the whole band were about to collapse under the weight of it.
        """
        builder = PatternBuilder("moon_backbeat_chaos")

        # Quarter-note crashes building in velocity — pure destruction
        velocities = [120, 125, 127, 127]
        for i, vel in enumerate(velocities):
            pos = i * 1.0
            builder.crash(pos, vel)
            # Kick on every other downbeat for pulse
            if i % 2 == 0:
                builder.kick(pos, VELOCITY.KICK_HEAVY)

        # Final floor-tom hit to anchor the chaos before section change
        builder.pattern.add_beat(3.75, InstrumentRegistry.get("tom_4_open_hit"), 115)

        return builder.build()
