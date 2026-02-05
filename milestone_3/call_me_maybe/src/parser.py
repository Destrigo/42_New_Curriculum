import json
from typing import List
from .models import (
    validate_function_definitions,
    validate_prompts
)


class Parser:
    """Parser for input files with Pydantic validation."""

    def __init__(
        self,
        file_input_prompt: str,
        file_input_func: str
    ) -> None:
        """Initialize parser and load input files.
        Args:
            file_input_prompt: Path to prompts JSON file
            file_input_func: Path to function definitions JSON file
        Raises:
            FileNotFoundError: If input file not found
            ValueError: If validation fails
        """
        self.prompt_list: List[str] = self._parse_prompts(file_input_prompt)
        self.func_list: List[str] = self._parse_func(file_input_func)

    def _parse_func(self, file_input_func: str) -> List[str]:
        """Parse and validate function definitions.
        Args:
            file_input_func: Path to function definitions JSON file
        Returns:
            List of function definition JSON strings
        Raises:
            FileNotFoundError: If file not found
            ValueError: If validation fails
            json.JSONDecodeError: If JSON is malformed
        """
        func_list: List[str] = []
        try:
            with open(file_input_func, "r", encoding="utf-8") as file_func:
                raw_data = json.load(file_func)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Function definitions file not found: {file_input_func}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in function definitions: {e.msg}",
                e.doc,
                e.pos
            )

        # Validate with Pydantic
        validation_result = validate_function_definitions(raw_data)

        if not validation_result.valid:
            errors_str = "; ".join(validation_result.errors)
            raise ValueError(f"Function definition "
                             f"validation failed: {errors_str}")

        # Convert validated models back to JSON strings
        for func_def in validation_result.data:
            # Use model_dump() for Pydantic v2
            func_dict = func_def.model_dump()
            func_string = json.dumps(func_dict, separators=(",", ":"))
            func_list.append(func_string)
        return func_list

    def _parse_prompts(self, file_input_prompt: str) -> List[str]:
        """Parse and validate prompts.
        Args:
            file_input_prompt: Path to prompts JSON file
        Returns:
            List of prompt strings
        Raises:
            FileNotFoundError: If file not found
            ValueError: If validation fails
            json.JSONDecodeError: If JSON is malformed
        """
        try:
            with open(file_input_prompt, "r", encoding="utf-8") as file_prompt:
                raw_data = json.load(file_prompt)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Prompts file not found: {file_input_prompt}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in prompts file: {e.msg}",
                e.doc,
                e.pos
            )

        # Validate with Pydantic
        validation_result = validate_prompts(raw_data)

        if not validation_result.valid:
            errors_str = "; ".join(validation_result.errors)
            raise ValueError(f"Prompt validation failed: {errors_str}")

        # Extract prompt strings from validated models
        prompt_list = [p.prompt for p in validation_result.data]
        return prompt_list
