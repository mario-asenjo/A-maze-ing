"""
Tests implementation of data strucutres of Maze's state and helper functions
"""

from __future__ import annotations

import pytest

from src.mazegen.errors import MazeConfigError
from src.mazegen.maze import (
    ALL_WALLS,
    assert_neighbor_wall_consistency,
    has_wall,
    set_wall_between
)


def _new_grid(width: int, height: int) -> list[list[int]]:
    """Create a rectangular grid initializing with all walls closed."""
    return [[ALL_WALLS for _x in range(width)] for _y in range(height)]


def test_set_wall_between_updates_both_sides() -> None:
    """
    Opening shared wall must update both adjacent cells consistently.
    """
    walls = _new_grid(3, 3)

    # Open a wall between (1, 1) and (2, 1) -> East(1, 1), West(2, 1)
    set_wall_between(walls, (1, 1), (2, 1), closed=False)

    assert has_wall(walls[1][1], "E") is False
    assert has_wall(walls[1][2], "W") is False

    # Everything else should still be closed for these cells in this test
    assert has_wall(walls[1][1], "N") is True
    assert has_wall(walls[1][1], "S") is True
    assert has_wall(walls[1][1], "W") is True

    assert has_wall(walls[1][2], "N") is True
    assert has_wall(walls[1][2], "S") is True
    assert has_wall(walls[1][2], "E") is True


def test_neighbor_consistency_validator_detects_inconsistencies() -> None:
    walls: list[list[int]] = _new_grid(2, 1)

    # We introduce inconsistency by hand: open East wall in left cell only.
    walls[0][0] = walls[0][0] & ~2  # Clear 'E' bit (E = 2)

    # Right cell still has W closed, so validator should fail here.
    with pytest.raises(MazeConfigError):
        assert_neighbor_wall_consistency(walls)


def test_neighbor_consistency_after_using_helpers() -> None:
    walls: list[list[int]] = _new_grid(4, 3)

    # We open a couple of internal connections safely.
    set_wall_between(walls, (0, 0), (1, 0), closed=False)
    set_wall_between(walls, (1, 0), (1, 1), closed=False)
    set_wall_between(walls, (2, 1), (3, 1), closed=False)

    # Right cell still has W closed, so validator should fail here.
    assert_neighbor_wall_consistency(walls)
