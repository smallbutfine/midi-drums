"""Ardour session export engine.

Generates a valid .ardourproj directory from a Song object, including:
- Native Ardour XML session file with Sources, Regions, Locations (markers),
  and Routes (tracks).
- Directory layout with interchange/ structure for Ardour source resolution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from midi_drums.core.models.song import Song

# ------------------------------------------------------------------ #
#  XML helpers                                                       #
# ------------------------------------------------------------------ #


def _escape_xml(text: str) -> str:
    """Escape XML-special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _xml_attrs(attrs: dict[str, Any]) -> str:
    """Render ``{k: v}`` as ``key1="val1" key2="val2"``."""
    return " ".join(
        f'{_escape_xml(str(k))}="{_escape_xml(str(v))}"'
        for k, v in attrs.items()
    )


# ------------------------------------------------------------------ #
#  Core Ardour exporter                                              #
# ------------------------------------------------------------------ #


class ArdourEngine:
    """Low-level engine that builds an Ardour session directory."""

    DEFAULT_SAMPLE_RATE = 48000

    def __init__(
        self,
        session_name: str = "session",
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ):
        self.session_name = session_name
        self.sample_rate = sample_rate

    # ------------------------------------------------------------------ #
    #  Public API                                                        #
    # ------------------------------------------------------------------ #

    def export(self, song: Song, midi_file_path: Path | str) -> Path:
        """Export *song* + MIDI to a complete Ardour session directory.

        Returns the path to the ``<session_name>.ardour`` file inside
        the new project folder.

        The caller is responsible for ensuring the MIDI file exists at
        *midi_file_path*.  This engine does **not** generate or copy
        MIDI -- that work belongs to :class:`~midi_drums.export.midi.engine.MIDIEngine`
        or a caller that writes the file beforehand.
        """
        midi_src = Path(midi_file_path).resolve()
        if not midi_src.exists():
            raise FileNotFoundError(f"MIDI file not found: {midi_src}")

        out_dir = self._ensure_directory(song)
        session_file = out_dir / f"{self.session_name}.ardour"
        session_file.write_text(
            self._build_xml(song, midi_src), encoding="utf-8"
        )
        return session_file

    # ------------------------------------------------------------------ #
    #  Directory layout                                                  #
    # ------------------------------------------------------------------ #

    def _ensure_directory(self, song: Song) -> Path:
        """Create the Ardour project folder + interchange structure.

        Returns the output directory path.
        """
        out_dir = Path(f"{self.session_name}")
        out_dir.mkdir(exist_ok=True)
        interchange_dir = out_dir / "interchange" / self.session_name / "audio"
        interchange_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    # ------------------------------------------------------------------ #
    #  XML generation                                                    #
    # ------------------------------------------------------------------ #

    def _build_xml(self, song: Song, midi_src: Path) -> str:
        """Build the complete Ardour session XML."""
        source_id = 1000001
        region_id = 2000001
        location_ids_start = 9000001
        route_id = 3000001
        playlist_id = 4000001

        midi_length_samples = int(
            song.total_duration_seconds() * self.sample_rate
        )

        sources_xml = self._render_sources(source_id, midi_src)
        regions_xml = self._render_regions(
            source_id, region_id, midi_src.name, midi_length_samples
        )
        locations_xml = self._render_locations(song, location_ids_start)
        routes_xml = self._render_routes(
            route_id, playlist_id, region_id, song.name
        )

        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<Session version="7000" name="{_escape_xml(self.session_name)}" sample-rate="{self.sample_rate}" end-link="0" unit-bits="32" stereo-clean-mix="false">
  <Config>
    <Option name="sample-rate" value="{self.sample_rate}"/>
    <Option name="sample-format" value="24bitInt"/>
    <Option name="srate" value="{self.sample_rate}"/>
  </Config>
  <Metadata/>
  <Sources>
{sources_xml}  </Sources>
  <Regions>
{regions_xml}  </Regions>
  <Locations>
{locations_xml}  </Locations>
  <Routes>
{routes_xml}  </Routes>
</Session>
"""

    def _render_sources(self, source_id: int, midi_src: Path) -> str:
        """<Sources> block."""
        escaped_name = _escape_xml(midi_src.name)
        return (
            f'    <Source type="midi" name="{escaped_name}" '
            f'id="{source_id}" origin="" flags=""/>\n'
        )

    def _render_regions(
        self,
        source_id: int,
        region_id: int,
        midi_filename: str,
        length_samples: int,
    ) -> str:
        """<Regions> block -- one Region covering the whole MIDI."""
        escaped_name = _escape_xml(Path(midi_filename).stem)
        return (
            f'    <Region id="{region_id}" name="{escaped_name}" '
            f'source="{source_id}" start="0" length="{length_samples}" '
            f'position="0" type="midi" flags="Opaque,Valid,WholeFile"/>\n'
        )

    def _render_locations(self, song: Song, start_id: int) -> str:
        """<Locations> block with markers for every section boundary and
        per-segment tempo/time-signature changes."""
        lines: list[str] = []
        elapsed = 0.0
        next_id = start_id

        for section in song.sections:
            # Section-start marker
            sample_pos = int(round(elapsed * self.sample_rate))
            name = _escape_xml(section.name.title())
            lines.append(
                f'    <Location id="{next_id}" name="{name}" '
                f'start="{sample_pos}" end="{sample_pos}" '
                f'flags="IsMark" locked="false" '
                f'position-lock-style="AudioTime"/>'
            )
            next_id += 1

            # Per-segment markers (only when the section has segments)
            if section.segments:
                seg_elapsed = elapsed
                for segment in section.segments:
                    bars = segment.bars
                    tempo = segment.tempo or song.tempo
                    ts = segment.time_signature or song.time_signature
                    beats = bars * ts.beats_per_bar
                    duration_secs = beats / (tempo / 60.0)

                    mid = seg_elapsed + duration_secs / 2.0
                    sample_pos = int(round(mid * self.sample_rate))
                    label = f"t{tempo}m{ts.num}/{ts.denom}"
                    lines.append(
                        f'    <Location id="{next_id}" name="{_escape_xml(label)}" '
                        f'start="{sample_pos}" end="{sample_pos}" '
                        f'flags="IsMark|TempoChange" locked="false" '
                        f'position-lock-style="AudioTime"/>'
                    )
                    next_id += 1
                    seg_elapsed += duration_secs

            # Advance elapsed for the current section
            beats = section.bars * song.time_signature.beats_per_bar
            duration_secs = beats / (song.tempo / 60.0)
            elapsed += duration_secs

        return (
            "\n".join(lines) + "\n" if lines else "    <!-- no locations -->\n"
        )

    def _render_routes(
        self, route_id: int, playlist_id: int, region_id: int, track_name: str
    ) -> str:
        """<Routes> block with one MIDI track containing the Region."""
        escaped_name = _escape_xml(track_name)
        return (
            f'    <Route id="{route_id}" name="{escaped_name} MIDI" '
            f'default-output-channels="2" flags="MidiTrack" active="yes" '
            f'locked="no">\n'
            f'      <Playlist id="{playlist_id}" '
            f'name="{escaped_name} MIDI 1" orig_track_id="{route_id}">\n'
            f'        <Region id="{region_id}" position="0"/>\n'
            f"      </Playlist>\n"
            f"    </Route>\n"
        )


# ------------------------------------------------------------------ #
#  Convenience                                                        #
# ------------------------------------------------------------------ #


def export_ardour_session(
    song: Song,
    midi_file_path: Path | str,
    session_name: str | None = None,
    sample_rate: int = ArdourEngine.DEFAULT_SAMPLE_RATE,
) -> Path:
    """High-level convenience function.

    Returns the path to the generated ``<name>.ardour`` file.
    """
    if session_name is None:
        stem = Path(midi_file_path).stem
        session_name = f"{stem}_ardour"

    engine = ArdourEngine(session_name, sample_rate)
    return engine.export(song, midi_file_path)
