# 🔧 Guida all'Installazione

## Problema Risolto ✅

Il `pyproject.toml` è stato corretto per includere:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src"]
```

## Installazione Passo-Passo

### 1. Estrai il progetto

```bash
unzip rag_project.zip
cd rag_project
```

### 2. Installa con uv

```bash
# Sync delle dipendenze
uv sync

# Oppure con pip install editable
uv pip install -e .
```

### 3. Verifica installazione

```bash
# Dovrebbe mostrare il CLI help
uv run python -m src --help
```

## Troubleshooting Installazione

### Errore: "Unable to determine which files to ship"

**Soluzione**: Il `pyproject.toml` ora include `packages = ["src"]`

### Errore: "No module named 'src'"

```bash
# Assicurati di essere nella directory del progetto
cd rag_project

# Reinstalla
uv sync
```

### Errore: Dipendenze mancanti

```bash
# Installa manualmente
uv pip install pydantic fire tqdm transformers torch rank-bm25
```

### Errore: torch installation problematica

```bash
# Se hai problemi con torch, usa la versione CPU
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Comandi Post-Installazione

### Test veloce

```bash
# Verifica che tutto funzioni
uv run python -m src --help
```

Dovresti vedere:

```
NAME
    src

COMMANDS
    answer
    answer_dataset
    evaluate
    index
    search
    search_dataset
```

### Prossimo Step

Segui il **QUICKSTART.md** per:
1. Scaricare il repository vLLM
2. Creare l'indice
3. Testare il sistema

## Struttura dopo Installazione

```
rag_project/
├── src/                    ← Codice sorgente (installato come package)
├── data/
│   ├── raw/               ← Qui metterai vLLM
│   ├── processed/         ← Qui verrà salvato l'indice BM25
│   └── output/            ← Qui andranno i risultati
├── datasets/              ← Dataset pubblici inclusi
└── .venv/                 ← Virtual environment (creato da uv)
```

## Check Finale

```bash
# 1. Check Python version
python --version  # Deve essere >= 3.10

# 2. Check uv
uv --version

# 3. Check installazione package
uv run python -c "from src.models import MinimalSource; print('OK!')"

# 4. Check dipendenze
uv pip list | grep -E 'pydantic|fire|torch|rank-bm25'
```

Se tutti i check passano → **Sei pronto! 🚀**

Vai al **QUICKSTART.md** per i prossimi passi.
