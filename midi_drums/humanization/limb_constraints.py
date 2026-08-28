"""Limb constraint engine for physical drum performance modeling."""

from enum import Enum
from typing import Dict, List

from midi_drums.core.models.pattern import Beat
from midi_drums.core.value_objects.drum_instrument import DrumInstrument


class Limb(Enum):
    LH = "LH"
    RH = "RH"
    LF = "LF"
    RF = "RF"


# Mapping instruments to limbs based on standard right-handed playing
# Note: Can be extended to support lefty/open-handed configurations
INSTRUMENT_TO_LIMB: Dict[DrumInstrument, Limb] = {
    # Kick
    DrumInstrument.KICK: Limb.RF,
    # Snare
    DrumInstrument.SNARE: Limb.LH,
    DrumInstrument.RIM: Limb.LH,
    DrumInstrument.SNARE_RIMSHOT: Limb.LH,
    # Hi-Hats (Assuming standard crossed-handed playing)
    DrumInstrument.CLOSED_HH: Limb.RH,
    DrumInstrument.CLOSED_HH_EDGE: Limb.RH,
    DrumInstrument.CLOSED_HH_TIP: Limb.RH,
    DrumInstrument.TIGHT_HH_EDGE: Limb.RH,
    DrumInstrument.TIGHT_HH_TIP: Limb.RH,
    DrumInstrument.OPEN_HH: Limb.RH,
    DrumInstrument.OPEN_HH_1: Limb.RH,
    DrumInstrument.OPEN_HH_2: Limb.RH,
    DrumInstrument.OPEN_HH_3: Limb.RH,
    DrumInstrument.OPEN_HH_MAX: Limb.RH,
    DrumInstrument.PEDAL_HH: Limb.LF,
    # Toms
    DrumInstrument.MID_TOM: Limb.RH,
    DrumInstrument.FLOOR_TOM: Limb.RH,
    DrumInstrument.TOM_EDGE_MID: Limb.RH,
    DrumInstrument.TOM_EDGE_FLOOR: Limb.RH,
    DrumInstrument.TOM_EDGE_3: Limb.RH,
    DrumInstrument.TOM_EDGE_4: Limb.RH,
    DrumInstrument.TOM_EDGE_1: Limb.RH,
    DrumInstrument.TOM_EDGE_2: Limb.RH,
    # Cymbals
    DrumInstrument.CRASH: Limb.RH,
    DrumInstrument.RIDE: Limb.RH,
    DrumInstrument.SPLASH: Limb.RH,
    DrumInstrument.CHINA: Limb.RH,
    DrumInstrument.RIDE_BELL: Limb.RH,
    DrumInstrument.CRASH_CHOKED_A: Limb.RH,
    DrumInstrument.CRASH_CHOKED_B: Limb.RH,
    DrumInstrument.CRASH_CHOKED_C: Limb.RH,
    DrumInstrument.CRASH_CHOKED_D: Limb.RH,
    DrumInstrument.RIDE_SHAFT: Limb.RH,
    DrumInstrument.RIDE_BELL_ALT: Limb.RH,
    DrumInstrument.RIDE_1_TIP: Limb.RH,
    DrumInstrument.CRASH_HEAVY: Limb.RH,
    DrumInstrument.CRASH_LIGHT: Limb.RH,
    DrumInstrument.CRASH_SPLASH: Limb.RH,
}


class LimbConstraintEngine:
    """Enforces physical limitations on drum performances."""

    def __init__(self, conflict_strategy: str = "flam"):
        """
        Args:
            conflict_strategy: How to resolve limb collisions ("flam" or "prioritize_accent")
        """
        self.conflict_strategy = conflict_strategy

    def process(self, beats: List[Beat]) -> List[Beat]:
        """Process beats to resolve physical limb collisions."""
        active_limbs: Dict[Limb, float] = {}
        processed_beats = []

        # Sort by position to process sequentially
        sorted_beats = sorted(beats, key=lambda b: b.position)

        for beat in sorted_beats:
            limb = INSTRUMENT_TO_LIMB.get(beat.instrument)

            # If no limb mapping, pass through
            if not limb:
                processed_beats.append(beat)
                continue

            # Check for collision (same limb within ~5ms)
            # 5ms is a standard threshold for humanly impossible simultaneous hits
            if (
                limb in active_limbs
                and abs(active_limbs[limb] - beat.position) < 0.005
            ):
                if self.conflict_strategy == "flam":
                    # Force a micro-timing flam
                    beat.position += 0.005
                elif self.conflict_strategy == "prioritize_accent":
                    # Simple drop if lower velocity (skipped here for simplicity)
                    pass

            active_limbs[limb] = beat.position
            processed_beats.append(beat)

        return processed_beats
