import sys
from src.app import parse_config
from src.app.ui import MazeApp
from src.mazegen.generator import MazeGenerator
from src.mazegen.errors import MazeError


def main() -> None:
    """Main entry point for the A-Maze-ing application."""
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 a_maze_ing.py config.txt\n")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = parse_config(config_path)
        gen = MazeGenerator(
            width=config["width"],
            height=config["height"],
            entry_c=config["entry"],
            exit_c=config["exit"],
            perfect=config["perfect"]
        )
        app = MazeApp(gen, config)
        app.run()
    except MazeError as e:
        sys.stderr.write(f"Maze error: {e}\n")
        sys.exit(1)
    except RuntimeError as e:
        # Handles MLX initialization or wrapper failures
        sys.stderr.write(f"Runtime Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Configuration Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
