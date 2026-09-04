#!/usr/bin/env python3
"""Generate complete multi-section songs using midi_drums CLI --song command."""

import subprocess
from pathlib import Path

OUTPUT_DIR = Path("reaper_test")
OUTPUT_DIR.mkdir(exist_ok=True)

# Genre/style combinations to generate
GENRE_STYLES = [
    ("metal", "doom"),
    ("metal", "death"),
    ("metal", "heavy"),
    ("rock", "classic"),
    ("rock", "blues"),
    ("rock", "alternative"),
    ("jazz", "swing"),
    ("jazz", "bebop"),
    ("jazz", "fusion"),
    ("funk", "classic"),
    ("funk", "shuffle"),
    ("funk", "pfunk"),
]

for genre, style in GENRE_STYLES:
    print(f"\nGenerating {genre}/{style}...")

    # GM MIDI
    subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "midi_drums.api.cli",
            "--song",
            f"--genre={genre}",
            f"--style={style}",
            f"-o={OUTPUT_DIR}/{genre}_{style}_song_gm.mid",
            "--mapping=gm",
        ],
        check=True,
    )

    # AD2 MIDI
    subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "midi_drums.api.cli",
            "--song",
            f"--genre={genre}",
            f"--style={style}",
            f"-o={OUTPUT_DIR}/{genre}_{style}_song_ad2.mid",
            "--mapping=ad2",
        ],
        check=True,
    )

    # RPP (REAPER project)
    subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "midi_drums.api.cli",
            "reaper",
            "export",
            f"--genre={genre}",
            f"--style={style}",
            f"--output={OUTPUT_DIR}/{genre}_{style}_song.rpp",
            "--preset-only",
        ],
        check=True,
    )

    print(f"  [OK] {genre}_{style} - GM/AD2/RPP")

print("\n=== COMPLETE ===")
print(f"Generated in: {OUTPUT_DIR.resolve()}")
