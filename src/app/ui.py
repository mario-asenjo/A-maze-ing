import ctypes
from src.app.mlx_wrapper import MLXWrapper
from typing import Any
from src.mazegen.generator import MazeGenerator
from src.mazegen.maze import Maze, has_wall


class MazeApp:
    def __init__(self, gen: MazeGenerator, config: dict[str, Any]) -> None:
        self.wrapper = MLXWrapper()
        self.mlx_ptr = self.wrapper.init()
        
        if not self.mlx_ptr:
            # Handle error gracefully per mandatory part [cite: 116]
            raise RuntimeError("Could not initialize MiniLibX. Is your DISPLAY set?")

        self.tile_size = 32
        self.show_path = False
        self.wall_color = 0xFFFFFF
            
        self.win_ptr = self.wrapper.new_window(
            self.mlx_ptr, 
            config["width"] * 32, 
            config["height"] * 32, 
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

    def render(self) -> None:
        """Draw the walls, entry, exit, and path to the window."""
        self.wrapper.lib.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell_walls = self.maze.walls[y][x]
                px, py = x * self.tile_size, y * self.tile_size
                
                # Draw Walls based on bits: N(1), E(2), S(4), W(8)
                if has_wall(cell_walls, "N"):
                    self._draw_line(px, py, px + self.tile_size, py)
                if has_wall(cell_walls, "E"):
                    self._draw_line(
                        px + self.tile_size,
                        py, px + self.tile_size, py + self.tile_size)
                # ... repeat for S and W ...

        # Highlight Entry (Green) and Exit (Red) 
        self._draw_rect(self.maze.entry, 0x00FF00)
        self._draw_rect(self.maze.exit, 0xFF0000)

    def handle_key(self, keycode: int) -> None:
        """Handle mandatory interactions."""
        if keycode == 53:  # ESC
            exit(0)
        elif keycode == 15:  # 'R' - Regenerate 
            self.maze = self.gen.generate()
        elif keycode == 35:  # 'P' - Toggle Path 
            self.show_path = not self.show_path
        elif keycode == 8:  # 'C' - Change Colors 
            self.wall_color = 0x0000FF  # Cycle logic here
        
        self.render()

    def run(self) -> None:
            """
            Starts the event loop.
            Uses CFUNCTYPE to pass a valid function pointer to C.
            """
            # Define the C callback: int func(int keycode, void *param)
            key_callback_type = ctypes.CFUNCTYPE(
                ctypes.c_int, ctypes.c_int, ctypes.c_void_p
            )
            # Store the callback in an attribute to prevent Garbage Collection
            self._key_callback = key_callback_type(self.handle_key)

            # Pass the callback: (window_ptr, function_ptr, param_ptr)
            self.wrapper.lib.mlx_key_hook(
                self.win_ptr, self._key_callback, None
            )
            
            self.render()
            self.wrapper.lib.mlx_loop(self.mlx_ptr)
