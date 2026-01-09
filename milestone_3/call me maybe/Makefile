# ==============================
# Project configuration
# ==============================

PYTHON := uv run python
SRC := src
INPUT_PROMPTS := data/input/function_calling_tests.json
INPUT_FUNCS := data/input/function_definition.json
OUTPUT := data/output/results.json

# ==============================
# Default target
# ==============================

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install    Install dependencies using uv"
	@echo "  make run        Run the full constrained decoding pipeline"
	@echo "  make format     Format code (ruff)"
	@echo "  make lint       Lint code (ruff)"
	@echo "  make clean      Remove generated files"

# ==============================
# Environment setup
# ==============================

.PHONY: install
install:
	uv sync

# ==============================
# Run pipeline
# ==============================

.PHONY: run
run:
	$(PYTHON) -m $(SRC) \
		--input $(INPUT_PROMPTS) \
		--input $(INPUT_FUNCS) \
		--output $(OUTPUT)

# ==============================
# Code quality
# ==============================

lint:
	uv run flake8 --exclude .venv
	uv run mypy .

# ==============================
# Cleanup
# ==============================

.PHONY: clean
clean:
	rm -f $(OUTPUT)
