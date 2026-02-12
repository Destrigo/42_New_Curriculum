.PHONY: install run debug clean lint lint-strict test activate

# Activate venv helper
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UV = uv

activate:
	@echo "Run: source .venv/bin/activate"

install:
	@echo "Creating virtual environment..."
	$(UV) venv $(VENV) || python3 -m venv $(VENV)
	@echo "Installing PyTorch CPU-only..."
	$(PIP) install torch --index-url https://download.pytorch.org/whl/cpu
	@echo "Installing project dependencies..."
	$(UV) pip install -e . || $(PIP) install -e .
	@echo "✓ Installation complete!"
	@echo ""
	@echo "Activate with: source .venv/bin/activate"

run:
	@if [ -f "$(VENV)/bin/activate" ]; then \
		$(PYTHON) -m src $(ARGS); \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

debug:
	@if [ -f "$(VENV)/bin/activate" ]; then \
		$(PYTHON) -m pdb -m src $(ARGS); \
	else \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf build dist

lint:
	@if [ -f "$(VENV)/bin/flake8" ]; then \
		$(VENV)/bin/flake8 .; \
		$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	else \
		echo "❌ Linting tools not installed. Run 'make install' first."; \
		exit 1; \
	fi

lint-strict:
	@if [ -f "$(VENV)/bin/flake8" ]; then \
		$(VENV)/bin/flake8 .; \
		$(VENV)/bin/mypy . --strict; \
	else \
		echo "❌ Linting tools not installed. Run 'make install' first."; \
		exit 1; \
	fi

test:
	@if [ -f "$(VENV)/bin/pytest" ]; then \
		$(VENV)/bin/pytest tests/ -v; \
	else \
		echo "⚠ pytest not installed. Install with: pip install pytest"; \
	fi

# Quick commands using uv run (recommended)
index:
	$(UV) run python -m src index --source_dir data/raw/vllm-0.10.1

search:
	$(UV) run python -m src search "$(QUERY)" --k $(K)

# Usage examples
help:
	@echo "Available commands:"
	@echo ""
	@echo "  make install        - Install all dependencies"
	@echo "  make run ARGS='...' - Run the CLI (e.g., make run ARGS='search \"query\" --k 5')"
	@echo "  make clean          - Clean cache and temporary files"
	@echo "  make lint           - Run linters"
	@echo ""
	@echo "Recommended: Use 'uv run' directly:"
	@echo "  uv run python -m src --help"
	@echo "  uv run python -m src search \"query\" --k 5"
	@echo ""
	@echo "Or activate venv manually:"
	@echo "  source .venv/bin/activate"
	@echo "  python -m src --help"
