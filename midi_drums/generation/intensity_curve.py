"""Section intensity curves - define the energy arc within a section.

Each curve specifies how complexity, density, and velocity evolve from bar 0
through the last bar of that section. Used by BarSelector to produce different
patterns per bar instead of one static loop repeated N times.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class IntensityPoint:
    """A single point on an intensity curve.

    Attributes:
        position: Normalised position within the section (0.0 = start, 1.0 = end).
        complexity_multiplier: Scales the overall pattern complexity at this point
            (values < 1 reduce hit count/density; > 1 increases it).
        velocity_bias: Global offset applied to all beat velocities at this point.
        density_factor: Multiplier on the *number* of beats in the bar
            (applied before generating individual beats, e.g. skip half the usual
            hi-hat hits when < 1).
    """

    position: float
    complexity_multiplier: float
    velocity_bias: int = 0
    density_factor: float = 1.0


class IntensityCurve(Enum):
    """Predefined section intensity arcs.

    Each enum member's value is a list of control points. The actual curve
    is interpolated between adjacent points so callers can pass any two-point
    list and get smooth transitions.
    """

    # Intro/verse building up: low start → high end
    ASCENDING = (
        [IntensityPoint(0.0, 0.3, -15, 0.6)],
        [IntensityPoint(1.0, 1.0, 0, 1.0)],
    )

    # Post-chorus or tag-down: high → low
    DESCENDING = (
        [IntensityPoint(0.0, 1.0, 0, 1.0)],
        [IntensityPoint(1.0, 0.3, -20, 0.5)],
    )

    # Steady groove: plateau in the middle
    PLATEAU = (
        [IntensityPoint(0.0, 0.6, -10, 0.8)],
        [IntensityPoint(0.5, 1.0, 5, 1.0)],
        [IntensityPoint(1.0, 0.7, 0, 0.9)],
    )

    # Dip-then-rise: tension → release (great for bridge → chorus)
    DIP_RISE = (
        [IntensityPoint(0.0, 0.6, -10, 0.8)],
        [IntensityPoint(0.3, 0.3, -25, 0.5)],
        [IntensityPoint(0.7, 1.0, 10, 1.1)],
        [IntensityPoint(1.0, 0.9, 0, 1.0)],
    )

    # Stair-step build (verse → chorus ramp)
    STEPS = (
        [IntensityPoint(0.0, 0.3, -15, 0.6)],
        [IntensityPoint(0.25, 0.5, -8, 0.75)],
        [IntensityPoint(0.5, 0.7, 0, 0.9)],
        [IntensityPoint(1.0, 1.0, 15, 1.2)],
    )


def interpolate_curve(
    curve_points: list[IntensityPoint], position: float
) -> tuple[float, int, float]:
    """Interpolate a single point on an intensity curve.

    Returns (complexity_multiplier, velocity_bias, density_factor).
    """
    if len(curve_points) == 1:
        pt = curve_points[0]
        return pt.complexity_multiplier, pt.velocity_bias, pt.density_factor

    # Clamp position to [0, 1] of the curve span
    first_pos = curve_points[0].position
    last_pos = curve_points[-1].position
    if first_pos == last_pos:
        return (
            curve_points[0].complexity_multiplier,
            curve_points[0].velocity_bias,
            curve_points[0].density_factor,
        )

    t = max(0.0, min(1.0, (position - first_pos) / (last_pos - first_pos)))

    # Find bracketing points
    lower_pt = curve_points[0]
    upper_pt = curve_points[-1]
    for i in range(len(curve_points) - 1):
        if curve_points[i].position <= t * last_pos + first_pos * (
            1 - t
        ):
            lower_pt = curve_points[i]
        else:
            upper_pt = curve_points[i + 1]

    # Linear interpolation
    frac = 0.0 if lower_pt.position == upper_pt.position else (
        (position - lower_pt.position) / (upper_pt.position - lower_pt.position)
    )
    complexity = lower_pt.complexity_multiplier + frac * (
        upper_pt.complexity_multiplier - lower_pt.complexity_multiplier
    )
    velocity_bias = int(
        lower_pt.velocity_bias
        + frac * (upper_pt.velocity_bias - lower_pt.velocity_bias)
    )
    density = lower_pt.density_factor + frac * (
        upper_pt.density_factor - lower_pt.density_factor
    )
    return complexity, velocity_bias, density
