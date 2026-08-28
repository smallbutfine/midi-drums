"""Tests for MIDIEngine's per-segment tempo/time-signature export.

Covers issue #53 AC Group 2: segmented Sections must actually produce
MIDI tempo/time-signature marker events at segment boundaries, while
non-segmented songs remain valid.
"""

from __future__ import annotations

import io

import pytest

from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.models.song import Section, Song, SongSegment
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.core.value_objects.time_signature import TimeSignature
from midi_drums.export.midi.engine import MIDIEngine


def _fixture_pattern() -> Pattern:
    pattern = Pattern("fixture_pattern")
    pattern.beats = [
        Beat(0.0, DrumInstrument.KICK, 105, 0.1),
        Beat(1.0, DrumInstrument.SNARE, 110, 0.1),
        Beat(0.5, DrumInstrument.CLOSED_HH, 80, 0.1),
        Beat(1.5, DrumInstrument.CLOSED_HH, 80, 0.1),
    ]
    return pattern


def _read_midob(midi_bytes: "bytes | io.BytesIO") -> list[dict]:
    """Parse MIDI bytes via mido and return tempo + time-sig events."""
    import io

    from mido import MidiFile

    buf = (
        midi_bytes.getvalue()
        if isinstance(midi_bytes, io.BytesIO)
        else midi_bytes
    )
    m = MidiFile(file=io.BytesIO(buf))
    # Flatten all tracks
    events: list[dict] = []
    tick = 0
    for track in m.tracks:
        for msg in track:
            ev = {"type": msg.type, "tick": tick}
            if hasattr(msg, "tempo"):
                # mido stores set_tempo as microseconds per quarter note
                ev["tempo"] = msg.tempo
                ev["bpm"] = int(60_000_000 / msg.tempo)
            elif hasattr(msg, "numerator") and hasattr(msg, "denominator"):
                ev["numerator"] = msg.numerator
                # mido stores the actual denominator (e.g. 4 for 4/4, 8 for 8/8)
                ev["denominator"] = msg.denominator
            events.append(ev)
            tick += msg.time
    return events


def _filter_events(events: list[dict], evt_type: str) -> list[dict]:
    if evt_type == "Tempo":
        return [e for e in events if e["type"] == "set_tempo"]
    elif evt_type == "TimeSignature":
        return [e for e in events if e["type"] == "time_signature"]
    return []


class TestNonSegmentedSongUnchanged:
    def test_valid_smf_output(self):
        """Non-segmented song produces valid SMF (mido can read it)."""
        pattern = _fixture_pattern()
        song = Song(name="fixture_song", tempo=120)
        song.add_section(Section("verse", pattern, bars=2))
        song.add_section(Section("chorus", pattern, bars=2))

        engine = MIDIEngine()
        buf = engine.song_to_midi(song)
        import io

        from mido import MidiFile

        m = MidiFile(file=io.BytesIO(buf.getvalue()))
        assert m.type == 0
        assert len(m.tracks) == 1
        # Should have at least tempo + notes + end_of_track
        total_msgs = sum(len(t) for t in m.tracks)
        assert total_msgs > 5

    def test_no_tempo_or_time_signature_events_beyond_the_initial_one(self):
        pattern = _fixture_pattern()
        song = Song(name="s", tempo=120)
        song.add_section(Section("verse", pattern, bars=4))

        midi = MIDIEngine().song_to_midi(song)
        events = _read_midob(midi)
        tempos = _filter_events(events, "Tempo")

        assert len(tempos) == 1  # only the initial song.tempo event
        assert len(_filter_events(events, "TimeSignature")) == 0


class TestSegmentedSongEmitsMarkers:
    def test_tempo_change_mid_section_emits_marker(self):
        pattern = _fixture_pattern()
        song = Song(name="s", tempo=120)
        song.add_section(
            Section(
                "verse",
                pattern,
                bars=4,
                segments=[
                    SongSegment(bars=2, tempo=120),
                    SongSegment(bars=2, tempo=160),
                ],
            )
        )

        midi = MIDIEngine().song_to_midi(song)
        events = _read_midob(midi)
        tempos = _filter_events(events, "Tempo")

        # Initial 120bpm event at t=0, plus a 160bpm event at bar 2's start.
        assert len(tempos) == 2
        bpms = [t["bpm"] for t in tempos]
        assert bpms == [120, 160]

    def test_meter_change_mid_section_emits_marker_and_reverts(self):
        # Mirrors song_map.json's "Verse 1": 8@4/4 -> 2@7/8 -> 6@4/4
        pattern = _fixture_pattern()
        song = Song(name="s", tempo=144)
        song.add_section(
            Section(
                "verse",
                pattern,
                bars=16,
                segments=[
                    SongSegment(bars=8, tempo=144),
                    SongSegment(
                        bars=2, tempo=144, time_signature=TimeSignature(7, 8)
                    ),
                    SongSegment(bars=6, tempo=144),
                ],
            )
        )

        midi = MIDIEngine().song_to_midi(song)
        events = _read_midob(midi)
        sigs = _filter_events(events, "TimeSignature")

        # One event entering the 7/8 insert, one event reverting to 4/4.
        assert len(sigs) == 2
        assert (sigs[0]["numerator"], sigs[0]["denominator"]) == (7, 8)
        assert (sigs[1]["numerator"], sigs[1]["denominator"]) == (4, 4)

    def test_section_without_segments_after_segmented_section_inherits_song_defaults(
        self,
    ):
        pattern = _fixture_pattern()
        song = Song(name="s", tempo=120)
        song.add_section(
            Section(
                "verse",
                pattern,
                bars=2,
                segments=[SongSegment(bars=2, tempo=180)],
            )
        )
        song.add_section(Section("chorus", pattern, bars=2))

        midi = MIDIEngine().song_to_midi(song)
        events = _read_midob(midi)
        tempos = _filter_events(events, "Tempo")

        # 120 (initial) -> 180 (segment) -> 120 (chorus reverting to song
        # global, since it has no segments of its own).
        bpms = [t["bpm"] for t in tempos]
        assert bpms == [120, 180, 120]


class TestSongDurationMatchesMidiLength:
    def test_get_midi_info_duration_accounts_for_segments(self):
        pattern = _fixture_pattern()
        song = Song(name="s", tempo=120)
        song.add_section(
            Section(
                "verse",
                pattern,
                bars=4,
                segments=[
                    SongSegment(bars=2, tempo=120),
                    SongSegment(bars=2, tempo=240),
                ],
            )
        )

        info = MIDIEngine().get_midi_info(song)
        # 2 bars @120bpm (4s) + 2 bars @240bpm (2s) = 6s
        assert info["duration_seconds"] == pytest.approx(6.0)


class TestPatternToMidiValidOutput:
    def test_pattern_produces_valid_smf(self):
        pattern = _fixture_pattern()
        engine = MIDIEngine()
        buf = engine.pattern_to_midi(pattern, tempo=120)

        import io

        from mido import MidiFile

        m = MidiFile(file=io.BytesIO(buf.getvalue()))
        assert m.type == 0
        assert len(m.tracks) == 1
        note_ons = [msg for t in m.tracks for msg in t if msg.type == "note_on"]
        assert len(note_ons) >= len(pattern.beats)
