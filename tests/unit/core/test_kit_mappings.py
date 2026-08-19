"""Tests for per-preset MIDI note mappings (issue #47, AC Group 1)."""

import json

import pytest

from midi_drums.core.models.kit import DrumKit
from midi_drums.core.value_objects.drum_instrument import DrumInstrument


class TestPresetsDivergeOnNoteMapping:
    """`get_midi_note()` must differ across presets for EZDrummer-specific
    articulations - previously every preset resolved identically because
    all `custom_mappings` dicts were empty."""

    @pytest.mark.parametrize(
        "instrument",
        [
            DrumInstrument.CLOSED_HH_EDGE,
            DrumInstrument.CLOSED_HH_TIP,
            DrumInstrument.TIGHT_HH_EDGE,
            DrumInstrument.TIGHT_HH_TIP,
            DrumInstrument.OPEN_HH_1,
            DrumInstrument.OPEN_HH_2,
            DrumInstrument.OPEN_HH_3,
            DrumInstrument.OPEN_HH_MAX,
        ],
    )
    def test_ezdrummer3_and_gm_diverge(self, instrument):
        ez_kit = DrumKit.create_ezdrummer3_kit()
        gm_kit = DrumKit.create_gm_drums_kit()

        assert ez_kit.get_midi_note(instrument) != gm_kit.get_midi_note(
            instrument
        )

    def test_gm_collapses_closed_hihat_family_to_gm_closed_hihat(self):
        gm_kit = DrumKit.create_gm_drums_kit()

        for instrument in (
            DrumInstrument.CLOSED_HH_EDGE,
            DrumInstrument.CLOSED_HH_TIP,
            DrumInstrument.TIGHT_HH_EDGE,
            DrumInstrument.TIGHT_HH_TIP,
        ):
            assert (
                gm_kit.get_midi_note(instrument)
                == DrumInstrument.CLOSED_HH.value
            )

    def test_gm_collapses_open_hihat_family_to_gm_open_hihat(self):
        gm_kit = DrumKit.create_gm_drums_kit()

        for instrument in (
            DrumInstrument.OPEN_HH_1,
            DrumInstrument.OPEN_HH_2,
            DrumInstrument.OPEN_HH_3,
            DrumInstrument.OPEN_HH_MAX,
        ):
            assert (
                gm_kit.get_midi_note(instrument) == DrumInstrument.OPEN_HH.value
            )

    def test_ezdrummer3_still_uses_its_own_extended_articulation_notes(self):
        ez_kit = DrumKit.create_ezdrummer3_kit()

        assert ez_kit.get_midi_note(DrumInstrument.OPEN_HH_MAX) == 60
        assert ez_kit.get_midi_note(DrumInstrument.CLOSED_HH_EDGE) == 22

    def test_shared_instruments_still_agree_across_presets(self):
        ez_kit = DrumKit.create_ezdrummer3_kit()
        gm_kit = DrumKit.create_gm_drums_kit()

        for instrument in (
            DrumInstrument.KICK,
            DrumInstrument.SNARE,
            DrumInstrument.CLOSED_HH,
            DrumInstrument.CRASH,
            DrumInstrument.RIDE,
        ):
            assert ez_kit.get_midi_note(instrument) == gm_kit.get_midi_note(
                instrument
            )


class TestAddictiveDrumsHasVendorSpecificNotes:
    """AD2 uses its own keymap (XLN Audio, June 2021) — must differ from GM.

    Previously AD2 was a GM-collapsed placeholder; it now has real vendor
    notes so several instruments resolve to different MIDI numbers than GM."""

    def test_addictive_drums_presets_differ_from_gm(self):
        ad_kit = DrumKit.create_addictive_drums_kit()
        gm_kit = DrumKit.create_gm_drums_kit()

        # Hi-hat positions differ between AD2 and GM
        for instrument in (
            DrumInstrument.CLOSED_HH,
            DrumInstrument.OPEN_HH,
            DrumInstrument.CLOSED_HH_EDGE,
            DrumInstrument.OPEN_HH_1,
        ):
            assert ad_kit.get_midi_note(instrument) != gm_kit.get_midi_note(
                instrument
            )

    def test_addictive_drums_presets_differ_from_ezdrummer3(self):
        ad_kit = DrumKit.create_addictive_drums_kit()
        ez_kit = DrumKit.create_ezdrummer3_kit()

        # Core hi-hat notes differ between AD2 and EZD3 extended positions
        assert ad_kit.get_midi_note(DrumInstrument.CLOSED_HH_EDGE) != (
            ez_kit.get_midi_note(DrumInstrument.CLOSED_HH_EDGE)
        )
        assert ad_kit.get_midi_note(DrumInstrument.OPEN_HH_1) != (
            ez_kit.get_midi_note(DrumInstrument.OPEN_HH_1)
        )

    def test_addictive_drums_core_instruments_match_gm_notes(self):
        """Core drums (kick, snare) are the same MIDI notes across presets."""
        ad_kit = DrumKit.create_addictive_drums_kit()

        assert ad_kit.get_midi_note(DrumInstrument.KICK) == 36
        assert ad_kit.get_midi_note(DrumInstrument.SNARE) == 38


