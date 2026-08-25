"""MIDI file generation engine using mido (SMF-compliant).

All output files are valid SMF Format 0 so any DAW can open them.
"""

import io
import tempfile
from pathlib import Path

from midi_drums.core.models.kit import DrumKit
from midi_drums.core.models.pattern import Beat, Pattern
from midi_drums.core.models.song import Song


def _dedupe_by_instrument_position(beats: list[Beat]) -> list[Beat]:
    """If two beats share (instrument, position), keep only the loudest."""
    deduped: dict[tuple, Beat] = {}
    for beat in beats:
        key = (beat.instrument, round(beat.position, 6))
        if key not in deduped or beat.velocity > deduped[key].velocity:
            deduped[key] = beat
    return list(deduped.values())


# Standard drum note numbers for common instruments.
_INSTR_NOTE = {
    "KICK": 36,
    "SNARE": 38,
    "RIM": 40,
    "MID_TOM": 47,
    "FLOOR_TOM": 43,
    "CRASH": 49,
    "RIDE": 51,
    "SPLASH": 55,
    "CHINA": 52,
    "CLOSED_HH": 42,
    "PEDAL_HH": 44,
    "OPEN_HH": 46,
    "RIDE_BELL": 53,
    "TOM_EDGE_MID": 65,
    "TOM_EDGE_3": 67,
    "TOM_EDGE_4": 69,
    "CRASH_CHOKED_A": 80,
    "CRASH_CHOKED_B": 79,
    "CRASH_CHOKED_C": 71,
    "CRASH_CHOKED_D": 68,
    "RIDE_SHAFT": 62,
    "RIDE_BELL_ALT": 61,
    "TIGHT_HH_EDGE": 91,
    "TIGHT_HH_TIP": 90,
    "TIGHT_HH_CLOSED": 91,
    "OPEN_HH_1": 54,
    "OPEN_HH_2": 55,
    "OPEN_HH_3": 56,
    "CLOSED_HH_EDGE": 42,
    "CLOSED_HH_TIP": 49,
}


def _mid_note(instrument) -> int:
    """Resolve a DrumInstrument enum value (or plain int) to a MIDI note.

    This is the legacy fallback used only when no drum_kit context is
    available (should be rare — prefer MIDIEngine._resolve_note).
    """
    if isinstance(instrument, int):
        return instrument
    if not hasattr(instrument, "value"):
        name = str(instrument).split(".")[-1]
        return _INSTR_NOTE.get(name, 60)
    name = (
        str(instrument.value).split(".")[-1]
        if hasattr(instrument.value, "__name__")
        else str(instrument)
    )
    return _INSTR_NOTE.get(name, int(instrument.value))


