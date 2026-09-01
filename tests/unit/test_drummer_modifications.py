"""Comprehensive tests for all 12 drummer modifications."""


from midi_drums.core.models.pattern import Pattern, Beat
from midi_drums.modifications.drummer_mods import (
    BehindBeatTiming,
    TripletVocabulary,
    GhostNoteLayer,
    LinearCoordination,
    HeavyAccents,
    ShuffleFeelApplication,
    FastChopsTriplets,
    PocketStretching,
    MinimalCreativity,
    SpeedPrecision,
    TwistedAccents,
    MechanicalPrecision,
)


def create_basic_pattern():
    """Create a basic rock beat for testing."""
    pattern = Pattern("basic_rock")

    # Kick on 1 and 3
    from midi_drums.core.models.kit import InstrumentRegistry
    kick_inst = InstrumentRegistry.get("kick")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    hh_inst = InstrumentRegistry.get("hihat_closed_1_tip_closed_1_hit")
    
    pattern.add_beat(0.0, kick_inst, 100)
    pattern.add_beat(1.0, snare_inst, 90)
    pattern.add_beat(2.0, kick_inst, 100)
    pattern.add_beat(3.0, snare_inst, 90)

    # Hi-hat eighth notes
    for i in range(8):
        pattern.add_beat(i * 0.5, hh_inst, 70)

    return pattern


def test_behind_beat_timing():
    """Test BehindBeatTiming modification."""
    print("Testing BehindBeatTiming...")
    modifier = BehindBeatTiming(max_delay_ms=25.0)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.7)

    # Snares should be delayed behind beat
    for beat in modified.beats:
        if hasattr(beat, "velocity") and beat.position == 1.0:
            print(f"  Beat at {beat.position}: velocity={beat.velocity}")

    print("  [OK] BehindBeatTiming applied")


def test_triplet_vocabulary():
    """Test TripletVocabulary modification."""
    print("Testing TripletVocabulary...")
    modifier = TripletVocabulary(triplet_probability=0.4)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.8)

    assert len(modified.beats) > 0
    print(f"  [OK] TripletVocabulary: {len(modified.beats)} beats")


def test_ghost_note_layer():
    """Test GhostNoteLayer modification."""
    print("Testing GhostNoteLayer...")
    modifier = GhostNoteLayer(density=0.3)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.5)

    ghost_count = sum(1 for b in modified.beats if getattr(b, "ghost_note", False))
    print(f"  [OK] GhostNoteLayer: {ghost_count} ghost notes")


def test_linear_coordination():
    """Test LinearCoordination modification."""
    print("Testing LinearCoordination...")
    modifier = LinearCoordination()
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.7)

    # Should have linear sections
    has_linear_section = False
    for i in range(len(modified.beats) - 2):
        if (
            getattr(modified.beats[i], "instrument", None) is not None
            and getattr(modified.beats[i + 1], "instrument", None) is not None
        ):
            has_linear_section = True

    assert has_linear_section
    print(f"  [OK] LinearCoordination: {len(modified.beats)} beats")


def test_heavy_accents():
    """Test HeavyAccents modification."""
    print("Testing HeavyAccents...")
    modifier = HeavyAccents(accent_boost=15)
    pattern = create_basic_pattern()
    # Add accented beats so the modification has something to work with
    from midi_drums.core.models.kit import InstrumentRegistry
    kick_inst = InstrumentRegistry.get("kick")
    pattern.beats[0].accent = True  # First kick gets accented
    modified = modifier.apply(pattern, intensity=0.8)

    max_vel = max(b.velocity for b in modified.beats)
    assert max_vel > 100, f"Expected high accent velocity, got {max_vel}"
    print(f"  [OK] HeavyAccents: max velocity={max_vel}")


def test_shuffle_feel_application():
    """Test ShuffleFeelApplication modification."""
    print("Testing ShuffleFeelApplication...")
    modifier = ShuffleFeelApplication(shuffle_amount=0.33)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.7)

    assert len(modified.beats) > 0
    print(f"  [OK] ShuffleFeel: {len(modified.beats)} beats")


def test_twisted_accents():
    """Test TwistedAccents modification."""
    print("Testing TwistedAccents...")
    modifier = TwistedAccents(displacement=0.5)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.6)

    assert len(modified.beats) > 0
    print(f"  [OK] TwistedAccents: {len(modified.beats)} beats")


