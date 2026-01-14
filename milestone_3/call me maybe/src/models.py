from enum import Enum, auto


class State(Enum):
    START = auto()
    AFTER_OPEN_BRACE = auto()
    AFTER_PROMPT_KEY = auto()
    AFTER_PROMPT_COLON = auto()
    IN_PROMPT_VALUE = auto()
    NEED_COMMA_1 = auto()
    AFTER_COMMA_1 = auto()
    AFTER_FN_NAME_KEY = auto()
    AFTER_FN_NAME_COLON = auto()
    IN_FN_NAME_VALUE = auto()
    CLOSE_QUOTE_FN_NAME = auto()
    NEED_COMMA_2 = auto()
    AFTER_COMMA_2 = auto()
    AFTER_ARGS_KEY = auto()
    AFTER_ARGS_COLON = auto()
    AFTER_ARGS_OPEN_BRACE = auto()
    IN_ARG_NAME = auto()
    CLOSE_QUOTE_ARG_NAME = auto()  # NEW: Need closing quote after arg name
    NEED_ARG_COLON = auto()
    AFTER_ARG_COLON = auto()
    IN_ARG_VALUE = auto()
    NEED_ARG_SEPARATOR = auto()
    AFTER_ARG_COMMA = auto()
    AFTER_ARGS_CLOSE_BRACE = auto()
    END = auto()


# class FSM:
#     """Finite State Machine representation"""
#     def __init__(self, functions: list[Function] = None, tokenizer=None) -> None:
#         self.state = State.START
#         self.functions = functions or []
#         self.tokenizer = tokenizer
        
#         self.selected_function = None
#         self.seen_args = set()
#         self.token_buffer = []
#         self.current_arg_name = None
#         self.current_arg_type = None
        
#         # Pre-tokenize common patterns
#         self.tk_open_brace = tokenizer.encode("{", add_special_tokens=False)[0] if tokenizer else None
#         self.tk_close_brace = tokenizer.encode("}", add_special_tokens=False)[0] if tokenizer else None
#         self.tk_colon = tokenizer.encode(":", add_special_tokens=False)[0] if tokenizer else None
#         self.tk_comma = tokenizer.encode(",", add_special_tokens=False)[0] if tokenizer else None
        
#         # Tokenize the full keys with quotes
#         self.tk_prompt_key = tokenizer.encode('"prompt"', add_special_tokens=False) if tokenizer else []
#         self.tk_fn_name_key = tokenizer.encode('"fn_name"', add_special_tokens=False) if tokenizer else []
#         self.tk_args_key = tokenizer.encode('"args"', add_special_tokens=False) if tokenizer else []

#     def get_current_state(self) -> State:
#         return self.state

#     def get_allowed_token_ids(self) -> set[int]:
#         """Return allowed token IDs for current state"""
        
#         if self.state == State.START:
#             return {self.tk_open_brace}
        
#         elif self.state == State.AFTER_OPEN_BRACE:
#             if not self.token_buffer:
#                 return {self.tk_prompt_key[0]}
#             idx = len(self.token_buffer)
#             if idx < len(self.tk_prompt_key):
#                 return {self.tk_prompt_key[idx]}
#             return set()
        
#         elif self.state == State.AFTER_PROMPT_KEY:
#             return {self.tk_colon}
        
#         elif self.state == State.AFTER_PROMPT_COLON:
#             quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#             return set(quote_tokens)
        
#         elif self.state == State.IN_PROMPT_VALUE:
#             return set(range(self.tokenizer.vocab_size))
        
#         elif self.state == State.NEED_COMMA_1:
#             return {self.tk_comma}
        
#         elif self.state == State.AFTER_COMMA_1:
#             if not self.token_buffer:
#                 return {self.tk_fn_name_key[0]}
#             idx = len(self.token_buffer)
#             if idx < len(self.tk_fn_name_key):
#                 return {self.tk_fn_name_key[idx]}
#             return set()
        
#         elif self.state == State.AFTER_FN_NAME_KEY:
#             return {self.tk_colon}
        
