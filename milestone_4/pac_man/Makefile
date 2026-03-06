# Pac-Man Makefile
# Required targets: install, run, debug, clean, lint
# Optional: lint-strict

PYTHON := python3
MAIN := pac-man.py
CONFIG := config.json

# Fix for mazegenerator wheel filename/version mismatch
export UV_SKIP_WHEEL_FILENAME_CHECK := 1

.PHONY: install run debug clean lint lint-strict package

## Install project dependencies
install:
	@rm -f uv.lock
	uv add pygame
	@MAZE_WHL=$$(ls mazegenerator*.whl 2>/dev/null | head -1); \
	if [ -n "$$MAZE_WHL" ]; then \
		uv add "$$MAZE_WHL"; \
	else \
		echo "Warning: No mazegenerator*.whl found."; \
	fi
	@echo "Dependencies installed."

## Run the game
run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)

## Run in debug mode with pdb
debug:
	uv run $(PYTHON) -m pdb $(MAIN) $(CONFIG)

## Remove temporary files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."

## Run linting (flake8 + mypy)
lint:
	uv run flake8 src/*
	uv run flake8 pac-man.py
	uv run flake8 build.py
	uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

## Run strict linting
lint-strict:
	uv run flake8 src/*
	uv run flake8 pac-man.py
	uv run flake8 build.py
	uv run mypy . --strict

## Build standalone package for Itch.io deployment
package:
	uv add pyinstaller
	uv run $(PYTHON) build.py