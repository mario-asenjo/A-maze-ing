import ctypes
import random
from src.app.config_parser import Config
from src.app.mlx_wrapper import MLXWrapper
from typing import Any
from mazegen import MazeStep
from mazegen import MazeGenerator
from mazegen import has_wall, ALL_WALLS, set_wall_between


# 1200x800 = maximum window size
MAX_W, MAX_H = 1200, 1200
MIN_W = 500


class MazeApp:
    def __init__(self, gen: MazeGenerator, config: Config) -> None:
        self.wrapper = MLXWrapper()
        self.mlx_ptr = self.wrapper.init()

        # 1. Calculate dynamic tile size to stay within screen limits
        ui_height = 64
        # 2. Calculate Tile Size
        tile_w = MAX_W // config["width"]
        tile_h = (MAX_H - ui_height) // config["height"]
        self.tile_size = max(4, min(tile_w, tile_h, 32))

        # 3. Calculate Final Dimensions
        maze_pixel_w = config["width"] * self.tile_size

        # The window width is either the maze width
        # OR the minimum required for the UI
        self.win_width = max(maze_pixel_w + 2, MIN_W)
        self.win_height = (config["height"] * self.tile_size) + ui_height

        # Calculate Offset to center the maze
        self.offset_x = (self.win_width - maze_pixel_w) // 2

        self.win_ptr = self.wrapper.new_window(
            self.mlx_ptr, self.win_width, self.win_height, "A-Maze-ing"
        )

        # Setup Buffer = where image object wil be held
        self.img_ptr = self.wrapper.lib.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height
        )

        # starting mem adress where pixels begins
        self.bits_per_pixel = ctypes.c_int()
        self.size_line = ctypes.c_int()
        self.endian = ctypes.c_int()

        self.img_data = self.wrapper.lib.mlx_get_data_addr(
            self.img_ptr,
            ctypes.byref(self.bits_per_pixel),
            ctypes.byref(self.size_line),
            ctypes.byref(self.endian)
        )

        self.gen = gen
        self.maze = gen.generate()
        # Animation to generate
        self.anim_walls = [row[:] for row in self.maze.walls]
        self.gen_steps: list[MazeStep] = []
        self.gen_step_idx = 0
        self.is_generating = False

        self.show_path = False
        self.path_status_msg = b""
        self.path_status_color = 0x888888
        self.path_str = ""
        self.path_step = 0
        self.wall_color = 0xFFFFFF
        self.path_color = 0xFFFFFF
        self.logo_color = 0xFFD700

        # 42 not made warning
        if self.gen.last_warnings:
            print(self.gen.last_warnings[-1])

    def _start_generation_animation(self) -> None:
        """
        Generate a maze while recording step deltas for animated playback.
        """
        steps: list[MazeStep] = []

        def _on_step(step: MazeStep) -> None:
            steps.append(step)

        self.maze = self.gen.generate(step_callback=_on_step, step_every=1)
        self.gen_steps = steps
        self.gen_step_idx = 0
        self.is_generating = True
        self.show_path = False
        self.path_step = 0

        self.anim_walls = [
            [ALL_WALLS for _ in range(self.maze.width)]
            for _ in range(self.maze.height)
        ]

    def _advance_generation_animation(self) -> None:
        """Apply one generation delta per frame."""
        if not self.is_generating:
            return

        if self.gen_step_idx >= len(self.gen_steps):
            self.is_generating = False
            self.anim_walls = [row[:] for row in self.maze.walls]
            return

        step = self.gen_steps[self.gen_step_idx]
        self.gen_step_idx += 1

        if step.kind in ("carve", "loop_open") and step.a and step.b:
            set_wall_between(self.anim_walls, step.a, step.b, closed=False)

    def _put_pixel_to_img(self, x: int, y: int, color: int) -> None:
        """Writes a pixel directly to the image buffer memory."""
        if 0 <= x < self.win_width and 0 <= y < self.win_height:
            # Calculate memory offset between each pixel
            bytes_per_pixel = self.bits_per_pixel.value // 8
            offset = y * self.size_line.value + x * bytes_per_pixel
            # point to that place in memory and add the color
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
        """
        Fills a tile with a specific color (used for Entry/Exit/42).
        """
        x_start = self.offset_x + coord[0] * self.tile_size
        y_start = coord[1] * self.tile_size
        for y in range(y_start, y_start + self.tile_size):
            for x in range(x_start, x_start + self.tile_size):
                self._put_pixel_to_img(x, y, color)

    def _change_colors(self) -> None:
        """Generates high-contrast colors for walls and the path."""
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        self.wall_color = (r << 16) | (g << 8) | b

        pr = random.randint(150, 255)
        pg = random.randint(150, 255)
        pb = 50  # Keep blue low to make it look yellow/orange/pink
        self.path_color = (pr << 16) | (pg << 8) | pb

        lr = random.randint(150, 255)
        lg = random.randint(150, 255)
        lb = random.randint(150, 255)
        self.logo_color = (lr << 16) | (lg << 8) | lb

    def _draw_path_node(self, coord: tuple[int, int], color: int) -> None:
        x_center = (
            self.offset_x + coord[0] * self.tile_size + (self.tile_size // 2)
        )
        y_center = coord[1] * self.tile_size + (self.tile_size // 2)

        # Draw a 4x4 pixel square at the center
        for i in range(-2, 3):
            for j in range(-2, 3):
                self._put_pixel_to_img(x_center + i, y_center + j, color)

    def _draw_rect_at(self,
                      cell_x: int, cell_y: int, size: int, color: int) -> None:
        center_x = (
            self.offset_x + (cell_x * self.tile_size) + (self.tile_size // 2)
        )
        center_y = (cell_y * self.tile_size) + (self.tile_size // 2)

        start_x = center_x - (size // 2)
        start_y = center_y - (size // 2)

        for y in range(start_y, start_y + size):
            for x in range(start_x, start_x + size):
                self._put_pixel_to_img(x, y, color)

    def _draw_legend_background(self) -> None:
        """Draws a UI panel with status indicators."""
        maze_bottom = self.maze.height * self.tile_size
        panel_height = 64

        # 1. DRAW THE PANEL BACKGROUND
        for y in range(maze_bottom, maze_bottom + panel_height):
            for x in range(self.maze.width * self.tile_size):
                self._put_pixel_to_img(x, y, 0x1A1A1A)

        # 2. DRAW THE SEPARATOR BORDER
        panel_end_x = self.offset_x + self.maze.width * self.tile_size
        for x in range(self.offset_x, panel_end_x):
            self._put_pixel_to_img(x, maze_bottom, 0x444444)

    def _draw_legend_text(self) -> None:
        """Puts the actual text strings on top of the rendered image."""
        maze_bottom = self.maze.height * self.tile_size
        white, grey = 0xFFFFFF, 0x888888
        y_text = maze_bottom + 25

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
            self.mlx_ptr, self.win_ptr, 500, y_text, white, b"G   -> ANIMATE"
        )

        self.wrapper.lib.mlx_string_put(
            self.mlx_ptr, self.win_ptr, 320, y_text,
            self.path_status_color, self.path_status_msg
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
        self._draw_rect(self.maze.entry, 0x00FF00)
        self._draw_rect(self.maze.exit, 0xFF0000)

        # 2 draw outer walls
        maze_x0 = self.offset_x
        maze_x1 = self.offset_x + self.maze.width * self.tile_size - 1
        maze_y0 = 0
        maze_y1 = self.maze.height * self.tile_size - 1

        # left/right
        for y in range(maze_y0, maze_y1 + 1):
            self._put_pixel_to_img(maze_x0, y, self.wall_color)
            self._put_pixel_to_img(maze_x1, y, self.wall_color)

        # top/bottom
        for x in range(maze_x0, maze_x1 + 1):
            self._put_pixel_to_img(x, maze_y0, self.wall_color)
            self._put_pixel_to_img(x, maze_y1, self.wall_color)

        # 3. Draw Walls in the buffer
        walls_to_draw = (
            self.anim_walls if self.is_generating else self.maze.walls
        )
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if (x, y) in self.maze.closed:
                    self._draw_rect((x, y), self.logo_color)
                cell_walls = walls_to_draw[y][x]
                px, py = self.offset_x + x * self.tile_size, y * self.tile_size

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
            curr_x, curr_y = self.maze.entry
            deltas = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

            for i in range(min(self.path_step, len(self.path_str))):
                move = self.path_str[i]
                dx, dy = deltas[move]
                curr_x += dx
                curr_y += dy
                dot_size = max(2, self.tile_size // 3)
                self._draw_rect_at(curr_x, curr_y, dot_size, self.path_color)

            if self.path_step < len(self.path_str):
                self.path_step += 1
            elif self.path_status_msg != b"PATH: SUCCESS":
                self.path_status_msg = b"PATH: SUCCESS"
                self.path_status_color = 0x00FF00
        self._draw_legend_background()
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
            import os
            os._exit(0)
        elif keycode == 114:  # 'R' - Regenerate
            self.maze = self.gen.generate()
            self.anim_walls = [row[:] for row in self.maze.walls]
            self.gen_steps = []
            self.gen_step_idx = 0
            self.is_generating = False
            self.show_path = False
            self.path_step = 0
        elif keycode in (103, 71):  # 'g' or 'G' - Animated generation
            self._start_generation_animation()
        elif keycode == 112:  # 'P' - Toggle Path
            self.show_path = not self.show_path
            print(f"Path toggled: {'ON' if self.show_path else 'OFF'}")
            self.path_step = 0  # Reset animation
            if self.show_path:
                self.path_str = self.gen.solve(self.maze)
                self.path_status_msg = b"PATH: RUNNING"
                self.path_status_color = 0xFFD700
            else:
                self.path_status_msg = b"PATH: OFF"
                self.path_status_color = 0x888888
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
        self.wrapper.lib.mlx_hook(
            self.win_ptr, 17, 0, self._key_callback, None
        )

        # wrapper that calls render for animation
        loop_callback_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

        def _loop_cb(_arg: object) -> int:
            self._advance_generation_animation()
            self.render()
            return 0

        self._loop_callback = loop_callback_type(_loop_cb)

        self.wrapper.lib.mlx_loop_hook(self.mlx_ptr, self._loop_callback, None)

        self.render()
        self.wrapper.lib.mlx_loop(self.mlx_ptr)
