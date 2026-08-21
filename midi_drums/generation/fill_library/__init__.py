"""Pattern Fill Library — 8-12 signature fills per drummer with context-aware selection.

Provides the infrastructure for filling diversity: each drummer gets a curated library
of signature fills, and the `FillPicker` selects which fill to insert based on section
context, recent fill history, and musical position.

Usage in drummer plugins:
    class BonhamPlugin(DrummerPlugin):
        def get_signature_fills(self) -> list[Fill]:
            return [
                FillContext("bonham_triple_fill", self._triple_fill()),
                FillContext("bonham_tom_solo", self._tom_solo()),
                ...  # 8-12 fills total per drummer
            ]

ComposerV2 calls `fill_picker.select_fills(section, params, recent_fills)` which returns
a weighted pool of candidate fills for the current bar.
"""
