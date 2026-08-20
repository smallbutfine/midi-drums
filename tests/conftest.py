"""Shared pytest fixtures and configuration for MIDI Drums tests."""

import os
from pathlib import Path

import pytest

from midi_drums.api.python_api import DrumGeneratorAPI
from midi_drums.generation.engines.drum_generator import DrumGenerator


# Test output directory
@pytest.fixture(scope="session")
def test_output_dir(tmp_path_factory):
    """Create temporary output directory for test files."""
    return tmp_path_factory.mktemp("test_output")


# Core fixtures
@pytest.fixture
def drum_generator():
    """Provide DrumGenerator instance."""
    return DrumGenerator()


@pytest.fixture
def drum_api():
    """Provide DrumGeneratorAPI instance."""
    return DrumGeneratorAPI()


# Markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "ai: AI tests (requires API key)")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line(
        "markers", "requires_api: Tests requiring API access"
    )


# ------------------------------------------------------------------ #
# Skip AI tests when no backend is configured                          #
# ------------------------------------------------------------------ #

def pytest_runtest_setup(item: pytest.Item) -> None:
    """Skip 'ai' + 'requires_api' markers when no API key is configured."""
    markers = item.iter_markers("requires_api") or item.iter_markers("ai")
    has_requirement = any(m.name in ("requires_api", "ai") for m in markers)
    if not has_requirement:
        return

    import os  # noqa: PLC0415

    # Check every real API key that could be set in .env or env
    provider_keys = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GROQ_API_KEY",
        "COHERE_API_KEY",
    ]
    has_key = any(os.getenv(k) for k in provider_keys)
    if not has_key:
        # Also check .env file directly
        dotenv_path = Path(__file__).parent.parent / ".env"
        env_vars = {}
        if dotenv_path.exists():
            for line in dotenv_path.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env_vars[k] = v
        has_key = any(env_vars.get(k) for k in provider_keys)

    if not has_key:
        pytest.skip(
            "No API key configured — 'ai'/'requires_api' tests skipped. "
            "Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GROQ_API_KEY or COHERE_API_KEY."
        )
