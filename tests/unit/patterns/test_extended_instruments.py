"""Tests for AD2 extended instrument support (brush sweeps, rimshots, tight HH)."""


from midi_drums.config import VELOCITY
from midi_drums.core.models.pattern import Pattern
from midi_drums.core.value_objects.drum_instrument import DrumInstrument


class TestPatternBuilderExtendedMethods:
    """Test that the new PatternBuilder methods correctly emit extended instruments."""

    def test_brush_sweep_emits_correct_variant(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("brush_test")
        for variant in "ABCDEF":
            builder.brush_sweep(0.0, variant)

        pattern = builder.build()
        assert len(pattern.beats) == 6

        for i, beat in enumerate(pattern.beats):
            expected_variants = ["A", "B", "C", "D", "E", "F"]
            inst = getattr(DrumInstrument, f"BRUSH_SWEEP_{expected_variants[i]}")
            assert beat.instrument == inst

    def test_brush_sweep_default_velocity(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("brush_test")
        builder.brush_sweep(0.0, "A")
        pattern = builder.build()
        assert pattern.beats[0].velocity == VELOCITY.BRUSH_NORMAL

    def test_snare_rimshot_emits_correct_instrument(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("rim_test")
        builder.snare_rimshot(1.0)
        pattern = builder.build()
        assert pattern.beats[0].instrument == DrumInstrument.SNARE_RIMSHOT
        assert pattern.beats[0].velocity == VELOCITY.SNARE_RIMSHOT

    def test_tom_edge_emits_correct_variant(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("tom_test")
        builder.tom_edge(0.0, "MID")
        pattern = builder.build()
        assert pattern.beats[0].instrument == DrumInstrument.TOM_EDGE_MID

    def test_crash_choked_emits_correct_variant(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("crash_test")
        builder.crash_choked(0.0, "A")
        pattern = builder.build()
        assert pattern.beats[0].instrument == DrumInstrument.CRASH_CHOKED_A
        assert pattern.beats[0].velocity == VELOCITY.CRASH_ACCENT

    def test_tight_hh_edge_emits_correct_instrument(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("tight_test")
        builder.tight_hh(0.0)  # closed
        pattern = builder.build()
        assert pattern.beats[0].instrument == DrumInstrument.TIGHT_HH_EDGE
        assert pattern.beats[0].velocity == VELOCITY.HIHAT_NORMAL

    def test_tight_hh_open_emits_tip_variant(self):
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("tight_test")
        builder.tight_hh(0.0, open=True)
        pattern = builder.build()
        assert pattern.beats[0].instrument == DrumInstrument.TIGHT_HH_TIP


class TestBrushGrooveTemplate:
    """Test the BrushGroove template generates correct brush patterns."""

    def test_generates_brush_sweeps(self):
        from midi_drums.patterns import BrushGroove
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("test")
        result = BrushGroove(density=1.0, use_ride=False).generate(builder)
        pattern = result.build()

        # All beats should be brush sweep instruments (no ride)
        assert len(pattern.beats) > 0
        for beat in pattern.beats:
            assert "BRUSH_SWEEP" in beat.instrument.name

    def test_density_filters_brush_hits(self):
        from midi_drums.patterns import BrushGroove
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("test")
        result = BrushGroove(density=0.0).generate(builder)
        pattern = result.build()

        # With density 0, no brush hits should be added (only ride if use_ride=True)
        brush_count = sum(1 for b in pattern.beats if "BRUSH_SWEEP" in b.instrument.name)
        assert brush_count == 0


class TestRimshotGrooveTemplate:
    """Test the RimshotGroove template generates correct rim patterns."""

    def test_generates_rimshots_on_backbeat(self):
        from midi_drums.patterns import RimshotGroove
        from midi_drums.generation.builders.pattern_builder import PatternBuilder

        builder = PatternBuilder("test")
        result = RimshotGroove(use_tight_hh=False).generate(builder)
        pattern = result.build()

        # Should have rimshots on beats 2 and 4 of bar 0
        beat_positions = [b.position % 4.0 for b in pattern.beats]
        rimshots_on_2_and_4 = any(
            p == 1.0 or p == 3.0 for p in beat_positions
        )
        assert rimshots_on_2_and_4


class TestConvenienceFunctions:
    """Test the new convenience pattern functions."""

    def test_create_jazz_ballad_pattern(self):
        from midi_drums.patterns import create_jazz_ballad_pattern

        pattern = create_jazz_ballad_pattern("test_ballad", bars=2)
        assert isinstance(pattern, Pattern)
        assert "brush" in pattern.name.lower() or "ballad" in pattern.name.lower()
        # Should have brush sweep beats
        has_brushes = any("BRUSH_SWEEP" in b.instrument.name for b in pattern.beats)
        assert has_brushes

    def test_create_funk_rimshot_pattern(self):
        from midi_drums.patterns import create_funk_rimshot_pattern

        pattern = create_funk_rimshot_pattern("test_funk", bars=1)
        assert isinstance(pattern, Pattern)
        # Should have rimshot beats
        has_rimshots = any(
            b.instrument == DrumInstrument.SNARE_RIMSHOT for b in pattern.beats
        )
        assert has_rimshots
