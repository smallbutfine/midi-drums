"""DrumKit — drum kit configuration and instrument mapping.

All MIDI note mappings are loaded dynamically from JSON keymap files in midi_drums/mappings/.
No MIDI notes or instrument names are hardcoded anywhere. All instruments come from the master template.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Dynamic Drum Instrument System ──────────────────────────────────────────

class DrumInstrument:
    """Dynamic drum instrument identity — no hardcoded values.
    
    All instruments are registered at runtime from the master template keymap.
    MIDI note mappings live in separate JSON keymap files (midi_drums/mappings/*.json).
    """
    
    _registry: dict[str, DrumInstrument] = {}  # class-level singleton registry
    
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
        return self._metadata.copy()  # Return a copy to prevent mutation
    
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
    """Manages all registered drum instruments. Initialized from the master template at startup."""
    
    _instruments: dict[str, DrumInstrument] = {}
    _initialized: bool = False
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered instruments (useful for testing)."""
        cls._instruments.clear()
        cls._initialized = False
    
    @classmethod
    def register(
        cls,
        name: str,
        description: str = "",
        metadata: dict | None = None,
    ) -> DrumInstrument:
        """Register a new instrument or retrieve existing one by name."""
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
        """Load all instruments from the master template keymap file."""
        if cls._initialized:
            return  # Already loaded
        
        if template_path is None:
            default = Path(__file__).parent.parent / "mappings" / "template.json"
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
        
        cls._initialized = True
    
    @classmethod
    def ensure_loaded(cls) -> None:
        """Ensure the registry is loaded (auto-initialize if needed)."""
        if not cls._initialized:
            cls.load_from_template()


# ── Keymap Loader ───────────────────────────────────────────────────────────

class KeymapLoader:
    """Loads and manages keymap JSON files from the mappings directory."""
    
    _loaded_keymaps: dict[str, dict[str, Any]] = {}  # name -> instruments dict
    
    @classmethod
    def load_all(cls) -> list[dict[str, Any]]:
        """Discover and load all keymap files. Returns list of loaded keymaps."""
        cls._loaded_keymaps.clear()
        
        mappings_dir = Path(__file__).parent.parent / "mappings"
        if not mappings_dir.exists():
            return []
        
        for fpath in sorted(mappings_dir.glob("*.json")):
            name = fpath.stem  # filename without .json extension
            data = json.loads(fpath.read_text(encoding="utf-8"))
            cls._loaded_keymaps[name] = data
        
        return list(cls._loaded_keymaps.values())
    
    @classmethod
    def get_keymap(cls, name: str) -> dict[str, Any] | None:
        """Get a loaded keymap by name (e.g., 'ad2', 'gm', 'ezd3')."""
        if name in cls._loaded_keymaps:
            return cls._loaded_keymaps[name]
        
        for km_name, data in cls._loaded_keymaps.items():
            if km_name.lower() == name.lower():
                return data
        
        return None
    
    @classmethod
    def get_midi_note(cls, instrument_name: str, keymap_name: str) -> int | None:
        """Get the MIDI note for an instrument from a specific keymap."""
        if not cls._loaded_keymaps:
            cls.load_all()
        
        keymap = cls.get_keymap(keymap_name)
        if keymap is None:
            return None
        
        instruments = keymap.get("instruments", {})
        instrument_data = instruments.get(instrument_name, {})
        
        midi_note = instrument_data.get("midi_note")
        return int(midi_note) if midi_note is not None else None
    
    @classmethod
    def get_all_instruments(cls) -> set[str]:
        """Get all unique instrument names across ALL loaded keymaps."""
        instruments = set()
        for keymap in cls._loaded_keymaps.values():
            instruments.update(keymap.get("instruments", {}).keys())
        return instruments
    
    @classmethod
    def get_unmapped_instruments(cls, keymap_name: str) -> set[str]:
        """Get instruments present in the template but unmapped in a specific keymap."""
        all_instruments = cls.get_all_instruments()
        
        keymap = cls.get_keymap(keymap_name)
        if keymap is None:
            return set()
        
        mapped = {
            name for name, data in keymap.get("instruments", {}).items()
            if data.get("midi_note") is not None
        }
        
        return all_instruments - mapped
    
    @classmethod
    def generate_user_keymap(cls, target_path: Path) -> None:
        """Generate a user-editable keymap from the template."""
        template = cls.get_keymap("template") or cls.get_keymap("ad2_master")
        if not template:
            raise FileNotFoundError("No template keymap found in mappings directory.")
        
        instruments = template.get("instruments", {})
        output = {
            "name": "User Custom Kit",
            "version": template.get("version", "1.0"),
            "description": "Custom keymap — fill in midi_note values. Leave as null for unavailable articulations.",
            "source": "User generated from template",
            "instruments": {}
        }
        
        for name, data in instruments.items():
            output["instruments"][name] = {
                "midi_note": None,
                "description": data.get("description", ""),
            }
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(output, indent=4), encoding="utf-8")


# ── Global Initialization ───────────────────────────────────────────────────

def initialize() -> None:
    """Initialize the instrument registry from the template (call once at startup)."""
    InstrumentRegistry.load_from_template()
    KeymapLoader.load_all()


# ── VelocityRange — unchanged ───────────────────────────────────────────────

@dataclass
class VelocityRange:
    """Velocity range for realistic drum dynamics."""
    
    min_velocity: int = 1
    max_velocity: int = 127
    default_velocity: int = 100
    
    def __post_init__(self):
        """Validate velocity values."""
        for vel in [self.min_velocity, self.max_velocity, self.default_velocity]:
            if not 1 <= vel <= 127:
                raise ValueError(f"Velocity must be 1-127, got {vel}")
        if self.min_velocity > self.max_velocity:
            raise ValueError("Min velocity cannot be greater than max velocity")


# ── DrumKit — the main class that uses dynamic instrument resolution ─────────

@dataclass
class DrumKit:
    """Drum kit configuration with instrument mappings and velocity ranges.
    
    MIDI note mappings are resolved at runtime by loading keymap files
    from midi_drums/mappings/. No hardcoded notes in this class.
    """
    
    name: str = "Standard Kit"
    channel: int = 9  # MIDI channel 10 (0-indexed)
    velocity_ranges: dict[str, VelocityRange] = field(
        default_factory=lambda: {
            "kick": VelocityRange(95, 120, 110),
            "snare": VelocityRange(90, 127, 115),
            "hihat": VelocityRange(60, 100, 80),
            "toms": VelocityRange(85, 115, 100),
            "cymbals": VelocityRange(70, 120, 95),
            "ride": VelocityRange(65, 100, 80),
        }
    )
    
    # Custom instrument mappings (overrides keymap defaults)
    custom_mappings: dict[str, int] = field(default_factory=dict)
    
    def get_midi_note(self, instrument_name: str, keymap_name: str = "gm") -> int | None:
        """Get MIDI note number for an instrument by name.
        
        Resolution order:
        1. custom_mappings if present
        2. Keymap file for the given preset (e.g., 'ad2', 'gm', 'ezd3')
        3. None if not found
        
        Args:
            instrument_name: Name of the instrument (e.g., 'kick', 'snare_1')
            keymap_name: Which keymap to load from (default: 'gm')
        
        Returns:
            MIDI note number or None if unmapped
        """
        if instrument_name in self.custom_mappings:
            return self.custom_mappings[instrument_name]
        
        return KeymapLoader.get_midi_note(instrument_name, keymap_name)
    
    def get_velocity_range(self, instrument_type: str) -> VelocityRange:
        """Get velocity range for an instrument type."""
        return self.velocity_ranges.get(
            instrument_type, 
            VelocityRange()  # Default range (1-127)
        )
    
    def randomize_velocity(self, instrument_type: str, base_velocity: int | None = None) -> int:
        """Get a randomized velocity within the instrument's range."""
        import random
        
        velocity_range = self.get_velocity_range(instrument_type)
        
        if base_velocity is None:
            min_vel = velocity_range.min_velocity
            max_vel = velocity_range.max_velocity
        else:
            min_vel = max(velocity_range.min_velocity, base_velocity - 15)
            max_vel = min(velocity_range.max_velocity, base_velocity + 15)
        
        return random.randint(min_vel, max_vel)
    
    @classmethod
    def from_keymap_name(cls, keymap_name: str) -> "DrumKit":
        """Create a DrumKit from a keymap file by name.
        
        Args:
            keymap_name: Name of the keymap (e.g., 'ad2', 'gm', 'ezd3')
        
        Returns:
            A configured DrumKit with mappings loaded from the keymap file
        """
        InstrumentRegistry.ensure_loaded()
        
        keymap = KeymapLoader.get_keymap(keymap_name)
        if keymap is None:
            raise ValueError(f"Keymap not found: {keymap_name}")
        
        custom_mappings = {}
        for instrument_name, data in keymap.get("instruments", {}).items():
            midi_note = data.get("midi_note")
            if midi_note is not None:
                custom_mappings[instrument_name] = int(midi_note)
        
        return cls(
            name=keymap.get("name", f"{keymap_name.title()} Kit"),
            custom_mappings=custom_mappings,
        )
    
    @classmethod
    def list_presets(cls) -> dict[str, str]:
        """List all available keymaps as presets."""
        if not KeymapLoader._loaded_keymaps:
            KeymapLoader.load_all()
        
        return {
            name: km.get("description", f"{name.title()} mapping")
            for name, km in KeymapLoader._loaded_keymaps.items()
            if name != "template"
        }


# ── Module Initialization ───────────────────────────────────────────────────

# Initialize at import time so instruments are ready immediately
initialize()
