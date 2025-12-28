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
    
    EXPECT_PROMPT_KEY = auto()
    IN_PROMPT_KEY = auto()
    AFTER_PROMPT_KEY = auto()
    PROMPT_COLON = auto()
    PROMPT_VALUE_QUOTE_START = auto()
    IN_PROMPT_VALUE = auto()
    PROMPT_VALUE_QUOTE_END = auto()
    AFTER_PROMPT_VALUE = auto()
    
    EXPECT_FN_KEY = auto()
    IN_FN_KEY = auto()
    AFTER_FN_KEY = auto()
    FN_COLON = auto()
    FN_VALUE_QUOTE_START = auto()
    IN_FN_VALUE = auto()
    FN_VALUE_QUOTE_END = auto()
    AFTER_FN_VALUE = auto()
    
    EXPECT_ARGS_KEY = auto()
    IN_ARGS_KEY = auto()
    AFTER_ARGS_KEY = auto()
    ARGS_COLON = auto()
    ARGS_OPEN_OBJECT = auto()
    
    EXPECT_ARG_KEY = auto()
    IN_ARG_KEY = auto()
    AFTER_ARG_KEY = auto()
    ARG_COLON = auto()
    
    ARG_VALUE_QUOTE_START = auto()
    IN_ARG_STRING_VALUE = auto()
    ARG_VALUE_QUOTE_END = auto()
    IN_ARG_NUMBER_VALUE = auto()
    IN_ARG_BOOL_VALUE = auto()
    
    AFTER_ARG_VALUE = auto()
    ARGS_CLOSE_OBJECT = auto()
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

    def __init__(self, registry: FunctionRegistry, original_prompt: str):
        self.state: State = State.START
        self.registry = registry
        self.original_prompt = original_prompt
        
        self.current_function: Optional[str] = None
        self.current_arg: Optional[str] = None
        self.remaining_args: list[str] = []
        
        # Track what we're building
        self.current_string_builder: list[str] = []
        self.current_number_builder: list[str] = []
        self.current_bool_builder: list[str] = []

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

            case State.EXPECT_PROMPT_KEY:
                return {'"'}

            case State.IN_PROMPT_KEY:
                # Building "prompt"
                expected = "prompt"[len(self.current_string_builder):]
                if expected:
                    return {expected[0]}
                return {'"'}
            
            case State.AFTER_PROMPT_KEY:
                return {'"'}
            
            case State.PROMPT_COLON:
                return {":"}
            
            case State.PROMPT_VALUE_QUOTE_START:
                return {'"'}
            
            case State.IN_PROMPT_VALUE:
                # Allow any character or closing quote
                return {self.original_prompt[len(self.current_string_builder)]} if len(self.current_string_builder) < len(self.original_prompt) else {'"'}
            
            case State.PROMPT_VALUE_QUOTE_END:
                return {'"'}
            
            case State.AFTER_PROMPT_VALUE:
                return {","}
            
            case State.EXPECT_FN_KEY:
                return {'"'}
            
            case State.IN_FN_KEY:
                expected = "fn_name"[len(self.current_string_builder):]
                if expected:
                    return {expected[0]}
                return {'"'}
            
            case State.AFTER_FN_KEY:
                return {'"'}
            
            case State.FN_COLON:
                return {":"}
            
            case State.FN_VALUE_QUOTE_START:
                return {'"'}
            
            case State.IN_FN_VALUE:
                # Allow valid function names
                fn_names = self.registry.function_names()
                possible_next = set()
                current = "".join(self.current_string_builder)
                
                for fn in fn_names:
                    if fn.startswith(current) and len(fn) > len(current):
                        possible_next.add(fn[len(current)])
                
                # Can also close the string if we have a complete function name
                if current in fn_names:
                    possible_next.add('"')
                
                return possible_next
            
            case State.FN_VALUE_QUOTE_END:
                return {'"'}
            
            case State.AFTER_FN_VALUE:
                return {","}
            
            case State.EXPECT_ARGS_KEY:
                return {'"'}
            
            case State.IN_ARGS_KEY:
                expected = "args"[len(self.current_string_builder):]
                if expected:
                    return {expected[0]}
                return {'"'}
            
            case State.AFTER_ARGS_KEY:
                return {'"'}
            
            case State.ARGS_COLON:
                return {":"}
            
            case State.ARGS_OPEN_OBJECT:
                return {"{"}
            
            case State.EXPECT_ARG_KEY:
                if not self.remaining_args:
                    return {"}"}
                return {'"'}
            
            case State.IN_ARG_KEY:
                # Allow building argument names
                possible_next = set()
                current = "".join(self.current_string_builder)
                
                for arg in self.remaining_args:
                    if arg.startswith(current) and len(arg) > len(current):
                        possible_next.add(arg[len(current)])
                
                if current in self.remaining_args:
                    possible_next.add('"')
                
                return possible_next
            
            case State.AFTER_ARG_KEY:
                return {'"'}
            
            case State.ARG_COLON:
                return {":"}
            
            case State.ARG_VALUE_QUOTE_START:
                return {'"'}
            
            case State.IN_ARG_STRING_VALUE:
                # Allow any printable characters or close quote
                import string
                return set(string.printable.replace('"', '').replace('\\', '')) | {'"'}
            
            case State.ARG_VALUE_QUOTE_END:
                return {'"'}
            
            case State.IN_ARG_NUMBER_VALUE:
                # Allow digits, decimal point, minus sign
                tokens = set("0123456789")
                if not self.current_number_builder:
                    tokens.add("-")
                if "." not in self.current_number_builder:
                    tokens.add(".")
                # Can also end with comma or close brace
                if self.current_number_builder:
                    tokens.add(",")
                    if not self.remaining_args:
                        tokens.add("}")
                return tokens
            
            case State.IN_ARG_BOOL_VALUE:
                # Building "true" or "false"
                current = "".join(self.current_bool_builder)
                if current in ["t", "tr", "tru"]:
                    return {"true"[len(current)]}
                elif current in ["f", "fa", "fal", "fals"]:
                    return {"false"[len(current)]}
                elif current == "true" or current == "false":
                    tokens = {","}
                    if not self.remaining_args:
                        tokens.add("}")
                    return tokens
                return set()
            
            case State.AFTER_ARG_VALUE:
                if self.remaining_args:
                    return {","}
                return {"}"}
            
            case State.ARGS_CLOSE_OBJECT:
                return {"}"}
            
            case State.CLOSE_OBJECT:
                return {"}"}
            
            case State.END:
                return set()
            
            case _:
                raise RuntimeError(f"Unhandled FSM state: {self.state}")

    # ------------------------------------------------------

    def advance(self, token: str) -> None:
        """
        Advance the FSM state based on the emitted token.
        """
        match self.state:
            case State.START if token == "{":
                self.state = State.OPEN_OBJECT
            
            case State.OPEN_OBJECT if token == '"':
                self.state = State.EXPECT_PROMPT_KEY
                self.current_string_builder = []
            
            case State.EXPECT_PROMPT_KEY if token == '"':
                self.state = State.IN_PROMPT_KEY
            
            case State.IN_PROMPT_KEY:
                if token == '"':
                    self.state = State.PROMPT_COLON
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.PROMPT_COLON if token == ":":
                self.state = State.PROMPT_VALUE_QUOTE_START
            
            case State.PROMPT_VALUE_QUOTE_START if token == '"':
                self.state = State.IN_PROMPT_VALUE
                self.current_string_builder = []
            
            case State.IN_PROMPT_VALUE:
                if token == '"':
                    self.state = State.AFTER_PROMPT_VALUE
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.AFTER_PROMPT_VALUE if token == ",":
                self.state = State.EXPECT_FN_KEY
            
            case State.EXPECT_FN_KEY if token == '"':
                self.state = State.IN_FN_KEY
                self.current_string_builder = []
            
            case State.IN_FN_KEY:
                if token == '"':
                    self.state = State.FN_COLON
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.FN_COLON if token == ":":
                self.state = State.FN_VALUE_QUOTE_START
            
            case State.FN_VALUE_QUOTE_START if token == '"':
                self.state = State.IN_FN_VALUE
                self.current_string_builder = []
            
            case State.IN_FN_VALUE:
                if token == '"':
                    fn_name = "".join(self.current_string_builder)
                    self.current_function = fn_name
                    fn = self.registry.get(fn_name)
                    self.remaining_args = list(fn.args_names)
                    self.state = State.AFTER_FN_VALUE
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.AFTER_FN_VALUE if token == ",":
                self.state = State.EXPECT_ARGS_KEY
            
            case State.EXPECT_ARGS_KEY if token == '"':
                self.state = State.IN_ARGS_KEY
                self.current_string_builder = []
            
            case State.IN_ARGS_KEY:
                if token == '"':
                    self.state = State.ARGS_COLON
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.ARGS_COLON if token == ":":
                self.state = State.ARGS_OPEN_OBJECT
            
            case State.ARGS_OPEN_OBJECT if token == "{":
                if self.remaining_args:
                    self.state = State.EXPECT_ARG_KEY
                else:
                    self.state = State.ARGS_CLOSE_OBJECT
            
            case State.EXPECT_ARG_KEY:
                if token == '"':
                    self.state = State.IN_ARG_KEY
                    self.current_string_builder = []
                elif token == "}":
                    self.state = State.CLOSE_OBJECT
            
            case State.IN_ARG_KEY:
                if token == '"':
                    arg_name = "".join(self.current_string_builder)
                    self.current_arg = arg_name
                    self.state = State.ARG_COLON
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.ARG_COLON if token == ":":
                # Determine type and go to appropriate state
                fn = self.registry.get(self.current_function)
                arg_type = fn.argument_type(self.current_arg)
                
                if arg_type == "str":
                    self.state = State.ARG_VALUE_QUOTE_START
                elif arg_type in ["int", "float"]:
                    self.state = State.IN_ARG_NUMBER_VALUE
                    self.current_number_builder = []
                elif arg_type == "bool":
                    self.state = State.IN_ARG_BOOL_VALUE
                    self.current_bool_builder = []
            
            case State.ARG_VALUE_QUOTE_START if token == '"':
                self.state = State.IN_ARG_STRING_VALUE
                self.current_string_builder = []
            
            case State.IN_ARG_STRING_VALUE:
                if token == '"':
                    self.remaining_args.remove(self.current_arg)
                    self.current_arg = None
                    self.state = State.AFTER_ARG_VALUE
                    self.current_string_builder = []
                else:
                    self.current_string_builder.append(token)
            
            case State.IN_ARG_NUMBER_VALUE:
                if token in [",", "}"]:
                    self.remaining_args.remove(self.current_arg)
                    self.current_arg = None
                    self.current_number_builder = []
                    if token == ",":
                        self.state = State.EXPECT_ARG_KEY
                    else:
                        self.state = State.CLOSE_OBJECT
                else:
                    self.current_number_builder.append(token)
            
            case State.IN_ARG_BOOL_VALUE:
                if token in [",", "}"]:
                    self.remaining_args.remove(self.current_arg)
                    self.current_arg = None
                    self.current_bool_builder = []
                    if token == ",":
                        self.state = State.EXPECT_ARG_KEY
                    else:
                        self.state = State.CLOSE_OBJECT
                else:
                    self.current_bool_builder.append(token)
            
            case State.AFTER_ARG_VALUE:
                if token == ",":
                    self.state = State.EXPECT_ARG_KEY
                elif token == "}":
                    self.state = State.CLOSE_OBJECT
            
            case State.CLOSE_OBJECT if token == "}":
                self.state = State.END
            
            case _:
                raise RuntimeError(
                    f"Invalid transition: state={self.state}, token={token}"
                )