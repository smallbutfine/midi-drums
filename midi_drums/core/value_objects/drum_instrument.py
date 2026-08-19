"""Drum instrument value object - standard MIDI note mappings."""

from enum import Enum


class DrumInstrument(Enum):
    """Standard drum kit instruments with MIDI note mappings."""

    # Core instruments (GM-standard positions)
    KICK = 36
    SNARE = 38
    RIM = 40
    MID_TOM = 47
    FLOOR_TOM = 43
    CRASH = 49
    RIDE = 51
    SPLASH = 55
    CHINA = 52

    # --- Extended hi-hat (EZDrummer-specific, non-GM) ---
    CLOSED_HH = 42  # GM standard
    CLOSED_HH_EDGE = 22  # EZDrummer specific
    CLOSED_HH_TIP = 61  # EZDrummer specific
    TIGHT_HH_EDGE = 62  # EZDrummer specific
    TIGHT_HH_TIP = 63  # EZDrummer specific
    PEDAL_HH = 44
    OPEN_HH = 46  # GM standard
    OPEN_HH_1 = 24  # EZDrummer specific
    OPEN_HH_2 = 25  # EZDrummer specific
    OPEN_HH_3 = 26  # EZDrummer specific
    OPEN_HH_MAX = 60  # EZDrummer specific - fully open

    # --- Ride bell ---
    RIDE_BELL = 53

    # --- Addictive Drums 2 extended instruments ---
    # Base values chosen to avoid GM percussion conflicts. Non-AD2 presets
    # do not map these explicitly (safe: unmapped -> enum fallback, no sound).

    # Brush sweep presets (Snare brush sweep zones)
    BRUSH_SWEEP_A = 35   # Close Soft Tap
    BRUSH_SWEEP_B = 34   # Sweep Mute
    BRUSH_SWEEP_C = 33   # Slow Dark Accent
    BRUSH_SWEEP_D = 32   # Fast Dark Accent
    BRUSH_SWEEP_E = 31   # Slow Bright Accent
    BRUSH_SWEEP_F = 30   # Fast Bright Accent

    # Snare rim / side stick variants
    SNARE_RIMSHOT = 92   # Unique: A#5 AD2 Cymbal Choke zone (rim articulation)

    # Tight hi-hat (velocity-tunable AD2 zones)
    TIGHT_HH_CLOSED = 91  # G5 - highest tight closed

    # Tom edge hits (rimmed tom strikes)
    TOM_EDGE_MID = 65    # Floor Tom Open Hit (AD2 mid edge)
    TOM_EDGE_FLOOR = 65  # Floor Tom Open Hit
    TOM_EDGE_3 = 67      # Tom 3 Rimshot Open Hit
    TOM_EDGE_4 = 69      # Tom 2 Rimshot Open Hit

    # Crash choke articulations
    CRASH_CHOKED_A = 80  # F#5 - Choke A
    CRASH_CHOKED_B = 79  # G4  - Choke B
    CRASH_CHOKED_C = 71  # F3  - Choke C
    CRASH_CHOKED_D = 68  # E3  - Choke D
