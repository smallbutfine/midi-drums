from pathlib import Path

import mido

# Read a GM file and show every unique note-on note number
gm_files = sorted(Path("reaper_test").glob("*_gm.mid"))[:3]
for f in gm_files:
    print(f"\n=== {f.name} ===")
    mid = mido.MidiFile(str(f))
    notes = set()
    for track in mid.tracks:
        tick = 0
        for msg in track:
            if hasattr(msg, "note"):
                notes.add((msg.note, msg.type))
    for note in sorted(notes):
        print(f"  {note}")