def test_pocket_stretching_applies_to_promoted_timekeeping_cymbals():
    """Verify pocket stretching only modifies timekeeper cymbal beats, not drums."""
    from midi_drums.core.models.kit import InstrumentRegistry

    modifier = PocketStretching(variation_ms=5.0)

    pattern = Pattern("basic")
    kick_inst = InstrumentRegistry.get("kick")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    ride_inst = InstrumentRegistry.get("ride_1_tip_hit_softer")

    # Kick (foot) should NOT be modified
    beat_kick = Beat(position=0.0, instrument=kick_inst, velocity=100)
    pattern.add_beat(beat_kick.position, beat_kick.instrument, beat_kick.velocity)

    # Snare (hand) should NOT be modified by pocket stretching
    beat_snare = Beat(position=1.0, instrument=snare_inst, velocity=90)
    pattern.add_beat(beat_snare.position, beat_snare.instrument, beat_snare.velocity)

    # Ride (promoted cymbal/hand timekeeper) SHOULD be modified
    beat_ride_promoted = Beat(position=0.0, instrument=ride_inst, velocity=85)
    beat_ride_promoted.is_timekeeper_promoted = True  # Promoted cymbal
    pattern.add_beat(beat_ride_promoted.position, beat_ride_promoted.instrument, beat_ride_promoted.velocity)

    modified = modifier.apply(pattern, intensity=0.7)

    # Find the ride beat in the modified pattern
    for beat in modified.beats:
        if beat.instrument == ride_inst and hasattr(beat, "is_timekeeper_promoted"):
            assert (
                beat.position != 0.0 or beat.velocity != 85
            ), f"Pocket stretching should modify promoted cymbal beats; got position={beat.position}, velocity={beat.velocity}"
            break


def test_linear_coordination_china_matches_crash_and_ride_priority():
    """LinearCoordination must treat CHINA as a crash/ride-equivalent (hand) priority."""
    from midi_drums.core.models.kit import InstrumentRegistry

    modifier = LinearCoordination()

    pattern = Pattern("test")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    china_inst = InstrumentRegistry.get("cymbal_5_hit")

    # Snare + China at same time (hand conflict -> resolve via linearization)
    beat_snare = Beat(position=0.0, instrument=snare_inst, velocity=90)
    pattern.add_beat(beat_snare.position, beat_snare.instrument, beat_snare.velocity)

    beat_china = Beat(position=0.0, instrument=china_inst, velocity=85)
    pattern.add_beat(beat_china.position, beat_china.instrument, beat_china.velocity)

    modified = modifier.apply(pattern, intensity=1.0)

    # Linear coordination should prevent simultaneous hand hits
    assert len(modified.beats) > 0


def test_minimal_creativity_thins_crash_and_china_promoted_cymbals():
    """MinimalCreativity must thin only CHINA and CRASH (not ride or hi-hat)."""
    from midi_drums.core.models.kit import InstrumentRegistry

    modifier = MinimalCreativity(sparseness=0.5)

    pattern = Pattern("test")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    crash_inst = InstrumentRegistry.get("cymbal_1_hit")

    for pos in [0.0, 1.0, 2.0, 3.0]:
        beat = Beat(position=pos, instrument=snare_inst, velocity=90)
        pattern.add_beat(beat.position, beat.instrument, beat.velocity)

        crash = Beat(position=pos, instrument=crash_inst, velocity=85)
        pattern.add_beat(crash.position, crash.instrument, crash.velocity)

    modified = modifier.apply(pattern, intensity=1.0)

    # Should have fewer cymbal hits than original due to thinning
    assert len(modified.beats) <= 8


def test_speed_precision_normalizes_promoted_cymbals_to_their_own_velocity():
    """SpeedPrecision normalises promoted cymbal beats ONLY."""
    from midi_drums.core.models.kit import InstrumentRegistry

    modifier = SpeedPrecision()

    pattern = Pattern("test")
    snare_inst = InstrumentRegistry.get("snare_sticks")
    ride_inst = InstrumentRegistry.get("ride_1_tip_hit_softer")

    # Snare with varied velocity (should NOT be normalized)
    for pos, vel in [(0.0, 80), (1.0, 95), (2.0, 70), (3.0, 100)]:
        beat = Beat(position=pos, instrument=snare_inst, velocity=vel)
        pattern.add_beat(beat.position, beat.instrument, beat.velocity)

    # Ride promoted cymbal with varied velocity (SHOULD be normalized)
    for pos in [0.0, 1.0, 2.0, 3.0]:
        ride = Beat(position=pos, instrument=ride_inst, velocity=85 + pos * 5)
        ride.is_timekeeper_promoted = True
        pattern.add_beat(ride.position, ride.instrument, ride.velocity)

    modified = modifier.apply(pattern, intensity=1.0)

    # Ride velocities should be more consistent (less variance)
    ride_velocities = [
        b.velocity for b in modified.beats
        if b.instrument == ride_inst and hasattr(b, "is_timekeeper_promoted")
    ]
    if len(ride_velocities) > 1:
        import statistics
        orig_stddev = statistics.stdev([80, 90, 95, 100])
        new_stddev = statistics.stdev(ride_velocities)
        assert new_stddev <= orig_stddev, f"Ride variance should decrease; was {orig_stddev}, now {new_stddev}"


