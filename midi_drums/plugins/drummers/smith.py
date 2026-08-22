"""Chad Smith drummer plugin - Red Hot Chili Peppers style funk-rock fusion.

Chad Smith (RHCP, Chickenfoot, Bombastic Meatbats) is known for:
- Funk-rock groove mastery — deep pocket grooves with hard rock power
- Heavy snare ghost notes learned from Larry Fratangelo (P-Funk lineage)
- Fast double-bass technique influenced by Buddy Rich and John Bonham
- Syncopated kick patterns locking tightly with Flea's bass guitar
- Massive tom fills across large drum kits (23-piece kit live)
- Behind-the-beat pocket feel with driving forward motion
- Influences: David Garibaldi, Jabo Starks, Clyde Stubblefield, Buddy Rich

Signature tracks: "Give It Away", "Can't Stop", "Dani California", "Under the Bridge",
"Snowjob" (Chickenfoot), plus Chickenfoot and Bombastic Meatbats material.

This plugin implements his style using composable modifications:
- GhostNoteLayer: Heavy snare ghost note density (P-Funk lineage)
- BehindBeatTiming: Pocket feel with slight drag
- HeavyAccents: Hard rock power for RHCP/Chickenfoot
- FastChopsTriplets: Rapid-fire fills (Buddy Rich influence)
- PocketStretching: Funk pocket tension/release
"""

import random

from midi_drums.config import TIMING, VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.models.song import Fill
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.modifications import (
    BehindBeatTiming,
    FastChopsTriplets,
    GhostNoteLayer,
    HeavyAccents,
    PocketStretching,
)
from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin


