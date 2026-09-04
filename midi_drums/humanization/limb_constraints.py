"""Limb constraint engine for physical drum performance modeling."""

from enum import Enum
from typing import Dict, List

from midi_drums.core.models.pattern import Beat


class Limb(Enum):
    LH = "LH"
    RH = "RH"
    LF = "LF"
    RF = "RF"


INSTRUMENT_TO_LIMB: Dict[str, Limb] = {
    # Kick
    "kick": Limb.RF,
    # Snare
    "snare_rimshot_open_hit": Limb.LH,
    "snare_side_stick": Limb.LH,
    # Hi-Hats (Assuming standard crossed-handed playing)
    "hihat_closed_1_tip_closed_1_hit": Limb.RH,
    "hihat_closed_2_tip_closed_2_hit": Limb.RH,
    "hihat_open_a": Limb.RH,
    "hihat_pedal_closed": Limb.LF,
    # Toms
    "tom_3_open_hit": Limb.RH,
    "tom_4_open_hit": Limb.RH,
    # Cymbals
    "cymbal_1_hit": Limb.RH,
    "ride_1_tip_hit_softer": Limb.RH,
}


class LimbConstraintEngine:
    """Enforces physical limitations on drum performances."""

    def __init__(self, conflict_strategy: str = "flam"):
        """
        Args:
            conflict_strategy: How to resolve limb collisions (flam or prioritize_accent)
        """
        self.conflict_strategy = conflict_strategy

    def process(self, beats: List[Beat]) -> List[Beat]:
        """Process beats to resolve physical limb collisions."""
        active_limbs: Dict[Limb, float] = {}
        processed_beats = []

        # Sort by position to process sequentially
        sorted_beats = sorted(beats, key=lambda b: b.position)

        for beat in sorted_beats:
            limb = INSTRUMENT_TO_LIMB.get(beat.instrument.name)

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
                    pass

            active_limbs[limb] = beat.position
            processed_beats.append(beat)

        return processed_beats
