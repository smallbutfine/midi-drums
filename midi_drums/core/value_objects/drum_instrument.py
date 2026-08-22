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

    # === Addictive Drums 2 extended instruments ===
    # Base values chosen to avoid GM percussion conflicts. Non-AD2 presets
    # do not map these explicitly (safe: unmapped -> enum fallback, no sound).

    # Brush sweep presets (Snare brush sweep zones)
    BRUSH_SWEEP_A = 35  # Close Soft Tap
    BRUSH_SWEEP_B = 34  # Sweep Mute
    BRUSH_SWEEP_C = 33  # Slow Dark Accent
    BRUSH_SWEEP_D = 32  # Fast Dark Accent
    BRUSH_SWEEP_E = 31  # Slow Bright Accent
    BRUSH_SWEEP_F = 30  # Fast Bright Accent

    # Snare rim / side stick variants
    SNARE_RIMSHOT = 92  # Unique: A#5 AD2 Cymbal Choke zone (rim articulation)

    # Tight hi-hat (velocity-tunable AD2 zones)
    TIGHT_HH_CLOSED = 91  # G5 - highest tight closed

    # Tom edge hits (rimmed tom strikes)
    TOM_EDGE_MID = 65  # Floor Tom Open Hit (AD2 mid edge)
    TOM_EDGE_FLOOR = 65  # Floor Tom Open Hit
    TOM_EDGE_3 = 67  # Tom 3 Rimshot Open Hit
    TOM_EDGE_4 = 69  # Tom 2 Rimshot Open Hit

    # Crash choke articulations
    CRASH_CHOKED_A = 80  # F#5 - Choke A
    CRASH_CHOKED_B = 79  # G4  - Choke B
    CRASH_CHOKED_C = 71  # F3  - Choke C
    CRASH_CHOKED_D = 68  # E3  - Choke D

    # === AD2 extended zones not in standard GM ===
    # These are unique to Addictive Drums 2 and provide timbral variety
    # All MIDI values taken from the AD2 keymap PDF (Addictive Drums 2 Keymap.pdf)

    # --- Ride cymbal variants (different striking positions) ---
    RIDE_SHAFT = 54  # B#2 - Ride shaft hit (metallic, bell-like timbre) for metal sections
    RIDE_BELL_ALT = 85  # C#5 - Alt bell position for fills/accents
    RIDE_1_TIP = 60  # C3 - Softer ride tip for verses/intros

    # --- Tom edge/rim across ALL toms (aggressive attack in rock/metal) ---
    TOM_EDGE_1 = 72  # F#4 - Tom 1 Rimshot Open Hit (tight high tom)
    TOM_EDGE_2 = 70  # A#3 - Tom 2 Rimshot Open Hit (mid tom)

    # --- Crash cymbal types (different pitches/timbres for variety) ---
    CRASH_HEAVY = 89  # F5 - Heavy crash for choruses/dynamics
    CRASH_LIGHT = 77  # F4 - Light/medium crash for verses
    CRASH_SPLASH = 93  # A5 - High splashy crash for fills

    # --- Tight HH full range (funk/rock pocket depth control) ---
    TIGHT_HH_A = 54  # B2 - Looser tight HH for funk groove
    TIGHT_HH_B = 56  # C3 - Medium-tight HH
    TIGHT_HH_C = 58  # D#3 - Tightest control (punk/alternative)

    # --- Open HH full range ---
    OPEN_HH_SOFT = 27  # A#1 - Softer open crash cymbal
    OPEN_HH_FULL = 28  # C2 - Full open for dramatic sections

    # --- Flexi triggers (multi-hit tom zones for progressive patterns) ---
    FLEXI_1 = 95  # B4 - Flexi Tom 1 trigger
    FLEXI_2 = 96  # C#5 - Flexi Tom 2 trigger
    FLEXI_3 = 101  # A#5 - Flexi Tom 3 trigger
