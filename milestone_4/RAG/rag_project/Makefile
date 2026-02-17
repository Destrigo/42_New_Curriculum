.PHONY: install clean lint help
.PHONY: index search search-dataset evaluate answer-dataset answer
.PHONY: test-search test-evaluate test-answer test-full

# Configuration
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UV = uv

# Default paths
VLLM_DIR ?= data/raw/vllm-0.10.1
DATASET_DOCS ?= datasets/UnansweredQuestions/dataset_docs_public.json
DATASET_CODE ?= datasets/UnansweredQuestions/dataset_code_public.json
DATASET_DOCS_GT ?= datasets/AnsweredQuestions/dataset_docs_public.json
DATASET_CODE_GT ?= datasets/AnsweredQuestions/dataset_code_public.json
OUTPUT_DIR ?= data/output/search_results
ANSWER_DIR ?= data/output/answers
K ?= 10
QUERY ?= "What is vLLM?"
MAX_CHUNK_SIZE ?= 2000

# Setup commands
install:
	@echo "Creating virtual environment..."
	$(UV) venv $(VENV)
	@echo "Installing project dependencies..."
	$(UV) pip install -e .
	@echo "✓ Installation complete!"

start:
	git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1
	cd data/raw/vllm-0.10.1
# 	git checkout v0.10.1

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports

# RAG commands
index:
	$(PYTHON) -m src index --source_dir $(VLLM_DIR) --max_chunk_size $(MAX_CHUNK_SIZE)

search:
	$(PYTHON) -m src search $(QUERY) --k $(K)

search-dataset:
	$(PYTHON) -m src search_dataset --dataset_path $(DATASET_DOCS) --k $(K) --save_directory $(OUTPUT_DIR)

search-dataset-code:
	$(PYTHON) -m src search_dataset --dataset_path $(DATASET_CODE) --k $(K) --save_directory $(OUTPUT_DIR)

evaluate:
	$(PYTHON) -m src evaluate --student_answer_path $(OUTPUT_DIR)/dataset_docs_public.json --dataset_path $(DATASET_DOCS_GT)

evaluate-code:
	$(PYTHON) -m src evaluate --student_answer_path $(OUTPUT_DIR)/dataset_code_public.json --dataset_path $(DATASET_CODE_GT)

answer-dataset:
	$(PYTHON) -m src answer_dataset --student_search_results_path $(OUTPUT_DIR)/dataset_docs_public.json --save_directory $(ANSWER_DIR)

answer-dataset-code:
	$(PYTHON) -m src answer_dataset --student_search_results_path $(OUTPUT_DIR)/dataset_code_public.json --save_directory $(ANSWER_DIR)

answer:
	$(PYTHON) -m src answer $(QUERY) --k $(K)

# Full workflow tests
test-search:
	make search QUERY="What is vLLM?" K=5

test-evaluate:
	make search-dataset
	make evaluate

test-answer:
	make answer QUERY="How does PagedAttention work?" K=5

test-full:
	@echo "Running full workflow..."
	make index
	make search-dataset
	make evaluate
	make answer-dataset

help:
	@echo "RAG Project Makefile Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install              - Install all dependencies"
	@echo "  make clean                - Clean cache and temp files"
	@echo ""
	@echo "RAG Commands:"
	@echo "  make index                - Index vLLM repository"
	@echo "  make search               - Search single query (QUERY='...' K=5)"
	@echo "  make search-dataset       - Search docs dataset"
	@echo "  make search-dataset-code  - Search code dataset"
	@echo "  make evaluate             - Evaluate docs results"
	@echo "  make evaluate-code        - Evaluate code results"
	@echo "  make answer-dataset       - Generate answers for docs"
	@echo "  make answer-dataset-code  - Generate answers for code"
	@echo "  make answer               - Answer single query (QUERY='...' K=5)"
	@echo ""
	@echo "Full Workflows:"
	@echo "  make test-search          - Test search command"
	@echo "  make test-evaluate        - Search + evaluate"
	@echo "  make test-answer          - Test answer command"
	@echo "  make test-full            - Full pipeline (index → search → evaluate → answer)"
	@echo ""
	@echo "Examples:"
	@echo "  make search QUERY='What is vLLM?' K=5"
	@echo "  make search-dataset K=10"
	@echo "  make answer QUERY='How does vLLM work?'"