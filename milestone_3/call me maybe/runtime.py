import json
from dataclasses import dataclass
from typing import Dict, List
from .fsm import FSMState
from .schema import FunctionSchema, SchemaRegistry


def load_schema(path: str) -> SchemaRegistry:
    with open(path, "r") as f:
        raw = json.load(f)

    functions = {}

    for fn in raw:
        functions[fn["fn_name"]] = FunctionSchema(
            name=fn["fn_name"],
            arg_names=fn["args_names"],
            arg_types=fn["args_types"],
            return_type=fn["return_type"],
        )

    return SchemaRegistry(functions=functions)


@dataclass
class FunctionDef:
    name: str
    arg_names: List[str]
    arg_types: Dict[str, str]


def load_function_defs(path: str) -> Dict[str, FunctionDef]:
    with open(path, "r") as f:
        raw = json.load(f)

    functions = {}
    for fn in raw:
        functions[fn["fn_name"]] = FunctionDef(
            name=fn["fn_name"],
            arg_names=fn["args_names"],
            arg_types=fn["args_types"],
        )
    return functions


def load_prompts(path: str) -> List[str]:
    with open(path, "r") as f:
        raw = json.load(f)

    return [item["prompt"] for item in raw]


@dataclass
class GenerationContext:
    state: FSMState
    selected_function: str | None
    used_args: set[str]
    current_arg: str | None
    buffer: str  # partial string/number buffer


def init_context() -> GenerationContext:
    return GenerationContext(
        state=FSMState.START,
        selected_function=None,
        used_args=set(),
        current_arg=None,
        buffer="",
    )
