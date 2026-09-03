"""Tests for drummer signature fills wiring."""

from midi_drums.core.models.kit import InstrumentRegistry


def test_drummer_signature_fills_wired():
    """Test that drummer plugins have their signature fills wired correctly."""
    from midi_drums import DrumGenerator

    generator = DrumGenerator()

    # Use the plugin registry to access drummers
    for drummer_name in ["bonham", "porcaro", "weckl"]:
        plugin = generator.plugin_manager.registry.get_drummer_plugin(
            drummer_name
        )
        if plugin:
            fills = plugin.get_signature_fills()
            assert isinstance(
                fills, list
            ), f"{drummer_name} should have signature fills as list"


def test_china_instrument_available():
    """Test that china instrument is available in the registry."""

    china = InstrumentRegistry.get("cymbal_5_hit")
    assert china is not None, "China cymbal should be in template"


def test_all_drummers_have_fills():
    """Test that all drummers have signature fills defined."""
    from midi_drums import DrumGenerator

    generator = DrumGenerator()
    drummers = generator.get_available_drummers()

    for drummer_name in drummers:
        plugin = generator.plugin_manager.registry.get_drummer_plugin(
            drummer_name
        )
        if plugin:
            fills = plugin.get_signature_fills()
            # Each drummer should have some fills defined
            assert isinstance(
                fills, list
            ), f"{drummer_name} should have signature fills as list"
