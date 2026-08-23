"""GrooveEngine — per-bar timing displacement for authentic drummer feel.

This engine calculates how much each bar should be shifted (positive = push ahead,
negative = drag behind) based on the drummer's groove profile.  The displacement
is stored as a **timing offset** rather than modifying beat positions directly —
beat positions within the pattern skeleton stay intact so musical structure is
preserved; only the global timing of when that bar starts relative to the song
timeline changes.

Applied in composer_v2.py: each bar's offset is accumulated and the final
offset for a section determines where that section's MIDI events start on the
song timeline (shifted by Section.offset_ms).
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class DrummerGrooveProfile:
    """Characteristics defining how a drummer creates groove/feel.

    Attributes:
        swing_ratio: 0.0 (straight/eight-note) to 1.0 (heavy triplet swing).
                     Mapped to timing displacement: swing=0.33 → ~-25ms,
                     swing=0.0 → ~±3ms micro-displacement only.
        timing_bias_ms: center of the timing-displacement range.
                        Positive = push forward (ahead of beat),
                        negative = lay back (behind beat).
        bias_range_ms: half-width of the displacement jitter. Each bar gets a
                       random shift within [bias - range, bias + range].
        description: Human-readable name for logging/debugging.
    """

    swing_ratio: float = 0.0
    timing_bias_ms: float = 0.0
    bias_range_ms: float = 5.0
    description: str = "straight"


# --- Drummer groove profiles (add new ones here as drummers are added) ---

_GROOVE_PROFILES: dict[str, DrummerGrooveProfile] = {
    "bonham": DrummerGrooveProfile(
        swing_ratio=0.60,  # Heavy triplet swing
        timing_bias_ms=-20.0,  # Behind-the-beat feel
        bias_range_ms=8.0,
        description="laid-back drag (Bonham)",
    ),
    "weckl": DrummerGrooveProfile(
        swing_ratio=0.15,  # Nearly straight
        timing_bias_ms=0.0,  # Centered
        bias_range_ms=3.0,  # Very tight micro-variations
        description="tight breathing (Weckl)",
    ),
    "chambers": DrummerGrooveProfile(
        swing_ratio=0.40,  # Moderate pocket feel
        timing_bias_ms=-5.0,  # Slight lay-back for pocket
        bias_range_ms=12.0,  # Dynamic push/pull
        description="pocket stretch (Chambers)",
    ),
    "roeder": DrummerGrooveProfile(
        swing_ratio=0.50,  # Heavy behind-beat
        timing_bias_ms=-25.0,  # Deep lay-back for sludge feel
        bias_range_ms=6.0,
        description="crushing drag (Roeder)",
    ),
    "carey": DrummerGrooveProfile(
        swing_ratio=0.20,  # Polyrhythmic odd-meter feel
        timing_bias_ms=-8.0,  # Subtle behind-beat for depth
        bias_range_ms=15.0,  # Larger variance for polyrhythmic displacement
        description="polyrhythmic push (Carey)",
    ),
    "hoglan": DrummerGrooveProfile(
        swing_ratio=0.05,  # Machine-tight
        timing_bias_ms=0.0,  # Centered
        bias_range_ms=1.0,  # Extremely tight
        description="mechanical precision (Hoglan)",
    ),
    "dee": DrummerGrooveProfile(
        swing_ratio=0.10,  # Straight with punch
        timing_bias_ms=3.0,  # Slight push for power feel
        bias_range_ms=4.0,
        description="forward punch (Dee)",
    ),
    "porcaro": DrummerGrooveProfile(
        swing_ratio=0.35,  # Shuffle/swing feel
        timing_bias_ms=-10.0,  # Slight lay-back for pocket
        bias_range_ms=8.0,
        description="half-time shuffle (Porcaro)",
    ),
    "rich": DrummerGrooveProfile(
        swing_ratio=0.25,  # Jazz-influenced slight swing
        timing_bias_ms=-3.0,  # Almost straight
        bias_range_ms=5.0,
        description="jazz pocket (Rich)",
    ),
    "copeland": DrummerGrooveProfile(
        swing_ratio=0.45,  # Off-beat reggae/ska feel
        timing_bias_ms=8.0,  # Push ahead for off-beat hi-hat feel
        bias_range_ms=10.0,
        description="off-beat push (Copeland)",
    ),
    "haake": DrummerGrooveProfile(
        swing_ratio=0.02,  # Machine-tight polyrhythmic
        timing_bias_ms=0.0,
        bias_range_ms=1.5,
        description="industrial precision (Haake)",
    ),
    "halpern": DrummerGrooveProfile(
        swing_ratio=0.08,  # Tight progressive feel
        timing_bias_ms=-2.0,
        bias_range_ms=2.0,
        description="tight polyrhythmic (Halpern)",
    ),
    "peart": DrummerGrooveProfile(
        swing_ratio=0.10,  # Precise straight feel
        timing_bias_ms=-1.0,  # Nearly dead-center, slight push
        bias_range_ms=2.0,  # Very tight (Peart known for precision)
        description="extreme precision (Peart)",
    ),
    "smith": DrummerGrooveProfile(
        swing_ratio=0.30,  # Moderate rock/groove feel
        timing_bias_ms=-3.0,  # Slight pocket lay-back
        bias_range_ms=8.0,  # Dynamic push/pull for Red Hot style
        description="funk-rock groove (Smith)",
    ),
}

# Default profile for unknown drummers
_DEFAULT_PROFILE = DrummerGrooveProfile(
    swing_ratio=0.15,
    timing_bias_ms=0.0,
    bias_range_ms=3.0,
    description="straight default",
)


class GrooveEngine:
    """Calculates per-bar timing displacement based on drummer groove profile.

    The engine produces a single timing offset (in milliseconds) per bar that
    should shift where the bar starts on the song timeline — NOT modify beat
    positions within the pattern skeleton.  This preserves musical structure
    while creating audible "laying back" or "pushing ahead" feel.

    The groove layer is **additive** to the existing BarSelector micro-jitter:
    - GrooveEngine displacement (±30ms): entire bar shifts on timeline → swing/feel
    - BarSelector per-note jitter (±3ms): tiny independent variation → naturalism
    """

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    @staticmethod
    def get_profile(drummer_name: str | None) -> DrummerGrooveProfile:
        """Get the groove profile for a drummer (or default if unknown)."""
        if not drummer_name:
            return _DEFAULT_PROFILE
        return _GROOVE_PROFILES.get(drummer_name.lower(), _DEFAULT_PROFILE)

    def get_bar_offset_ms(
        self,
        bar_index: int,
        tempo: int,
        intensity_pt: tuple | None = None,
        section_name: str | None = None,
        drummer_name: str | None = None,
    ) -> float:
        """Calculate timing offset (ms) for this bar.

        Args:
            bar_index: 0-based bar position within the section.
            tempo: Current tempo in BPM (for modulation range).
            intensity_pt: (complexity_mult, velocity_bias, density_factor) from
                          the intensity curve; complexity affects swing magnitude.
            section_name: Section type for contextual modulation.
            drummer_name: Drummer style name (e.g., "bonham", "carey").

        Returns:
            Timing offset in milliseconds for this bar's start position on
            the song timeline.  Positive = push ahead, negative = drag behind.
        """
        profile = self.get_profile(drummer_name)

        # Calculate base swing magnitude (swing=1.0 → ±30ms, swing=0.0 → ±5ms)
        swing_magnitude_ms = 5.0 + profile.swing_ratio * 25.0

        # Modulate by intensity: high energy = tighter timing, low energy = more sway
        if intensity_pt and len(intensity_pt) >= 1:
            complexity_mult = intensity_pt[0]
            # At complexity=0 (quiet/soft), swing is full; at complexity=1 (loud), reduced
            energy_factor = max(0.2, 1.0 - complexity_mult * 0.6)
        else:
            energy_factor = 0.7

        # Section context modulation
        section_modifier = self._section_context_modifier(section_name)
        total_magnitude = swing_magnitude_ms * energy_factor * section_modifier

        # Compute displacement with drummer's timing bias as the center
        return profile.timing_bias_ms + (
            self._rng.uniform(-0.5, 0.5) * total_magnitude
        )

    def apply(
        self,
        pattern: "Pattern",  # noqa: F821 - type annotation only
        bar_index: int,
        tempo: int,
        intensity_pt: tuple | None = None,
        section_name: str | None = None,
        drummer_name: str | None = None,
    ) -> "Pattern":  # noqa: F821 - type annotation only
        """Return pattern with a timing offset stored in metadata.

        Does NOT modify beat positions directly — that would create artificial
        non-musical patterns where notes jump to wrong positions when wrapping
        across bar boundaries.  Instead stores the offset on the pattern so
        composer_v2 can accumulate and apply it globally per section.

        Args:
            pattern: Input pattern (unchanged except for metadata addition).
            bar_index: 0-based bar position within the section.
            tempo: Current tempo in BPM.
            intensity_pt: Intensity curve point from this bar's position.
            section_name: Section type name.
            drummer_name: Drummer style name.

        Returns:
            New pattern with metadata["groove_offset_ms"] set for this bar.
        """
        offset_ms = self.get_bar_offset_ms(
            bar_index=bar_index,
            tempo=tempo,
            intensity_pt=intensity_pt,
            section_name=section_name,
            drummer_name=drummer_name,
        )

        import copy  # noqa: PLC0415

        new_pattern = copy.deepcopy(pattern)
        new_pattern.metadata["groove_offset_ms"] = offset_ms
        return new_pattern

    def _section_context_modifier(self, section_name: str | None) -> float:
        """Contextual modulation factor based on section type.

        Return values >1.0 increase displacement (more dramatic feel), <1.0
        tightens timing (straighter/controlled).
        """
        if not section_name:
            return 1.0
        name_lower = section_name.lower()
        if name_lower in ("bridge", "pre_chorus"):
            return 1.3  # More dramatic timing in transitions
        elif name_lower == "chorus":
            return 0.7  # Tighter for power/impact
        elif name_lower == "breakdown":
            return 1.2  # Heavy, dragging feel
        elif name_lower == "solo":
            return 1.4  # Most dramatic (drummer freedom)
        elif name_lower in ("intro", "outro"):
            return 0.9  # Slightly looser
        return 1.0
