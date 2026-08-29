"""Test genre/drummer plugin auto-discovery and registration."""

import types

import pytest

from midi_drums.plugins.interfaces.drummer_plugin import DrummerPlugin
from midi_drums.plugins.registry.plugin_registry import PluginManager


@pytest.mark.unit
def test_discover_plugins_loads_external_directory(tmp_path):
    """discover_plugins(plugin_dirs=[...]) must still support directories
    outside midi_drums.plugins (a documented extension point for
    third-party/custom plugins) - not just the built-in genres/drummers
    subpackages.
    """
    external_dir = tmp_path / "my_custom_plugins"
    external_dir.mkdir()
    (external_dir / "__init__.py").write_text("")
    (external_dir / "custom_drummer.py").write_text(
        "from midi_drums.plugins.base import DrummerPlugin\n"
        "\n"
        "class CustomDrummerPlugin(DrummerPlugin):\n"
        "    @property\n"
        "    def drummer_name(self):\n"
        "        return '_external_test_drummer'\n"
        "\n"
        "    @property\n"
        "    def preferred_genres(self):\n"
        "        return ['rock']\n"
        "\n"
        "    def apply_style(self, pattern):\n"
        "        return pattern\n"
        "\n"
        "    def get_signature_fills(self):\n"
        "        return []\n"
    )

    manager = PluginManager()
    manager.discover_plugins([external_dir])

    plugin = manager.registry.get_drummer_plugin("_external_test_drummer")
    assert plugin is not None
    assert type(plugin).__module__ == "my_custom_plugins.custom_drummer"


@pytest.mark.unit
def test_register_plugins_from_module_registers_locally_defined_class_once():
    """A plugin class actually defined in the scanned module registers
    exactly once, even if bound to two attribute names in that module.
    """

    class _LocalDrummer(DrummerPlugin):
        @property
        def drummer_name(self) -> str:
            return "_local_test_drummer"

        @property
        def preferred_genres(self) -> list[str]:
            return ["rock"]

        def apply_style(self, pattern):
            return pattern

        def get_signature_fills(self):
            return []

    fake_module = types.ModuleType("fake_module_local")
    _LocalDrummer.__module__ = "fake_module_local"
    fake_module.LocalDrummer = _LocalDrummer
    fake_module.LocalDrummerAlias = _LocalDrummer

    manager = PluginManager()
    manager._register_plugins_from_module(fake_module)

    assert (
        manager.registry.get_drummer_plugin("_local_test_drummer") is not None
    )
    assert (
        manager.registry.get_available_drummers().count("_local_test_drummer")
        == 1
    )


@pytest.mark.unit
def test_discover_plugins_loads_all_builtin_drummers():
    """After cleanup (legacy files removed, _refactored suffixes dropped),
    discovery still finds all current drummer plugins.
    """
    manager = PluginManager()
    manager.discover_plugins()

    expected = {
        "bonham",
        "carey",
        "chambers",
        "chadsmith",  # Chad Smith - RHCP funk-rock groove mastery
        "copeland",
        "dee",
        "haake",  # Thomas Haake - Meshuggah polyrhythmic djent style
        "halpern",  # Matt Halpern - Periphery odd-time/djent style
        "hoglan",
        "moon",  # Keith Moon - The Who chaotic crash/tom style
        "peart",
        "porcaro",
        "rich",
        "roeder",
        "weckl",
        "composite_doom_blues",
    }
    assert set(manager.registry.get_available_drummers()) == expected


@pytest.mark.unit
def test_discover_plugins_loads_all_builtin_genres():
    """Discovery finds all genre plugins."""
    manager = PluginManager()
    manager.discover_plugins()

    expected = {"metal", "rock", "jazz", "funk", "electronic"}
    assert set(manager.registry.get_available_genres()) == expected
