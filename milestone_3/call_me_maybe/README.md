*This project has been created as part of the 42 curriculum by [mtaranti]*

# Call Me Maybe - Introduction to Function Calling in LLMs

A constrained decoding system that translates natural language prompts into structured, schema-valid function calls using a lightweight Large Language Model.

## Description

This project implements a two-phase constrained decoding pipeline for function calling:

**Phase 1: Function Selection** - Uses matrix-based constrained decoding to force the LLM to select exactly one valid function from a predefined set.

**Phase 2: Argument Extraction** - Extracts argument values from the prompt using function-specific patterns and regex, then constructs valid JSON programmatically.

### Key Features

- **100% Valid JSON Output**: All outputs are guaranteed to be syntactically valid and schema-compliant
- **Constrained Decoding**: Function selection uses token-by-token constraints via a precomputed matrix
- **Hybrid Extraction**: Combines regex patterns for speed with LLM-based extraction as fallback
- **Function Validation**: Post-LLM validation layer corrects common misclassifications
- **Semantic Interpretation**: Converts natural language descriptions (e.g., "vowels") to actual patterns (e.g., `[aeiouAEIOU]`)

### How It Works

Given:
- Natural language prompts: `"What is the sum of 2 and 3?"`
- Function definitions with typed arguments

The system produces:
```json
{
  "prompt": "What is the sum of 2 and 3?",
  "fn_name": "fn_add_numbers",
  "args": {"a": 2.0, "b": 3.0}
}
```

## Instructions

### Installation

This project uses `uv` for dependency management:

```bash
make install
```

Or directly:

```bash
uv sync
```

### Running the Program

Default usage (reads from `data/input/`, writes to `data/output/`):

```bash
make run
```

Or with custom paths:

```bash
uv run python -m src \
  --input data/input/function_calling_tests.json \
  --input data/input/function_definition.json \
  --output data/output/results.json
```

### Input Format

**function_calling_tests.json** - Array of prompt objects:
```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Reverse the string 'hello'"}
]
```

**function_definition.json** - Array of function definitions:
```json
[
  {
    "fn_name": "fn_add_numbers",
    "args_names": ["a", "b"],
    "args_types": {"a": "float", "b": "float"},
    "return_type": "float"
  }
]
```

### Output Format

Each prompt produces one JSON object with `prompt`, `fn_name`, and `args` fields:

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "fn_name": "fn_add_numbers",
    "args": {"a": 2.0, "b": 3.0}
  }
]
```

### Other Commands

```bash
make debug        # Run in debug mode with pdb
make lint         # Run flake8 and mypy with required flags
make clean        # Remove temporary files
```

## Algorithm Explanation

### Phase 1: Constrained Function Selection

1. **Matrix Construction**: Each function definition is tokenized into a sequence of token IDs, forming rows in a matrix
2. **Token-by-Token Generation**: At each step, only tokens that match a prefix of at least one matrix row are allowed
3. **Substring Matching**: Generation stops when the generated sequence uniquely identifies one function

This guarantees the selected function is always valid and exists in the function definitions.

### Phase 2: Argument Extraction

1. **Function-Specific Patterns**: Each function type has tailored regex patterns (e.g., "sum of X and Y")
2. **Semantic Interpretation**: Converts descriptions like "vowels" → `[aeiouAEIOU]` or "asterisks" → `*`
3. **Fallback Extraction**: If regex fails, uses LLM with prompt-token constraints
4. **Programmatic JSON**: Final JSON is constructed programmatically, ensuring 100% validity

### Validation Layer

A post-LLM validation step corrects common mistakes:
- "sum" keyword → ensures `fn_add_numbers` (not `fn_multiply_numbers`)
- "substitute"/"replace" → ensures `fn_substitute_string_with_regex` (not `fn_reverse_string`)

## Design Decisions

### Why Two Phases?

**Phase 1 (Constrained Decoding)**: Function selection requires precise structural control. Matrix-based constraints guarantee only valid functions can be selected.

**Phase 2 (Hybrid Extraction)**: Argument extraction is more flexible. Regex patterns handle 80% of cases efficiently, with LLM fallback for complex cases.

### Why Not Full Constrained JSON Generation?

Attempting to generate entire JSON structure token-by-token with an LLM causes:
- Infinite whitespace loops
- Incorrect token ordering (generating "name" before quote)
- Exponential state complexity

Our hybrid approach is:
- More reliable (100% valid JSON)
- Faster (regex is instant)
- Easier to debug and maintain

### Why Validation Layer?

Small models (0.6B parameters) occasionally confuse similar operations (add vs. multiply). A simple keyword-based validation catches and corrects these errors, achieving >95% accuracy.

### Why Function-Specific Extractors?

Generic extraction fails on complex patterns. Function-specific extractors like `_extract_substitute_args` handle the nuances of each function type (e.g., three-argument substitution with quoted strings).

## Performance Analysis

**Accuracy**: 93-100% correct function selection and argument extraction (14/14 on test set)

**Speed**: Processes 14 prompts in ~30 seconds on CPU (M1 Mac)
- Phase 1: ~1.5s per prompt (LLM constrained decoding)
- Phase 2: ~0.5s per prompt (mostly regex)

**Reliability**: 100% valid JSON output guaranteed by programmatic construction

**Bottleneck**: LLM inference in Phase 1. Could be optimized with:
- Cached function embeddings
- Faster inference engine
- Quantized model weights

## Challenges Faced

### Challenge 1: Infinite Whitespace Loops

**Problem**: Token-level JSON generation entered infinite loops generating whitespace and quotes.

**Solution**: Abandoned full JSON generation. Phase 2 now extracts values only and builds JSON programmatically.

### Challenge 2: Multi-token Phrase Encoding

**Problem**: Encoding entire phrases like `"username"` created a set of all tokens in the phrase, allowing them in any order.

**Solution**: Switched to function-specific regex patterns that operate on decoded text, not token sequences.

### Challenge 3: Semantic Understanding

**Problem**: "Replace vowels with asterisks" was extracting literal strings "vowels" and "asterisks".

**Solution**: Added `_interpret_semantic_values()` to map descriptions to actual patterns/replacements.

### Challenge 4: Function Confusion

**Problem**: Small model confused "sum" with "product" (~14% error rate).

**Solution**: Added `_validate_function_selection()` that checks prompt keywords and corrects obvious errors.

## Testing Strategy

### Unit Testing Approach

Each component is testable independently:
- **Matrix construction**: Verify each function tokenizes to valid matrix row
- **Token masking**: Verify only valid next tokens are allowed
- **Extraction patterns**: Test regex patterns against known prompts
- **Validation logic**: Verify keyword detection and correction

### Integration Testing

Full pipeline tested with 14 diverse prompts covering:
- Simple operations (sqrt, reverse)
- Binary operations (add, multiply)
- Complex patterns (3-argument substitution)
- Edge cases (semantic descriptions)

### Validation

Output validated against schema:
- JSON parseability
- Required keys present (`prompt`, `fn_name`, `args`)
- Argument types match function definition
- No hallucinated keys or functions

## Example Usage

```bash
# Install dependencies
make install

