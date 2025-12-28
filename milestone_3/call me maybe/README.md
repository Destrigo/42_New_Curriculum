Constrained Function Calling with Finite State Machines
Overview

This project implements a constrained decoding pipeline for Large Language Models (LLMs) that enables deterministic, schema-valid function calling.

Given:

A list of natural language prompts

A list of available function definitions (name, arguments, types)

The system produces, for each prompt, a valid JSON object that:

Selects exactly one function

Provides only valid arguments

Conforms strictly to the provided schema

Is guaranteed to be syntactically valid JSON

This is achieved using:

A Finite State Machine (FSM) to enforce JSON structure

Schema-aware token constraints

Token-by-token constrained decoding

A lightweight Hugging Face causal language model

The model is never allowed to hallucinate structure or arguments. It can only choose among tokens that are explicitly permitted at each decoding step.

Key Concepts
1. Finite State Machine (FSM)

The FSM tracks the current position in the JSON structure and enforces correct syntax.

Example states:

START_OBJECT ({)

KEY

COLON

VALUE

STRING

NUMBER

END_OBJECT (})

At every generation step, the FSM determines what kinds of tokens are legal next.

The FSM is purely deterministic and contains no ML logic.

2. Schema Enforcement

Function definitions are loaded dynamically from function_definitions.json.

Each function specifies:

Function name

Argument names

Argument types

Return type

The schema layer ensures:

Only existing function names can be emitted

Only valid argument names can be used

Argument values respect expected types

This guarantees semantic correctness, not just syntactic correctness.

3. Constrained Decoding

Instead of letting the model freely generate text, the system performs token-by-token decoding:

The model produces logits for the next token

Invalid tokens are masked out based on:

FSM state

Schema rules

The highest-probability valid token is selected

The FSM advances to the next state

The process repeats until the JSON is complete

The LLM chooses among allowed tokens, but never invents new structure.

4. Role of the LLM

The LLM is responsible for:

Understanding the prompt semantics

Selecting the appropriate function

Selecting appropriate argument values

The LLM is not responsible for:

JSON formatting

Argument validation

Structural correctness

Those responsibilities are handled entirely by deterministic code.

Project Structure
.
├── README.md
├── pyproject.toml
├── uv.lock
├── Makefile
├── llm_sdk/
│   └── small_llm_model.py
├── data/
│   └── input/
│       ├── function_calling_tests.json
│       └── function_definitions.json
└── src/
    ├── __main__.py
    ├── cli.py
    ├── pipeline.py
    ├── constrained_decoder.py
    ├── fsm.py
    ├── schema.py
    ├── models.py
    └── errors.py

Installation

This project uses uv for dependency management.

uv sync


This installs all required dependencies in a virtual environment.

Usage
Run the full pipeline
uv run python -m src \
  --input data/input/function_calling_tests.json \
  --output data/output/results.json

Input format
function_calling_tests.json
[
  { "prompt": "What is the sum of 2 and 3?" },
  { "prompt": "Reverse the string 'hello'" }
]

function_definitions.json
[
  {
    "fn_name": "fn_add_numbers",
    "args_names": ["a", "b"],
    "args_types": { "a": "float", "b": "float" },
    "return_type": "float"
  }
]

Output format

Each prompt produces exactly one JSON object:

{
  "prompt": "What is the sum of 2 and 3?",
  "fn_name": "fn_add_numbers",
  "args": {
    "a": 2,
    "b": 3
  }
}


All outputs are guaranteed to be:

Valid JSON

Schema-compliant

Deterministic

Design Decisions
Why FSM instead of post-validation?

Post-validating JSON after free generation allows:

Hallucinated keys

Invalid argument types

Partial or malformed JSON

FSM-based constrained decoding prevents errors instead of correcting them.

Why token-level constraints?

Constraining only at the string or regex level is insufficient.

Token-level constraints allow:

Exact control over structure

Deterministic guarantees

Formal reasoning about correctness

Why lightweight model?

The focus of the project is algorithmic correctness, not model size.

Any causal LLM can be used, as correctness comes from constraints, not scale.

Error Handling

The system fails fast and explicitly in cases such as:

Invalid input JSON

Schema mismatch

Impossible decoding state

Errors are centralized and produce clear diagnostic messages.

Testing Strategy

Deterministic decoding ensures reproducibility

FSM state transitions are unit-testable

Schema validation is independent of the model

Input files can be swapped without code changes

AI Usage Disclosure

An AI assistant was used during development to:

Discuss architectural patterns

Clarify FSM-based constrained decoding concepts

Refine explanations and documentation

All core logic, design decisions, and implementation were authored and understood by the developer.

Summary

This project demonstrates:

Deterministic function calling

Schema-safe LLM integration

Formal use of FSMs for structured generation

A clean separation between learning-based and rule-based components

The result is a robust, auditable, and extensible system for constrained LLM output generation.