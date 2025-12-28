# ==============================
# Project configuration
# ==============================

PYTHON := uv run python
SRC := src
INPUT := data/input/function_calling_tests.json
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
		--input $(INPUT) \
		--output $(OUTPUT)

# ==============================
# Code quality
# ==============================

.PHONY: format
format:
	uv run ruff format .

.PHONY: lint
lint:
	uv run ruff check .

# ==============================
# Cleanup
# ==============================

.PHONY: clean
clean:
	rm -f $(OUTPUT)
