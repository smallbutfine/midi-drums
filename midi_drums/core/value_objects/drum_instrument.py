"""Dynamic DrumInstrument registration system.

All instruments are discovered at runtime by loading the master template.
No hardcoded enum members — everything comes from JSON keymaps.

Usage:
    # At program startup, register all instruments once
    from midi_drums.core.value_objects.drum_instrument import InstrumentRegistry
    
    registry = InstrumentRegistry.load_from_template()  # or load_custom(template_path)
    
    # Now access instruments by string name
    kick = registry.get("kick")           # -> DrumInstrument("kick")
    snare = registry.get("snare_1")       # -> DrumInstrument("snare_1")
    
    # Get all registered instruments
    for inst in registry.all():
        print(f"{inst.name} -> {inst.description}")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DrumInstrument:
    """A drum instrument identity — dynamically registered from keymaps.
    
    Instruments have NO MIDI note values baked in. Notes live in separate
    keymap files (JSON) that map instrument names to specific notes.
    
    Each instance is a string-backed value object with metadata attached.
    """
    
    _registry: dict[str, DrumInstrument] = {}  # class-level registry
    
    def __init__(self, name: str, description: str = "", metadata: dict | None = None):
        self._name = name
        self._description = description
        self._metadata = metadata or {}
        
        if self not in DrumInstrument._registry.values():
            DrumInstrument._registry[name] = self
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def metadata(self) -> dict:
        return self._metadata.copy()  # return a copy to prevent mutation
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DrumInstrument):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"DrumInstrument('{self.name}')"


class InstrumentRegistry:
    """Manages all registered drum instruments across all keymaps.
    
    This is the single source of truth for which instruments exist.
    MIDI note mappings live in separate keymap files.
    """
    
    _instruments: dict[str, DrumInstrument] = {}
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered instruments (useful for testing)."""
        cls._instruments.clear()
    
    @classmethod
    def register(
        cls,
        name: str,
        description: str = "",
        metadata: dict | None = None,
    ) -> DrumInstrument:
        """Register a new instrument or retrieve existing one by name.
        
        If the instrument already exists in the registry, returns the existing instance
        (singleton behavior). Creates a new one otherwise.
        
        Args:
            name: Unique string identifier for this instrument (e.g., 'kick', 'snare_1')
            description: Human-readable description of the instrument/articulation
            metadata: Optional dict with additional attributes
        
        Returns:
            The DrumInstrument instance (always the same object for the same name)
        """
        if name in cls._instruments:
            return cls._instruments[name]
        
        inst = DrumInstrument(
            name=name,
            description=description,
            metadata=metadata or {}
        )
        cls._instruments[name] = inst
        return inst
    
    @classmethod
    def get(cls, name: str) -> DrumInstrument | None:
        """Get a registered instrument by name, or None if not found."""
        return cls._instruments.get(name)
    
    @classmethod
    def all(cls) -> list[DrumInstrument]:
        """Return all registered instruments as a list."""
        return list(cls._instruments.values())
    
    @classmethod
    def all_names(cls) -> set[str]:
        """Return all registered instrument names as a set."""
        return set(cls._instruments.keys())
    
    @classmethod
    def load_from_template(
        cls,
        template_path: str | Path | None = None,
    ) -> None:
        """Load all instruments from a master template keymap file.
        
        Scans the template's instrument keys and registers each one with its description.
        This should be called once at program startup to initialize the registry.
        
        Args:
            template_path: Path to the master template JSON file.
                          Defaults to midi_drums/mappings/template.json
        """
        if template_path is None:
            # Default path relative to this module's location
            from pathlib import Path as _Path
            default = _Path(__file__).parent.parent / "mappings" / "template.json"
            if default.exists():
                template_path = default
            else:
                raise FileNotFoundError(
                    f"Template not found at {default}. Specify path explicitly."
                )
        
        data = json.loads(Path(template_path).read_text(encoding="utf-8"))
        instruments = data.get("instruments", {})
        
        for name, info in instruments.items():
            cls.register(
                name=name,
                description=info.get("description", ""),
                metadata={"source": data.get("source", "template")}
            )
    
    @classmethod
    def load_custom(cls, template_path: str | Path) -> None:
        """Alias for load_from_template — explicit method name."""
        cls.load_from_template(template_path)


# ── Convenience Functions ───────────────────────────────────────────────────

def get_instrument(name: str) -> DrumInstrument:
    """Get a registered instrument by name. Raises KeyError if not found."""
    inst = InstrumentRegistry.get(name)
    if inst is None:
        available = ", ".join(sorted(InstrumentRegistry.all_names()))
        raise KeyError(
            f"Unknown drum instrument '{name}'. "
            f"Available: {available}"
        )
    return inst


def get_all_instruments() -> list[DrumInstrument]:
    """Get all registered instruments."""
    return InstrumentRegistry.all()


def register_instrument(name: str, description: str = "") -> DrumInstrument:
    """Register a new instrument directly (alias for registry.register)."""
    return InstrumentRegistry.register(name, description)
