mkdir -p /goinfre/mtaranti/.cache/uv
rm -rf ~/.cache/uv
ln -s /goinfre/mtaranti/.cache/uv ~/.cache/uv

export UV_CACHE_DIR=/goinfre/mtaranti/.cache/uv
source ~/.zshrc
rm -rf .venv
uv sync --python /usr/bin/python3



uv sync
git clone https://github.com/vllm-project/vllm.git data/raw/vllm-0.10.1
cd data/raw/vllm-0.10.1
git checkout v0.10.1
cd ../../..

make start

make index
make test-evaluate

make search-dataset-code
make evaluate-code

make answer-dataset
make answer-dataset-code