from __future__ import annotations

from enum import Enum, auto
from typing import Optional, Set

from models import FunctionRegistry, TypeConstraints, ArgType


# ==========================================================
# FSM states
# ==========================================================

class State(Enum):
    START = auto()
    OPEN_OBJECT = auto()

    KEY_PROMPT = auto()
    VALUE_PROMPT = auto()

    KEY_FN_NAME = auto()
    VALUE_FN_NAME = auto()

    KEY_ARGS = auto()
    OPEN_ARGS = auto()

    ARG_KEY = auto()
    ARG_VALUE = auto()
    BETWEEN_ARGS = auto()

    CLOSE_ARGS = auto()
    CLOSE_OBJECT = auto()
    END = auto()


# ==========================================================
# JSON FSM
# ==========================================================

class JSONFSM:
    """
    Finite State Machine controlling valid JSON generation
    for function calling output.
    """

    def __init__(self, registry: FunctionRegistry):
        self.state: State = State.START
        self.registry = registry

        self.current_function: Optional[str] = None
        self.current_arg: Optional[str] = None
        self.remaining_args: list[str] = []

    # ------------------------------------------------------

    def allowed_tokens(self) -> Set[str]:
        """
        Return the set of allowed token strings
        given the current FSM state.
        """
        match self.state:
            case State.START:
                return {"{"}

            case State.OPEN_OBJECT:
                return {'"'}

            case State.KEY_PROMPT:
                return {'prompt'}

            case State.VALUE_PROMPT:
                return {'"'}

            case State.KEY_FN_NAME:
                return {'fn_name'}

            case State.VALUE_FN_NAME:
                return {'"'}

            case State.KEY_ARGS:
                return {'args'}

            case State.OPEN_ARGS:
                return {"{"}

            case State.ARG_KEY:
                return {'"'}

            case State.ARG_VALUE:
                return self._allowed_arg_value_tokens()

            case State.BETWEEN_ARGS:
                return {",", "}"}

            case State.CLOSE_ARGS:
                return {"}"}

            case State.CLOSE_OBJECT:
                return {"}"}

            case State.END:
                return set()

            case _:
                raise RuntimeError(f"Unhandled FSM state: {self.state}")

    # ------------------------------------------------------

    def _allowed_arg_value_tokens(self) -> Set[str]:
        if not self.current_function or not self.current_arg:
            raise RuntimeError("ARG_VALUE without active function/arg")

        fn = self.registry.get(self.current_function)
        arg_type: ArgType = fn.argument_type(self.current_arg)

        return TypeConstraints.allowed_tokens(arg_type)

    # ------------------------------------------------------

    def advance(self, token: str) -> None:
        """
        Advance the FSM state based on the emitted token.
        """
        match self.state:
            case State.START if token == "{":
                self.state = State.OPEN_OBJECT

            case State.OPEN_OBJECT if token == '"':
                self.state = State.KEY_PROMPT

            case State.KEY_PROMPT:
                self.state = State.VALUE_PROMPT

            case State.VALUE_PROMPT:
                self.state = State.KEY_FN_NAME

            case State.KEY_FN_NAME:
                self.state = State.VALUE_FN_NAME

            case State.VALUE_FN_NAME:
                self.current_function = token
                fn = self.registry.get(token)
                self.remaining_args = list(fn.args_names)
                self.state = State.KEY_ARGS

            case State.KEY_ARGS:
                self.state = State.OPEN_ARGS

            case State.OPEN_ARGS if token == "{":
                self.state = State.ARG_KEY

            case State.ARG_KEY:
                self.current_arg = token
                self.state = State.ARG_VALUE

            case State.ARG_VALUE:
                self.remaining_args.remove(self.current_arg)
                self.current_arg = None
                self.state = State.BETWEEN_ARGS

            case State.BETWEEN_ARGS if token == ",":
                self.state = State.ARG_KEY

            case State.BETWEEN_ARGS if token == "}":
                self.state = State.CLOSE_OBJECT

            case State.CLOSE_OBJECT if token == "}":
                self.state = State.END

            case _:
                raise RuntimeError(
                    f"Invalid transition: state={self.state}, token={token}"
                )
