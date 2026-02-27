"""
Reproducibility test

Asserts same seed produces same walls.
Will assert in future that different seed generates different walls.
"""


from __future__ import annotations

from mazegen import Maze
from mazegen.generator import MazeGenerator


def test_same_seed_produces_same_walls() -> None:
    generator_1: MazeGenerator = MazeGenerator(
        width=10,
        height=7,
        entry_c=(0, 0),
        exit_c=(9, 6),
        perfect=True,
        seed=123
    )

    generator_2: MazeGenerator = MazeGenerator(
        width=10,
        height=7,
        entry_c=(0, 0),
        exit_c=(9, 6),
        perfect=True,
        seed=123
    )

    maze_1: Maze = generator_1.generate()
    maze_2: Maze = generator_2.generate()

    assert maze_1.walls == maze_2.walls
    assert maze_1.entry == maze_2.entry
    assert maze_1.exit == maze_2.exit
