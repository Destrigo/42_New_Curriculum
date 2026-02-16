uv sync
git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1
cd data/raw/vllm-0.10.1
git checkout v0.10.1
cd ../../..

make run

# Index vLLM repository (takes ~2-5 minutes)
python -m src index --source_dir data/raw/vllm-0.10.1 --max_chunk_size 2000
```

**What happens:**
- Reads all `.py` and `.md` files
- Chunks them intelligently (AST for Python, semantic for text)
- Creates BM25 index
- Saves to `data/processed/bm25_index.pkl`

**Output:**
```
Found 1234 files to index
Chunking files: 100%|████████| 1234/1234
Created 5678 chunks
Building BM25 index...
Indexing complete!
Index saved to data/processed/bm25_index.pkl


# Test a single search query
python -m src search "What is vLLM?" --k 5

# Try more examples
python -m src search "How to configure OpenAI server?" --k 10
python -m src search "What models are supported?" --k 5
```

**Output:**
```
Top 5 results for: What is vLLM?

1. docs/source/getting_started/quickstart.md
   Characters: 0-1250

2. README.md
   Characters: 100-1500
...



# Process documentation questions
python -m src search_dataset \
  --dataset_path datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 \
  --save_directory data/output/search_results
```

**Output:**
```
Loading dataset from datasets/UnansweredQuestions/dataset_docs_public.json
Searching: 100%|████████| 100/100 [00:15<00:00]

Saved student_search_results to 
data/output/search_results/dataset_docs_public.json


# Evaluate how good your retrieval is
python -m src evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json
```

**Output:**
```
Evaluation Results
========================================
Questions evaluated: 100
Recall@1: 0.450 (45.0%)
Recall@3: 0.590 (59.0%)
Recall@5: 0.650 (65.0%)  ← Target: 75%+
Recall@10: 0.720 (72.0%)



# Generate answers for the search results
python -m src answer_dataset \
  --student_search_results_path data/output/search_results/dataset_docs_public.json \
  --save_directory data/output/answers
```

**Output:**
```
Loading model Qwen/Qwen3-0.6B on cpu...
Model loaded successfully!

Generating answers: 100%|████████| 100/100 [03:20<00:00, 2.0s/it]

Saved answers to data/output/answers/dataset_docs_public.json


# Ask a question
python -m src answer "What is vLLM?" --k 5
```

**Output:**
```
Question: What is vLLM?

Answer: vLLM is a high-throughput and memory-efficient inference 
engine for large language models. It uses PagedAttention to optimize 
memory usage and achieve high throughput...

Sources (5):
1. docs/source/getting_started/quickstart.md
2. README.md
3. docs/source/serving/deploying_with_docker.md
...










 Index
uv run python -m src index --source_dir data/raw/vllm-0.10.1

# Search
uv run python -m src search "What is vLLM?" --k 5

# Search dataset
uv run python -m src search_dataset \
  --dataset_path datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10

# Evaluate
uv run python -m src evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json
```

**Advantage:** No need to remember `source .venv/bin/activate`

---

## 📊 What You Get

After running the workflow:
```
data/output/
├── search_results/
│   ├── dataset_docs_public.json     ← Retrieval results
│   └── dataset_code_public.json
└── answers/
    ├── dataset_docs_public.json     ← With LLM answers
    └── dataset_code_public.json
