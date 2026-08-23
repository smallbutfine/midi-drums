"""Quick test to verify pattern flavors produce different patterns with Carey."""
from dataclasses import dataclass
from midi_drums.plugins.genres.rock import RockGenrePlugin
from midi_drums.plugins.drummers.carey import CareyPlugin

# Simple mock for GenerationParameters
@dataclass
class MockParams:
    style: str = "classic"
    complexity: float = 0.5

def count_kicks(pattern):
    return sum(1 for b in pattern.beats if str(b.instrument) == 'DrumInstrument.KICK')

plugin = RockGenrePlugin()
fv = plugin.get_section_flavors('verse', MockParams())

print("Flavor kick counts for classic verse (BEFORE Carey style):")
for i, f in enumerate(fv):
    print(f"  Flavor {i+1}: {len(f.beats)} beats, {count_kicks(f)} kicks")

# Now test with Carey style applied
carey = CareyPlugin()
print("\nAfter Carey style applied:")
for i, f in enumerate(fv):
    styled = carey.apply_style(f)
    print(f"  Flavor {i+1}: {len(styled.beats)} beats, {count_kicks(styled)} kicks")

# The key: do flavors still have DIFFERENT kick counts after Carey?
after_kick_counts = [count_kicks(carey.apply_style(f)) for f in fv]
print(f"\nKick counts across flavors after Carey: {after_kick_counts}")
if len(set(after_kick_counts)) > 1:
    print("✓ FLAVORS ARE DISTINCT - different kick counts means structural difference preserved")
else:
    print("✗ FLAVORS CONVERGED - all flavors have same kick count, differences lost")
