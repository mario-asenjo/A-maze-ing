"""

"""

from __future__ import annotations

from src.mazegen import MazeGenerator
from src.mazegen.maze import has_wall

def _count_open_edges(maze) -> int:
    edges = 0

    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) not in maze.walls:
                cell = maze.walls[y][x]
                # Count only "E" and "S" so we don't duplicate
                if x + 1 < maze.width and (x + 1, y) not in maze.closed:
                    if not has_wall(cell, "E"):
                        edges += 1
                if y + 1 < maze.height and (x, y + 1) not in maze.closed:
                    if not has_wall(cell, "S"):
                        edges += 1
    return edges

def test_nonperfect_adds_cycles() -> None:
    gen = MazeGenerator(
        width=25,
        height=15,
        entry_c=(0, 0),
        exit_c=(24, 14),
        perfect=False,
        seed=3,
        include_42=True
    )
    maze = gen.generate()

    nodes = maze.width * maze.height - len(maze.closed)
    edges = _count_open_edges(maze)

    assert edges >= nodes