"""Pattern builder - fluent construction API for Pattern."""


from midi_drums.config import VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.value_objects.drum_instrument import DrumInstrument
from midi_drums.core.value_objects.time_signature import TimeSignature


class PatternBuilder:
    """Builder pattern for creating drum patterns."""

    def __init__(self, name: str, time_signature: TimeSignature | None = None):
        self.pattern = Pattern(
            name=name, time_signature=time_signature or TimeSignature()
        )

    def kick(self, position: float, velocity: int = 100) -> "PatternBuilder":
        """Add kick drum at position."""
        self.pattern.add_beat(position, DrumInstrument.KICK, velocity)
        return self

    def snare(self, position: float, velocity: int = 100) -> "PatternBuilder":
        """Add snare at position."""
        self.pattern.add_beat(position, DrumInstrument.SNARE, velocity)
        return self

    def hihat(
        self, position: float, velocity: int = 80, open: bool = False
    ) -> "PatternBuilder":
        """Add hi-hat at position."""
        instrument = (
            DrumInstrument.OPEN_HH if open else DrumInstrument.CLOSED_HH
        )
        self.pattern.add_beat(position, instrument, velocity)
        return self

    def ride(self, position: float, velocity: int = 80) -> "PatternBuilder":
        """Add ride cymbal at position."""
        self.pattern.add_beat(position, DrumInstrument.RIDE, velocity)
        return self

    def hihat_foot(
        self, position: float, velocity: int = VELOCITY.HIHAT_PEDAL
    ) -> "PatternBuilder":
        """Add hi-hat foot pedal ("chick") at position."""
        self.pattern.add_beat(position, DrumInstrument.PEDAL_HH, velocity)
        return self

    def crash(self, position: float, velocity: int = 110) -> "PatternBuilder":
        """Add crash cymbal at position."""
        self.pattern.add_beat(position, DrumInstrument.CRASH, velocity)
        return self

    # --- Extended instruments (AD2 / EZDrummer zones) ---

    def brush_sweep(
        self,
        position: float,
        variant: str = "A",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add snare brush sweep at position.

        AD2 provides 6 distinct brush presets that trigger different swish
        and shimmer samples. Variant A is the most neutral; F produces the
        fastest, darkest accent.

        Args:
            position: Beat position (float).
            variant: "A" through "F" selecting the sweep preset.
            velocity: Override (None = default brush velocity 55).
        """
        inst = getattr(DrumInstrument, f"BRUSH_SWEEP_{variant}")
        vel = velocity if velocity is not None else VELOCITY.BRUSH_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def snare_rimshot(
        self,
        position: float,
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add snare rimshot (side stick / rim click) at position."""
        vel = velocity if velocity is not None else VELOCITY.SNARE_RIMSHOT
        self.pattern.add_beat(position, DrumInstrument.SNARE_RIMSHOT, vel)
        return self

    def tom_edge(
        self,
        position: float,
        variant: str = "MID",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add rimmed/edge tom hit at position.

        Tom edges produce a tighter, more metallic attack than an open tom.
        Useful for funk backbeats and accent fills.

        Args:
            position: Beat position (float).
            variant: "MID", "FLOOR", "3", or "4" selecting the tom zone.
            velocity: Override (None = default tom edge velocity 100).
        """
        inst = getattr(DrumInstrument, f"TOM_EDGE_{variant}")
        vel = velocity if velocity is not None else VELOCITY.TOM_HEAVY
        self.pattern.add_beat(position, inst, vel)
        return self

    def crash_choked(
        self,
        position: float,
        variant: str = "A",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add a choked crash at position (hit + immediate dampen).

        Produces the characteristic 'chick' decay of a crashed cymbal
        grabbed mid-ring by the drummer.

        Args:
            position: Beat position (float).
            variant: "A", "B", "C", or "D" selecting the choke zone.
            velocity: Override (None = default crash choked velocity 105).
        """
        inst = getattr(DrumInstrument, f"CRASH_CHOKED_{variant}")
        vel = velocity if velocity is not None else VELOCITY.CRASH_ACCENT
        self.pattern.add_beat(position, inst, vel)
        return self

    def tight_hh(
        self,
        position: float,
        open: bool = False,
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add a tightly tuned hi-hat (dry, pencil-like attack).

        Tight HH zones sit high in the note range (90-91) and trigger AD2's
        tight-pair sample — ideal for funk 16th-note comping and fusion.

        Args:
            position: Beat position (float).
            open: Whether to add a slight dampen (variant B).
            velocity: Override (None = default tight HH velocity 85).
        """
        if open:
            inst = DrumInstrument.TIGHT_HH_TIP
            vel = VELOCITY.HIHAT_LIGHT
        else:
            inst = DrumInstrument.TIGHT_HH_EDGE
            vel = VELOCITY.HIHAT_NORMAL
        self.pattern.add_beat(position, inst, vel)
        return self

    def ride_bell(
        self, position: float, velocity: int = 80
    ) -> "PatternBuilder":
        """Add ride bell (bell) at position."""
        self.pattern.add_beat(position, DrumInstrument.RIDE_BELL, velocity)
        return self

    def tom(
        self,
        position: float,
        variant: str = "MID",
        velocity: int | None = None,
    ) -> "PatternBuilder":
        """Add tom hit (general-purpose tom method)."""
        inst_map = {
            "MID": DrumInstrument.MID_TOM,
            "FLOOR": DrumInstrument.FLOOR_TOM,
        }
        inst = inst_map.get(variant, DrumInstrument.MID_TOM)
        vel = velocity if velocity is not None else VELOCITY.TOM_NORMAL
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