class TestAddictiveDrumsExtendedInstruments:
    """Verify AD2's vendor-specific instruments resolve to correct MIDI notes."""

    def test_brush_sweeps_resolve_to_vendor_notes(self):
        ad = DrumKit.create_addictive_drums_kit()
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_A) == 35
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_B) == 34
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_C) == 33
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_D) == 32
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_E) == 31
        assert ad.get_midi_note(DrumInstrument.BRUSH_SWEEP_F) == 30

    def test_snare_rimshot_is_side_stick(self):
        ad = DrumKit.create_addictive_drums_kit()
        # AD2: RIM maps to Side Stick (40), SNARE_RIMSHOT maps to Rimshot (37)
        assert ad.get_midi_note(DrumInstrument.SNARE_RIMSHOT) == 37
        assert ad.get_midi_note(DrumInstrument.RIM) == 40

    def test_tom_edge_hits_resolve_to_vendor_notes(self):
        ad = DrumKit.create_addictive_drums_kit()
        assert ad.get_midi_note(DrumInstrument.TOM_EDGE_MID) == 65
        assert ad.get_midi_note(DrumInstrument.TOM_EDGE_FLOOR) == 65
        assert ad.get_midi_note(DrumInstrument.TOM_EDGE_3) == 67
        assert ad.get_midi_note(DrumInstrument.TOM_EDGE_4) == 69

    def test_tight_hh_closed_resolve_to_vendor_notes(self):
        ad = DrumKit.create_addictive_drums_kit()
        assert ad.get_midi_note(DrumInstrument.TIGHT_HH_EDGE) == 91
        assert ad.get_midi_note(DrumInstrument.TIGHT_HH_TIP) == 90

    def test_crash_choked_resolve_to_vendor_notes(self):
        ad = DrumKit.create_addictive_drums_kit()
        assert ad.get_midi_note(DrumInstrument.CRASH_CHOKED_A) == 80
        assert ad.get_midi_note(DrumInstrument.CRASH_CHOKED_B) == 79
        assert ad.get_midi_note(DrumInstrument.CRASH_CHOKED_C) == 71
        assert ad.get_midi_note(DrumInstrument.CRASH_CHOKED_D) == 68

    def test_ad2_extended_hihat_differ_from_gm(self):
        """AD2's tight HH notes are high (90-91) unlike GM (42/46)."""
        ad = DrumKit.create_addictive_drums_kit()
        gm = DrumKit.create_gm_drums_kit()
        for inst in (
            DrumInstrument.TIGHT_HH_EDGE,
            DrumInstrument.TIGHT_HH_TIP,
        ):
            assert ad.get_midi_note(inst) != gm.get_midi_note(inst)


class TestGmBaselineCompleteCoverage:
    """GM-baseline presets map every core instrument explicitly.

    Previously they relied on _GM_HIHAT_COLLAPSE only (8 instruments).
    Now _GM_BASELINE covers all 13 core instruments + collapse handles the rest.
    """

    def test_every_core_instrument_has_explicit_mapping(self):
        gm = DrumKit.create_gm_drums_kit()
        # All 13 core instruments must be in custom_mappings (explicit)
        expected = {
            DrumInstrument.KICK,
            DrumInstrument.SNARE,
            DrumInstrument.RIM,
            DrumInstrument.CLOSED_HH,
            DrumInstrument.PEDAL_HH,
            DrumInstrument.OPEN_HH,
            DrumInstrument.MID_TOM,
            DrumInstrument.FLOOR_TOM,
            DrumInstrument.CRASH,
            DrumInstrument.RIDE,
            DrumInstrument.RIDE_BELL,
            DrumInstrument.SPLASH,
            DrumInstrument.CHINA,
        }
        mapped = set(gm.custom_mappings.keys())
        assert expected.issubset(mapped)


