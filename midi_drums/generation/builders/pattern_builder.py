"""Pattern builder - fluent construction API for Pattern."""

from midi_drums.config import VELOCITY
from midi_drums.core.models.kit import DrumInstrument, InstrumentRegistry
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.value_objects.time_signature import TimeSignature


class PatternBuilder:
    """Builder pattern for creating drum patterns."""

    def __init__(self, name: str, time_signature: TimeSignature | None = None):
        self.pattern = Pattern(
            name=name, time_signature=time_signature or TimeSignature()
        )

    # ── Core instruments (convenience methods) ───────────────────────────────

    def kick(self, position: float, velocity: int = 100) -> "PatternBuilder":
        """Add kick drum at position."""
        inst = InstrumentRegistry.get("kick")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def snare(self, position: float, velocity: int = 100) -> "PatternBuilder":
        """Add snare (sticks) at position."""
        inst = InstrumentRegistry.get("snare_sticks")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def hihat(
        self, position: float, velocity: int = 80, open: bool = False
    ) -> "PatternBuilder":
        """Add hi-hat at position."""
        if open:
            inst = InstrumentRegistry.get("hihat_open_a")
        else:
            inst = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def ride(self, position: float, velocity: int = 80) -> "PatternBuilder":
        """Add ride cymbal at position."""
        inst = InstrumentRegistry.get("ride_1_tip_hit_softer")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def hihat_foot(
        self, position: float, velocity: int = VELOCITY.HIHAT_PEDAL
    ) -> "PatternBuilder":
        """Add hi-hat foot pedal (chick) at position."""
        inst = InstrumentRegistry.get("hihat_pedal_closed")
        self.pattern.add_beat(position, inst, velocity)
        return self

    # ── Snare articulations ─────────────────────────────────────────────────

    def snare_shallow(
        self, position: float, velocity: int | None = None
    ) -> "PatternBuilder":
        """Add snare shallow (shallow head) hit at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_GHOST
        inst = InstrumentRegistry.get("snare_shallow_hit_closed_shallow_hit")
        self.pattern.add_beat(position, inst, vel)
        return self

    def snare_rimshot(
        self, position: float, velocity: int | None = None
    ) -> "PatternBuilder":
        """Add snare rimshot at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_RIMSHOT
        inst = InstrumentRegistry.get("snare_rimshot_open_hit")
        self.pattern.add_beat(position, inst, vel)
        return self

    def snare_side_stick(
        self, position: float, velocity: int | None = None
    ) -> "PatternBuilder":
        """Add snare side stick (cross-stick/noodle) at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_GHOST
        inst = InstrumentRegistry.get("snare_side_stick")
        self.pattern.add_beat(position, inst, vel)
        return self

    def brush_sweep(
        self, position: float, variant: str = "A", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add a snare brush sweep at position.

        Alias for :meth:`snare_sweep` (backwards-compatible name).
        """
        return self.snare_sweep(position, variant=variant, velocity=velocity)

    def snare_sweep(
        self, position: float, variant: str = "A", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add a snare brush sweep at position.

        Variant maps to AD2 brush sweep presets (A–F).
        A=fast_bright_accent, B=slow_bright_accent, C=fast_dark_accent,
        D=slow_dark_accent, E=no_accent, F=no_accent
        """
        _SWEEP_MAP = {
            "A": "snare_brushes_only_sweep_fast_bright_accent",
            "B": "snare_brushes_only_sweep_slow_bright_accent",
            "C": "snare_brushes_only_sweep_fast_dark_accent",
            "D": "snare_brushes_only_sweep_slow_dark_accent",
            "E": "snare_brushes_only_sweep_fast_bright_accent",
            "F": "snare_brushes_only_sweep_no_accent",
        }
        inst = InstrumentRegistry.get(
            _SWEEP_MAP.get(variant.upper(), _SWEEP_MAP["A"])
        )
        vel = velocity if velocity is not None else VELOCITY.BRUSH_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    # ── Tom articulations ───────────────────────────────────────────────────

    def tom(
        self, position: float, variant: str = "2", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add tom hit at position.

        ``variant`` accepts numbers ("1"–"4") or aliases:

        * "HIGH"/"1" → top tom (highest pitch)
        * "MID"/"2"  → mid tom (default)
        * "LOW"/"3"  → low tom
        * "FLOOR"/"4"→ floor tom (lowest pitch)
        """
        _TOM_MAP = {
            "1": "tom_1_open_hit",
            "2": "tom_2_open_hit",
            "3": "tom_3_open_hit",
            "4": "tom_4_open_hit",
        }
        alias_map = {"HIGH": "1", "MID": "2", "LOW": "3", "FLOOR": "4"}
        numeric = alias_map.get(variant, variant)
        key = _TOM_MAP.get(numeric, _TOM_MAP["2"])  # default mid tom
        inst = InstrumentRegistry.get(key)
        vel = velocity if velocity is not None else VELOCITY.TOM_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def tom_edge(
        self, position: float, variant: str = "2", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add tom rimshot/edge hit at position.

        Same ``variant`` aliases as ``.tom()`` (HIGH, MID, LOW, FLOOR or 1–4).
        """
        _EDGE_MAP = {
            "1": "tom_1_rimshot_open_hit_dbl",
            "2": "tom_2_rimshot_open_hit_dbl",
            "3": "tom_3_rimshot_open_hit_dbl",
            "4": "tom_4_rimshot_open_hit_dbl",
        }
        alias_map = {"HIGH": "1", "MID": "2", "LOW": "3", "FLOOR": "4"}
        numeric = alias_map.get(variant, variant)
        key = _EDGE_MAP.get(numeric, _EDGE_MAP["2"])  # default mid tom edge
        inst = InstrumentRegistry.get(key)
        vel = velocity if velocity is not None else VELOCITY.TOM_HEAVY
        self.pattern.add_beat(position, inst, vel)
        return self

    # ── Cymbal articulations ────────────────────────────────────────────────

    def crash(
        self, position: float, variant: str = "1", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add crash cymbal at position.

        ``variant`` accepts numbers ("1"–"6") to select which crash:

        * "1" → cymbal_1_hit (lightest)
        * "2" → cymbal_2_hit
        * "3" → cymbal_3_hit
        * "4" → cymbal_4_hit (heaviest)
        * "5" → cymbal_5_hit (china)
        * "6" → cymbal_6_hit (largest/finest)
        """
        inst_name = f"cymbal_{variant}_hit"
        inst = InstrumentRegistry.get(inst_name)
        if inst is None:
            inst = InstrumentRegistry.get("cymbal_1_hit")  # fallback
        vel = velocity if velocity is not None else VELOCITY.CRASH_ACCENT
        self.pattern.add_beat(position, inst, vel)
        return self

    def crash_choked(
        self, position: float, variant: str = "A", velocity: int | None = None
    ) -> "PatternBuilder":
        """Add a choked crash at position.

        ``variant`` accepts numbers ("1"–"6") or letters (A–F):

        * "A"/"1" → cymbal_1_choke
        * "B"/"2" → cymbal_2_choke
        * "C"/"3" → cymbal_3_choke
        * "D"/"4" → cymbal_4_choke
        * "E"/"5" → cymbal_5_choke
        * "F"/"6" → cymbal_6_choke
        """
        _CHOKE_MAP = {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5",
            "F": "6",
        }
        num = _CHOKE_MAP.get(variant.upper(), variant)
        inst_name = f"cymbal_{num}_choke"
        inst = InstrumentRegistry.get(inst_name)
        if inst is None:
            inst = InstrumentRegistry.get("cymbal_1_choke")  # fallback
        vel = velocity if velocity is not None else VELOCITY.CRASH_ACCENT
        self.pattern.add_beat(position, inst, vel)
        return self

    def ride_bell(
        self, position: float, velocity: int = 80
    ) -> "PatternBuilder":
        """Add ride bell hit at position (ride_1)."""
        inst = InstrumentRegistry.get("ride_1_bell")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def ride_shaft(
        self, position: float, velocity: int = 80
    ) -> "PatternBuilder":
        """Add ride shaft stick hit at position (ride_1)."""
        inst = InstrumentRegistry.get("ride_1_shaft_hit_stronger")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def cymbal_open(
        self,
        position: float,
        variant: str = "1",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add an open crash/ride hit (any pitched cymbal).

        Accepts variant numbers 1–6 to select which cymbal.
        Also accepts short aliases: A=cymbal_1, B=cymbal_2, etc.
        """
        alias_map = {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5",
            "F": "6",
        }
        num = alias_map.get(variant.upper(), variant)
        inst_name = f"cymbal_{num}_hit"
        inst = InstrumentRegistry.get(inst_name)
        if inst is None:
            inst = InstrumentRegistry.get("cymbal_1_hit")
        vel = velocity if velocity is not None else VELOCITY.CRASH_ACCENT
        self.pattern.add_beat(position, inst, vel)
        return self

    # ── Hi-hat variants ─────────────────────────────────────────────────────

    def tight_hh(
        self, position: float, open: bool = False, velocity: int | None = None
    ) -> "PatternBuilder":
        """Add tightly tuned hi-hat at position."""
        if open:
            inst = InstrumentRegistry.get("hihat_closed_2_tip_closed_2_hit")
        else:
            inst = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
        vel = velocity if velocity is not None else VELOCITY.HIHAT_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    # ── Generic helper ──────────────────────────────────────────────────────

    def add_hit(
        self, instrument: DrumInstrument, position: float, velocity: int = 100
    ) -> "PatternBuilder":
        """Generic method to add any drum instrument hit."""
        self.pattern.add_beat(position, instrument, velocity)
        return self

    def build(self) -> Pattern:
        """Build and return the pattern."""
        return self.pattern
