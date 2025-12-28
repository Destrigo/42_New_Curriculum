from __future__ import annotations

from typing import Dict, List, Literal, Set

from pydantic import BaseModel


# ==========================================================
# Function schema models
# ==========================================================

ArgType = Literal["float", "int", "str", "bool"]


class FunctionArgument(BaseModel):
    name: str
    type: ArgType


class FunctionDefinition(BaseModel):
    fn_name: str
    args_names: List[str]
    args_types: Dict[str, ArgType]
    return_type: ArgType

    def argument_type(self, arg_name: str) -> ArgType:
        if arg_name not in self.args_types:
            raise KeyError(f"Unknown argument: {arg_name}")
        return self.args_types[arg_name]


# ==========================================================
# Function registry
# ==========================================================

class FunctionRegistry(BaseModel):
    functions: Dict[str, FunctionDefinition]

    @classmethod
    def from_json(cls, raw: list[dict]) -> "FunctionRegistry":
        functions: Dict[str, FunctionDefinition] = {}

        for item in raw:
            fn = FunctionDefinition(**item)
            functions[fn.fn_name] = fn

        return cls(functions=functions)

    def get(self, fn_name: str) -> FunctionDefinition:
        if fn_name not in self.functions:
            raise KeyError(f"Function not found: {fn_name}")
        return self.functions[fn_name]

    def function_names(self) -> Set[str]:
        return set(self.functions.keys())


# ==========================================================
# Token constraints by argument type
# ==========================================================

class TypeConstraints:
    """
    Maps argument types to allowed JSON token fragments.
    """

    @staticmethod
    def allowed_tokens(arg_type: ArgType) -> Set[str]:
        if arg_type == "str":
            return TypeConstraints._string_tokens()
        if arg_type in {"int", "float"}:
            return TypeConstraints._number_tokens()
        if arg_type == "bool":
            return {"true", "false"}

        raise ValueError(f"Unsupported argument type: {arg_type}")

    # ------------------------------------------------------

    @staticmethod
    def _string_tokens() -> Set[str]:
        """
        Strings must be quoted in JSON.
        Content is unconstrained at this level.
        """
        return {'"'}

    @staticmethod
    def _number_tokens() -> Set[str]:
        """
        Digits and decimal separator.
        """
        return set("0123456789.")  # FSM controls placement
