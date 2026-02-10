import curses
from typing import Any
from src.mazegen.generator import MazeGenerator
from src.mazegen.errors import MazeGenerationError
from src.mazegen.maze import Maze, has_wall


def render_maze_to_buffer(maze: Maze, show_path: bool, path_str: str = "") -> list[str]:
    """
    Converts the maze data into a list of strings for curses display.
    
    Each cell is represented by a 3x3 character area:
    - Center: ' ' (Path) or '.' (Shortest Path)
    - Edges: '|', '-', or '+' for walls [cite: 191]
    """
    # Create a buffer with spaces (3 characters per cell width/height)
    buf_height = maze.height * 2 + 1
    buf_width = maze.width * 2 + 1
    buffer = [[" " for _ in range(buf_width)] for _ in range(buf_height)]

    # Draw the structural grid
    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.walls[y][x]
            by, bx = y * 2 + 1, x * 2 + 1
            
            # Place corner joints
            buffer[by-1][bx-1] = "+"
            buffer[by-1][bx+1] = "+"
            buffer[by+1][bx-1] = "+"
            buffer[by+1][bx+1] = "+"

            # Draw walls if bits are set [cite: 148, 151]
            if has_wall(cell, "N"): buffer[by-1][bx] = "-"
            if has_wall(cell, "S"): buffer[by+1][bx] = "-"
            if has_wall(cell, "W"): buffer[by][bx-1] = "|"
            if has_wall(cell, "E"): buffer[by][bx+1] = "|"
            
            # Special highlighting for "42" pattern cells [cite: 140, 196]
            if (x, y) in maze.closed:
                buffer[by][bx] = "X"

    # Overlay shortest path if requested [cite: 194]
    if show_path and path_str:
        curr_x, curr_y = maze.entry
        buffer[curr_y * 2 + 1][curr_x * 2 + 1] = "."
        
        dirs = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        for step in path_str:
            dx, dy = dirs[step]
            # Mark the wall we passed through
            buffer[curr_y * 2 + 1 + dy][curr_x * 2 + 1 + dx] = "."
            curr_x, curr_y = curr_x + dx, curr_y + dy
            # Mark the next cell
            buffer[curr_y * 2 + 1][curr_x * 2 + 1] = "."

    return ["".join(row) for row in buffer]


def start_ui(gen: MazeGenerator, config: dict[str, Any]) -> None:
    """Initialize curses and start the main interaction loop."""
    curses.wrapper(lambda stdscr: ui_loop(stdscr, gen, config))
    # lambda makes a one argument function take more arguments (3 here)


def ui_loop(
        stdscr: curses.window,
        gen: MazeGenerator,
        config: dict[str, Any]) -> None:
    """Main UI event loop."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)  # Walls
    curses.init_pair(2, curses.COLOR_CYAN, -1)   # Path
    curses.curs_set(0)  # Hide cursor

    # Initial generation
    maze = gen.generate()
    if gen.last_warnings:
        raise MazeGenerationError
    show_path = False

    while True:
        stdscr.clear()

        # UI requirements:
        # 1. Display Maze
        # 2. Toggle Shortest Path
        # 3. Re-generate
        # 4. Color rotation
        
        stdscr.addstr(0, 0, "A-MAZE-ING (v1.0) - Press 'q' to quit")
        stdscr.addstr(1, 0, f"Size: {config['width']}x{config['height']} |"
                      f" 'r': Regenerate | 'p': Toggle Path")
        
        # Inside your while True loop in ui_loop:
        path_string = gen.solve(maze) if show_path else ""
        maze_lines = render_maze_to_buffer(maze, show_path, path_string)

        for i, line in enumerate(maze_lines):
            # Ensure we don't draw outside terminal bounds
            if i + 3 < curses.LINES:
                stdscr.addstr(i + 3, 2, line)
                
        stdscr.refresh()
        key = stdscr.getch()
        # Handle mandatory interaction: Color Rotation [cite: 195]
        if key == ord('c'):
            # Logic to cycle through curses.init_pair values
            pass
        if key == ord('q'):
            break
        elif key == ord('r'):
            maze = gen.generate()
        elif key == ord('p'):
            show_path = not show_path
