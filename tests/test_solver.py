"""
This test validates that the path goes from entry to exit Coord, each step
is orthogonal, does not go through walls, does not step into closed cells
and that is the shortest path.
"""


from __future__ import annotations

from collections import deque
from typing import Deque, cast
from mazegen import MazeGenerator
from mazegen import (
    DIR_TO_DELTA,
    Direction,
    has_wall,
    in_bounds,
    Maze,
    Coord
)


def test_solver_path_is_valid_and_minimal() -> None:
    generator: MazeGenerator = MazeGenerator(
        width=20,
        height=12,
        entry_c=(0, 0),
        exit_c=(19, 11),
        perfect=True,
        seed=7,
        include_42=True
    )
    maze: Maze = generator.generate()

    path: str = generator.solve(maze)

    # Simulate the path
    x, y = maze.entry
    for ch in path:
        assert ch in ("N", "E", "S", "W")
        direction: Direction = cast(Direction, ch)
        cell_mask: int = maze.walls[y][x]
        assert has_wall(cell_mask, direction) is False

        dir_x, dir_y = DIR_TO_DELTA[direction]
        x, y = x + dir_x, y + dir_y

        assert in_bounds(x, y, maze.width, maze.height)
        assert (x, y) not in maze.closed

    assert (x, y) == maze.exit

    assert len(path) == _bfs_distance(maze, maze.entry, maze.exit)


def _bfs_distance(gen_maze: Maze, start: Coord, goal: Coord) -> int:
    queue: Deque[tuple[int, int]] = deque([start])
    dist: dict[tuple[int, int], int] = {start: 0}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return dist[(x, y)]

        cell_mask: int = gen_maze.walls[y][x]
        for d in ("N", "E", "S", "W"):
            direction: Direction = d
            if has_wall(cell_mask, direction):
                continue
            dir_x, dir_y = DIR_TO_DELTA[direction]
            next_x, next_y = x + dir_x, y + dir_y
            if not in_bounds(next_x, next_y, gen_maze.width, gen_maze.height):
                continue
            nxt = (next_x, next_y)
            if nxt in gen_maze.closed:
                continue
            if nxt in dist:
                continue
            dist[nxt] = dist[(x, y)] + 1
            queue.append(nxt)

    raise AssertionError("No path found by reference BFS (unexpected).")
