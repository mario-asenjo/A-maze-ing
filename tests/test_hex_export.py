"""
This test validates the exporting part of the core in hexadecimal format.
"""


from __future__ import annotations

from mazegen import MazeGenerator, Maze


def test_hex_lines_dimensions() -> None:
    generator: MazeGenerator = MazeGenerator(
        width=13,
        height=9,
        entry_c=(0, 0),
        exit_c=(12, 8),
        perfect=True,
        seed=1,
        include_42=True
    )
    maze: Maze = generator.generate()

    lines: list[str] = generator.to_hex_lines(maze)
    assert len(lines) == 9
    assert all(len(line) == 13 for line in lines)