class SmithPlugin(DrummerPlugin):
    """Chad Smith drummer style plugin.

    Characteristics:
    - Funk-rock fusion groove — deep pocket with hard rock power
    - Heavy snare ghost notes (P-Funk lineage via Larry Fratangelo)
    - Fast double-bass technique (Buddy Rich / Bonham influence)
    - Syncopated kick patterns locking with bass guitar
    - Massive tom fills across large drum kits
    - Behind-the-beat pocket feel with driving forward motion

    Implemented using composable modifications:
    - GhostNoteLayer: Heavy ghost note density for funk texture
    - BehindBeatTiming: Slightly behind the beat for pocket feel
    - HeavyAccents: Hard rock power and dynamic contrast
    - FastChopsTriplets: Rapid-fire fills (Buddy Rich influence)
    - PocketStretching: Funk groove tension and release
    """

    def __init__(self):
        self.ghost_notes = GhostNoteLayer(density=0.75)  # Heavy ghost notes
        self.behind_beat = BehindBeatTiming(max_delay_ms=18.0)
        self.accents = HeavyAccents(accent_boost=20)
        self.fast_chops = FastChopsTriplets(probability=0.35)
        self.pocket = PocketStretching(variation_ms=6.0)

    @property
    def drummer_name(self) -> str:
        return "chadsmith"

    @property
    def preferred_genres(self) -> list[str]:
        return ["rock", "funk", "alternative", "hard_rock", "funk_rock"]

    def apply_style(self, pattern: Pattern) -> Pattern:
        """Apply Chad Smith's signature funk-rock style to a pattern."""
        styled = pattern.copy()
        styled.name = f"{pattern.name}_chadsmith"

        # Layer modifications for Chad Smith's sound
        styled = self.ghost_notes.apply(styled, intensity=0.8)
        styled = self.behind_beat.apply(styled, intensity=0.5)
        styled = self.accents.apply(styled, intensity=0.7)
        styled = self.fast_chops.apply(styled, intensity=0.6)
        styled = self.pocket.apply(styled, intensity=0.6)

        return styled

    def get_signature_fills(self) -> list[Fill]:
        """Return Chad Smith's signature fill patterns.

        Based on RHCP, Chickenfoot, and Bombastic Meatbats discography:
          - Give It Away funk groove: syncopated kick locked with bass
          - Can't Stop gallop: iconic double-kick + snare ghost notes
          - Dani California driving rock: heavy forward motion funk-rock
          - Under the Bridge sparse atmospheric: minimal but powerful
          - Snowjob Chickenfoot: massive tom fills, hard rock power
          - Bombastic Meatbats fusion: pure funk-tom vocabulary
          - RHCP live one-drop: deep pocket with double-bass accent
          - Fast hand-chops: Buddy Rich-style rapid-fire snare/tom
        """
        return [
            Fill(
                pattern=self._create_give_it_away_funk(),
                trigger_probability=0.95,
                section_position="start",
            ),
            Fill(
                pattern=self._create_cant_stop_gallop(),
                trigger_probability=0.9,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_dani_california_driving_rock(),
                trigger_probability=0.85,
                section_position="end",
            ),
            Fill(
                pattern=self._create_under_the_bridge_sparse(),
                trigger_probability=0.7,
                section_position="start",
            ),
            Fill(
                pattern=self._create_snowjob_tom_fills(),
                trigger_probability=0.85,
                section_position="middle",
            ),
            Fill(
                pattern=self._create_bombastic_meatbats_fusion(),
                trigger_probability=0.75,
                section_position="end",
            ),
            Fill(
                pattern=self._create_live_one_drop(),
                trigger_probability=0.8,
                section_position="start",
            ),
            Fill(
                pattern=self._create_fast_hand_chops_showcase(),
                trigger_probability=0.75,
                section_position="middle",
            ),
        ]

    def _create_give_it_away_funk(self) -> Pattern:
        """Give It Away funk groove with syncopated kick locked with bass.

        The iconic RHCP track where Chad's drumming is almost entirely
        syncopated, avoiding the downbeat in favor of locking with Flea's
        walking bass line. Heavy ghost notes on snare create rhythmic tension.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_give_it_away")

        # Kick pattern avoiding beat 1 — locks with Flea's bass (syncopated)
        kick_hits = [
            (TIMING.EIGHTH * 0.5, VELOCITY.KICK_HEAVY),    # "and" of 1
            (TIMING.HALF + TIMING.EIGHTH * 0.5, VELOCITY.KICK_HEAVY),  # "and" of 3
            (TIMING.HALF * 2 - TIMING.SIXTEENTH, VELOCITY.KICK_NORMAL),
            (TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.KICK_HEAVY),
        ]
        for offset, vel in kick_hits:
            builder.kick(offset, vel)

        # Snare ghost notes densely layered (P-Funk lineage)
        builder.snare(TIMING.QUARTER + TIMING.SIXTEENTH, VELOCITY.SNARE_HEAVY)
        builder.snare(TIMING.HALF * 3 + TIMING.SIXTEENTH, VELOCITY.SNARE_NORMAL)
        for i in range(1, 8):
            pos = TIMING.EIGHTH * i - TIMING.SIXTEENTH
            if random.random() < 0.7:
                builder.pattern.add_beat(
                    pos, DrumInstrument.SNARE,
                    VELOCITY.SNARE_GHOST + random.randint(0, 15),
                )

        # Tight closed hi-hat (driving the groove)
        for i in range(8):
            builder.hihat(TIMING.EIGHTH * i, VELOCITY.HIHAT_NORMAL)

        return builder.build()

    def _create_cant_stop_gallop(self) -> Pattern:
        """Can't Stop iconic double-kick + snare ghost note groove.

        The most recognizable Chad Smith pattern: continuous eighth-note
        double-bass gallop locking with Flea's descending bass line, heavy
        snare on 2 and 4 buried under dense ghost notes. The gallop creates
        relentless forward motion while the pocket stays deep.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_cant_stop_gallop")

        # Continuous double-kick gallop (the signature)
        for i in range(8):
            pos = TIMING.EIGHTH * i
            vel = VELOCITY.KICK_HEAVY if i % 2 == 0 else min(VELOCITY.KICK_NORMAL + 10, 127)
            builder.kick(pos, vel)

        # Heavy snare backbeats with ghost notes between
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_HEAVY)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY + 5)

        # Ghost note net between beats (dense for funk feel)
        for i in range(1, 8):
            pos = TIMING.EIGHTH * i
            if random.random() < 0.6:
                builder.pattern.add_beat(
                    pos, DrumInstrument.SNARE,
                    VELOCITY.SNARE_GHOST + random.randint(2, 15),
                )

        # Open hi-hat accents (RHCP live style — slightly open)
        for i in range(4):
            builder.pattern.add_beat(
                TIMING.HALF * i, DrumInstrument.OPEN_HH,
                VELOCITY.HIHAT_NORMAL + 5 + random.randint(-3, 8),
            )

        return builder.build()

    def _create_dani_california_driving_rock(self) -> Pattern:
        """Dani California driving funk-rock pattern.

        From Dani California — a more straight-ahead rock groove that still
        retains Chad's pocket feel. Heavy double-bass accents, powerful snare,
        and the characteristic behind-the-beat drag on cymbal crashes.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_dani_california")

        # Driving kick pattern with double-bass accents
        builder.kick(0.0, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.EIGHTH_TRIPLET * 2, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF, VELOCITY.KICK_HEAVY)
        builder.kick(TIMING.HALF + TIMING.SIXTEENTH, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF * 3, VELOCITY.KICK_HEAVY)

        # Heavy snare backbeats
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_HEAVY + 5)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY + 3)

        # Ghost note fill on the transition (bars 2-3 approach)
        for i in range(4):
            pos = TIMING.EIGHTH * (i + 0.5)
            builder.pattern.add_beat(
                pos, DrumInstrument.SNARE,
                VELOCITY.SNARE_GHOST + random.randint(5, 18),
            )

        # Hi-hat driving eighth notes with open accents
        for i in range(8):
            open_flag = i % 4 == 0
            builder.hihat(TIMING.EIGHTH * i,
                VELOCITY.HIHAT_NORMAL + (6 if open_flag else 0),
                open=open_flag,
            )

        return builder.build()

    def _create_under_the_bridge_sparse(self) -> Pattern:
        """Under the Bridge sparse atmospheric pattern.

        From Under the Bridge — Chad's most minimal pattern. Sparse kick hits,
        light snare on 2 and 4, tight closed hi-hat. The drumming serves the song
        by staying out of the way, then explodes in the chorus. This fill captures
        the verse approach: room to breathe with deep pocket feel.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_under_bridge_sparse")

        # Sparse kick — only on key downbeats and transitions
        builder.kick(0.0, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF, min(VELOCITY.KICK_LIGHT + 5, VELOCITY.KICK_NORMAL))

        # Light snare backbeats (not heavy — song demands restraint)
        builder.snare(TIMING.QUARTER, VELOCITY.SNARE_NORMAL - 3)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_NORMAL - 2)

        # Tight closed hi-hat (keeping time without dominating)
        for i in range(8):
            builder.hihat(TIMING.EIGHTH * i, VELOCITY.HIHAT_LIGHT + 3)

        return builder.build()

    def _create_snowjob_tom_fills(self) -> Pattern:
        """Snowjob massive tom fills (Chickenfoot).

        From Chickenfoot's Snowjob — Chad unleashes his signature massive tom
        fills across a huge kit. Heavy, powerful, with dramatic cascades from
        rack to floor tom. The hard rock context means everything is played loud
        and accented, unlike the funk grooves where he uses ghost notes.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_snowjob_tom_fills")

        # Heavy kick foundation (hard rock context)
        for i in range(4):
            builder.kick(TIMING.HALF * i, VELOCITY.KICK_HEAVY + 5)

        # Massive snare on every bar boundary with heavy accent
        builder.snare(0.0, VELOCITY.SNARE_HEAVY + 10)
        builder.snare(TIMING.HALF * 2, VELOCITY.SNARE_HEAVY + 8)
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)

        # Tom cascade: rapid descent from rack to floor (the signature fill)
        tom_sequence = [
            (TIMING.QUARTER * 0.5, DrumInstrument.MID_TOM),
            (TIMING.QUARTER * 1.0, DrumInstrument.MID_TOM),
            (TIMING.QUARTER * 1.5, DrumInstrument.FLOOR_TOM),
            (TIMING.QUARTER * 2.0, DrumInstrument.FLOOR_TOM),
            (TIMING.QUARTER * 2.5, DrumInstrument.MID_TOM),
            (TIMING.QUARTER * 3.0, DrumInstrument.FLOOR_TOM),
            (TIMING.HALF * 4 - TIMING.SIXTEENTH, DrumInstrument.FLOOR_TOM),
        ]
        for pos, inst in tom_sequence:
            builder.pattern.add_beat(
                pos, inst, VELOCITY.TOM_HEAVY + random.randint(0, 12),
            )

        # Crash accents after fills (chicken on top)
        for i in range(4):
            builder.pattern.add_beat(
                TIMING.HALF * i + TIMING.QUARTER, DrumInstrument.CRASH,
                VELOCITY.CHINA_ACCENT - 10,
            )

        return builder.build()

    def _create_bombastic_meatbats_fusion(self) -> Pattern:
        """Bombastic Meatbats pure funk-tom vocabulary showcase.

        From Chad Smith's Bombastic Meatbats — an all-instrumental funk/fusion
        band. This captures the essence of Chad's funk drumming without rock
        compression: deep pocket, syncopated kick patterns, and extensive tom
        work using rim/edge hits for tonal variety. Influenced by David Garibaldi
        (Tower of Power) and Clyde Stubblefield (James Brown).
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_meatbats_fusion")

        # Syncopated kick pattern (funk foundation — locks with bass)
        kick_hits = [
            (0.0, VELOCITY.KICK_HEAVY),
            (TIMING.EIGHTH * 1.5, VELOCITY.KICK_NORMAL),
            (TIMING.HALF + TIMING.SIXTEENTH, VELOCITY.KICK_HEAVY),
            (TIMING.HALF * 3 + TIMING.EIGHTH_TRIPLET, VELOCITY.KICK_NORMAL),
        ]
        for offset, vel in kick_hits:
            builder.kick(offset, vel)

        # Heavy tom rim/edge work with tight ghost notes on snare
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            if i % 4 == 0:
                # Accent on floor tom edge (deep tone)
                builder.tom_edge(pos, "FLOOR", VELOCITY.TOM_HEAVY + random.randint(-5, 12))
            elif i % 3 == 0:
                # Ghost note snare rim
                builder.pattern.add_beat(
                    pos, DrumInstrument.SNARE,
                    VELOCITY.SNARE_GHOST + random.randint(3, 15),
                )
            else:
                # Mid tom rim shot for tonal variety
                builder.tom_edge(pos, "MID", VELOCITY.TOM_NORMAL)

        # Tight hi-hat keeping the pocket
        for i in range(8):
            builder.tight_hh(TIMING.EIGHTH * i, open=False)

        return builder.build()

    def _create_live_one_drop(self) -> Pattern:
        """RHCP live one-drop with double-bass accent.

        A live-performance groove combining the reggae/funk one-drop feel (kick
        only on 1) with Chad's signature double-bass accents during transitions.
        Deep pocket, heavy ghost notes, and the characteristic behind-the-beat
        drag that makes the groove feel both laid-back and powerful.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_one_drop_live")

        # One-drop: kick only on 1 (deep pocket foundation)
        builder.kick(0.0, VELOCITY.KICK_HEAVY + 5)

        # Double-bass accent during transition (Chad's flair)
        builder.kick(TIMING.HALF + TIMING.EIGHTH, VELOCITY.KICK_NORMAL)
        builder.kick(TIMING.HALF * 2 - TIMING.SIXTEENTH, VELOCITY.KICK_HEAVY)

        # Snare on 3 (one-drop style) with ghost notes
        builder.snare(TIMING.HALF * 3, VELOCITY.SNARE_HEAVY)
        for i in range(1, 8):
            pos = TIMING.EIGHTH * i - TIMING.SIXTEENTH
            if random.random() < 0.5:
                builder.pattern.add_beat(
                    pos, DrumInstrument.SNARE,
                    VELOCITY.SNARE_GHOST + random.randint(2, 14),
                )

        # Tight hi-hat (not open — keeping the pocket tight)
        for i in range(8):
            builder.tight_hh(TIMING.EIGHTH * i, open=False)

        return builder.build()

    def _create_fast_hand_chops_showcase(self) -> Pattern:
        """Fast hand-chops rapid-fire snare/tom showcase (Buddy Rich influence).

        Chad's Buddy Rich-influenced rapid-fire fills feature fast alternating
        snare and tom hits with thunderous double-bass underneath. The fills
        demonstrate technical speed while staying musical — no gratuitous
        busywork, just devastating power and precision derived from his classical
        drum corps background and years of practicing with the RHCP's relentless
        touring schedule.
        """
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("smith_fast_chops")

        # Thunderous double-kick foundation
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            vel = VELOCITY.KICK_HEAVY if i % 2 == 0 else min(VELOCITY.KICK_NORMAL + 15, 127)
            builder.kick(pos, vel)

        # Rapid snare/tom alternating pattern (hand chops)
        for i in range(16):
            pos = TIMING.SIXTEENTH * i
            if i % 4 == 0:
                builder.snare(pos, VELOCITY.SNARE_HEAVY + random.randint(0, 8))
            elif i % 2 == 0:
                builder.pattern.add_beat(
                    pos, DrumInstrument.MID_TOM if i < 8 else DrumInstrument.FLOOR_TOM,
                    VELOCITY.TOM_HEAVY + random.randint(-5, 12),
                )

        # Cymbal crash punctuation at fill transition points
        builder.pattern.add_beat(TIMING.HALF * 4, DrumInstrument.CRASH, VELOCITY.CHINA_ACCENT)

        return builder.build()


# backward-compat alias for existing test imports
SmithPluginRefactored = SmithPlugin
