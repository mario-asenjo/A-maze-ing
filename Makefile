PY=python3
VENV=.venv
BIN=$(VENV)/bin

CODE_DIRS = a_maze_ing.py src tests

MLX_DIR = minilibx
MLX_SO  = $(MLX_DIR)/libmlx.so
MLX_URL = https://github.com/42Paris/minilibx-linux.git


install:
	@echo "--- 1. Creating/Updating Virtual Environment ---"
	@if [ ! -d "$(VENV)" ]; then $(PY) -m venv $(VENV); fi
	@$(BIN)/pip install -U pip
	@$(BIN)/pip install -e .[dev]

	@echo "--- 2. Setting up MiniLibX (Linux) ---"
	@if [ ! -d "$(MLX_DIR)" ]; then \
		git clone $(MLX_URL) $(MLX_DIR); \
	fi
	
	@echo "Configuring MiniLibX..."
	@cd $(MLX_DIR) && ./configure
	
	@echo "Rebuilding MiniLibX with -fPIC..."
	# We pass CFLAGS directly to make to force -fPIC on every file
	@make -C $(MLX_DIR) clean
	@make -C $(MLX_DIR) CFLAGS=" -fPIC -I. -I.. -I/usr/include"
	
	@echo "Creating Shared Object for Python..."
	@gcc -shared -o $(MLX_SO) -Wl,--whole-archive $(MLX_DIR)/libmlx.a -Wl,--no-whole-archive -lXext -lX11 -lm
	@echo "--- Setup Complete! ---"

run:
	PYTHONPATH=src LD_LIBRARY_PATH=$(MLX_DIR) $(BIN)/python3 a_maze_ing.py config.txt

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
	rm -rf $(MLX_DIR)

.PHONY: install run debug lint lint-strict test build clean
