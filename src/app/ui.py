import ctypes
import random
from src.app.config_parser import Config
from src.app.mlx_wrapper import MLXWrapper
from typing import Any
from src.mazegen.generator import MazeGenerator
from src.mazegen.maze import has_wall

# makefile minilibx inside make install
# bigger needs to fin in screen
# 42 in a different color
# move the screen a keep seeing maze
# add output file


class MazeApp:
    def __init__(self, gen: MazeGenerator, config: Config) -> None:
        self.wrapper = MLXWrapper()
        self.mlx_ptr = self.wrapper.init()

        if not self.mlx_ptr:
            raise RuntimeError(
                "Could not initialize MiniLibX. Is your DISPLAY set?")

        self.tile_size = 32
        self.show_path = False
        self.wall_color = 0xFFFFFF
        self.path_color = 0xFFFFFF
        ui_height = 64
        self.win_ptr = self.wrapper.new_window(
            self.mlx_ptr,
            config["width"] * 32,
            (config["height"] * 32) + ui_height,
            "A-Maze-ing"
        )
        self.gen = gen
        self.maze = gen.generate()

    def _draw_pixel(self, x: int, y: int, color: int) -> None:
        """Draws a single pixel using the MLX wrapper."""
        self.wrapper.lib.mlx_pixel_put(self.mlx_ptr, self.win_ptr, x, y, color)

    def _draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draws a line between two points (horizontal or vertical)."""
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self._draw_pixel(x1, y, self.wall_color)
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self._draw_pixel(x, y1, self.wall_color)

    def _draw_rect(self, coord: tuple[int, int], color: int) -> None:
        """Fills a tile with a specific color (used for Entry/Exit/42)."""
        x_start, y_start = coord[0] * self.tile_size, coord[1] * self.tile_size
        for y in range(y_start + 1, y_start + self.tile_size):
            for x in range(x_start + 1, x_start + self.tile_size):
                self._draw_pixel(x, y, color)

    def _change_colors(self) -> None:
        """Generates random color for walls for the path."""
        # Generate a bright random color: 0xRRGGBB
        self.wall_color = random.getrandbits(24) | 0x444444
        self.path_color = random.getrandbits(24) | 0x888888

    def _draw_path_node(self, coord: tuple[int, int], color: int) -> None:
        x_center = coord[0] * self.tile_size + (self.tile_size // 2)
        y_center = coord[1] * self.tile_size + (self.tile_size // 2)

        # Draw a 4x4 pixel square at the center
        for i in range(-2, 3):
            for j in range(-2, 3):
                self._draw_pixel(x_center + i, y_center + j, color)

    def _draw_rect_at(self,
                      cell_x: int, cell_y: int, size: int, color: int) -> None:
        # DEBUG: See if these numbers look right in your terminal
        print(f"Drawing path at: {cell_x}, {cell_y} with color {hex(color)}")

        # Calculate top-left corner of the path "dot"
        # This centers a 10x10 square inside a 32x32 cell
        start_x = (cell_x * self.tile_size)
        + (self.tile_size // 2) - (size // 2)
        start_y = (cell_y * self.tile_size)
        + (self.tile_size // 2) - (size // 2)

        for y in range(start_y, start_y + size):
            for x in range(start_x, start_x + size):
                self.wrapper.lib.mlx_pixel_put(
                    self.mlx_ptr, self.win_ptr, x, y, color)

    def _draw_legend(self) -> None:
        """Draws a professional UI panel with status indicators."""
        maze_bottom = self.maze.height * self.tile_size
        panel_height = 64

        # 1. DRAW THE PANEL BACKGROUND
        # Filling the bottom area with a subtle charcoal grey
        for y in range(maze_bottom, maze_bottom + panel_height):
            for x in range(self.maze.width * self.tile_size):
                self.wrapper.lib.mlx_pixel_put(
                    self.mlx_ptr,
                    self.win_ptr, x, y, 0x1A1A1A)

        # 2. DRAW THE SEPARATOR BORDER
        # A thin line to separate the maze from the menu
        for x in range(self.maze.width * self.tile_size):
            self.wrapper.lib.mlx_pixel_put(
                self.mlx_ptr, self.win_ptr, x, maze_bottom, 0x444444)

        # 3. DEFINE COLORS AND TEXT
        white = 0xFFFFFF
        grey = 0x888888
        y_text = maze_bottom + 25

        # Status Logic
        path_status = b"ON" if self.show_path else b"OFF"
        path_color = 0x00FF00 if self.show_path else 0xFF0000

        # 4. RENDER COLUMNS
        # Column 1: Navigation
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 20, y_text, white, b"ESC -> EXIT")
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 20, y_text + 20, white,
            b"R   -> REGEN")

        # Column 2: Visuals
        self.wrapper.lib.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        160, y_text, white, b"C   -> COLOR")
        self.wrapper.lib.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        160, y_text + 20,
                                        white, b"P   -> PATH")

        # Column 3: Live Stats
        self.wrapper.lib.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        320, y_text, grey, b"PATH:")
        self.wrapper.lib.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        380, y_text, path_color, path_status)

        size_info = f"SIZE: {self.maze.width}x{self.maze.height}".encode()
        self.wrapper.lib.mlx_string_put(self.mlx_ptr, self.win_ptr, 320,
                                        y_text + 20, grey, size_info)

    def render(self) -> None:
        """Draw the walls, entry, exit, and path to the window."""
        self.wrapper.lib.mlx_clear_window(self.mlx_ptr, self.win_ptr)

        # 1. Draw Walls
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell_walls = self.maze.walls[y][x]
                px, py = x * self.tile_size, y * self.tile_size

                if has_wall(cell_walls, "N"):
                    self._draw_line(px, py, px + self.tile_size, py)
                if has_wall(cell_walls, "E"):
                    self._draw_line(
                        px + self.tile_size,
                        py, px + self.tile_size,
                        py + self.tile_size)
                if has_wall(cell_walls, "S"):
                    self._draw_line(px,
                                    py + self.tile_size,
                                    px + self.tile_size,
                                    py + self.tile_size)
                if has_wall(cell_walls, "W"):
                    self._draw_line(px, py, px, py + self.tile_size)

        # 2. Draw Path (if enabled)
        if self.show_path:
            # path_str is something like "NNESW"
            path_str = self.gen.solve(self.maze)

            # Start at the beginning
            curr_x, curr_y = self.maze.entry

            # Map for the walking logic (Mirroring your generator's DELTAS)
            deltas = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

            # Draw the first dot at entry
            self._draw_rect_at(curr_x, curr_y, 10, self.path_color)

            for move in path_str:
                dx, dy = deltas[move]
                curr_x += dx
                curr_y += dy
                # Draw a dot for every step we take
                self._draw_rect_at(curr_x, curr_y, 10, self.path_color)

        # 3. Draw Entry/Exit LAST so they are on top
        self._draw_rect(self.maze.entry, 0x00FF00)  # Green
        self._draw_rect(self.maze.exit, 0xFF0000)  # Red
        self._draw_legend()

    def handle_key(self, keycode: int, param: Any) -> int:
        """Handle mandatory interactions."""
        print(f"Key pressed: {keycode}")
        if keycode == 65307 or keycode == 0:  # ESC or "X" button click
            print("Closing window and cleaning up resources...")
            if self.win_ptr:
                self.wrapper.lib.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
                self.win_ptr = None
            if self.mlx_ptr:
                self.wrapper.lib.mlx_destroy_display(self.mlx_ptr)
            # this is to avoid seg fault by IMMIDETELY exiting instead
            # of returning to the event loop
            import os
            os._exit(0)
        elif keycode == 114:  # 'R' - Regenerate
            self.maze = self.gen.generate()
        elif keycode == 112:  # 'P' - Toggle Path
            self.show_path = not self.show_path
            print(f"Path toggled: {'ON' if self.show_path else 'OFF'}")
        elif keycode == 99:  # 'C' - Change Colors
            self._change_colors()
        self.render()
        return (0)

    def run(self) -> None:
        """
        Starts the event loop.
        Uses CFUNCTYPE to pass a valid function pointer to C.
        """
        output_content = self.gen.build_output_sections(self.gen.generate())
        # print(output_content)
        with open("output_maze.txt", 'w') as f:
            for line in output_content[0]:
                f.write(line + "\n")
            f.write("\n" + output_content[1])
            f.write("\n" + output_content[2])
            f.write("\n" + output_content[3] + "\n")

        key_callback_type = ctypes.CFUNCTYPE(
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p)
        self._key_callback = key_callback_type(self.handle_key)
        # Hook for Keyboard (Event 2)
        self.wrapper.lib.mlx_hook(
            self.win_ptr, 2, 1, self._key_callback, None
        )

        # Hook for the "X" Close Button (Event 17)
        # We use the same callback function;
        # the keycode passed will be different
        self.wrapper.lib.mlx_hook(
            self.win_ptr, 17, 0, self._key_callback, None
        )
        self.render()
        self.wrapper.lib.mlx_loop(self.mlx_ptr)
