# Pac-Man Makefile
# Required targets: install, run, debug, clean, lint
# Optional: lint-strict

PYTHON := uv
MAIN := pac-man.py
CONFIG := config.json

.PHONY: install run debug clean lint lint-strict package

## Install project dependencies
install:
	@# Install pygame
	@if command -v uv > /dev/null 2>&1; then \
		uv add pygame; \
	else \
		pip install pygame; \
	fi
	@# Install mazegenerator wheel (handle filename/version mismatch)
	@MAZE_WHL=$$(ls mazegenerator*.whl 2>/dev/null | head -1); \
	if [ -n "$$MAZE_WHL" ]; then \
		if command -v uv > /dev/null 2>&1; then \
			CORRECT_NAME=$$($(PYTHON) -c "import zipfile,re; \
				z=zipfile.ZipFile('$$MAZE_WHL'); \
				m=z.read([n for n in z.namelist() if n.endswith('METADATA')][0]).decode(); \
				v=re.search(r'Version: (.+)',m).group(1).strip(); \
				n=re.search(r'Name: (.+)',m).group(1).strip(); \
				print(f'{n}-{v}-py3-none-any.whl')"); \
			if [ "$$MAZE_WHL" != "$$CORRECT_NAME" ]; then \
				echo "Renaming $$MAZE_WHL -> $$CORRECT_NAME (fixing version mismatch)"; \
				cp "$$MAZE_WHL" "$$CORRECT_NAME"; \
				uv add "$$CORRECT_NAME"; \
				rm -f "$$CORRECT_NAME"; \
			else \
				uv add "$$MAZE_WHL"; \
			fi; \
		else \
			pip install "$$MAZE_WHL"; \
		fi; \
	else \
		echo "Warning: No mazegenerator*.whl found. Place it in the project root."; \
	fi
	@echo "Dependencies installed."

## Run the game
run:
	$(PYTHON) run $(MAIN) $(CONFIG)

## Run in debug mode with pdb
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

## Remove temporary files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."

## Run linting (flake8 + mypy)
lint:
	flake8 src/*
	mypy src/* --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

## Build standalone package for Itch.io deployment
package:
	uv add pyinstaller
	uv run build.py
