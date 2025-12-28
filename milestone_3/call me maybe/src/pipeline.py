# src/pipeline.py

import json
from typing import Any, List, Dict
from pathlib import Path

from llm_sdk.small_llm_model import Small_LLM_Model
from models import FunctionRegistry
from fsm import JSONFSM
from constrained_decoder import ConstrainedDecoder
from errors import FileFormatError, DecoderError, FSMError


def load_json_file(path: str) -> Any:
    """Load and parse a JSON file, with error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise FileFormatError(f"Invalid JSON file: {path}") from e
    except FileNotFoundError as e:
        raise FileFormatError(f"File not found: {path}") from e


def save_json_file(data: Any, path: str) -> None:
    """Write JSON to a file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_pipeline(
    input_file: str,
    functions_file: str,
    output_file: str,
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
) -> None:
    """
    Main pipeline: process all prompts and generate function call outputs.
    
    Args:
        input_file: Path to JSON file with prompts
        functions_file: Path to JSON file with function definitions
        output_file: Path where results will be written
        model_name: HuggingFace model identifier
    """
    print(f"Loading prompts from {input_file}...")
    prompts = load_json_file(input_file)
    
    print(f"Loading function definitions from {functions_file}...")
    functions_raw = load_json_file(functions_file)
    registry = FunctionRegistry.from_json(functions_raw)
    
    print(f"Initializing LLM model: {model_name}...")
    llm = Small_LLM_Model(model_name=model_name)
    
    results: List[Dict[str, Any]] = []
    
    print(f"\nProcessing {len(prompts)} prompts...")
    for i, entry in enumerate(prompts, 1):
        prompt_text = entry.get("prompt")
        if not prompt_text:
            print(f"  [{i}/{len(prompts)}] Skipping empty prompt")
            continue
        
        print(f"  [{i}/{len(prompts)}] Processing: {prompt_text[:50]}...")
        
        try:
            # Create fresh FSM and decoder for this prompt
            fsm = JSONFSM(registry=registry, original_prompt=prompt_text)
            decoder = ConstrainedDecoder(llm=llm, fsm=fsm)
            
            # Generate constrained output
            json_output = decoder.generate(prompt=prompt_text)
            
            # Parse and validate the result
            result = json.loads(json_output)
            results.append(result)
            
            print(f"      ✓ Success: {result.get('fn_name')}")
            
        except (DecoderError, FSMError) as e:
            print(f"      ✗ Error: {str(e)}")
            results.append({
                "prompt": prompt_text,
                "fn_name": None,
                "args": {},
                "error": str(e)
            })
        except Exception as e:
            print(f"      ✗ Unexpected error: {str(e)}")
            results.append({
                "prompt": prompt_text,
                "fn_name": None,
                "args": {},
                "error": f"Unexpected: {str(e)}"
            })
    
    print(f"\nSaving results to {output_file}...")
    save_json_file(results, output_file)
    
    # Print summary
    successful = sum(1 for r in results if r.get("fn_name") is not None)
    print(f"\n{'='*60}")
    print(f"Pipeline complete!")
    print(f"  Total prompts: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(results) - successful}")
    print(f"{'='*60}")