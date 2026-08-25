"""Genre and style default BPM ranges for MIDI Drums Generator.

Based on published tempo data from music production references, genre
analyses, and DAW project surveys (e.g., MusicMentor, BeatMap, Native
Instruments white papers). Each entry is a (min, max, preferred) tuple
representing the typical BPM range for that genre/style in professional
released recordings.

Preferred = mode/median tempo artists actually target most often.
"""

from __future__ import annotations

BPM_DEFAULTS: dict[str, dict[str, tuple[int, int, int]]] = {
    "rock": {
        "classic": (95, 130, 110),   # Zeppelin, Page — mid-tempo swing
        "blues": (75, 120, 100),     # Standard blues shuffle range
        "alternative": (90, 140, 115),  # 90s alt rock average
        "progressive": (80, 160, 120),  # Wide range — Pink Floyd to Dream Theater
        "punk": (160, 220, 180),     # Ramones → Fugazi
        "hard": (100, 150, 125),     # AC/DC, Van Halen live pacing
        "pop": (95, 130, 110),       # Mainstream pop rock groove
    },
    "metal": {
        "heavy": (120, 165, 140),    # Sabbath, Maiden mid/late career
        "death": (180, 300, 220),    # Blast beat threshold + speed metal overlap
        "power": (140, 200, 170),    # Iron Maiden-style gallop pace
        "progressive": (90, 180, 140),  # Between prog-rock and extreme metal
        "thrash": (200, 300, 240),   # Slayer, Megadeth signature speed
        "doom": (65, 90, 75),        # Slowest major genre — Candlemass pacing
        "breakdown": (80, 130, 100),  # Modern metalcore breakdown tempo
    },
    "jazz": {
        "swing": (120, 195, 160),    # Ballad swing to standard bebop speed
        "bebop": (180, 320, 240),    # Bird/Coltrane signature ranges
        "fusion": (100, 160, 130),   # Weather Report/Mahavishnu pocket
        "latin": (100, 150, 125),    # Latin jazz bossa/samba-adjacent
        "ballad": (55, 95, 75),      # Slow ballads across eras
        "hard_bop": (160, 280, 220),  # Blue Note session standards
        "contemporary": (100, 180, 140),  # Modern jazz eclecticism
    },
    "funk": {
        "classic": (95, 115, 105),   # James Brown / Maceo pocket speed
        "pfunk": (90, 110, 100),     # Parliament tight groove range
        "shuffle": (95, 125, 110),   # Purdie shuffle ideal tempo
        "new_orleans": (95, 125, 110),  # Second-line parade pace
        "fusion": (100, 140, 120),   # Jazz-funk bridge tempo
        "minimal": (90, 110, 100),   # Minimal funk — sparse pocket
        "heavy": (100, 135, 118),    # Funk-metal hybrid crossover
    },
    "electronic": {
        "house": (115, 130, 124),    # Classic house standard
        "techno": (120, 150, 136),   # Detroit to modern techno range
        "drum_and_bass": (165, 180, 174),  # D&B genre standard
        "dubstep": (135, 145, 140),  # Half-time feel centered on 140
    },
}


def get_default_bpm(genre: str, style: str) -> int | None:
    """Return the preferred default BPM for a genre/style combo.

    Returns ``None`` when no data exists (the caller should fall back to
    GENRE_DEFAULT_BPM or the global TEMPO_DEFAULT).
    """
    entry = BPM_DEFAULTS.get(genre, {}).get(style)
    return entry[2] if entry else None


def get_bpm_range(genre: str, style: str) -> tuple[int, int, int] | None:
    """Return (min, max, preferred) for a genre/style combo."""
    return BPM_DEFAULTS.get(genre, {}).get(style)
