"""Test constants module integration.

This test verifies that the new constants module works correctly
and can be used to replace magic numbers throughout the codebase.
"""

from midi_drums.config import DEFAULTS, TIMING, VELOCITY
from midi_drums.core.models.kit import InstrumentRegistry
from midi_drums.core.models.pattern import Beat


def test_velocity_constants():
    """Test that velocity constants work in Beat creation."""
    print("Testing velocity constants...")

    # Create beats using constants
    kick_inst = InstrumentRegistry.get("kick")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    hh_inst = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")

    kick = Beat(
        position=0.0,
        instrument=kick_inst,
        velocity=VELOCITY.KICK_NORMAL,
        duration=TIMING.QUARTER,
    )

    snare = Beat(
        position=1.0,
        instrument=snare_inst,
        velocity=VELOCITY.SNARE_HEAVY,
        duration=TIMING.QUARTER,
    )

    hihat = Beat(
        position=0.0,
        instrument=hh_inst,
        velocity=VELOCITY.HIHAT_NORMAL,
        duration=TIMING.EIGHTH,
    )

    assert kick.velocity == 100, f"Expected 100, got {kick.velocity}"
    assert (
        snare.velocity == VELOCITY.SNARE_HEAVY
    ), f"Expected {VELOCITY.SNARE_HEAVY}, got {snare.velocity}"
    assert hihat.velocity == 80, f"Expected 80, got {hihat.velocity}"

    print("  [OK] Velocity constants work correctly")


def test_timing_constants():
    """Test that timing constants work for positioning."""
    print("Testing timing constants...")

    assert TIMING.QUARTER == 1.0
    assert TIMING.HALF == 2.0
    assert TIMING.EIGHTH == 0.5
    assert TIMING.SIXTEENTH == 0.25

    print("  [OK] Timing constants are correct")


def test_default_constants():
    """Test that default constants have expected values."""
    print("Testing default constants...")

    assert DEFAULTS.TEMPO_DEFAULT >= 60 and DEFAULTS.TEMPO_DEFAULT <= 300
    assert DEFAULTS.COMPLEXITY_DEFAULT >= 0 and DEFAULTS.COMPLEXITY_DEFAULT <= 1
    assert (
        DEFAULTS.HUMANIZATION_DEFAULT >= 0
        and DEFAULTS.HUMANIZATION_DEFAULT <= 1
    )

    print("  [OK] Default constants are in valid range")


if __name__ == "__main__":
    test_velocity_constants()
    test_timing_constants()
    test_default_constants()
    print("\nAll constants integration tests passed!")
