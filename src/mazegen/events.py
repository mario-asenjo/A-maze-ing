"""
Event model used to animate maze generation.

The core generator can emit events (deltas) that allow a UI
to  animate generation without copying the full grid at every step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from .maze import Coord

StepKind = Literal["pattern_42", "carve", "backtrack", "loop_open", "done"]

@dataclass(frozen=True, slots=True)
class MazeStep:
    """
    A single generation event.

    Attributes:
        kind: Event category.
        a: Primary coordinate (e.g., current cell).
        b: Secondary coordinate (e.g., neighbor cell for a carved edge).
        visited: Number of visited walkable cells so far (best-effort).
    """

    kind: StepKind
    a: Optional[Coord]
    b: Optional[Coord]
    visited: int
