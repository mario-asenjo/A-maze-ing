"""
Maze data structures and wall manipulation helpers.

Each cell stores a 4-bit mask representing CLOSED walls in NSEW order:
- bit0: North wall (1 = closed, 0 = open)
- bit1: East wall
- bit2: South wall
- bit3: West wall
"""
from dataclasses import dataclass
from typing import Literal, Final, Mapping, Iterable

from mazegen.errors import MazeConfigError

Coord = tuple[int, int]
Direction = Literal["N", "E", "S", "W"]

N: Final[int] = 1 << 0
E: Final[int] = 1 << 1
S: Final[int] = 1 << 2
W: Final[int] = 1 << 3

ALL_WALLS: Final[int] = N | E | S | W

DIR_TO_BIT: Final[Mapping[Direction, int]] = {"N": N, "E": E, "S": S, "W": W}
DIR_TO_DELTA: Final[Mapping[Direction, tuple[int, int]]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0)
}
OPPOSITE: Final[Mapping[Direction, Direction]] = {
    "N": "S",
    "E": "W",
    "S": "N",
    "W": "E"
}

@dataclass(frozen=True, slots=True)
class Maze:
    """
    Maze container.

    Attributes:
        width: Grid width (number of columns).
        height: Grid height (number of rows).
        walls: 2D grid [y][x] of wall bitmasks (0..15).
        entry: Entry coordinate (x, y).
        exit: Exit coordinate (x, y).
        closed: Coordinates that are not walkable (e.g., the "42" pattern).
    """

    width: int
    height: int
    walls: list[list[int]]
    entry: Coord
    exit: Coord
    closed: set[Coord]


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    """Return True if (x, y) lies inside a width x height grid."""
    return 0 <= x < width and 0 <= y < height


def neighbor_of(x: int, y: int, direction: Direction) -> Coord:
    """Return the neighboring coordinate in the given direction."""
    dx, dy = DIR_TO_DELTA[direction]
    return x + dx, y + dy


def has_wall(cell: int, direction: Direction) -> bool:
    """Return True if the given direction wall is closed in the cell bitmask."""
    bit = DIR_TO_BIT[direction]
    return (cell & bit) != 0


def set_wall(cell: int, direction: Direction, *, closed: bool) -> int:
    """
    Return a new cell bitmask with the given wall set to closed/open.

    Args:
        cell: Current bitmask.
        direction: One of "N", "E", "S", "W".
        closed: True to close the wall, False to open it.
    """
    bit = DIR_TO_BIT[direction]
    if closed:
        return cell | bit
    return cell & ~bit


def iter_orthogonal_neighbors(x: int,
                              y: int,
                              width: int,
                              height: int
                              ) -> Iterable[tuple[Direction, Coord]]:
    """
    Yield valid (direction, neighbor_coord) for orthogonal neighbors inside bounds.
    """
    for d in ("N", "E", "S", "W"):
        direction: Direction = d
        nx, ny = neighbor_of(x, y, direction)
        if in_bounds(nx, ny, width, height):
            yield direction, (nx, ny)


def direction_between(a: Coord, b: Coord) -> Direction:
    """
    Return the direction from coord 'a' to its orthogonal neighbor 'b'.

    Raises:
        MazeConfigError: If a and b are not orthogonal neighbors.
    """
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay

    ret_val: Direction | None = None

    if dx == 0 and dy == -1:
        ret_val = "N"
    elif dx == 1 and dy == 0:
        ret_val = "E"
    elif dx == 0 and dy == 1:
        ret_val = "S"
    elif dx == -1 and dy == 0:
        ret_val = "W"
    else:
        raise MazeConfigError(f"Coordinates {a} and {b} are not orthogonal neighbors.")
