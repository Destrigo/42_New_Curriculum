from dataclasses import dataclass
from typing import Dict, List, Literal


JSONType = Literal["float", "int", "str", "bool"]


@dataclass(frozen=True)
class FunctionSchema:
    """
    Represents a single callable function schema.
    """
    name: str
    arg_names: List[str]
    arg_types: Dict[str, JSONType]
    return_type: JSONType


@dataclass
class SchemaRegistry:
    """
    Holds all function schemas loaded from function_definitions.json.
    """
    functions: Dict[str, FunctionSchema]

    def get_function_names(self) -> List[str]:
        return list(self.functions.keys())

    def get(self, name: str) -> FunctionSchema:
        return self.functions[name]
