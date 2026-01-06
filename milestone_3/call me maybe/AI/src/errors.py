class FunctionCallingError(Exception):
    """Base class for all errors in the function calling system."""
    pass


class FileFormatError(FunctionCallingError):
    """Raised when an input JSON file is missing or has invalid format."""
    def __init__(self, message: str = "Invalid or missing JSON file"):
        super().__init__(message)


class FSMError(FunctionCallingError):
    """Raised when the FSM encounters an invalid state or transition."""
    def __init__(self, message: str = "Finite State Machine error"):
        super().__init__(message)


class DecoderError(FunctionCallingError):
    """Raised during constrained decoding when an invalid
    token or schema violation occurs."""
    def __init__(self, message: str = "Decoder error"):
        super().__init__(message)
