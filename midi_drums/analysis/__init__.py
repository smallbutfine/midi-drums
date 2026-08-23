"""Audio analysis for riff-locked drum generation.

Requires ``midi_drums[rfi]`` extras (librosa + soundfile) — optional dependency group.
"""

from midi_drums.analysis.audio_analysis import analyze_onsets, detect_beats

__all__ = ["analyze_onsets", "detect_beats"]
