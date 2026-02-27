"""
This test proves the blocking of the cells in 42 pattern inside the maze.
"""
from mazegen import MazeGenerator, Maze, ALL_WALLS


def test_42_present_when_size_allows() -> None:
    gen: MazeGenerator = MazeGenerator(
        width=10,
        height=7,
        entry_c=(0, 0),
        exit_c=(9, 6),
        perfect=True,
        include_42=True
    )
    maze: Maze = gen.generate()

    assert gen.used_42 is True
    assert len(maze.closed) > 0

    for (x, y) in maze.closed:
        assert maze.walls[y][x] == ALL_WALLS


def test_42_absent_when_too_small() -> None:
    gen: MazeGenerator = MazeGenerator(
        width=6,
        height=4,
        entry_c=(0, 0),
        exit_c=(5, 3),
        perfect=True,
        seed=1,
        include_42=True
    )
    maze: Maze = gen.generate()

    assert gen.used_42 is False
    assert len(maze.closed) == 0
    assert len(gen.last_warnings) >= 1
