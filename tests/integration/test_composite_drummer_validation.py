"""Tests for composite drummer plugins."""


from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.generation.builders.pattern_builder import PatternBuilder


# Instrument references
_KICK = InstrumentRegistry.get("kick")
_SNARE = InstrumentRegistry.get("snare_sticks")
_RIDE = InstrumentRegistry.get("ride_1_tip_hit_softer")
_CLOSED_HH = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
_CRASH = InstrumentRegistry.get("cymbal_1_hit")


def _basic_pattern():
    """Create a basic rock pattern for testing."""
    builder = PatternBuilder("test")
    for i in range(4):
        base = i * 4.0
        builder.kick(base, 100).kick(base + 2.0, 100)
        builder.snare(base + 1.0, 100).snare(base + 3.0, 100)
        for j in range(8):
            builder.hihat(base + j * 0.5, 80)
    return builder.build()


def _basic_pattern_with_ride():
    """Create pattern with ride cymbal."""
    builder = PatternBuilder("test_ride")
    builder.kick(0.0, 100).kick(2.0, 100)
    builder.snare(1.0, 100).snare(3.0, 100)
    for i in range(8):
        builder.ride(i * 0.5, 90)
    return builder.build()


def test_composite_drummer_applies_style():
    """Test that composite drummer plugin applies style correctly."""
    from midi_drums.plugins.drummers.composite.doom_blues import CompositeDoomBluesPlugin
    
    plugin = CompositeDoomBluesPlugin()
    pattern = _basic_pattern()
    
    styled = plugin.apply_style(pattern)
    assert styled is not None
    assert len(styled.beats) > 0


def test_composite_drummer_signature_fills():
    """Test that composite drummer has signature fills."""
    from midi_drums.plugins.drummers.composite.doom_blues import CompositeDoomBluesPlugin
    
    plugin = CompositeDoomBluesPlugin()
    fills = plugin.get_signature_fills()
    
    assert isinstance(fills, list)


def test_basic_pattern_has_expected_instruments():
    """Test that basic pattern contains expected instruments."""
    pattern = _basic_pattern()
    
    has_kick = any(b.instrument == _KICK for b in pattern.beats)
    has_snare = any(b.instrument == _SNARE for b in pattern.beats)
    has_hihat = any(b.instrument == _CLOSED_HH for b in pattern.beats)
    
    assert has_kick, "Pattern should have kick"
    assert has_snare, "Pattern should have snare"
    assert has_hihat, "Pattern should have hi-hat"


def test_pattern_with_ride():
    """Test pattern with ride cymbal."""
    pattern = _basic_pattern_with_ride()
    
    has_ride = any(b.instrument == _RIDE for b in pattern.beats)
    assert has_ride, "Pattern should have ride"


def test_crash_accent():
    """Test pattern with crash accent."""
    builder = PatternBuilder("test_crash")
    builder.kick(0.0, 100).kick(2.0, 100)
    builder.snare(1.0, 100).snare(3.0, 100)
    builder.crash(0.0, 115)
    
    pattern = builder.build()
    
    has_crash = any(b.instrument == _CRASH for b in pattern.beats)
    assert has_crash, "Pattern should have crash"
