from typing import Literal

from src.mazegen.generator import MazeGenerator

def test_same_seed_same_maze_for_each_algorith() -> None:
    for algo in ["dfs", "prim", "kruskal"]:
        gen_1 = MazeGenerator(
            width=20,
            height=20,
            entry_c=(0, 0),
            exit_c=(19, 19),
            perfect=True,
            seed=7,
            include_42=True,
            algorithm=algo
        )
        gen_2 = MazeGenerator(
            width=20,
            height=20,
            entry_c=(0, 0),
            exit_c=(19, 19),
            perfect=True,
            seed=7,
            include_42=True,
            algorithm=algo
        )
        maze_1 = gen_1.generate()
        maze_2 = gen_2.generate()

        assert maze_1.walls == maze_2.walls


def test_solver_works_for_each_algorith() -> None:
    for algo in ["dfs", "prim", "kruskal"]:
        gen_1 = MazeGenerator(
            width=20,
            height=20,
            entry_c=(0, 0),
            exit_c=(19, 19),
            perfect=True,
            seed=7,
            include_42=True,
            algorithm=algo
        )
        maze_1 = gen_1.generate()
        path = gen_1.solve(maze_1)
        assert len(path) > 0
