import sys
# from typing import NoReturn
from src.app import parse_config


def main() -> None:
    """Main entry point for the A-Maze-ing application."""
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 a_maze_ing.py config.txt\n")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = parse_config(config_path)
        # Then pass to Developer A's generator
    except Exception as e:
        sys.stderr.write(f"Configuration Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
