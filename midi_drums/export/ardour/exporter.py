"""High-level API for Ardour DAW integration.

Provides convenient methods for exporting MIDI drum generation to Ardour
session projects (.ardourproj).

Example:
    >>> from midi_drums import DrumGenerator
    >>> from midi_drums.export.ardour.exporter import ArdourExporter
    >>>
    >>> # Generate drums
    >>> generator = DrumGenerator()
    >>> song = generator.create_song("metal", "doom", tempo=120)
    >>>
    >>> # Export to Ardour
    >>> exporter = ArdourExporter()
    >>> session_file = exporter.export_with_markers(
    ...     song=song,
    ...     output_name="doom_metal"
    ... )
"""

from __future__ import annotations

from pathlib import Path

from midi_drums.core.models.kit import DrumKit
from midi_drums.core.models.song import Song
from midi_drums.export.ardour.engine import ArdourEngine
from midi_drums.export.midi.engine import MIDIEngine


class ArdourExporter:
    """High-level API for exporting to Ardour sessions.

    Generates a complete Ardour session directory (.ardourproj) from a Song,
    including markers for each section boundary and per-segment tempo/meter
    changes.

    Example:
        >>> exporter = ArdourExporter()
        >>> session_file = exporter.export_with_markers(
        ...     song=my_song,
        ...     output_name="my_project",
        ...     sample_rate=48000
        ... )
        >>> print(f"Session created at: {session_file}")
    """

    def __init__(self, drum_kit: DrumKit | None = None):
        """Initialize Ardour exporter.

        Args:
            drum_kit: Optional kit for MIDI generation (defaults to GM).
        """
        self.midi_engine = MIDIEngine(drum_kit) if drum_kit else MIDIEngine()

    def export_with_markers(
        self,
        song: Song,
        output_name: str | Path = "session",
        sample_rate: int = 48000,
        midi_filename: str | None = None,
    ) -> Path:
        """Export song with markers to a complete Ardour session directory.

        Creates a new Ardour project folder containing:
        - A ``<name>.ardour`` session file with Sources, Regions,
          Locations (markers), and Routes (tracks).
        - The generated MIDI file copied into the interchange/ structure.

        Args:
            song: Song object with sections to export.
            output_name: Base name for the Ardour session folder and
                ``<name>.ardour`` file.  If a ``Path``, only the stem is
                used as the session name.
            sample_rate: Audio sample rate (default 48000 Hz).
            midi_filename: Override filename for the embedded MIDI file
                (defaults to ``<song.name>.mid``).

        Returns:
            Path to the generated ``<output_name>.ardour`` file.

        Raises:
            ValueError: If *song* has no sections.
            FileNotFoundError: If the generated MIDI bytes can't be written.
        """
        if not song.sections:
            raise ValueError("Song must have at least one section")

        out_path = Path(output_name)
        session_base = (
            out_path.stem if out_path.suffix else str(out_path)
        )

        # Build Ardour session directory first (creates interchange/ etc.)
        engine = ArdourEngine(session_base, sample_rate)

        # Write MIDI into the engine's output directory
        out_dir = Path(f"{session_base}")
        midi_dest = out_dir / (midi_filename or f"{song.name}.mid")
        midi_dest.parent.mkdir(parents=True, exist_ok=True)
        self.midi_engine.save_song_midi(song, midi_dest)

        # Generate the .ardour session file
        return engine.export(song, midi_dest)

    def export_session_xml(
        self, song: Song, midi_file_path: Path | str
    ) -> str:
        """Return the Ardour session XML string without writing files.

        Useful for debugging or embedding in other workflows (e.g., Lua
        scripts that parse the XML).

        Args:
            song: Song with section structure.
            midi_file_path: Path to the pre-existing MIDI file that will
                be referenced by ``<Source>``.

        Returns:
            Complete Ardour session XML as a string.
        """
        stem = Path(midi_file_path).stem
        engine = ArdourEngine(f"{stem}_session")
        return engine._build_xml(song, Path(midi_file_path))


__all__ = ["ArdourExporter"]
