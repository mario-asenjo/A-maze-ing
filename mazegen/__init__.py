"""
mazegen package public API.

This allows imports from mazegen directly.
"""


from .errors import (
    MazeConfigError,
    MazeError,
    MazeGenerationError,
    MazeUnsolvableError
)

from .maze import (
    ALL_WALLS,
    N,
    E,
    S,
    W,
    Coord,
    Direction,
    Maze,
    assert_neighbor_wall_consistency,
    ensure_outer_borders_closed,
    has_wall,
    in_bounds,
    neighbor_of,
    set_wall,
    set_wall_between
)

from .generator import MazeGenerator

__all__ = [
    "ALL_WALLS",
    "N",
    "E",
    "S",
    "W",
    "Coord",
    "Direction",
    "Maze",
    "MazeError",
    "MazeConfigError",
    "MazeGenerationError",
    "MazeUnsolvableError",
    "assert_neighbor_wall_consistency",
    "ensure_outer_borders_closed",
    "has_wall",
    "in_bounds",
    "neighbor_of",
    "set_wall",
    "set_wall_between",
    "MazeGenerator"
]
