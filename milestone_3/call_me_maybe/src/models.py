"""
Pydantic models for input/output validation.

Provides runtime validation for:
- Function definitions (input)
- Prompts (input)
- Function call results (output)
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Union


class FunctionDefinition(BaseModel):
    """Schema for function definition input."""
    fn_name: str = Field(..., min_length=1, description="Function name")
    args_names: List[str] = Field(default_factory=list,
                                  description="Argument names")
    args_types: Dict[str, str] = Field(default_factory=dict,
                                       description="Argument types")
    return_type: str = Field(..., min_length=1, description="Return type")

    @field_validator('fn_name')
    @classmethod
    def validate_fn_name(cls, v: str) -> str:
        """Validate function name format."""
        if not v.startswith('fn_'):
            raise ValueError(f"Function name must start with 'fn_': {v}")
        return v

    @field_validator('args_types')
    @classmethod
    def validate_args_types(cls, v: Dict[str, str],
                            info: Any) -> Dict[str, str]:
        """Validate that args_types keys match args_names."""
        # Access args_names from the data being validated
        args_names = info.data.get('args_names', [])
        for arg_name in args_names:
            if arg_name not in v:
                raise ValueError(f"Missing type for argument: {arg_name}")
        return v


class PromptInput(BaseModel):
    """Schema for prompt input."""
    prompt: str = Field(..., min_length=1, max_length=1000,
                        description="User prompt")

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate prompt is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace")
        return v


class FunctionCallOutput(BaseModel):
    """Schema for function call output."""
    prompt: str = Field(..., description="Original prompt")
    fn_name: str = Field(..., description="Selected function name")
    args: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict,
        description="Function arguments"
    )

    @field_validator('fn_name')
    @classmethod
    def validate_fn_name(cls, v: str) -> str:
        """Validate function name format."""
        if not v.startswith('fn_'):
            raise ValueError(f"Function name must start with 'fn_': {v}")
        return v


class ValidationResult(BaseModel):
    """Result of validation operation."""
    valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list,
                              description="Validation errors")
    data: Any = Field(default=None, description="Validated data if successful")


def validate_function_definitions(raw_data: List[Dict]) -> ValidationResult:
    """Validate a list of function definitions.
    Args:
        raw_data: List of raw dictionaries from JSON
    Returns:
        ValidationResult with validated FunctionDefinition objects
    """
    errors: List[str] = []
    validated: List[FunctionDefinition] = []
    for i, item in enumerate(raw_data):
        try:
            func_def = FunctionDefinition(**item)
            validated.append(func_def)
        except Exception as e:
            errors.append(f"Function {i+1}: {str(e)}")
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        data=validated if not errors else None
    )


def validate_prompts(raw_data: List[Dict]) -> ValidationResult:
    """Validate a list of prompts.
    Args:
        raw_data: List of raw dictionaries or strings from JSON
    Returns:
        ValidationResult with validated PromptInput objects
    """
    errors: List[str] = []
    validated: List[PromptInput] = []
    for i, item in enumerate(raw_data):
        try:
            if isinstance(item, str):
                prompt_input = PromptInput(prompt=item)
            elif isinstance(item, dict) and "prompt" in item:
                prompt_input = PromptInput(**item)
            else:
                raise ValueError(f"Invalid prompt format: {type(item)}")
            validated.append(prompt_input)
        except Exception as e:
            errors.append(f"Prompt {i+1}: {str(e)}")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        data=validated if not errors else None
    )


def validate_output(raw_data: Dict) -> ValidationResult:
    """Validate a single output object.
    Args:
        raw_data: Raw dictionary for output
    Returns:
        ValidationResult with validated FunctionCallOutput object
    """
    errors: List[str] = []
    validated = None

    try:
        validated = FunctionCallOutput(**raw_data)
    except Exception as e:
        errors.append(str(e))

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        data=validated
    )