#         elif self.state == State.AFTER_FN_NAME_COLON:
#             quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#             return set(quote_tokens)
        
#         elif self.state == State.IN_FN_NAME_VALUE:
#             if not self.token_buffer:
#                 return {func.tkname[0] for func in self.functions if func.tkname}
#             idx = len(self.token_buffer)
#             allowed = set()
#             for func in self.functions:
#                 if len(func.tkname) > idx and func.tkname[:idx] == self.token_buffer:
#                     allowed.add(func.tkname[idx])
#             return allowed
        
#         elif self.state == State.CLOSE_QUOTE_FN_NAME:
#             quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#             return set(quote_tokens)
        
#         elif self.state == State.NEED_COMMA_2:
#             return {self.tk_comma}
        
#         elif self.state == State.AFTER_COMMA_2:
#             if not self.token_buffer:
#                 return {self.tk_args_key[0]}
#             idx = len(self.token_buffer)
#             if idx < len(self.tk_args_key):
#                 return {self.tk_args_key[idx]}
#             return set()
        
#         elif self.state == State.AFTER_ARGS_KEY:
#             return {self.tk_colon}
        
#         elif self.state == State.AFTER_ARGS_COLON:
#             return {self.tk_open_brace}
        
#         elif self.state == State.AFTER_ARGS_OPEN_BRACE:
#             # Only allow closing brace if function has NO arguments
#             # Otherwise, must start with arg name
#             if self.selected_function and self.selected_function.args:
#                 # Function has args - must provide them
#                 quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#                 return set(quote_tokens)
#             else:
#                 # Function has no args - can close immediately
#                 allowed = {self.tk_close_brace}
#                 return allowed
        
#         elif self.state == State.IN_ARG_NAME:
#             if not self.token_buffer:
#                 remaining = [a for a in self.selected_function.args if a not in self.seen_args]
#                 allowed = set()
#                 for arg_name in remaining:
#                     for i, tkarg in enumerate(self.selected_function.tkargs):
#                         if self.selected_function.args[i] == arg_name and tkarg:
#                             allowed.add(tkarg[0])
#                             break
#                 return allowed
            
#             idx = len(self.token_buffer)
#             remaining = [a for a in self.selected_function.args if a not in self.seen_args]
#             allowed = set()
#             for arg_name in remaining:
#                 for i, tkarg in enumerate(self.selected_function.tkargs):
#                     if self.selected_function.args[i] == arg_name:
#                         if len(tkarg) > idx and tkarg[:idx] == self.token_buffer:
#                             allowed.add(tkarg[idx])
#                         break
#             return allowed
        
#         elif self.state == State.CLOSE_QUOTE_ARG_NAME:
#             quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#             return set(quote_tokens)
        
#         elif self.state == State.NEED_ARG_COLON:
#             return {self.tk_colon}
        
#         elif self.state == State.AFTER_ARG_COLON:
#             allowed = set()
#             if self.current_arg_type == "str":
#                 quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#                 allowed.update(quote_tokens)
#             elif self.current_arg_type in ["int", "float"]:
#                 # Allow digits, decimal point, minus sign, and also separators
#                 for char in "0123456789-.,}":
#                     tokens = self.tokenizer.encode(char, add_special_tokens=False)
#                     allowed.update(tokens)
#                 # Also allow space tokens
#                 space_tokens = self.tokenizer.encode(" ", add_special_tokens=False)
#                 allowed.update(space_tokens)
#             elif self.current_arg_type == "bool":
#                 true_tokens = self.tokenizer.encode("true", add_special_tokens=False)
#                 false_tokens = self.tokenizer.encode("false", add_special_tokens=False)
#                 allowed.add(true_tokens[0])
#                 allowed.add(false_tokens[0])
#             return allowed
        
