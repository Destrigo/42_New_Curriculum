from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Literal
from pydantic import BaseModel, ValidationError, field_validator


PrimitiveType = Literal["string", "number", "boolean"]


class ArgumentDefinition(BaseModel):
    type: PrimitiveType


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ArgumentDefinition]
    returns: ArgumentDefinition

    @field_validator("parameters")
    @classmethod
    def non_empty_parameters(cls,
                             value: Dict[str, ArgumentDefinition]
                             ) -> Dict[str, ArgumentDefinition]:
        if not value:
            raise ValueError("Function must define at least one parameter")
        return value


class FunctionSchema(BaseModel):
    functions: Dict[str, FunctionDefinition]

    @classmethod
    def from_json_file(cls, path: Path) -> "FunctionSchema":
        """
        Load and validate function definitions from a JSON file.
        """
        try:
            raw = json.loads(path.read_text())
        except FileNotFoundError:
            raise RuntimeError(f"Function definition file not found: {path}")
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid JSON in function"
                               f" definition file: {exc}") from exc

        if not isinstance(raw, list):
            raise RuntimeError("Function definition file "
                               "must contain a JSON array")

        functions: Dict[str, FunctionDefinition] = {}

        for item in raw:
            try:
                fn = FunctionDefinition.model_validate(item)
            except ValidationError as exc:
                raise RuntimeError("Invalid function "
                                   f"definition: {exc}") from exc

            if fn.name in functions:
                raise RuntimeError("Duplicate function "
                                   f"name detected: {fn.name}")

            functions[fn.name] = fn

        if not functions:
            raise RuntimeError("No valid function definitions found")

        return cls(functions=functions)

    def get_function(self, name: str) -> FunctionDefinition:
        """
        Retrieve a function definition by name.
        """
        try:
            return self.functions[name]
        except KeyError as exc:
            raise RuntimeError(f"Unknown function requested: {name}") from exc

    def list_function_names(self) -> list[str]:
        """
        Return all valid function names.
        """
        return list(self.functions.keys())