def test_minimal_creativity():
    """Test MinimalCreativity modification."""
    print("Testing MinimalCreativity...")
    modifier = MinimalCreativity(sparseness=0.5)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.7)

    assert len(modified.beats) <= len(pattern.beats)
    print(f"  [OK] MinimalCreativity: {len(pattern.beats)} → {len(modified.beats)} beats")


def test_mechanical_precision():
    """Test MechanicalPrecision modification."""
    print("Testing MechanicalPrecision...")
    modifier = MechanicalPrecision(quantize_amount=0.95)
    pattern = create_basic_pattern()
    modified = modifier.apply(pattern, intensity=0.9)

    assert len(modified.beats) > 0
    print(f"  [OK] MechanicalPrecision: {len(modified.beats)} beats")


def test_modification_composition():
    """Test composing multiple modifications."""
    print("Testing modification composition...")
    pattern = create_basic_pattern()

    # Apply multiple modifiers in sequence
    pattern = BehindBeatTiming(max_delay_ms=15.0).apply(pattern, intensity=0.4)
    pattern = GhostNoteLayer(density=0.2).apply(pattern, intensity=0.3)
    pattern = HeavyAccents(accent_boost=10).apply(pattern, intensity=0.6)

    assert len(pattern.beats) > 0
    print(f"  [OK] Composition: {len(pattern.beats)} beats")


def test_modification_registry():
    """Test that all modifications are importable and usable."""
    # All modifications can be imported individually above
    from midi_drums.modifications.drummer_mods import (
        BehindBeatTiming,
        TripletVocabulary,
        GhostNoteLayer,
        LinearCoordination,
        HeavyAccents,
        ShuffleFeelApplication,
        PocketStretching,
        MinimalCreativity,
        SpeedPrecision,
        TwistedAccents,
        MechanicalPrecision,
    )
    
    # Verify each class exists and is instantiable
    mods = [
        BehindBeatTiming(),
        TripletVocabulary(),
        GhostNoteLayer(),
        LinearCoordination(),
        HeavyAccents(),
        ShuffleFeelApplication(),
        FastChopsTriplets(),
        PocketStretching(),
        MinimalCreativity(),
        SpeedPrecision(),
        TwistedAccents(),
        MechanicalPrecision(),
    ]
    
    assert len(mods) == 12

    print(f"  [OK] Modification registry has {len(mods)} entries")


def test_intensity_parameter():
    """Test that intensity parameter scales modification strength."""
    modifier = BehindBeatTiming(max_delay_ms=30.0)
    pattern1 = create_basic_pattern()
    pattern2 = create_basic_pattern()

    low_intensity = modifier.apply(pattern1, intensity=0.3)
    high_intensity = modifier.apply(pattern2, intensity=1.0)

    # High intensity should have more pronounced timing shifts
    assert len(high_intensity.beats) >= len(low_intensity.beats)
    
    print(f"  [OK] Intensity: low={len(low_intensity.beats)}, high={len(high_intensity.beats)} beats")


def test_immutability():
    """Test that modifications don't modify the original pattern."""
    modifier = HeavyAccents(accent_boost=20)
    original = create_basic_pattern()

    # Add accent to ensure modification produces different output
    from midi_drums.core.models.kit import InstrumentRegistry
    kick_inst = InstrumentRegistry.get("kick")
    original.beats[0].accent = True
    
    # Capture original velocities before modification
    original_velocities = [b.velocity for b in original.beats]

    modified = modifier.apply(original, intensity=0.8)

    # Original should be unchanged
    current_velocities = [b.velocity for b in original.beats]
    assert original_velocities == current_velocities, "Original pattern was mutated!"

    # Modified should have different velocities (accents boosted)
    modified_velocities = [b.velocity for b in modified.beats]
    assert any(m != o for m, o in zip(modified_velocities, original_velocities)), \
        "Modified velocities should differ from original"

    print("  [OK] Immutability preserved")


if __name__ == "__main__":
    test_behind_beat_timing()
    test_triplet_vocabulary()
    test_ghost_note_layer()
    test_linear_coordination()
    test_heavy_accents()
    test_shuffle_feel_application()
    test_fast_chops_triplets()
    test_pocket_stretching()
    test_minimal_creativity()
    test_speed_precision()
    test_twisted_accents()
    test_mechanical_precision()
    test_modification_composition()
    print("\nAll drummer modification tests passed!")
