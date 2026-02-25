This project has been created as part of the 42 curriculum by acaire-d and mario.
# A-maze-ing
Repository for my team's A-maze-ing project



## Technical Documentation: Project "A-Maze-ing"

### ANAIS
### 1. The Build System (Makefile & Linker Logic)

The most challenging part of the setup was bridging a C library (MiniLibX) with Python. 

* **The `-fPIC` Requirement:** Python's `ctypes` requires a Shared Object (`.so`). Standard MLX compiles to a static library (`.a`). We had to inject the `-fPIC` (Position Independent Code) flag into the MLX Makefile to allow the code to be relocated in memory when loaded by Python.
* **The Linker Wrapper:** Since MLX doesn't natively produce a `.so` on Linux, we implemented a custom `gcc` command that packs the static `libmlx.a` and its X11 dependencies (`-lX11`, `-lXext`, `-lm`) into a single shared library.


### 2. Rendering Engine: Double Buffering chanllenge

To eliminate the flickering we experienced early on, we shifted from direct-to-window drawing to **Double Buffering**.

* **The Image Buffer:** Instead of calling `mlx_pixel_put` (which communicates with the X-Server for every single pixel), we allocate a raw memory block in RAM using `mlx_new_image`.
* **Memory Manipulation:** We use `ctypes.c_uint32.from_address` to write hex color values directly into this memory block.
* **Formula:** `offset = (y * win_width * 4) + (x * 4)`. This calculates the exact byte address for a pixel in a 32-bit (4-byte) BGRA color space.

* **The Frame Push:** Once the entire frame (walls, path, and motif) is "painted" in RAM, we call `mlx_put_image_to_window` once. This provides the smooth, flicker-free animation we achieved.


### 3. Responsive UI & Scaling

A major "Aha!" moment was making the maze fit regardless of its size.

* **Adaptive Tile Size:** The project calculates `tile_size` based on `min(MAX_WINDOW_W / maze_width, MAX_WINDOW_H / maze_height)`.
* **Centering Offset:** If a maze is too small (e.g., $5 \times 5$), we calculate an `offset_x` to center the maze in the window. This ensures the window is always wide enough (minimum 450px) to show the "X" button and the full legend.


### 5. Interaction & State Management

The application uses an event-driven model via `mlx_hook` and `mlx_loop_hook`.

| Key           | Action    | Technical Logic                                                                   |
| **ESC / [X]** | Close     | Cleanly destroys the window/display and calls `os._exit(0)` to prevent Segfaults. |
| **P (Path)**  | Toggle    | Triggers the A* or BFS solver and starts the `path_step` incrementer.             |
| **R (Regen)** | Reset     | Generates a new maze and resets the animation counter to 0.                       |
| **C (Color)** | Randomize | Re-calculates global `wall_color` and `path_color` variables.                     |
