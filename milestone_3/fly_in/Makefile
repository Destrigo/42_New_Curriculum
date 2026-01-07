# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: your_login <your_login@student.42.fr>      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/01/06 00:00:00 by your_login       #+#    #+#              #
#    Updated: 2025/01/06 00:00:00 by your_login      ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

.PHONY: all install run debug clean lint lint-strict help
PYTHON := python3
MAIN_SCRIPT :=  -m fly_in.main

all: help

help:
	@echo "=========================================="
	@echo "  Fly-in: Drone Routing System"
	@echo "=========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make install      - Install project dependencies"
	@echo "  make run          - Execute the main script"
	@echo "  make debug        - Run the main script in debug mode"
	@echo "  make clean        - Remove temporary files and caches"
	@echo "  make lint         - Run flake8 and mypy (mandatory checks)"
	@echo "  make lint-strict  - Run flake8 and mypy with strict flags"
	@echo "  make help         - Show this help message"
	@echo ""

install:
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install flake8 mypy
	@echo "✓ Dependencies installed successfully!"

run:

	@$(PYTHON) $(MAIN_SCRIPT)

debug:
	@echo "Running in debug mode (Python debugger)..."
	@$(PYTHON) -m pdb $(MAIN_SCRIPT)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true

lint:
	@echo "→ Running flake8..."
	@$(PYTHON) -m flake8 . || (echo "✗ flake8 found issues" && exit 1)
	@echo "✓ flake8 passed"
	@echo ""
	@echo "→ Running mypy with mandatory flags..."
	@$(PYTHON) -m mypy . --explicit-package-bases --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || (echo "✗ mypy found issues" && exit 1)
	@echo "✓ mypy passed"