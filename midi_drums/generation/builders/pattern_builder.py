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

    def crash(self, position: float, velocity: int = 110) -> "PatternBuilder":
        """Add crash cymbal at position."""
        inst = InstrumentRegistry.get("cymbal_1_hit")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def snare_rimshot(
        self,
        position: float,
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add snare rimshot at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_RIMSHOT
        inst = InstrumentRegistry.get("snare_rimshot_open_hit")
        self.pattern.add_beat(position, inst, vel)
        return self

    def snare_side_stick(
        self,
        position: float,
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add snare side stick (cross-stick/noodle) at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_GHOST
        inst = InstrumentRegistry.get("snare_side_stick")
        self.pattern.add_beat(position, inst, vel)
        return self

    def tom(
        self,
        position: float,
        variant: str = "MID",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add tom hit at position."""
        tom_map = {
            "1": "tom_1_open_hit",
            "2": "tom_2_open_hit",
            "3": "tom_3_open_hit",
            "4": "tom_4_open_hit",
        }
        key = tom_map.get(variant, tom_map["3"])
        inst = InstrumentRegistry.get(key)
        vel = velocity if velocity is not None else VELOCITY.TOM_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def tom_edge(
        self,
        position: float,
        variant: str = "MID",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add tom rimshot/edge hit at position."""
        edge_map = {
            "1": "tom_1_rimshot_open_hit_dbl",
            "2": "tom_2_rimshot_open_hit_dbl",
            "3": "tom_3_rimshot_open_hit_dbl",
            "4": "tom_4_rimshot_open_hit_dbl",
        }
        key = edge_map.get(variant, edge_map["3"])
        inst = InstrumentRegistry.get(key)
        vel = velocity if velocity is not None else VELOCITY.TOM_HEAVY
        self.pattern.add_beat(position, inst, vel)
        return self

    def crash_choked(
        self,
        position: float,
        variant: str = "A",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add a choked crash at position."""
        inst_name = f"cymbal_{int(variant)}_choke" if variant.isdigit() else "cymbal_1_choke"
        # Map A/B/C/D to cymbal numbers
        choke_map = {"A": "cymbal_1_choke", "B": "cymbal_2_choke", "C": "cymbal_3_choke", "D": "cymbal_4_choke"}
        inst_name = choke_map.get(variant.upper(), "cymbal_1_choke")
        inst = InstrumentRegistry.get(inst_name)
        vel = velocity if velocity is not None else VELOCITY.CRASH_ACCENT
        self.pattern.add_beat(position, inst, vel)
        return self

    def tight_hh(
        self,
        position: float,
        open: bool = False,
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add tightly tuned hi-hat at position."""
        if open:
            inst = InstrumentRegistry.get("hihat_closed_2_tip_closed_2_hit")
        else:
            inst = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
        vel = velocity if velocity is not None else VELOCITY.HIHAT_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def ride_bell(
        self, position: float, velocity: int = 80
    ) -> "PatternBuilder":
        """Add ride bell at position."""
        inst = InstrumentRegistry.get("ride_1_bell")
        self.pattern.add_beat(position, inst, velocity)
        return self

    def brush_sweep(
        self,
        position: float,
        variant: str = "A",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add a snare brush sweep at position.
        
        Variant maps to AD2 brush sweep presets (A-F).
        A=fast_bright_accent, B=slow_bright_accent, C=fast_dark_accent,
        D=slow_dark_accent, E=fast_bright_accent, F=no_accent
        """
        variant_map = {
            "A": "snare_brushes_only_sweep_fast_bright_accent",
            "B": "snare_brushes_only_sweep_slow_bright_accent",
            "C": "snare_brushes_only_sweep_fast_dark_accent",
            "D": "snare_brushes_only_sweep_slow_dark_accent",
            "E": "snare_brushes_only_sweep_fast_bright_accent",
            "F": "snare_brushes_only_sweep_no_accent",
        }
        key = variant_map.get(variant.upper(), variant_map["A"])
        inst = InstrumentRegistry.get(key)
        vel = velocity if velocity is not None else VELOCITY.BRUSH_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def add_hit(
        self, instrument: DrumInstrument, position: float, velocity: int = 100
    ) -> "PatternBuilder":
        """Generic method to add any drum instrument hit."""
        self.pattern.add_beat(position, instrument, velocity)
        return self

    def build(self) -> Pattern:
        """Build and return the pattern."""
        return self.pattern
