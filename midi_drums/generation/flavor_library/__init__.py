"""Pattern Flavor Library — distinct pattern variations for each section type.

Provides the infrastructure for generating multiple "flavors" of a pattern per
section so ComposerV2 can rotate between them, giving every bar real musical
diversity instead of only velocity tweaks on the same skeleton.

Usage in genre plugins:
    def get_section_variations(self, section: str) -> list[Pattern]:
        return [self._verse_flavor_1(), self._verse_flavor_2(), ...]

ComposerV2 handles selection via _select_bar_flavor().
"""
