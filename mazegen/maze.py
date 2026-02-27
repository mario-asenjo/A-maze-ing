"""
Maze data structures and wall manipulation helpers.

Each cell stores a 4-bit mask representing CLOSED walls in NSEW order:
- bit0: North wall (1 = closed, 0 = open)
- bit1: East wall
- bit2: South wall
- bit3: West wall
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Final, Mapping, Iterable

from .errors import MazeConfigError

Coord = tuple[int, int]
Direction = Literal["N", "E", "S", "W"]

N: Final[int] = 1 << 0  # 0001
E: Final[int] = 1 << 1  # 0010
S: Final[int] = 1 << 2  # 0100
W: Final[int] = 1 << 3  # 1000

ALL_WALLS: Final[int] = N | E | S | W  # 1111

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
    """
    Return True if the given direction wall is closed in the cell bitmask.
    """
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


def iter_orthogonal_neighbors(
        x: int,
        y: int,
        width: int,
        height: int
) -> Iterable[tuple[Direction, Coord]]:
    """
    Yield valid (direction, neighbor_coord) for orthogonal neighbors inside
    bounds.
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

    ret_val: Direction

    if dx == 0 and dy == -1:
        ret_val = "N"
    elif dx == 1 and dy == 0:
        ret_val = "E"
    elif dx == 0 and dy == 1:
        ret_val = "S"
    elif dx == -1 and dy == 0:
        ret_val = "W"
    else:
        raise MazeConfigError(
            f"Coordinates {a} and {b} are not orthogonal neighbors."
        )

    return ret_val


def set_wall_between(
        walls: list[list[int]],
        a: Coord,
        b: Coord,
        *,
        closed: bool
) -> None:
    """
    Set the wall between two orthogonal neighbor cells to closed/open,
    consistently on both sides.

    This is the *critical* helper that prevents the classic bug where one
    side is opened but neighbor still thinks it's closed.

    Args:
        walls: 2D grid [y][x] of wall bitmasks.
        a: First coordinate (x, y).
        b: Second coordinate (x, y) (must be orthogonal neighbor of a).
        closed: True closes the wall, False opens it.

    Raises:
        MazeConfigError: If coordinates are out of bounds or not neighbors.
    """
    height: int = len(walls)
    if height == 0:
        raise MazeConfigError("Walls grid must have at least 1 row.")
    width: int = len(walls[0])
    if any(len(row) != width for row in walls):
        raise MazeConfigError("Walls grid must be rectangular.")

    ax, ay = a
    bx, by = b
    if (not in_bounds(ax, ay, width, height)
            or not in_bounds(bx, by, width, height)):
        raise MazeConfigError(
            f"Coordinates out of bounds: a={a}, "
            f"b={b} for grid {width}x{height}."
        )
    d = direction_between(a, b)
    od = OPPOSITE[d]

    walls[ay][ax] = set_wall(walls[ay][ax], d, closed=closed)
    walls[by][bx] = set_wall(walls[by][bx], od, closed=closed)


def ensure_outer_borders_closed(walls: list[list[int]]) -> None:
    """
    Ensure all outer border walls are closed.

    Even if internal carving is correct, explicitly enforcing borders prevents
    accidental openings to "outside the grid", which is invalid per spec.
    """
    height: int = len(walls)
    if height == 0:
        return
    width: int = len(walls[0])
    if width == 0:
        return
    if any(len(row) != width for row in walls):
        raise MazeConfigError("Walls grid must be rectangular.")

    for x in range(width):
        # Top Row - Close N
        walls[0][x] = set_wall(walls[0][x], "N", closed=True)
        # Bottom Row - Close S
        walls[height - 1][x] = set_wall(
            walls[height - 1][x],
            "S",
            closed=True
        )

    for y in range(height):
        # Left col - Close W
        walls[y][0] = set_wall(walls[y][0], "W", closed=True)
        # Right col - Close E
        walls[y][width - 1] = set_wall(walls[y][width - 1], "E", closed=True)


def assert_neighbor_wall_consistency(walls: list[list[int]]) -> None:
    """
    Validate that neighboring cells agree on their shared wall encoding.

    Raises:
        MazeConfigError: If the grid is malformed or any inconsistency is
        found.
    """
    height: int = len(walls)
    if height == 0:
        return
    width: int = len(walls[0])
    if any(len(row) != width for row in walls):
        raise MazeConfigError("Walls grid must be rectangular.")

    for y in range(height):
        for x in range(width):
            cell: int = walls[y][x]

            # North neighbor: my N == neighbor's S
            if y > 0:
                north: int = walls[y - 1][x]
                if has_wall(cell, "N") != has_wall(north, "S"):
                    raise MazeConfigError(f"Inconsistent N/S wall at ({x},{y})"
                                          f" and ({x},{y - 1}).")

            # South neighbor: my S == neighbor's N
            if y < height - 1:
                south: int = walls[y + 1][x]
                if has_wall(cell, "S") != has_wall(south, "N"):
                    raise MazeConfigError(f"Inconsistent S/N wall at ({x},{y})"
                                          f" and ({x},{y + 1}).")

            # East neighbor: my E == neighbor's W
            if x < width - 1:
                east: int = walls[y][x + 1]
                if has_wall(cell, "E") != has_wall(east, "W"):
                    raise MazeConfigError(f"Inconsistent E/W wall at ({x},{y})"
                                          f" and ({x + 1},{y}).")

            # West neighbor: my W == neighbor's E
            if x > 0:
                west: int = walls[y][x - 1]
                if has_wall(cell, "W") != has_wall(west, "E"):
                    raise MazeConfigError(f"Inconsistent W/E wall at ({x},{y})"
                                          f" and ({x - 1},{y}).")
