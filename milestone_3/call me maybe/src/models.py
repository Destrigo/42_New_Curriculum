from enum import Enum, auto


class State(Enum):
    START = auto()           # Beginning, expecting "{"
    OPEN_OBJECT = auto()     # After "{", expecting first key
    KEY_PROMPT = auto()      # Expecting "prompt"
    COLON_PROMPT = auto()    # After "prompt", expecting ":"
    VALUE_PROMPT = auto()    # After ":", expecting the prompt string value
    COMMA_1 = auto()         # After prompt value, expecting ","
    KEY_FN_NAME = auto()     # Expecting "fn_name"
    COLON_FN_NAME = auto()   # After "fn_name", expecting ":"
    VALUE_FN_NAME = auto()   # After ":", expecting function name string
    COMMA_2 = auto()         # After fn_name value, expecting ","
    KEY_ARGS = auto()        # Expecting "args"
    COLON_ARGS = auto()      # After "args", expecting ":"
    OPEN_ARGS = auto()       # After ":", expecting "{"
    ARG_KEY = auto()         # Inside args object, expecting argument name
    COLON_ARG = auto()       # After arg name, expecting ":"
    ARG_VALUE = auto()       # After ":", argument value (int/float/str/bool)
    BETWEEN_ARGS = auto()    # After arg value, expecting "," or "}"
    CLOSE_ARGS = auto()      # After "}", expecting "}"
    END = auto()


class Function:
    """Function representation"""
    def __init__(self,
                 name: str,
                 args: list,
                 types: dict,
                 return_type: str) -> None:
        self.name = name
        self.tkname = []  # tokenized name (list of token IDs)
        self.args = args  # list of argument names
        self.tkargs = []  # list of tokenized argument names (each is list of token IDs)
        self.types = types  # dict of arg_name -> type_name
        self.tktypes = {}  # dict of arg_name -> tokenized type_name
        self.return_type = return_type
        self.tkreturn_type = []  # tokenized return type


