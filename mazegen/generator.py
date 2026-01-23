"""
Maze generator core.

Implements a reproducible perfect maze generator (spanning tree over cells)
using an iterative DFS (recursive backtracker).
"""


import random
from typing import Final, Optional

from mazegen.errors import MazeConfigError, MazeGenerationError
from mazegen.maze import (
    ALL_WALLS,
    Coord,
    Maze,
    assert_neighbor_wall_consistency,
    ensure_outer_borders_closed,
    in_bounds,
    iter_orthogonal_neighbors,
    set_wall_between
)


class MazeGenerator:
    """
    Generate mazes for the A-Maze-Ing project.

    This core generator is reusable and deterministic given a seed.
    """

    __width: int
    __height: int
    __entry: Coord
    __exit: Coord
    __perfect: bool
    __rng: random.Random
    __used42: bool
    __warnings: list[str]

    def __init__(
            self,
            *,
            width: int,
            height: int,
            entry: Coord,
            exit: Coord,
            perfect: bool,
            seed: Optional[int] = None,
            include_42: bool = True
    ) -> None:
        """
        Initialize the generator.

        Args:
            width: Maze width (columns).
            height: Maze height (rows).
            entry: Entry coordinate (x, y).
            exit: Exit coordinate (x, y).
            perfect: Whether the maze must be perfect (unique paths).
            seed: Random seed for reproducibility.
            include_42: Placeholder for future "42" insertion (Milestone 3).

        Raises:
            MazeConfigError: If parameters are invalid.
        """
        if width <= 0 or height <= 0:
            raise MazeConfigError(
                "Arguments width and height must be positive integers."
            )

        entry_x, entry_y = entry
        exit_x, exit_y = exit
        if not in_bounds(entry_x, entry_y, width, height):
            raise MazeConfigError(
                f"entry {entry} is out of bounds for {width} x {height}."
            )
        if not in_bounds(exit_x, exit_y, width, height):
            raise MazeConfigError(
                f"exit {exit} is out of bounds for {width} x {height}."
            )
        if entry == exit:
            raise MazeConfigError(
                "entry and exit must be different coordinates."
            )

        self.__width = width
        self.__height = height
        self.__entry = entry
        self.__exit = exit
        self.__perfect = perfect
        self.__rng = random.Random(seed)

        # This will be implemented in Phase 3 of project flowchart.
        self.__used42 = False
        self.__warnings = []
        if include_42:
            pass

    @property
    def used_42(self) -> bool:
        """Return True if the last generated maze included the '42' pattern."""
        return self.__used42

    @property
    def last_warnings(self) -> list[str]:
        """Return warnings produced during the last generation attempt."""
        return list(self.__warnings)

    def generate(self) -> Maze:
        """
        Generate and return a new maze.

        For now, this implements perfect maze generation only.
        Non-perfect mode will be implemented later.

        Raises:
            MazeGenerationError: If generation fails unexpectedly.
        """
        walls: list[list[int]] = [
            [ALL_WALLS for _x in range(self.__width)]
            for _y in range(self.__height)
        ]

        # No closed cells yet (Phase 3 of project flowchart)
        closed: set[Coord] = set()

        # Choose start: entry is a good deterministic anchor.
        start: Final[Coord] = self.__entry
        if start in closed:
            raise MazeGenerationError("Entry cannot be in a closed cell.")

        visited: set[Coord] = {start}
        stack: list[Coord] = [start]

        # DFS carve
        while stack:
            cell_x, cell_y = stack[-1]

            candidates: list[Coord] = []
            for _d, (next_x, next_y) in iter_orthogonal_neighbors(
                    cell_x,
                    cell_y,
                    self.__width,
                    self.__height
            ):
                neighbor = (next_x, next_y)
                if neighbor in closed:
                    continue
                if neighbor not in visited:
                    candidates.append(neighbor)

            if not candidates:
                stack.pop()
                continue

            nxt_candidate = self.__rng.choice(candidates)
            set_wall_between(
                walls,
                (cell_x, cell_y),
                nxt_candidate,
                closed=False
            )
            visited.add(nxt_candidate)
            stack.append(nxt_candidate)

        # Enforce borders and validate consistency
        ensure_outer_borders_closed(walls)
        assert_neighbor_wall_consistency(walls)

        if len(visited) != (self.__width * self.__height):
            raise MazeGenerationError(
                "Not all cells were reached during generation of Maze."
            )

        return Maze(
            width=self.__width,
            height=self.__height,
            walls=walls,
            entry=self.__entry,
            exit=self.__exit,
            closed=closed
        )