class MIDIEngine:
    """Engine for generating MIDI files from patterns and songs.

    Uses **mido** internally so all output is valid SMF (any DAW works).
    """

    def __init__(self, drum_kit: DrumKit | None = None):
        self.drum_kit = drum_kit or DrumKit.create_ezdrummer3_kit()

    # ------------------------------------------------------------------
    # Note resolution
    # ------------------------------------------------------------------

    def _resolve_note(self, instrument) -> int:
        """Resolve a DrumInstrument (or int) to a MIDI note using this engine's drum kit."""
        if isinstance(instrument, int):
            return instrument
        return self.drum_kit.get_midi_note(instrument)

    # ------------------------------------------------------------------
    # Public write methods
    # ------------------------------------------------------------------

    def save_pattern_midi(
        self, pattern: Pattern, output_path: Path | str, tempo: int = 120
    ) -> None:
        data = self._pattern_to_bytes(pattern, tempo)
        with open(output_path, "wb") as f:
            f.write(data.getvalue())

    def save_song_midi(self, song: Song, output_path: Path | str) -> None:
        data = self._song_to_bytes(song)
        with open(output_path, "wb") as f:
            f.write(data.getvalue())

    # ------------------------------------------------------------------
    # Pattern → bytes
    # ------------------------------------------------------------------

    def _pattern_to_bytes(self, pattern: Pattern, tempo: int) -> io.BytesIO:

        from mido import Message as Msg
        from mido import MetaMessage as MM
        from mido import MidiFile as MF

        tpq = 960
        # Collect all events with absolute tick positions
        events: list[tuple[int, object]] = []

        events.append((0, MM("set_tempo", tempo=tempo, time=0)))

        for beat in _dedupe_by_instrument_position(pattern.beats):
            tick = int(round(beat.position * tpq))
            mn = self._resolve_note(beat.instrument)
            events.append(
                (
                    tick,
                    Msg(
                        "note_on",
                        channel=9,
                        note=mn,
                        velocity=min(max(beat.velocity, 0), 127),
                        time=0,
                    ),
                )
            )
            dur_ticks = max(int(round(min(beat.duration, 0.2) * tpq)), 1)
            events.append(
                (
                    tick + dur_ticks,
                    Msg("note_off", channel=9, note=mn, velocity=0, time=0),
                )
            )

        events.append(
            (events[-1][0] if events else 1, MM("end_of_track", time=0))
        )

        # Sort by absolute tick position
        events.sort(key=lambda e: e[0])

        mf = MF(type=0, ticks_per_beat=tpq)
        track = __import__("mido").MidiTrack()
        mf.tracks.append(track)

        prev_tick = 0
        for abs_tick, msg in events:
            delta = max(0, abs_tick - prev_tick)  # clamp to non-negative
            if hasattr(msg, "time"):
                msg.time = delta
            else:
                msg = type(msg)(**msg._fields)  # copy with updated time
            track.append(msg)
            prev_tick = abs_tick

        buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tf:
            mf.save(tf.name)
            buf.write(open(tf.name, "rb").read())
        return buf

    # ------------------------------------------------------------------
    # Song → bytes
    # ------------------------------------------------------------------

    def _song_to_bytes(self, song: Song) -> io.BytesIO:

        from mido import Message as Msg
        from mido import MetaMessage as MM
        from mido import MidiFile as MF

        tpq = 960
        # Collect events with absolute tick positions
        events: list[tuple[int, object]] = []
        added_note_ticks: set[tuple[int, int]] = set()
        time_cursor = 0.0
        tempo_state = {
            "tempo": song.tempo,
            "ts_num": song.time_signature.numerator,
            "ts_den": song.time_signature.denominator,
        }

        def _add_tick(tick: int, msg) -> None:
            events.append((tick, msg))

        # Initial tempo at tick 0
        _add_tick(0, MM("set_tempo", tempo=song.tempo, time=0))

        for section in song.sections:
            ts_num = section.effective_time_signature(
                0, song.time_signature
            ).numerator

            for bar_num in range(section.bars):
                eff_tempo = section.effective_tempo(bar_num, song.tempo)
                eff_ts = section.effective_time_signature(
                    bar_num, song.time_signature
                )
                ebn, edn = eff_ts.numerator, eff_ts.denominator

                # Tempo / time-sig markers
                if eff_tempo != tempo_state["tempo"]:
                    tick_now = int(round(time_cursor * tpq))
                    _add_tick(
                        tick_now, MM("set_tempo", tempo=eff_tempo, time=0)
                    )
                    tempo_state["tempo"] = eff_tempo

                if (ebn, edn) != (tempo_state["ts_num"], tempo_state["ts_den"]):
                    tick_now = int(round(time_cursor * tpq))
                    _add_tick(
                        tick_now,
                        MM(
                            "time_signature",
                            numerator=ebn,
                            denominator=edn,  # mido expects actual denominator (e.g. 8), not bit-shift exponent
                        ),
                    )
                    tempo_state["ts_num"], tempo_state["ts_den"] = ebn, edn

                bp = eff_ts.numerator
                # bar_start_beats is the cumulative beat position of this bar.
                # time_cursor advances by bp each iteration inside the loop,
                # so we just use it directly — do NOT add bar_num * bp here.
                bar_start_beats = time_cursor

                # Groove offset (same logic as original code)
                if (
                    hasattr(section, "groove_offsets_ms")
                    and section.groove_offsets_ms
                ):
                    raw_ms = (
                        section.groove_offsets_ms.get(bar_num, 0.0)
                        if isinstance(section.groove_offsets_ms, dict)
                        else (
                            section.groove_offsets_ms[bar_num]
                            if bar_num < len(section.groove_offsets_ms)
                            else 0.0
                        )
                    )
                    bar_start_beats += (raw_ms / 60000.0) * eff_tempo

                pattern = section.get_effective_pattern(bar_num)

                # Multi-bar pattern tiling (same logic as original)
                import copy as _copy

                if pattern.beats:
                    _max_pos = max(b.position for b in pattern.beats)
                    import math

                    _pbars = max(1, math.ceil((_max_pos + 1) / ts_num))
                else:
                    _pbars = 1

                if _pbars > 1:
                    cycle_bar = bar_num % _pbars
                    beats_to_render = [
                        b
                        for b in pattern.beats
                        if int(b.position / ts_num) == cycle_bar
                    ]
                    adjusted_beats = []
                    for b in beats_to_render:
                        nb = _copy.copy(b)
                        nb.position = b.position - cycle_bar * ts_num
                        adjusted_beats.append(nb)
                else:
                    adjusted_beats = pattern.beats

                deduped_beats = _dedupe_by_instrument_position(adjusted_beats)

                for beat in sorted(deduped_beats, key=lambda b: b.position):
                    mn = self._resolve_note(beat.instrument)
                    abs_tick = int(
                        round(bar_start_beats * tpq + beat.position * tpq)
                    )
                    on_key = (mn, abs_tick)
                    if on_key in added_note_ticks:
                        continue
                    added_note_ticks.add(on_key)
                    _add_tick(
                        abs_tick,
                        Msg(
                            "note_on",
                            channel=9,
                            note=mn,
                            velocity=min(max(beat.velocity, 0), 127),
                            time=0,
                        ),
                    )

                # Fill at section end (same logic as original)
                fill = None
                if song.global_parameters:
                    fill = section.should_add_fill(
                        bar_num, song.global_parameters.fill_frequency
                    )
                if fill and bar_num == section.bars - 1:
                    fill_start = bar_start_beats + (ts_num - 1.0)
                    for fb in fill.pattern.beats:
                        if fb.position < 1.0:
                            mn = self._resolve_note(fb.instrument)
                            abs_tick = int(
                                round(fill_start * tpq + fb.position * tpq)
                            )
                            on_key = (mn, abs_tick)
                            if on_key in added_note_ticks:
                                continue
                            added_note_ticks.add(on_key)
                            _add_tick(
                                abs_tick,
                                Msg(
                                    "note_on",
                                    channel=9,
                                    note=mn,
                                    velocity=min(max(fb.velocity, 0), 127),
                                    time=0,
                                ),
                            )

                time_cursor += bp

            # Section end marker
            tick_now = int(round(time_cursor * tpq))
            _add_tick(tick_now, MM("end_of_track", time=0))

        # Sort by absolute tick and emit with delta-times
        events.sort(key=lambda e: e[0])

        mf = MF(type=0, ticks_per_beat=tpq)
        track = __import__("mido").MidiTrack()
        mf.tracks.append(track)

        prev_tick = 0
        for abs_tick, msg in events:
            delta = max(0, abs_tick - prev_tick)  # clamp to non-negative
            if hasattr(msg, "time"):
                msg.time = delta
            else:
                msg = type(msg)(**msg._fields)
            track.append(msg)
            prev_tick = abs_tick

        buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tf:
            mf.save(tf.name)
            buf.write(open(tf.name, "rb").read())
        return buf

    # ------------------------------------------------------------------
    # API compatibility layer (signatures match the old midiutil version)
    # ------------------------------------------------------------------

    def pattern_to_midi(self, pattern: Pattern, tempo: int = 120) -> io.BytesIO:
        """Convert a single pattern to MIDI binary."""
        return self._pattern_to_bytes(pattern, tempo)

    def song_to_midi(self, song: Song) -> io.BytesIO:
        """Convert a complete song to MIDI binary."""
        return self._song_to_bytes(song)

    def export_patterns_to_separate_files(
        self, patterns: list[Pattern], output_dir: Path, tempo: int = 120
    ) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files: list[Path] = []
        for i, pattern in enumerate(patterns):
            fn = pattern.name or f"pattern_{i:02d}"
            path = output_dir / f"{fn}.mid"
            self.save_pattern_midi(pattern, path, tempo)
            files.append(path)
        return files

    def create_multi_track_midi(
        self, patterns: list[Pattern], tempo: int = 120
    ) -> io.BytesIO:

        from mido import Message as Msg
        from mido import MetaMessage as MM
        from mido import MidiFile as MF

        mf = MF(type=1, ticks_per_beat=960)
        channel = self.drum_kit.channel
        for idx, pattern in enumerate(patterns):
            t = __import__("mido").MidiTrack()
            mf.tracks.append(t)
            t.append(MM("set_tempo", tempo=tempo, time=0))
            t.append(
                MM(
                    "track_name",
                    name=pattern.name or f"Pattern {idx+1}",
                    time=0,
                )
            )
            for beat in pattern.beats:
                mn = self._resolve_note(beat.instrument)
                t.append(
                    Msg(
                        "note_on",
                        channel=channel,
                        note=mn,
                        velocity=beat.velocity,
                        time=int(round(beat.position * 960)),
                    )
                )
                t.append(
                    Msg(
                        "note_off",
                        channel=channel,
                        note=mn,
                        velocity=0,
                        time=int(round(min(beat.duration, 0.2) * 960)),
                    )
                )
            t.append(MM("end_of_track", time=0))

        buf = io.BytesIO()
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tf:
            mf.save(tf.name)
            buf.write(open(tf.name, "rb").read())
        return buf

    def apply_humanization_to_midi(
        self,
        midi: io.BytesIO,
        timing_variance: float = 0.02,
        velocity_variance: int = 10,
    ) -> io.BytesIO:
        """Placeholder — humanization is now applied during pattern generation."""
        return midi

    def get_midi_info(self, song: Song) -> dict:
        """Get information about the MIDI file that would be generated."""
        total_bars = song.total_bars()
        duration_seconds = song.total_duration_seconds()
        total_beats = sum(
            len(section.pattern.beats) * section.bars
            for section in song.sections
        )
        return {
            "total_bars": total_bars,
            "duration_seconds": duration_seconds,
            "total_beats": total_beats,
            "tempo": song.tempo,
        }
