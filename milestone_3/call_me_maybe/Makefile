PYTHON := uv run python
SRC := src
INPUT_DIR := data/input
OUTPUT_DIR := data/output
INPUT_PROMPTS := $(INPUT_DIR)/function_calling_tests.json
INPUT_FUNCS := $(INPUT_DIR)/function_definition.json
OUTPUT := $(OUTPUT_DIR)/function_definition_results.json

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install       Install project dependencies using uv"
	@echo "  make run           Execute the main script"
	@echo "  make debug         Run the main script in debug mode"
	@echo "  make clean         Remove temporary files and caches"
	@echo "  make lint          Run flake8 and mypy with required flags"
	@echo "  make lint-strict   Run flake8 and mypy with strict flags (optional)"

.PHONY: install
install:
	uv sync

.PHONY: run
run:
	$(PYTHON) -m $(SRC) \
		--input $(INPUT_PROMPTS) \
		--input $(INPUT_FUNCS) \
		--output $(OUTPUT)

.PHONY: debug
debug:
	$(PYTHON) -m pdb -m $(SRC) \
		--input $(INPUT_PROMPTS) \
		--input $(INPUT_FUNCS) \
		--output $(OUTPUT)

.PHONY: lint
lint:
	python3 -m flake8 src/*
	python3 -m mypy src/*.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf $(SRC)/__pycache__
	rm -rf $(SRC)/*.pyc
	rm -f $(OUTPUT)