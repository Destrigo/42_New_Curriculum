# Quick Start Guide

## 🚀 Setup Rapido

### 1. Installa dipendenze

```bash
cd rag_project
make install
```

### 2. Prepara i dati

Il progetto richiede il repository vLLM. Hai due opzioni:

#### Opzione A: Download completo

```bash
# Scarica il repository vLLM
git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1
cd data/raw/vllm-0.10.1
git checkout v0.10.1
cd ../../..
```

#### Opzione B: Testing veloce (usa solo i file menzionati nei dataset)

I dataset forniti in `datasets/` contengono già i file path, quindi puoi:
- Creare file fittizi per testare solo il pipeline
- Oppure scaricare solo i file specifici menzionati

### 3. Testa con un esempio

```bash
# Index (questo creerà l'indice BM25)
uv run python -m src index --source_dir data/raw/vllm-0.10.1 --max_chunk_size 2000

# Cerca
uv run python -m src search "What is vLLM?" --k 5

# Processa un dataset
uv run python -m src search_dataset \
  --dataset_path datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 5 \
  --save_directory data/output/search_results

# Genera risposte
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/dataset_docs_public.json \
  --save_directory data/output/answers

# Valuta
uv run python -m src evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json
```

## 📊 Dataset Forniti

Il progetto include:

- `datasets/AnsweredQuestions/` - Dataset CON ground truth (per training e evaluation)
  - `dataset_docs_public.json` - Domande su documentazione
  - `dataset_code_public.json` - Domande su codice

- `datasets/UnansweredQuestions/` - Dataset SENZA ground truth (per testing)
  - `dataset_docs_public.json` - Solo domande
  - `dataset_code_public.json` - Solo domande

## 🎯 Workflow Tipico

### Development Workflow

```bash
# 1. Index
make run index --source_dir data/raw/vllm-0.10.1

# 2. Testa retrieval
uv run python -m src search_dataset \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json \
  --k 10

# 3. Valuta
uv run python -m src evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json

# 4. Itera e migliora!
```

### Production Workflow

```bash
# 1. Index (già fatto)

# 2. Processa dataset senza ground truth
uv run python -m src search_dataset \
  --dataset_path datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10

# 3. Genera risposte
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/dataset_docs_public.json

# 4. Submit il file JSON!
```

## 🐛 Troubleshooting

### "No module named 'src'"

```bash
# Assicurati di essere nella directory del progetto
cd rag_project

# Reinstalla
make install
```

### "Index file not found"

```bash
# Devi prima creare l'indice
uv run python -m src index --source_dir data/raw/vllm-0.10.1
```

### Model download lento

Il primo run scaricherà Qwen/Qwen3-0.6B (~1.2GB). Ci vorrà qualche minuto.

### Out of memory

```bash
# Usa CPU invece di GPU
export CUDA_VISIBLE_DEVICES=""
```

## 📝 Note

- **Indexing time**: ~2-5 minuti su un repository medio
- **First model load**: ~30-60 secondi
- **Retrieval**: ~10-30 secondi per 100 domande
- **Generation**: ~1-2 secondi per risposta

## 🎓 Prossimi Passi

1. Leggi il README.md completo
2. Esplora i Pydantic models in `src/models/`
3. Guarda come funziona il chunking in `src/indexing/chunking.py`
4. Migliora i risultati:
   - Tweaka il chunking
   - Prova semantic search
   - Ottimizza i prompts per Qwen

Buon coding! 🚀
