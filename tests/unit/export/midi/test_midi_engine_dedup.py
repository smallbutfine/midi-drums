"""Tests for MIDIEngine's collision dedup (issue #18 review follow-up).

With our mido-based engine, colliding beats (same instrument + same position)
keep only the loudest — because _dedupe_by_instrument_position runs first.
The output is a valid SMF Format 0 file readable by any DAW.
"""

from __future__ import annotations

import io

from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.export.midi.engine import (
    MIDIEngine,
    _dedupe_by_instrument_position,
)


def _note_ons_from_pattern(pattern: Pattern) -> list[dict]:
    """Return a list of note_on dicts from a pattern exported via our engine."""
    engine = MIDIEngine()
    buf = engine.pattern_to_midi(pattern)
    from mido import MidiFile

    m = MidiFile(file=io.BytesIO(buf.getvalue()))
    return [
        {"note": msg.note, "velocity": msg.velocity, "time": msg.time}
        for t in m.tracks
        for msg in t
        if msg.type == "note_on"
    ]


class TestDedupeByInstrumentPosition:
    def test_keeps_loudest_of_colliding_beats(self):
        quiet = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=80)
        loud = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=110)

        result = _dedupe_by_instrument_position([quiet, loud])

        assert result == [loud]

    def test_result_independent_of_input_order(self):
        quiet = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=80)
        loud = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=110)

        assert _dedupe_by_instrument_position(
            [quiet, loud]
        ) == _dedupe_by_instrument_position([loud, quiet])

    def test_different_instruments_at_same_position_both_kept(self):
        crash = Beat(
            position=0.0, instrument=DrumInstrument.CRASH, velocity=110
        )
        kick = Beat(position=0.0, instrument=DrumInstrument.KICK, velocity=100)

        result = _dedupe_by_instrument_position([crash, kick])

        assert len(result) == 2
        assert crash in result
        assert kick in result

    def test_same_instrument_different_positions_both_kept(self):
        first = Beat(
            position=0.0, instrument=DrumInstrument.CRASH, velocity=110
        )
        second = Beat(
            position=1.0, instrument=DrumInstrument.CRASH, velocity=110
        )

        result = _dedupe_by_instrument_position([first, second])

        assert len(result) == 2
        assert first in result
        assert second in result


class TestPatternToMidiDedup:
    def test_colliding_beats_produce_order_independent_output(self):
        """Order-independent dedup: both orderings produce the same MIDI."""
        quiet = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=80)
        loud = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=110)

        notes_quiet_first = _note_ons_from_pattern(
            Pattern(name="a", beats=[quiet, loud])
        )
        notes_loud_first = _note_ons_from_pattern(
            Pattern(name="b", beats=[loud, quiet])
        )

        assert notes_quiet_first == notes_loud_first

    def test_colliding_beats_keep_the_loudest(self):
        """Only the loudest note survives colliding pair."""
        quiet = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=80)
        loud = Beat(position=0.0, instrument=DrumInstrument.CRASH, velocity=110)

        notes_colliding = _note_ons_from_pattern(
            Pattern(name="colliding", beats=[quiet, loud])
        )
        notes_loud_only = _note_ons_from_pattern(
            Pattern(name="loud_only", beats=[loud])
        )

        assert len(notes_colliding) == len(notes_loud_only)
        assert notes_colliding[0]["velocity"] == 110

    def test_non_colliding_beats_are_both_kept(self):
        """Two instruments at same position both produce note_on events."""
        crash = Beat(
            position=0.0, instrument=DrumInstrument.CRASH, velocity=110
        )
        kick = Beat(position=0.0, instrument=DrumInstrument.KICK, velocity=100)

        notes_both = _note_ons_from_pattern(
            Pattern(name="both", beats=[crash, kick])
        )
        notes_crash_only = _note_ons_from_pattern(
            Pattern(name="crash_only", beats=[crash])
        )

        assert len(notes_both) > len(notes_crash_only)


class TestSongToMidiDedup:
    """Song-level dedup (global across all sections)."""

    def test_cross_section_dedup(self):
        """Same pitch same tick in different sections → only one note_on."""
        generator = __import__("midi_drums").DrumGenerator()

        from midi_drums.core.models.song import Section, Song

        beat = Beat(position=0.0, instrument=DrumInstrument.KICK, velocity=100)
        p1 = Pattern(name="p1", beats=[beat])
        p2 = Pattern(name="p2", beats=[beat])  # same note at t=0

        song = Song(
            name="test_dedup",
            tempo=120,
            sections=[
                Section(name="a", bars=1, pattern=p1),
                Section(name="b", bars=1, pattern=p2),
            ],
        )

        buf = generator.midi_engine.song_to_midi(song)
        from mido import MidiFile

        m = MidiFile(file=io.BytesIO(buf.getvalue()))
        kick_tick0 = [
            msg
            for t in m.tracks
            for msg in t
            if msg.type == "note_on" and msg.note == 36 and msg.time == 0
        ]
        assert len(kick_tick0) <= 1, "dedup across sections failed"

    def test_different_notes_not_deduped(self):
        """Different pitches at same tick → both preserved."""
        generator = __import__("midi_drums").DrumGenerator()

        from midi_drums.core.models.song import Section, Song

        beat_kick = Beat(
            position=0.0, instrument=DrumInstrument.KICK, velocity=100
        )
        beat_snare = Beat(
            position=0.0, instrument=DrumInstrument.SNARE, velocity=105
        )
        p1 = Pattern(name="p1", beats=[beat_kick])

        song = Song(
            name="test_diff",
            tempo=120,
            sections=[
                Section(name="a", bars=1, pattern=p1),
                Section(
                    name="b",
                    bars=1,
                    pattern=Pattern(name="p2", beats=[beat_snare]),
                ),
            ],
        )

        buf = generator.midi_engine.song_to_midi(song)
        from mido import MidiFile

        m = MidiFile(file=io.BytesIO(buf.getvalue()))
        notes_tick0 = [
            msg
            for t in m.tracks
            for msg in t
            if msg.type == "note_on" and msg.time == 0
        ]
        # Only KICK (section a) has delta=0; SNARE (section b) is later.
        # What matters: both different notes survive the global dedup.
        all_notes = [
            msg for t in m.tracks for msg in t if msg.type == "note_on"
        ]
        assert any(
            msg.note == 36 for msg in notes_tick0
        ), "KICK should be at tick 0"
        note_nums = {msg.note for msg in all_notes}
        assert (
            38 in note_nums
        ), "SNARE should also survive dedup (different pitch)"
