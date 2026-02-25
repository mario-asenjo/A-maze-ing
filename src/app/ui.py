import ctypes
import random
from src.app.config_parser import Config
from src.app.mlx_wrapper import MLXWrapper
from typing import Any
from src.mazegen.generator import MazeGenerator
from src.mazegen.maze import has_wall


class MazeApp:
    def __init__(self, gen: MazeGenerator, config: Config) -> None:
        self.wrapper = MLXWrapper()
        self.mlx_ptr = self.wrapper.init()

        # 1. Calculate dynamic tile size to stay within screen limits
        # We assume 1200x800 as maximum window size
        MAX_W, MAX_H = 1200, 800
        MIN_W = 500
        ui_height = 64
        # 2. Calculate Tile Size
        tile_w = MAX_W // config["width"]
        tile_h = (MAX_H - ui_height) // config["height"]
        self.tile_size = max(4, min(tile_w, tile_h, 32))

        # 3. Calculate Final Dimensions
        maze_pixel_w = config["width"] * self.tile_size

        # The window width is either the maze width
        # OR the minimum required for the UI
        self.win_width = max(maze_pixel_w, MIN_W)
        self.win_height = (config["height"] * self.tile_size) + ui_height

        # Calculate Offset to center the maze
        # if the window is wider than the maze
        self.offset_x = (self.win_width - maze_pixel_w) // 2

        self.win_ptr = self.wrapper.new_window(
            self.mlx_ptr, self.win_width, self.win_height, "A-Maze-ing"
        )

        # 3. Setup Buffer for these exact dimensions == to draw in RAM
        self.img_ptr = self.wrapper.lib.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height
        )
        self.img_data = self.wrapper.lib.mlx_get_data_addr(
            self.img_ptr,
            ctypes.byref(ctypes.c_int()),
            ctypes.byref(ctypes.c_int()),
            ctypes.byref(ctypes.c_int())
        )

        self.gen = gen
        self.maze = gen.generate()
        self.show_path = False
        self.path_step = 0
        self.wall_color = 0xFFFFFF
        self.path_color = 0xFFFFFF

    def _put_pixel_to_img(self, x: int, y: int, color: int) -> None:
        """Writes a pixel directly to the image buffer memory."""
        if 0 <= x < self.win_width and 0 <= y < self.win_height:
            # Calculate memory offset:
            # (y * line_length) + (x * bits_per_pixel / 8)
            # For most Linux systems, it's 4 bytes per pixel (BGRA)
            offset = (y * self.win_width * 4) + (x * 4)
            ctypes.c_uint32.from_address(self.img_data + offset).value = color

    def _draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draws a line between two points (horizontal or vertical)."""
        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self._put_pixel_to_img(x1, y, self.wall_color)
        elif y1 == y2:  # Horizontal line
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self._put_pixel_to_img(x, y1, self.wall_color)

    def _draw_rect(self, coord: tuple[int, int], color: int) -> None:
        """Fills a tile with a specific color (used for Entry/Exit/42)."""
        x_start, y_start = coord[0] * self.tile_size, coord[1] * self.tile_size
        for y in range(y_start, y_start + self.tile_size):
            for x in range(x_start, x_start + self.tile_size):
                self._put_pixel_to_img(x, y, color)

    def _change_colors(self) -> None:
        """Generates high-contrast colors for walls and the path."""
        # Bright Neon Wall Color
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        self.wall_color = (r << 16) | (g << 8) | b

        # Bright Path Color (Different from walls)
        pr = random.randint(150, 255)
        pg = random.randint(150, 255)
        pb = 50  # Keep blue low to make it look yellow/orange/pink
        self.path_color = (pr << 16) | (pg << 8) | pb

    def _draw_path_node(self, coord: tuple[int, int], color: int) -> None:
        x_center = coord[0] * self.tile_size + (self.tile_size // 2)
        y_center = coord[1] * self.tile_size + (self.tile_size // 2)

        # Draw a 4x4 pixel square at the center
        for i in range(-2, 3):
            for j in range(-2, 3):
                self._put_pixel_to_img(x_center + i, y_center + j, color)

    def _draw_rect_at(self,
                      cell_x: int, cell_y: int, size: int, color: int) -> None:
        # DEBUG: See if these numbers look right in your terminal
        print(f"Drawing path at: {cell_x}, {cell_y} with color {hex(color)}")
        center_x = (cell_x * self.tile_size) + (self.tile_size // 2)
        center_y = (cell_y * self.tile_size) + (self.tile_size // 2)

        start_x = center_x - (size // 2)
        start_y = center_y - (size // 2)

        for y in range(start_y, start_y + size):
            for x in range(start_x, start_x + size):
                self._put_pixel_to_img(x, y, color)

    def _draw_legend_background(self) -> None:
        """Draws a professional UI panel with status indicators."""
        maze_bottom = self.maze.height * self.tile_size
        panel_height = 64

        # 1. DRAW THE PANEL BACKGROUND
        # Filling the bottom area with a subtle charcoal grey
        for y in range(maze_bottom, maze_bottom + panel_height):
            for x in range(self.maze.width * self.tile_size):
                self._put_pixel_to_img(x, y, 0x1A1A1A)

        # 2. DRAW THE SEPARATOR BORDER
        # A thin line to separate the maze from the menu
        for x in range(self.maze.width * self.tile_size):
            self._put_pixel_to_img(x, maze_bottom, 0x444444)

    def _draw_legend_text(self) -> None:
        """Puts the actual text strings on top of the rendered image."""
        maze_bottom = self.maze.height * self.tile_size
        white, grey = 0xFFFFFF, 0x888888
        y_text = maze_bottom + 25

        # Status logic
        path_status = b"ON" if self.show_path else b"OFF"
        path_color = 0x00FF00 if self.show_path else 0xFF0000

        # Render Columns
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 20, y_text, white, b"ESC -> EXIT"
        )
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 20, y_text + 20, white, b"R   -> REGEN"
        )

        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 160, y_text, white, b"C   -> COLOR"
        )
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 160, y_text + 20, white, b"P   -> PATH"
        )

        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 320, y_text, grey, b"PATH:"
        )
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 380, y_text, path_color, path_status
        )

        size_info = f"SIZE: {self.maze.width}x{self.maze.height}".encode()
        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 320, y_text + 20, grey, size_info
        )

    def render(self) -> None:
        """Draw the walls, entry, exit, and path to the window."""
        # clear the buffer and not the window
        ctypes.memset(self.img_data, 0, self.win_width * self.win_height * 4)
        # 1. Draw Entry/Exit
        self._draw_rect(self.maze.entry, 0x00FF00)  # Green
        self._draw_rect(self.maze.exit, 0xFF0000)  # Red

        # 3. Draw Walls in the buffer
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
            path_str = self.gen.solve(self.maze)
            curr_x, curr_y = self.maze.entry
            deltas = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

            # Only draw up to the current animation step
            for i in range(min(self.path_step, len(path_str))):
                move = path_str[i]
                dx, dy = deltas[move]
                curr_x += dx
                curr_y += dy
                dot_size = max(2, self.tile_size // 3)
                self._draw_rect_at(curr_x, curr_y, dot_size, self.path_color)

            # to stop at the end
            if self.path_step < len(path_str):
                self.path_step += 1

        self._draw_legend_background()
        # push the finished image to the window. (one frame at a time)
        self.wrapper.lib.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                                 self.img_ptr, 0, 0)
        self._draw_legend_text()

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
            self.show_path = False  # Hide the path
            self.path_step = 0
        elif keycode == 112:  # 'P' - Toggle Path
            self.show_path = not self.show_path
            print(f"Path toggled: {'ON' if self.show_path else 'OFF'}")
            self.path_step = 0  # Reset animation
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

        # NEW: The Loop Hook (Animation)
        # We create a simple wrapper that just calls render
        loop_callback_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

        def _loop_cb(_arg: object) -> int:
            self.render()
            return 0

        self._loop_callback = loop_callback_type(_loop_cb)

        self.wrapper.lib.mlx_loop_hook(self.mlx_ptr, self._loop_callback, None)

        self.render()
        self.wrapper.lib.mlx_loop(self.mlx_ptr)
