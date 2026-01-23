"""
Maze generator core.

Implements a reproducible perfect maze generator (spanning tree over cells)
using an iterative DFS (recursive backtracker).
"""


from __future__ import annotations

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
from mazegen.patterns import compute_pattern_closed_cells


class MazeGenerator:
    """
    Generate mazes for the A-Maze-Ing project.

    This core generator is reusable and deterministic given a seed.
    """

    _width: int
    _height: int
    _entry: Coord
    _exit: Coord
    _perfect: bool
    _rng: random.Random
    _used_42: bool
    _warnings: list[str]
    _include_42: bool

    def __init__(
            self,
            *,
            width: int,
            height: int,
            entry_c: Coord,
            exit_c: Coord,
            perfect: bool,
            seed: Optional[int] = None,
            include_42: bool = True
    ) -> None:
        """
        Initialize the generator.

        Args:
            width: Maze width (columns).
            height: Maze height (rows).
            entry_c: Entry coordinate (x, y).
            exit_c: Exit coordinate (x, y).
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

        entry_x, entry_y = entry_c
        exit_x, exit_y = exit_c
        if not in_bounds(entry_x, entry_y, width, height):
            raise MazeConfigError(
                f"entry {entry_c} is out of bounds for {width} x {height}."
            )
        if not in_bounds(exit_x, exit_y, width, height):
            raise MazeConfigError(
                f"exit {exit_c} is out of bounds for {width} x {height}."
            )
        if entry_c == exit_c:
            raise MazeConfigError(
                "entry and exit must be different coordinates."
            )

        self._width = width
        self._height = height
        self._entry = entry_c
        self._exit = exit_c
        self._perfect = perfect
        self._rng = random.Random(seed)

        # This will be implemented in Phase 3 of project flowchart.
        self._used_42 = False
        self._warnings = []
        self._include_42 = include_42

    @property
    def used_42(self) -> bool:
        """Return True if the last generated maze included the '42' pattern."""
        return self._used_42

    @property
    def last_warnings(self) -> list[str]:
        """Return warnings produced during the last generation attempt."""
        return list(self._warnings)

    def generate(self) -> Maze:
        """
        Generate and return a new maze.

        For now, this implements perfect maze generation only.
        Non-perfect mode will be implemented later.

        Raises:
            MazeGenerationError: If generation fails unexpectedly.
        """
        if not self._perfect:
            raise MazeGenerationError(
                "Non-perfect generation is not implemented yet."
            )

        self._warnings = []
        self._used_42 = False

        walls: list[list[int]] = [
            [ALL_WALLS for _x in range(self._width)]
            for _y in range(self._height)
        ]

        closed: set[Coord] = set()
        if self._include_42:
            maybe_closed: set[Coord] | None = compute_pattern_closed_cells(
                self._width,
                self._height
            )
            if maybe_closed is None:
                self._warnings.append(
                    "Maze too small to include the 42 pattern "
                    "(needs at least 7x5)."
                )
            else:
                closed = maybe_closed
                self._used_42 = True
                for x, y in closed:
                    walls[y][x] = ALL_WALLS

        # Choose start: entry is a good deterministic anchor.
        start: Final[Coord] = self._entry
        if start in closed:
            raise MazeGenerationError("Entry canno t be in a closed cell.")

        visited: set[Coord] = {start}
        stack: list[Coord] = [start]

        # DFS carve
        while stack:
            cell_x, cell_y = stack[-1]

            candidates: list[Coord] = []
            for _d, (next_x, next_y) in iter_orthogonal_neighbors(
                    cell_x,
                    cell_y,
                    self._width,
                    self._height
            ):
                neighbor = (next_x, next_y)
                if neighbor in closed:
                    continue
                if neighbor not in visited:
                    candidates.append(neighbor)

            if not candidates:
                stack.pop()
                continue

            nxt_candidate = self._rng.choice(candidates)
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

        target: int = self._width * self._height - len(closed)
        if len(visited) != target:
            raise MazeGenerationError(
                "Not all cells were reached during generation of Maze."
            )

        return Maze(
            width=self._width,
            height=self._height,
            walls=walls,
            entry=self._entry,
            exit=self._exit,
            closed=closed
        )