class FSM:
    """Finite State Machine representation - works with token IDs"""
    def __init__(self, functions: list[Function] = None, tokenizer=None) -> None:
        self.state = State.START
        self.functions = functions or []
        self.tokenizer = tokenizer
        
        # Track which function was selected
        self.selected_function = None
        # Track which arguments we've seen so far
        self.seen_args = set()
        # Track partial token matching for multi-token sequences
        self.token_buffer = []
        self.target_tokens = []  # tokens we're trying to match
        self.current_arg_name = None
        
        # Pre-encode fixed tokens
        self.fixed_tokens = {}
        if tokenizer:
            self.fixed_tokens["{"] = tokenizer.encode("{",
                                                      add_special_tokens=False)
            self.fixed_tokens["}"] = tokenizer.encode("}",
                                                      add_special_tokens=False)
            self.fixed_tokens[":"] = tokenizer.encode(":",
                                                      add_special_tokens=False)
            self.fixed_tokens[","] = tokenizer.encode(",",
                                                      add_special_tokens=False)
            self.fixed_tokens['"'] = tokenizer.encode('"', add_special_tokens=False)
            self.fixed_tokens['fn_name'] = tokenizer.encode('fn_name', add_special_tokens=False)
            self.fixed_tokens['prompt'] = tokenizer.encode('prompt', add_special_tokens=False)
            self.fixed_tokens['args'] = tokenizer.encode('args', add_special_tokens=False)
            self.fixed_tokens["true"] = tokenizer.encode("true", add_special_tokens=False)
            self.fixed_tokens["false"] = tokenizer.encode("false", add_special_tokens=False)

    def get_current_state(self) -> State:
        return self.state

    def get_allowed_token_ids(self) -> set[int]:
        """Return set of allowed token IDs based on current state and context"""
        if self.state == State.START:
            return set(self.fixed_tokens["{"])

        if self.state == State.OPEN_OBJECT:
            if not self.token_buffer:
                # Return first token of "prompt"
                return {self.fixed_tokens['prompt'][0]}
            else:
                # Continue matching "prompt"
                return {self.fixed_tokens['prompt'][len(self.token_buffer)]}

        # For COLON_PROMPT, COLON_FN_NAME, COLON_ARGS, COLON_ARG: expect ":"
        if self.state in [State.COLON_PROMPT,
                          State.COLON_FN_NAME,
                          State.COLON_ARGS,
                          State.COLON_ARG]:
            return set(self.fixed_tokens[":"])

        # For COMMA_1, COMMA_2: expect ","
        if self.state in [State.COMMA_1,
                          State.COMMA_2]:
            return set(self.fixed_tokens[","])

        # For KEY_FN_NAME: expect '"fn_name"'
        if self.state == State.KEY_FN_NAME:
            if not self.token_buffer:
                return set(self.fixed_tokens['"'])          # opening quote
            elif self.token_buffer == ['"']:
                return {self.fixed_tokens['fn_name'][0]}    # identifier
            elif len(self.token_buffer) < 1 + len(self.fixed_tokens['fn_name']):
                return {self.fixed_tokens['fn_name'][len(self.token_buffer) - 1]}
            else:
                return set(self.fixed_tokens['"'])          # closing quote

        # For KEY_ARGS: expect '"args"'
        if self.state == State.KEY_ARGS:
            if not self.token_buffer:
                return {self.fixed_tokens['args'][0]}
            else:
                return {self.fixed_tokens['args'][len(self.token_buffer)]}

        # For OPEN_ARGS: expect "{" or "}" (empty args)
        if self.state == State.OPEN_ARGS:
            return set(self.fixed_tokens["{"]) | set(self.fixed_tokens["}"])

        # For CLOSE_ARGS: expect "}"
        if self.state == State.CLOSE_ARGS:
            return set(self.fixed_tokens["}"])

        # For VALUE_PROMPT: allow any quoted string token (starting with ")
        if self.state == State.VALUE_PROMPT:
            return set(self.fixed_tokens['"'])

        # For VALUE_FN_NAME: return valid function name tokens
        if self.state == State.VALUE_FN_NAME:
            if not self.token_buffer:
                # first token of any function name
                return {
                    seq[0]
                    for seq in self.candidate_sequences
                    if seq
                }
            else:
                idx = len(self.token_buffer)
                return {
                    seq[idx]
                    for seq in self.candidate_sequences
                    if len(seq) > idx
                }

        # For ARG_KEY: return valid argument names for selected function
        if self.state == State.ARG_KEY:
            if not self.candidate_sequences:
                return set()
            if not self.token_buffer:
                return {
                        seq[0]
                        for seq in self.candidate_sequences
                        if seq
                    }
            else:
                idx = len(self.token_buffer)
                return {
                    seq[idx]
                    for seq in self.candidate_sequences
                    if len(seq) > idx
                }

        # For ARG_VALUE: return tokens based on argument type
        if self.state == State.ARG_VALUE:
            if self.selected_function is None or self.current_arg_name is None:
                return set()
            arg_type = self.selected_function.types.get(self.current_arg_name)
            if arg_type == "str":
                # Allow string tokens (this is simplified - ideally filter to string-like tokens)
                return set(range(self.tokenizer.vocab_size))
            elif arg_type in ["int", "float"]:
                # Allow number tokens (simplified - ideally filter to digit tokens)
                return set(range(self.tokenizer.vocab_size))
            elif arg_type == "bool":
                return set(self.fixed_tokens["true"]) | set(self.fixed_tokens["false"])
            return set()

        # For BETWEEN_ARGS: check if we have more args to parse
        if self.state == State.BETWEEN_ARGS:
            if self.selected_function is None:
                return set(self.fixed_tokens["}"])
            remaining_args = set(self.selected_function.args) - self.seen_args
            if remaining_args:
                # Can add more args or close
                return set(self.fixed_tokens[","]) | set(self.fixed_tokens["}"])
            else:
                # Must close if all args seen
                return set(self.fixed_tokens["}"])
        return set()

    def consume_token_id(self, token_id: int) -> None:
        """Consume a token ID and transition to next state"""
        allowed = self.get_allowed_token_ids()
        if token_id not in allowed:
            token_str = self.tokenizer.decode([token_id])
            raise Exception(
                f"Token ID {token_id} ('{token_str}') not allowed in state {self.state}"
            )
        # Handle OPEN_OBJECT: matching "prompt"
        if self.state == State.OPEN_OBJECT:
            self.token_buffer.append(token_id)
            if len(self.token_buffer) == len(self.fixed_tokens['prompt']):
                self.state = State.COLON_PROMPT
                self.token_buffer = []
            return

        # Handle KEY_FN_NAME: matching "fn_name"
        if self.state == State.COLON_FN_NAME and token_id in self.fixed_tokens[":"]:
            self.state = State.VALUE_FN_NAME
            self.token_buffer = []
            self.candidate_sequences = [f.tkname for f in self.functions]
            self.candidate_meta = self.functions[:]  # parallelo
            return

        if self.state == State.KEY_FN_NAME:
            tok = self.tokenizer.decode([token_id])

            self.token_buffer.append(tok)

            if (
                self.token_buffer[0] == '"'
                and ''.join(self.token_buffer[1:-1]) == 'fn_name'
                and self.token_buffer[-1] == '"'
            ):
                self.token_buffer = []
                self.state = State.COLON_FN_NAME
            return

        # Handle KEY_ARGS: matching "args"
        if self.state == State.KEY_ARGS:
            self.token_buffer.append(token_id)
            if len(self.token_buffer) == len(self.fixed_tokens['args']):
                self.state = State.COLON_ARGS
                self.token_buffer = []
            return

        if self.state == State.START and token_id in self.fixed_tokens["{"]:
            self.state = State.OPEN_OBJECT
            return
        if self.state == State.COLON_PROMPT and token_id in self.fixed_tokens[":"]:
            self.state = State.VALUE_PROMPT
            return
        if self.state == State.VALUE_PROMPT:
            self.state = State.COMMA_1
            return
        if self.state == State.COMMA_1 and token_id in self.fixed_tokens[","]:
            self.state = State.KEY_FN_NAME
            return
        if self.state == State.COLON_FN_NAME and token_id in self.fixed_tokens[":"]:
            self.state = State.VALUE_FN_NAME
            self.token_buffer = []
            self.candidate_sequences: list[list[int]] = [func.tkname for func
                                                         in self.functions]
            return
        if self.state == State.VALUE_FN_NAME:
            if not self.token_buffer:
                # Starting to match a function name
                for func in self.functions:
                    if func.tkname and func.tkname[0] == token_id:
                        self.target_tokens = func.tkname
                        self.token_buffer.append(token_id)
                        if len(self.token_buffer) == len(self.target_tokens):
                            self.selected_function = func
                            self.token_buffer = []
                            self.target_tokens = []
                            self.state = State.COMMA_2
                        return
            else:
                self.token_buffer.append(token_id)
                if len(self.token_buffer) == len(self.target_tokens):
                    self.state = State.COMMA_2
                    self.token_buffer = []
                    self.target_tokens = []
                return
        if self.state == State.COMMA_2 and token_id in self.fixed_tokens[","]:
            self.state = State.KEY_ARGS
            return
        if self.state == State.COLON_ARGS and token_id in self.fixed_tokens[":"]:
            self.state = State.OPEN_ARGS
            return
        if self.state == State.OPEN_ARGS:
            self.token_buffer.append(token_id)
            # match "{"
            if self.token_buffer == self.fixed_tokens["{"]:
                self.token_buffer = []
                self.state = State.ARG_KEY
                return
            # match "}"
            if self.token_buffer == self.fixed_tokens["}"]:
                self.token_buffer = []
                self.state = State.END
                return
            # still matching prefix?
            if (
                self.fixed_tokens["{"][:len(self.token_buffer)] == self.token_buffer
                or self.fixed_tokens["}"][:len(self.token_buffer)] == self.token_buffer
            ):
                return
            raise Exception("Invalid token sequence in OPEN_ARGS")
        if self.state == State.ARG_KEY:
            self.token_buffer.append(token_id)

            new_seq = []
            new_meta = []
            for seq, arg in zip(self.candidate_sequences, self.candidate_meta):
                if seq[:len(self.token_buffer)] == self.token_buffer:
                    new_seq.append(seq)
                    new_meta.append(arg)

            self.candidate_sequences = new_seq
            self.candidate_meta = new_meta

            if not self.candidate_sequences:
                raise Exception("No matching argument names")

            if len(self.candidate_sequences) == 1 and \
               len(self.token_buffer) == len(self.candidate_sequences[0]):
                self.current_arg_name = self.candidate_meta[0]
                self.seen_args.add(self.current_arg_name)
                self.state = State.COLON_ARG
                self.token_buffer = []
                self.candidate_sequences = []
                self.candidate_meta = []

            return
        if self.state == State.COLON_ARG and token_id in self.fixed_tokens[":"]:
            self.state = State.ARG_VALUE
            return
        if self.state == State.ARG_VALUE:
            # Simplified: assume single token for arg value
            self.state = State.BETWEEN_ARGS
            return
        if self.state == State.BETWEEN_ARGS:
            if token_id in self.fixed_tokens[","]:
                self.state = State.ARG_KEY
                self.token_buffer = []
                return
            elif token_id in self.fixed_tokens["}"]:
                self.state = State.CLOSE_ARGS
                return
        if self.state == State.CLOSE_ARGS:
            self.token_buffer.append(token_id)

            if self.token_buffer == self.fixed_tokens["}"]:
                self.token_buffer = []
                self.state = State.END
                return

            if self.fixed_tokens["}"][:len(self.token_buffer)] == self.token_buffer:
                return

            raise Exception("Invalid token sequence in CLOSE_ARGS")
        # If we get here, the token is not valid for this state
        token_str = self.tokenizer.decode([token_id]) if self.tokenizer else str(token_id)
        raise Exception(f"Token ID {token_id} ('{token_str}') not allowed in state {self.state}")