#         elif self.state == State.IN_ARG_VALUE:
#             # Allow any reasonable token for the value
#             if self.current_arg_type == "str":
#                 # For strings, allow everything except we need to eventually hit closing quote
#                 return set(range(self.tokenizer.vocab_size))
#             elif self.current_arg_type in ["int", "float"]:
#                 # For numbers, allow digits, decimal, minus, and separators
#                 allowed = set()
#                 for char in "0123456789-., }":
#                     tokens = self.tokenizer.encode(char, add_special_tokens=False)
#                     allowed.update(tokens)
#                 return allowed
#             elif self.current_arg_type == "bool":
#                 # For booleans, we should have already consumed the value
#                 # Allow separators
#                 return {self.tk_comma, self.tk_close_brace}
#             return set(range(self.tokenizer.vocab_size))
        
#         elif self.state == State.NEED_ARG_SEPARATOR:
#             allowed = {self.tk_close_brace}
#             remaining = [a for a in self.selected_function.args if a not in self.seen_args]
#             if remaining:
#                 allowed.add(self.tk_comma)
#             return allowed
        
#         elif self.state == State.AFTER_ARG_COMMA:
#             quote_tokens = self.tokenizer.encode('"', add_special_tokens=False)
#             return set(quote_tokens)
        
#         elif self.state == State.AFTER_ARGS_CLOSE_BRACE:
#             return {self.tk_close_brace}
        
#         return set()

#     def consume_token_id(self, token_id: int) -> None:
#         """Process one token and update state"""
#         token_str = self.tokenizer.decode([token_id])
        
#         if self.state == State.START:
#             self.state = State.AFTER_OPEN_BRACE
#             self.token_buffer = []
        
#         elif self.state == State.AFTER_OPEN_BRACE:
#             self.token_buffer.append(token_id)
#             if self.token_buffer == self.tk_prompt_key:
#                 self.state = State.AFTER_PROMPT_KEY
#                 self.token_buffer = []
        
#         elif self.state == State.AFTER_PROMPT_KEY:
#             self.state = State.AFTER_PROMPT_COLON
        
#         elif self.state == State.AFTER_PROMPT_COLON:
#             self.state = State.IN_PROMPT_VALUE
        
#         elif self.state == State.IN_PROMPT_VALUE:
#             # Check if token contains closing quote
#             if '"' in token_str:
#                 # Check if comma is also in this token
#                 if ',' in token_str:
#                     # Token contains both " and , (e.g., "hello",)
#                     self.state = State.AFTER_COMMA_1
#                     self.token_buffer = []
#                 else:
#                     # Only closing quote, need comma next
#                     self.state = State.NEED_COMMA_1
        
#         elif self.state == State.NEED_COMMA_1:
#             self.state = State.AFTER_COMMA_1
#             self.token_buffer = []
        
#         elif self.state == State.AFTER_COMMA_1:
#             self.token_buffer.append(token_id)
#             if self.token_buffer == self.tk_fn_name_key:
#                 self.state = State.AFTER_FN_NAME_KEY
#                 self.token_buffer = []
        
#         elif self.state == State.AFTER_FN_NAME_KEY:
#             self.state = State.AFTER_FN_NAME_COLON
        
#         elif self.state == State.AFTER_FN_NAME_COLON:
#             self.state = State.IN_FN_NAME_VALUE
#             self.token_buffer = []
        
#         elif self.state == State.IN_FN_NAME_VALUE:
#             self.token_buffer.append(token_id)
#             for func in self.functions:
#                 if func.tkname == self.token_buffer:
#                     self.selected_function = func
#                     self.token_buffer = []
#                     # Need closing quote after function name
#                     self.state = State.CLOSE_QUOTE_FN_NAME
#                     return
        
#         elif self.state == State.CLOSE_QUOTE_FN_NAME:
#             # Should be closing quote, then need comma
#             self.state = State.NEED_COMMA_2
        
#         elif self.state == State.NEED_COMMA_2:
#             # Check if this token is just comma or contains comma
#             if ',' in token_str:
#                 # Move to AFTER_COMMA_2
#                 self.state = State.AFTER_COMMA_2
#                 self.token_buffer = []
#             else:
#                 # Unexpected - but try to recover
#                 self.state = State.AFTER_COMMA_2
#                 self.token_buffer = []
        
#         elif self.state == State.AFTER_COMMA_2:
#             self.token_buffer.append(token_id)
#             if self.token_buffer == self.tk_args_key:
#                 self.state = State.AFTER_ARGS_KEY
#                 self.token_buffer = []
        
