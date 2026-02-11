import ctypes
import random
from src.app.mlx_wrapper import MLXWrapper
from typing import Any
from src.mazegen.generator import MazeGenerator
from src.mazegen.maze import Maze, has_wall


class MazeApp:
    def __init__(self, gen: MazeGenerator, config: dict[str, Any]) -> None:
        self.wrapper = MLXWrapper()
        self.mlx_ptr = self.wrapper.init()
        
        if not self.mlx_ptr:
            raise RuntimeError(
                "Could not initialize MiniLibX. Is your DISPLAY set?")

        self.tile_size = 32  # Each cell is 32x32 pixels
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
        """Generates a new random color for walls and a contrasting one for the path."""
        # Generate a bright random color: 0xRRGGBB
        self.wall_color = random.getrandbits(24) | 0x444444  # Ensure it's not too dark
        self.path_color = random.getrandbits(24) | 0x888888

    def _draw_path_node(self, coord: tuple[int, int], color: int) -> None:
        x_center = coord[0] * self.tile_size + (self.tile_size // 2)
        y_center = coord[1] * self.tile_size + (self.tile_size // 2)
        
        # Draw a 4x4 pixel square at the center
        for i in range(-2, 3):
            for j in range(-2, 3):
                self._draw_pixel(x_center + i, y_center + j, color)

    def _draw_rect_at(self, cell_x: int, cell_y: int, size: int, color: int) -> None:
        # DEBUG: See if these numbers look right in your terminal
        print(f"Drawing path at: {cell_x}, {cell_y} with color {hex(color)}")
        
        # Calculate top-left corner of the path "dot"
        # This centers a 10x10 square inside a 32x32 cell
        start_x = (cell_x * self.tile_size) + (self.tile_size // 2) - (size // 2)
        start_y = (cell_y * self.tile_size) + (self.tile_size // 2) - (size // 2)
        
        for y in range(start_y, start_y + size):
            for x in range(start_x, start_x + size):
                self.wrapper.lib.mlx_pixel_put(self.mlx_ptr, self.win_ptr, x, y, color)
    
    def _draw_legend(self) -> None:
        """Draws the control instructions at the bottom of the window."""
        # Calculate the Y position starting after the maze grid
        y_start = (self.maze.height * self.tile_size) + 20
        text_color = 0xFFFFFF  # White text
        
        # Text strings to display
        instructions = [
            "ESC: Quit",
            "C: Random Colors",
            "P: Toggle Path",
            "R: Regenerate Maze"
        ]
        
        # Draw each line of text
        for i, text in enumerate(instructions):
            # We offset each line by 15 pixels vertically
            self.wrapper.lib.mlx_string_put(
                self.mlx_ptr, 
                self.win_ptr, 
                20,                # X position (left margin)
                y_start + (i * 15), # Y position
                text_color, 
                text.encode('utf-8')
            )

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
                    self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size)
                if has_wall(cell_walls, "S"):
                    self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size)
                if has_wall(cell_walls, "W"):
                    self._draw_line(px, py, px, py + self.tile_size)

        if self.show_path:
            solution = self.gen.solve(self.maze)
            if solution:
                for pos_str in solution:
                    # This cleans out (), [], and spaces before splitting
                    clean_str = pos_str.replace('(', '').replace(')', '').replace('[', '').replace(']', '').strip()
                    if ',' in clean_str:
                        parts = clean_str.split(',')
                        x = int(parts[0])
                        y = int(parts[1])
                        self._draw_rect_at(x, y, 12, self.path_color)

        # 3. Draw Entry/Exit LAST so they are on top
        self._draw_rect(self.maze.entry, 0x00FF00) # Green
        self._draw_rect(self.maze.exit, 0xFF0000)  # Red
        self._draw_legend()

    def handle_key(self, keycode: int, param: Any) -> None:
        """Handle mandatory interactions."""
        print(f"Key pressed: {keycode}")
        if keycode == 65307:  # ESC
            print("Cleaning up resources...")
            # 1. Destroy window first
            if self.win_ptr:
                self.wrapper.lib.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
                self.win_ptr = None
            
            # 2. Destroy display
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
        elif keycode == 99:  # 'C' - Change Colors
            self._change_colors()
        self.render()
        return (0)

    def run(self) -> None:
        """
        Starts the event loop.
        Uses CFUNCTYPE to pass a valid function pointer to C.
        """
        # The 3 types here correspond to: (Return Type, Arg1 Type, Arg2 Type)
        key_callback_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
        self._key_callback = key_callback_type(self.handle_key)
        # Store the callback in an attribute to prevent Garbage Collection
        self._key_callback = key_callback_type(self.handle_key)

        self.wrapper.lib.mlx_hook(
            self.win_ptr, 2, 1, self._key_callback, None
        )

        # Pass the callback: (window_ptr, function_ptr, param_ptr)
        self.wrapper.lib.mlx_key_hook(
            self.win_ptr, self._key_callback, None
        )
        self.render()
        self.wrapper.lib.mlx_loop(self.mlx_ptr)
