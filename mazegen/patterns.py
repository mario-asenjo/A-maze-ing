"""
Built-in patterns for maze generation.

Includes the "42" pattern defined as closed (blocked) cells.
"""


from __future__ import annotations

from typing import Final

from .maze import Coord

_DIGIT_4: Final[list[list[int]]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1]
]

_DIGIT_2: Final[list[list[int]]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1]
]


def compute_pattern_closed_cells(width: int, height: int) -> set[Coord] | None:
    """
    Compute the set of blocked cells forming a "42" pattern, centered.

    The pattern uses a 3x5 digits with a 1-column gap:
    total size = 7x5

    Returns:
        A set of coordinates (x, y) that must be blocked (closed), or None if
        the maze is too small to fit the pattern.
    """
    pattern_w = 7
    pattern_h = 5

    if width < pattern_w or height < pattern_h:
        return None

    offset_x = (width - pattern_w) // 2
    offset_y = (height - pattern_h) // 2

    closed: set[Coord] = set()

    # Place digit '4' at x in [0..2]
    for p_y in range(pattern_h):
        for p_x in range(3):
            if _DIGIT_4[p_y][p_x] == 1:
                closed.add((offset_x + p_x, offset_y + p_y))

    # Gap column at x=3
    # Place digit '2' at x in [4..6]
    for p_y in range(pattern_h):
        for p_x in range(3):
            if _DIGIT_2[p_y][p_x] == 1:
                closed.add((offset_x + 4 + p_x, offset_y + p_y))

    return closed
