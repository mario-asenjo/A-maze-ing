from __future__ import annotations

from src.mazegen.events import MazeStep
from src.mazegen.generator import MazeGenerator


def on_step(s: MazeStep) -> None:
    if s.kind in ("carve", "loop_open"):
        print(f"{s.kind}: {s.a} -> {s.b} (visited={s.visited})")
    else:
        print(f"{s.kind} (visited={s.visited})")

if __name__ == "__main__":
    gen = MazeGenerator(
        width=20,
        height=12,
        entry_c=(0, 0),
        exit_c=(19, 11),
        perfect=True,
        seed=7,
        include_42=True
    )
    gen.generate(step_callback=on_step, step_every=1)
