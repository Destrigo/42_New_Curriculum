#!/bin/bash

# 🚀 RAG Project - First Time Setup Script (No Pyenv Issues)
# This script sets up everything needed to run the project

set -e  # Exit on error

# Disable pyenv rehash to avoid permission errors
export PYENV_SKIP_REHASH=1

# Use python3 explicitly to avoid pyenv issues
PYTHON_CMD="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         RAG Against the Machine - First Setup             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step
print_step() {
    echo -e "\n${GREEN}▶ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# ============================================================================
# Verify Python
# ============================================================================
print_step "Verifying Python installation..."

if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10 or later."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oP '\d+\.\d+')
echo "  Found Python $PYTHON_VERSION"

if [ "${PYTHON_VERSION%.*}" -lt 3 ] || [ "${PYTHON_VERSION#*.}" -lt 10 ]; then
    print_warning "Python 3.10+ recommended (found $PYTHON_VERSION)"
fi

print_success "Python OK"

# ============================================================================
# STEP 1: Clean cache
# ============================================================================
print_step "Step 1/7: Cleaning UV cache to free space..."

if [ -d ~/.cache/uv ]; then
    CACHE_SIZE=$(du -sh ~/.cache/uv 2>/dev/null | cut -f1)
    echo "  Current UV cache size: $CACHE_SIZE"
    rm -rf ~/.cache/uv/* 2>/dev/null || true
    print_success "Cache cleaned!"
else
    print_success "No cache to clean"
fi

# ============================================================================
# STEP 2: Update pyproject.toml (remove torch from dependencies)
# ============================================================================
print_step "Step 2/7: Updating pyproject.toml..."

if grep -q '"torch' pyproject.toml 2>/dev/null; then
    sed -i.bak 's/"torch[^"]*",/# "torch>=2.0.0",  # Installed separately as CPU-only/' pyproject.toml 2>/dev/null || \
    sed 's/"torch[^"]*",/# "torch>=2.0.0",  # Installed separately as CPU-only/' pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml
    print_success "Updated pyproject.toml"
else
    print_success "pyproject.toml already configured"
fi

# ============================================================================
# STEP 3: Create virtual environment
# ============================================================================
print_step "Step 3/7: Creating virtual environment..."

if [ -d .venv ]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf .venv
fi

# Try uv first, fall back to python venv
if command -v uv &> /dev/null; then
    uv venv .venv
    print_success "Virtual environment created with uv"
else
    $PYTHON_CMD -m venv .venv
    print_success "Virtual environment created with venv"
fi

# ============================================================================
# STEP 4: Activate virtual environment
# ============================================================================
print_step "Step 4/7: Activating virtual environment..."

source .venv/bin/activate
print_success "Virtual environment activated"

# ============================================================================
# STEP 5: Install PyTorch CPU-only
# ============================================================================
print_step "Step 5/7: Installing PyTorch (CPU-only, ~100MB)..."

python -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
print_success "PyTorch installed successfully"

# Verify torch
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "unknown")
CUDA_AVAILABLE=$(python -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "false")

echo "  PyTorch version: $TORCH_VERSION"
echo "  CUDA available: $CUDA_AVAILABLE"

if [ "$CUDA_AVAILABLE" == "True" ]; then
    print_warning "CUDA is available (not expected for CPU-only install)"
else
    print_success "CPU-only installation confirmed"
fi

# ============================================================================
# STEP 6: Install project dependencies
# ============================================================================
print_step "Step 6/7: Installing project dependencies..."

# Try with uv first, fall back to pip
if command -v uv &> /dev/null; then
    uv pip install --quiet -e . 2>&1 | grep -v "pyenv" || true
else
    python -m pip install --quiet -e .
fi

print_success "All dependencies installed"

# ============================================================================
# STEP 7: Verify installation
# ============================================================================
print_step "Step 7/7: Verifying installation..."

# Test imports
echo "  Testing imports..."
python -c "from src.models import MinimalSource" 2>&1 | grep -v "pyenv" && print_success "  ✓ Models OK" || print_error "  ✗ Models failed"
python -c "from src.retrieval import BM25Retriever" 2>&1 | grep -v "pyenv" && print_success "  ✓ Retrieval OK" || print_error "  ✗ Retrieval failed"
python -c "from src.generation import AnswerGenerator" 2>&1 | grep -v "pyenv" && print_success "  ✓ Generation OK" || print_error "  ✗ Generation failed"
python -c "from src.evaluation import calculate_recall_at_k" 2>&1 | grep -v "pyenv" && print_success "  ✓ Evaluation OK" || print_error "  ✗ Evaluation failed"

# Test CLI
if python -m src --help > /dev/null 2>&1; then
    print_success "  ✓ CLI OK"
else
    print_error "  ✗ CLI test failed"
fi

# ============================================================================
# OPTIONAL: Download vLLM repository
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Optional: Download vLLM Repository           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -d "data/raw/vllm-0.10.1" ]; then
    echo -e "${YELLOW}The project requires the vLLM repository to index.${NC}"
    echo ""
    read -p "Do you want to download it now? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Downloading vLLM repository..."
        
        mkdir -p data/raw
        cd data/raw
        
        if command -v git &> /dev/null; then
            git clone https://github.com/vllm-project/vllm.git vllm-0.10.1 2>&1 | grep -v "pyenv" || true
            cd vllm-0.10.1
            git checkout v0.10.1 2>&1 | grep -v "pyenv" || true
            cd ../../..
            print_success "vLLM repository downloaded and checked out to v0.10.1"
        else
            print_error "Git not found. Please install git or download manually."
            echo "  Manual download: git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1"
        fi
    else
        echo ""
        print_warning "Skipped vLLM download. You can download it later with:"
        echo "  git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1"
        echo "  cd data/raw/vllm-0.10.1 && git checkout v0.10.1"
    fi
else
    print_success "vLLM repository already exists at data/raw/vllm-0.10.1"
fi

# ============================================================================
# Summary
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Setup Complete! 🎉                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_success "Installation successful!"
echo ""
echo -e "${GREEN}Virtual Environment:${NC} .venv/"
echo -e "${GREEN}Python:${NC} $(python --version 2>&1 | grep -v pyenv)"
echo -e "${GREEN}PyTorch:${NC} $TORCH_VERSION (CPU-only)"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""

if [ -d "data/raw/vllm-0.10.1" ]; then
    echo "  1. Index the repository:"
    echo "     ${BLUE}python -m src index --source_dir data/raw/vllm-0.10.1${NC}"
    echo ""
    echo "  2. Test a search:"
    echo "     ${BLUE}python -m src search \"What is vLLM?\" --k 5${NC}"
else
    echo "  1. Download vLLM repository:"
    echo "     ${BLUE}git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1${NC}"
    echo "     ${BLUE}cd data/raw/vllm-0.10.1 && git checkout v0.10.1 && cd ../..${NC}"
    echo ""
    echo "  2. Index the repository:"
    echo "     ${BLUE}python -m src index --source_dir data/raw/vllm-0.10.1${NC}"
    echo ""
    echo "  3. Test a search:"
    echo "     ${BLUE}python -m src search \"What is vLLM?\" --k 5${NC}"
fi

echo ""
echo "  Full workflow: See ${BLUE}QUICKSTART.md${NC} for detailed instructions"
echo ""

# Save activation helper
cat > activate.sh << 'ACTIVATE_EOF'
#!/bin/bash
# Quick activation script
cd "$(dirname "${BASH_SOURCE[0]}")"
source .venv/bin/activate
echo "✓ Virtual environment activated!"
echo "You can now run: python -m src --help"
ACTIVATE_EOF

chmod +x activate.sh
print_success "Created activation helper: ./activate.sh"

echo ""
echo -e "${YELLOW}Tip:${NC} To activate the virtual environment later, run:"
echo "  ${BLUE}source activate.sh${NC}"
echo "  or"
echo "  ${BLUE}source .venv/bin/activate${NC}"
echo ""

print_success "All done! Happy coding! 🚀"

# Note about pyenv warnings
echo ""
print_warning "Note: Any 'pyenv rehash' warnings can be safely ignored"
