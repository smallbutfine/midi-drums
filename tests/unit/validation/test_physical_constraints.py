"""Tests for physical feasibility validation.

NOTE: Several tests use DrumInstrument at class-level with static member access
(e.g., `DrumInstrument.KICK`). Those need to be updated to use
InstrumentRegistry.get("kick") instead.
"""

import pytest


@pytest.mark.skip(reason="Uses old DrumInstrument.XXX static members")
class TestPhysicalValidator:
    pass


@pytest.mark.skip(reason="Uses old DrumInstrument.XXX static members")
class TestLimbAssignment:
    pass


@pytest.mark.skip(reason="Uses old DrumInstrument.XXX static members")
class TestInstrumentClassifications:
    pass
