#!/bin/bash
# Complete manual setup for RAG project

set -e

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "🚀 RAG Project - Complete Setup"
echo "================================"
echo ""

# 1. Clean cache
echo "1/6 Cleaning cache..."
rm -rf ~/.cache/uv/* 2>/dev/null || true
rm -rf ~/.cache/pip/* 2>/dev/null || true

# 2. Remove old venv
echo "2/6 Removing old venv..."
rm -rf .venv

# 3. Create venv
echo "3/6 Creating virtual environment..."
python3 -m venv .venv

# 4. Activate
echo "4/6 Activating venv..."
source .venv/bin/activate

# 5. Install torch
echo "5/6 Installing PyTorch CPU (~100MB)..."
pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu

# 6. Install project
echo "6/6 Installing project dependencies..."
pip install --quiet -e .

echo ""
echo "✅ Setup complete!"
echo ""

# Verify
echo "Verifying installation..."
python -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
python -c "from src.models import MinimalSource; print('✓ Models OK')"
python -c "from src.retrieval import BM25Retriever; print('✓ Retrieval OK')"
python -c "from src.generation import AnswerGenerator; print('✓ Generation OK')"
python -m src --help > /dev/null && echo "✓ CLI OK"

echo ""
echo "🎉 All done!"
echo ""
echo "Next steps:"
echo "  1. Activate venv: source .venv/bin/activate"
echo "  2. Run CLI: python -m src --help"
echo ""
echo "Or use uv run:"
echo "  uv run python -m src --help"
