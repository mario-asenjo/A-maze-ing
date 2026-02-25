"""

"""

from __future__ import annotations

from src.mazegen import MazeGenerator
from src.mazegen.maze import has_wall, Maze


def _is_3x3_fully_open(maze: Maze, x0: int, y0: int) -> bool:
    for yy in range(y0, y0 + 3):
        for xx in range(x0, x0 + 3):
            if (xx, yy) in maze.closed:
                return False

    for yy in range(y0, y0 + 3):
        for xx in range(x0, x0 + 2):
            if has_wall(maze.walls[yy][xx], "E"):
                return False
            if has_wall(maze.walls[yy][xx + 1], "W"):
                return False

    for yy in range(y0, y0 + 2):
        for xx in range(x0, x0 + 3):
            if has_wall(maze.walls[yy][xx], "S"):
                return False
            if has_wall(maze.walls[yy + 1][xx], "N"):
                return False

    return True


def test_no_open_3x3_in_nonperfect() -> None:
    gen = MazeGenerator(
        width=30,
        height=20,
        entry_c=(0, 0),
        exit_c=(29, 19),
        perfect=False,
        seed=9,
        include_42=True
    )
    maze = gen.generate()

    for y0 in range(0, maze.height - 2):
        for x0 in range(0, maze.width - 2):
            assert not _is_3x3_fully_open(maze, x0, y0)
