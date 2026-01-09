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
    CLOSE_OBJECT = auto()    # After final "}"
    END = auto()


class Function:
    """Function representation"""
    def __init__(self,
                 name: str,
                 description: str,
                 parameters: dict) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters


class FSM:
    """Finite State Machine representation"""
    def __init__(self) -> None:
        self.state = State.START

        # token -> next_state
        self.transitions: dict[State, dict[str, State]] = {
            State.START: {
                "{": State.OPEN_OBJECT
            },

            State.OPEN_OBJECT: {
                '"prompt"': State.COLON_PROMPT
            },

            State.COLON_PROMPT: {
                ":": State.VALUE_PROMPT
            },

            State.VALUE_PROMPT: {
                "<STRING>": State.COMMA_1
            },

            State.COMMA_1: {
                ",": State.KEY_FN_NAME
            },

            State.KEY_FN_NAME: {
                '"fn_name"': State.COLON_FN_NAME
            },

            State.COLON_FN_NAME: {
                ":": State.VALUE_FN_NAME
            },

            State.VALUE_FN_NAME: {
                "<STRING>": State.COMMA_2
            },

            State.COMMA_2: {
                ",": State.KEY_ARGS
            },

            State.KEY_ARGS: {
                '"args"': State.COLON_ARGS
            },

            State.COLON_ARGS: {
                ":": State.OPEN_ARGS
            },

            State.OPEN_ARGS: {
                "{": State.ARG_KEY,
                "}": State.CLOSE_OBJECT   # empty args
            },

            State.ARG_KEY: {
                "<STRING>": State.COLON_ARG
            },

            State.COLON_ARG: {
                ":": State.ARG_VALUE
            },

            State.ARG_VALUE: {
                "<STRING>": State.BETWEEN_ARGS,
                "<NUMBER>": State.BETWEEN_ARGS,
                "<BOOL>": State.BETWEEN_ARGS
            },

            State.BETWEEN_ARGS: {
                ",": State.ARG_KEY,
                "}": State.CLOSE_ARGS
            },

            State.CLOSE_ARGS: {
                "}": State.END
            },
        }

    def get_current_state(self) -> State:
        return self.state

    def get_allowed_tokens(self) -> list[str]:
        if self.state not in self.transitions:
            raise Exception(f"No transitions from state {self.state}")
        return list(self.transitions[self.state].keys())

    def consume(self, token: str) -> None:
        transitions = self.transitions.get(self.state, {})

        for expected, next_state in transitions.items():
            if self._match(expected, token):
                self.state = next_state
                return

        raise Exception(
            f"Token {token!r} not allowed in state {self.state}"
        )

    @staticmethod
    def _match(expected: str, token: str) -> bool:
        if expected == "<STRING>":
            return token.startswith('"')
        if expected == "<NUMBER>":
            return token.replace(".", "", 1).isdigit()
        if expected == "<BOOL>":
            return token in {"true", "false"}
        return expected == token