class TestGmBaselinePresetsAreActuallyGmCompliant:
    """Regression: GM-baseline presets must match gm_drums for every DrumInstrument."""

    @pytest.mark.parametrize(
        "factory",
        [
            DrumKit.create_studio_drummer3_kit,
            DrumKit.create_bfd3_kit,
            DrumKit.create_modo_drums_kit,
            DrumKit.create_ml_drums_kit,
        ],
    )
    def test_matches_gm_drums_note_table(self, factory):
        kit = factory()
        gm_kit = DrumKit.create_gm_drums_kit()

        for instrument in DrumInstrument:
            assert kit.get_midi_note(instrument) == gm_kit.get_midi_note(
                instrument
            )

    def test_presets_do_not_share_a_mutable_mappings_dict(self):
        """Each factory call must get its own custom_mappings dict - a
        shared mutable default would let mutating one preset's mappings
        leak into every other GM-baseline preset."""
        kit_a = DrumKit.create_bfd3_kit()
        kit_a.custom_mappings[DrumInstrument.KICK] = 1

        kit_b = DrumKit.create_modo_drums_kit()

        assert (
            kit_b.get_midi_note(DrumInstrument.KICK)
            == DrumInstrument.KICK.value
        )


class TestDrumKitFromDict:
    """DrumKit.from_dict() lets users supply a fully custom mapping."""

    def test_builds_custom_mappings_from_instrument_names(self):
        kit = DrumKit.from_dict(
            {
                "name": "My Custom Kit",
                "channel": 3,
                "mappings": {"KICK": 35, "SNARE": 40},
            }
        )

        assert kit.name == "My Custom Kit"
        assert kit.channel == 3
        assert kit.get_midi_note(DrumInstrument.KICK) == 35
        assert kit.get_midi_note(DrumInstrument.SNARE) == 40

    def test_defaults_name_and_channel_when_omitted(self):
        kit = DrumKit.from_dict({"mappings": {"KICK": 35}})

        assert kit.name
        assert kit.channel == 9

    def test_unmapped_instruments_fall_back_to_enum_value(self):
        kit = DrumKit.from_dict({"mappings": {"KICK": 35}})

        assert (
            kit.get_midi_note(DrumInstrument.RIDE) == DrumInstrument.RIDE.value
        )

    def test_unknown_instrument_name_raises_value_error(self):
        with pytest.raises(ValueError):
            DrumKit.from_dict({"mappings": {"NOT_A_REAL_INSTRUMENT": 40}})

    def test_instrument_name_lookup_is_case_insensitive(self):
        kit = DrumKit.from_dict({"mappings": {"kick": 35}})

        assert kit.get_midi_note(DrumInstrument.KICK) == 35

    def test_non_numeric_note_value_raises_value_error(self):
        """Regression: int(note) used to be called unguarded, so a
        non-numeric string raised Python's raw int() ValueError and a
        list/dict value raised an undocumented TypeError instead of the
        class's own uniformly-typed ValueError."""
        with pytest.raises(ValueError):
            DrumKit.from_dict({"mappings": {"KICK": "thirty-six"}})

    def test_non_scalar_note_value_raises_value_error_not_type_error(self):
        with pytest.raises(ValueError):
            DrumKit.from_dict({"mappings": {"KICK": [36]}})


class TestDrumKitFromJson:
    """DrumKit.from_json() loads a mapping file from disk."""

    def test_loads_kit_from_json_file(self, tmp_path):
        mapping_path = tmp_path / "custom_kit.json"
        mapping_path.write_text(
            json.dumps(
                {
                    "name": "File Kit",
                    "mappings": {"KICK": 35, "SNARE": 37},
                }
            ),
            encoding="utf-8",
        )

        kit = DrumKit.from_json(mapping_path)

        assert kit.name == "File Kit"
        assert kit.get_midi_note(DrumInstrument.KICK) == 35
        assert kit.get_midi_note(DrumInstrument.SNARE) == 37

    def test_accepts_str_path(self, tmp_path):
        mapping_path = tmp_path / "custom_kit.json"
        mapping_path.write_text(
            json.dumps({"mappings": {"KICK": 30}}), encoding="utf-8"
        )

        kit = DrumKit.from_json(str(mapping_path))

        assert kit.get_midi_note(DrumInstrument.KICK) == 30
