# 🚀 Quick Installation Guide

## First Time Setup (One Command!)

```bash
chmod +x setup.sh
./setup.sh
```

That's it! The script will:
1. ✅ Clean UV cache
2. ✅ Update pyproject.toml
3. ✅ Create virtual environment
4. ✅ Install PyTorch CPU-only (~100MB)
5. ✅ Install all dependencies
6. ✅ Verify installation
7. ✅ Optionally download vLLM repository

## After Setup

### Activate environment (every time you start)

```bash
source activate.sh
# or
source .venv/bin/activate
```

### Test it works

```bash
# Should show CLI help
python -m src --help
```

## Next Steps

Follow the instructions printed at the end of `setup.sh`, or see **QUICKSTART.md** for full workflow.

## Troubleshooting

### "Permission denied"
```bash
chmod +x setup.sh
```

### "No space left on device"
The script uses CPU-only PyTorch (~100MB) instead of CUDA version (~2.5GB).
If still having issues, clean more cache:
```bash
rm -rf ~/.cache/pip/*
rm -rf ~/.cache/uv/*
```

### "Command not found: uv"
Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Manual Installation

If you prefer manual steps, see **INSTALL.md**.
