from __future__ import annotations

from typing import List
from mazegen import MazeStep
from mazegen.generator import MazeGenerator


def test_generate_emits_events() -> None:
    steps: List[MazeStep] = list()

    def on_step(s: MazeStep) -> None:
        steps.append(s)

    gen: MazeGenerator = MazeGenerator(
        width=10,
        height=7,
        entry_c=(0, 0),
        exit_c=(9, 6),
        perfect=True,
        seed=1,
        include_42=True
    )
    maze = gen.generate(step_callback=on_step, step_every=5)

    assert maze.width == 10
    assert len(steps) > 0
    assert steps[-1].kind == "done"
