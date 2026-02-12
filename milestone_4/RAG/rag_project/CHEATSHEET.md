# 🚀 RAG Project - Quick Reference Card

## 📦 FIRST TIME SETUP

### Option 1: Automated (setup.sh)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual (manual_setup.sh)
```bash
chmod +x manual_setup.sh
./manual_setup.sh
```

### Option 3: Ultra-Manual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e .
```

---

## ⚡ DAILY USAGE

### Before Each Session:
```bash
# Option A: Use uv run (NO activation needed!)
uv run python -m src --help

# Option B: Activate venv manually
source .venv/bin/activate
python -m src --help

# Option C: Use helper script
source activate.sh
```

---

## 📝 COMMON COMMANDS

### Search
```bash
# With uv run (recommended)
uv run python -m src search "What is vLLM?" --k 5

# With activated venv
python -m src search "What is vLLM?" --k 5
```

### Index Repository
```bash
uv run python -m src index --source_dir data/raw/vllm-0.10.1
```

### Process Dataset
```bash
uv run python -m src search_dataset \
  --dataset_path datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 \
  --save_directory data/output/search_results
```

### Generate Answers
```bash
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/dataset_docs_public.json \
  --save_directory data/output/answers
```

### Evaluate
```bash
uv run python -m src evaluate \
  --student_answer_path data/output/search_results/dataset_docs_public.json \
  --dataset_path datasets/AnsweredQuestions/dataset_docs_public.json
```

### Answer Single Question
```bash
uv run python -m src answer "How does vLLM work?" --k 5
```

---

## 🛠️ MAKEFILE COMMANDS

```bash
make install        # Install everything
make clean          # Clean cache
make lint           # Run linters
make help           # Show help

# Run with args (venv auto-activated)
make run ARGS="search 'query' --k 5"
make run ARGS="--help"
```

---

## 🐛 TROUBLESHOOTING

### Error: "No module named 'torch'"
```bash
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Error: "No module named 'src'"
```bash
source .venv/bin/activate
pip install -e .
```

### Error: "make: command not found"
```bash
# Use uv run instead
uv run python -m src --help
```

### Error: "pyenv: cannot rehash"
```bash
# Already fixed in setup.sh, but if you see it, ignore it!
# Or use: export PYENV_SKIP_REHASH=1
```

---

## ✅ VERIFICATION

After setup, test:
```bash
source .venv/bin/activate
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "from src.models import MinimalSource; print('Models: OK')"
python -m src --help
```

Should output:
```
PyTorch: 2.x.x+cpu
Models: OK
NAME
    src
COMMANDS
    ...
```

---

## 📁 FILE STRUCTURE

```
RAG/
├── .venv/              ← Virtual environment (created by setup)
├── setup.sh            ← Automated setup
├── manual_setup.sh     ← Fallback manual setup
├── activate.sh         ← Quick venv activation
├── Makefile            ← Task automation
├── src/                ← Source code
├── data/               ← Data directory
│   ├── raw/           ← Put vLLM repo here
│   ├── processed/     ← BM25 index saved here
│   └── output/        ← Results saved here
└── datasets/           ← Test datasets (included)
```

---

## 💡 TIPS

1. **Always use `uv run`** - No need to activate venv!
2. **Or activate once** with `source .venv/bin/activate`
3. **Never use bare `python`** - Use venv's python
4. **Check venv is active**: `which python` should show `.venv`
5. **Deactivate venv**: `deactivate`

---

## 🔗 QUICK LINKS

- Full docs: `README.md`
- Installation guide: `INSTALL.md`
- Quick start: `QUICKSTART.md`
- Setup issues: `INSTALL_QUICK.md`
- Pyenv fix: See `setup.sh` (already fixed)

---

**Remember:** Either use `uv run` OR activate venv first! 🚀
