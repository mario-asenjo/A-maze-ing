PY=python3

CODE_DIRS = a_maze_ing.py src tests

install:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e .[dev]
	# Linux-specific MLX flags
	MLX_FLAGS = -Lminilibx -lmlx -lXext -lX11 -lm -lbsd

run:
	PYTHONPATH=src LD_LIBRARY_PATH=./minilibx $(PY) a_maze_ing.py config.txt

debug:
	$(PY) -m pdb a_maze_ing.py config.txt

lint:
	$(PY) -m flake8 $(CODE_DIRS)
	$(PY) -m mypy $(CODE_DIRS) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY) -m flake8 $(CODE_DIRS)
	$(PY) -m mypy $(CODE_DIRS) --strict

test:
	$(PY) -m pytest -q

build:
	$(PY) -m build

clean:
	rm -rf dist build .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf

.PHONY: install run debug lint lint-strict test build clean
