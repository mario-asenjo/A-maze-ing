PY=python3

.PHONY: install run debug lint lint-strict test build clean

install:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e .[dev]

run:
	$(PY) a_maze_ing.py config.txt

debug:
	$(PY) -m pdb a_maze_ing.py config.txt

lint:
	$(PY) -m flake8 .
	$(PY) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY) -m flake8 .
	$(PY) -m mypy . --strict

test:
	$(PY) -m pytest -q

build:
	$(PY) -m build

clean:
	rm -rf dist build .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -print0 | xargs -0 rm -rf
