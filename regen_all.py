#!/usr/bin/env python3
"""Generate all songs for all drummers and styles (GM + AD2 + RPP)."""
import subprocess, sys, os

drummers = ["bonham", "porcaro", "weckl", "chambers", "carey", "dee",
            "roeder", "hoglan", "rich", "copeland", "smith", "haake", "halpern", "peart"]

genres = {
    "metal": ["doom", "death", "heavy", "power", "progressive", "thrash", "breakdown"],
    "rock": ["classic", "blues", "alternative", "progressive", "punk", "hard", "pop"],
    "jazz": ["swing", "bebop", "fusion", "latin", "ballad", "hard_bop", "contemporary"],
    "funk": ["classic", "pfunk", "shuffle", "new_orleans", "fusion", "minimal", "heavy"],
    "electronic": ["house", "techno", "drum_and_bass", "dubstep"],
}

os.makedirs("reaper_test", exist_ok=True)
count = 0

for genre, styles in genres.items():
    print(f"\n[{genre.upper()}]")
    for style in styles:
        for drummer in drummers:
            slug = f"{genre}_{style}_{drummer}"
            prefix = f"reaper_test/{slug}"

            # GM MIDI (default mapping)
            r1 = subprocess.run(
                ["midi-drums", "--song", "--genre", genre, "--style", style,
                 "--output", f"{prefix}_gm.mid"],
                capture_output=True, text=True
            )
            if r1.returncode != 0:
                print(f"  GM ERROR ({slug}): {r1.stderr.strip()}")

            # AD2 MIDI
            r2 = subprocess.run(
                ["midi-drums", "--song", "--genre", genre, "--style", style,
                 "--output", f"{prefix}_ad2.mid", "--mapping", "addictive_drums"],
                capture_output=True, text=True
            )
            if r2.returncode != 0:
                print(f"  AD2 ERROR ({slug}): {r2.stderr.strip()}")

            # RPP
            r3 = subprocess.run(
                ["midi-drums", "reaper", "export", "--genre", genre, "--style", style,
                 "--output", f"{prefix}.rpp", "--preset-only"],
                capture_output=True, text=True
            )
            if r3.returncode != 0:
                print(f"  RPP ERROR ({slug}): {r3.stderr.strip()}")

            count += 1
            if count % 50 == 0:
                print(f"  Progress: {count}/1344", file=sys.stderr)

print(f"\nDone! Generated {count} song combos.")
