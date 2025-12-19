from enum import Enum, auto


class FSMState(Enum):
    """
    Finite State Machine states for JSON function-call generation.
    Each state represents a structural position in the output JSON.
    """
    START = auto()                  # Before anything is generated
    OPEN_OBJECT = auto()             # {
    EXPECT_KEY = auto()              # Expecting a JSON key (string)
    IN_KEY = auto()                  # Generating a key string
    AFTER_KEY = auto()               # After key, expecting :
    EXPECT_VALUE = auto()            # Expecting a value
    IN_STRING = auto()               # Inside a string value
    IN_NUMBER = auto()               # Inside a numeric value
    IN_BOOLEAN = auto()              # true / false
    AFTER_VALUE = auto()             # After value, expecting , or }
    CLOSE_OBJECT = auto()            # }
    END = auto()