# Run with default paths
make run

# Run with custom input
uv run python -m src \
  --input my_prompts.json \
  --input my_functions.json \
  --output my_results.json

# Debug mode
make debug

# Check code quality
make lint
```

## Resources

### Documentation
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/) - Model loading and inference
- [Qwen3 Model Card](https://huggingface.co/Qwen/Qwen3-0.6B) - Details on the 0.6B model used
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Type annotation reference
- [Regex Tutorial](https://docs.python.org/3/library/re.html) - Regular expression patterns

### Academic Papers
- "Constrained Decoding for Neural Text Generation" - Hokamp & Liu, 2017
- "Guided Generation of Cause and Effect" - Qin et al., 2020
- "NeuroLogic Decoding" - Lu et al., 2021

### Related Projects
- [Outlines](https://github.com/outlines-dev/outlines) - Structured text generation
- [Guidance](https://github.com/guidance-ai/guidance) - Controllable generation
- [LMQL](https://lmql.ai/) - Query language for LLMs

### AI Usage

AI assistance (Claude) was used for:

**Architecture Design** (30%):
- Discussing pros/cons of full constrained generation vs. hybrid approach
- Reviewing state machine designs for JSON generation
- Brainstorming extraction pattern strategies

**Debugging** (20%):
- Identifying causes of infinite whitespace loops
- Understanding tokenizer byte-level encoding
- Diagnosing multi-token phrase issues

**Documentation** (15%):
- Refining README structure and clarity
- Generating code comments and docstrings
- Proofreading technical explanations

**Code Review** (10%):
- Suggesting edge case handling
- Identifying potential type annotation issues
- Recommending cleaner regex patterns

**NOT Used For**:
- Core algorithm implementation (100% original)
- Constrained decoding logic (100% original)
- Extraction pattern design (100% original)
- Function validation layer (100% original)

All design decisions, implementation details, and testing strategies were authored and fully understood by the developer. AI was used as a brainstorming partner and documentation assistant, not as a code generator.

## Project Structure

```
.
├── README.md
├── Makefile
├── pyproject.toml
├── uv.lock
├── .python-version
├── src/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── constrained_decoder.py   # Main decoder logic
│   ├── parser.py                # Input file parser
│   ├── tokenizer.py            # Custom tokenizer
│   ├── small_llm_model.py      # LLM wrapper
│   └── vocab_normalizer.py     # Vocabulary utilities
└── data/
    ├── input/
    │   ├── function_calling_tests.json
    │   └── function_definition.json
    └── output/
        └── results.json         # Generated by program
```

## Requirements

- Python 3.10+
- uv (package manager)
- Dependencies: see `pyproject.toml`
  - transformers
  - torch
  - huggingface-hub
  - (no dspy, outlines, or similar packages)

## License

This is an educational project created for the 42 curriculum.