#         elif self.state == State.AFTER_ARGS_KEY:
#             self.state = State.AFTER_ARGS_COLON
        
#         elif self.state == State.AFTER_ARGS_COLON:
#             self.state = State.AFTER_ARGS_OPEN_BRACE
        
#         elif self.state == State.AFTER_ARGS_OPEN_BRACE:
#             if token_id == self.tk_close_brace:
#                 self.state = State.AFTER_ARGS_CLOSE_BRACE
#             else:
#                 self.state = State.IN_ARG_NAME
#                 self.token_buffer = []
        
#         elif self.state == State.IN_ARG_NAME:
#             self.token_buffer.append(token_id)
#             remaining = [a for a in self.selected_function.args if a not in self.seen_args]
#             for arg_name in remaining:
#                 for i, tkarg in enumerate(self.selected_function.tkargs):
#                     if self.selected_function.args[i] == arg_name and tkarg == self.token_buffer:
#                         self.current_arg_name = arg_name
#                         self.current_arg_type = self.selected_function.types[arg_name]
#                         self.seen_args.add(arg_name)
#                         self.token_buffer = []
#                         # Need closing quote after arg name
#                         self.state = State.CLOSE_QUOTE_ARG_NAME
#                         return
        
#         elif self.state == State.CLOSE_QUOTE_ARG_NAME:
#             # Should be closing quote
#             self.state = State.NEED_ARG_COLON
        
#         elif self.state == State.NEED_ARG_COLON:
#             self.state = State.AFTER_ARG_COLON
        
#         elif self.state == State.AFTER_ARG_COLON:
#             self.state = State.IN_ARG_VALUE
        
#         elif self.state == State.IN_ARG_VALUE:
#             # For strings, look for closing quote
#             if self.current_arg_type == "str" and '"' in token_str:
#                 # Count how many closing braces are in the token
#                 brace_count = token_str.count('}')
                
#                 if brace_count >= 2:
#                     # Token has "}}  - both args close and outer close
#                     self.state = State.END
#                 elif brace_count == 1:
#                     # Token has "}  - only args close
#                     self.state = State.AFTER_ARGS_CLOSE_BRACE
#                 elif ',' in token_str:
#                     # Token has ",  - more args coming
#                     self.state = State.AFTER_ARG_COMMA
#                     self.token_buffer = []
#                 else:
#                     # Only closing quote, need separator
#                     self.state = State.NEED_ARG_SEPARATOR
#             elif self.current_arg_type in ["int", "float"]:
#                 # For numbers, check separators
#                 brace_count = token_str.count('}')
#                 if brace_count >= 2:
#                     self.state = State.END
#                 elif brace_count == 1:
#                     self.state = State.AFTER_ARGS_CLOSE_BRACE
#                 elif ',' in token_str:
#                     self.state = State.AFTER_ARG_COMMA
#                     self.token_buffer = []
#                 else:
#                     # Continue or need separator
#                     if any(c in token_str for c in ['}', ',']):
#                         self.state = State.NEED_ARG_SEPARATOR
#             elif self.current_arg_type == "bool":
#                 self.state = State.NEED_ARG_SEPARATOR
        
#         elif self.state == State.NEED_ARG_SEPARATOR:
#             if token_id == self.tk_comma:
#                 self.state = State.AFTER_ARG_COMMA
#             elif token_id == self.tk_close_brace:
#                 self.state = State.AFTER_ARGS_CLOSE_BRACE
#             else:
#                 # Token might contain both separator and other chars
#                 # Check what's in it
#                 if '}' in token_str:
#                     self.state = State.AFTER_ARGS_CLOSE_BRACE
#                 elif ',' in token_str:
#                     self.state = State.AFTER_ARG_COMMA
#                     self.token_buffer = []
        
#         elif self.state == State.AFTER_ARG_COMMA:
#             self.state = State.IN_ARG_NAME
#             self.token_buffer = []
        
#         elif self.state == State.AFTER_ARGS_CLOSE_BRACE:
#             self.state = State.END