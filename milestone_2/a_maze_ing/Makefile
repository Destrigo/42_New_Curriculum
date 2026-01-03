MAIN        := a_maze_ing.py
CONFIG      := config.txt

.PHONY: install test run debug build clean lint lint-strict

install:
	uv sync

build:
	uv build --out-dir .

test:
	uv run pytest

run:
	uv run $(MAIN) $(CONFIG)

debug:
	uv run -m pdb $(MAIN) $(CONFIG)

lint:
	uv run flake8 --exclude .venv
	uv run mypy .

lint-strict:
	uv run flake8 --exclude .venv
	uv run mypy . --strict

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache .pytest_cache \
		mazegen-*.whl mazegen-*.tar.gz mazegen.egg-info htmlcov dist

