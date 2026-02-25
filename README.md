*This project has been created as part of the 42 curriculum by acaire-d, MARIO.*

# A-Maze-ing

A robust, graphical maze generator and solver built in Python using the MiniLibX library.

## Description

The goal of this project is to create a deterministic maze generator that produces "perfect" mazes—mazes where any two cells are connected by exactly one path. The application includes a graphical user interface (GUI) to visualize the generation process, an animated solver, and a custom branding feature that integrates a "42" pattern into the maze layout.

## Instructions

### Prerequisites

As this project uses **MiniLibX (Linux)**, ensure you are on a Linux environment with X11 development libraries installed.

### Installation

We use a `Makefile` to automate the setup of the Python virtual environment and the compilation of the MLX shared library:

```bash
make install

```

*Note: This command handles the creation of a `.venv` and builds the `libmlx.so` required for Python to communicate with C.*

### Execution

To run the generator with a configuration file:

```bash
make run

```

To run tests or linting:

```bash
make test
make lint

```

## Config File Structure

The project uses a `config.txt` file (parsed via `pyproject.toml` and internal parsers) with the following format:

* **Width/Height**: Integer dimensions of the maze grid.
* **Entry/Exit**: Coordinates `(x, y)` for the start and end points.
* **Seed**: (Optional) An integer to ensure reproducible maze generation.

## Technical Choices

### Maze Generation Algorithm: Iterative DFS

We chose the **Iterative Depth-First Search (Recursive Backtracker)** algorithm.

* **Why this algorithm?** MARIO
* **Implementation**: MARIO

### Rendering: The Image Buffer Strategy

Instead of drawing pixels one by one to the window, we write directly to raw memory using an **Image Buffer**.

* We calculate a memory **offset** ($offset = (y \times \text{line\_length}) + (x \times 4)$) to locate pixels.
* We use `ctypes.c_uint32.from_address` to write colors instantly to RAM.
* This prevents flickering and allows for smooth animations.

## Reusability

The **`mazegen` package** is entirely decoupled from the UI.

* `generator.py` and `maze.py` can be imported into any other Python project or CLI tool to generate mazes without needing the MiniLibX library.
* The `Maze` dataclass provides a clean interface for any solver or visualizer.

## Resources

* **42 Docs - MiniLibX**: [Getting Started](https://harm-smits.github.io/42docs/libs/minilibx/getting_started.html).
* **Python Ctypes**: [Official Documentation](https://docs.python.org/3/library/ctypes.html).

### Use of AI

AI was utilized as a collaborative peer for the following tasks:

* **Infrastructure**: Assisting in the `Makefile` configuration for 42 school computers.
* **Debugging**: Explaining complex `ctypes` memory mapping and pointer arithmetic.

## Team and Project Management

* **Roles**:
* **Mario**: Core Maze Generation logic and Solver implementation.
* **Anaïs**: UI Architecture, MLX Wrapper, and Memory Buffer rendering.


* **Planning**:
* **Initial**: Simple Windows-based Python script.
* **Evolution**: Pivoted to Linux and MiniLibX to meet 42 curriculum standards and performance requirements.


* **Tools**: GitHub for version control, `mypy` and `flake8` for code quality, and `ctypes` for C-integration.