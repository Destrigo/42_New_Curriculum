# src/pipeline.py

import json
from typing import Any, List, Dict

from llm_sdk import Small_LLM_Model
from fsm import FunctionCallingFSM
from decoder import ConstrainedDecoder
from errors import FileFormatError, DecoderError, FSMError


class FunctionCallingPipeline:
    """
    Orchestrates the full function calling process:
    1. Loads prompts and function definitions
    2. Uses LLM to predict function calls with constrained decoding
    3. Outputs structured JSON results
    """

    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        self.llm = Small_LLM_Model(model_name=model_name)
        self.decoder = ConstrainedDecoder(self.llm)
        self.fsm = FunctionCallingFSM()

    def load_json_file(self, path: str) -> Any:
        """Load and parse a JSON file, with error handling."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileFormatError(f"Invalid JSON file: {path}") from e
        except FileNotFoundError as e:
            raise FileFormatError(f"File not found: {path}") from e

    def save_json_file(self, data: Any, path: str) -> None:
        """Write JSON to a file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def run(
        self, prompts_path: str, functions_path: str, output_path: str
    ) -> None:
        """Process all prompts and generate function call outputs."""
        prompts = self.load_json_file(prompts_path)
        functions = self.load_json_file(functions_path)

        results: List[Dict[str, Any]] = []

        for entry in prompts:
            prompt_text = entry.get("prompt")
            if not prompt_text:
                continue  # skip empty prompts

            try:
                # FSM determines which function the prompt might call
                valid_functions = self.fsm.get_allowed_functions(prompt_text,
                                                                 functions)

                # Constrained decoder generates JSON for function name + args
                result = self.decoder.decode_prompt(
                    prompt_text, valid_functions
                )

                results.append(result)
            except (DecoderError, FSMError) as e:
                results.append(
                    {
                        "prompt": prompt_text,
                        "fn_name": None,
                        "args": {},
                        "error": str(e)
                    }
                )

        # Save final structured output
        self.save_json_file(results, output_path)
