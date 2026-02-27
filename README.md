*This project has been created as part of the 42 curriculum by acaire-d, masenjo.*

# A-Maze-ing
A robust, graphical maze generator and solver built in Python using the MiniLibX library.

---

## Description
A-Maze-ing is a configurable and interactive maze generator developed in Python.

The project features:

-   Perfect and non-perfect maze generation
-   Multiple algorithms (DFS, Prim, Kruskal)
-   42 pattern embedding
-   Animated maze generation via event system
-   BFS shortest-path solver
-   Hexadecimal export format
-   Fully reusable pip-installable module
-   Strict typing and test coverage

The architecture cleanly separates:

-   `mazegen/` → reusable core module
-   `src/app/` → graphical interface (MiniLibX)
-   CLI entry point → `a_maze_ing.py`
---

# Instructions

## Instalation & Setup
This project includes a fully automated Makefile.

### Full Setup (Recommended)

```bash
  make install
```

This command:

1. Creates or updates the virtual environment (`.venv`)
2. Installs the project in editable mode with dev dependencies
3. Clones MiniLibX.
4. Configures and rebuilds MiniLibX with `-fPIC`
5. Builds `libmlx.so` for Python compatibility

After this, everything is ready to run.

---

## Running the Application

```bash
  make run
```

This is equivalent to:
```bash
  PYTHONPATH=src LD_LIBRARY_PATH=minilibx .venv/bin/python3 a_maze_ing.py config.txt
```

---

## Debug Mode

```bash
  make debug
```

Runs the application with Python debugger (pdb).

---

### Code Quality & Testing

Linting:

```bash
  make lint
```

Strict Linting:

```bash
  make lint-strict
```

Run tests:
```bash
  make test
```

---

## Build Reusable Package

```bash
  make build
```

Creates:
- dist/\*.whl
- dist/\*.tar.gz

Install locally:
```bash
  pip install dist/mazegen_anais_mario-1.0.0-py3-none-any.whl
```

---

## Cleaning the Project

```bash
  make clean
```

Removes:
- dist/
- buidl/
- caches
- MiniLibX clone

---

## Config File Structure

The project uses a `config.txt` file (parsed via `pyproject.toml` and internal parsers) with the following format:

Example:

```text
    WIDTH=20
    HEIGHT=20
    ENTRY=1,5
    EXIT=9,19
    OUTPUT_FILE=maze.txt
    PERFECT=True
    ALGORITHM=dfs
    SEED=42
```

Mandatory:

```text
    WIDTH
    HEIGHT
    ENTRY
    EXIT
    OUTPUT_FILE
    PERFECT
```

Optional:

```text
    ALGORITHM (dfs \| prim \| kruskal)
    SEED
```

---

## Maze Generation Algorithms (Bonus)
Supported algorithms:

### DFS (Recursive Backtracker)

-   Fast
-   Deterministic with seed
-   Naturally produces perfect mazes

### Prim

-   Randomized MST-based generation
-   More uniform expansion

### Kruskal

-   Disjoint-set based MST algorithm
-   Global randomized wall removal

All share the same Maze data model.

---

## 42 Pattern

- If maze size ≥ 7x5, a 42 pattern is embedded as closed cells.
- If size is too small, generation continues and a warning is stored.

---

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