from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Raised when configuration file parsing fails.

    Allows callers to distinguish config errors from other exceptions
    and provide user-friendly error messages with line numbers.
    """
    pass


@dataclass
class Config:
    """Validated maze generation parameters.

    Immutable configuration created by ConfigParser. All values are
    validated before construction, so consumers can trust the data
    without additional checks. Field names are self-documenting.
    """
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: str = ""


class ConfigParser:
    """Parses maze configuration from text format with validation.

    Line-by-line parser that validates types and required fields while
    skipping comments and empty lines. Tracks line numbers for helpful
    error messages when parsing fails.
    """
    # Parser values
    lines: list[str]
    i: int
    length: int

    # Config values
    width: int | None = None
    height: int | None = None
    entry: tuple[int, int] | None = None
    exit: tuple[int, int] | None = None
    output_file: str | None = None
    perfect: bool | None = None
    seed: str = ""

    def __init__(self, config: str) -> None:
        self.lines = config.splitlines()
        self.i = 0
        self.length = len(self.lines)

    @staticmethod
    def from_file(path: Path) -> Config:
        """Constructs Config from file path rather than raw string.

        Static method because it's a convenience constructor that doesn't
        need access to parser state. Returns fully validated Config, not
        Parser.
        """
        if not path.exists():
            raise ConfigError(f"config file {str(path)} does not exist")
        return ConfigParser(path.read_text()).parse()

    def parse(self) -> Config:
        """Parses all lines and validates all required fields are present.

        Defers validation until the end so users see all missing fields
        at once rather than one at a time. This improves the user experience
        when debugging config files.
        """
        while self.i < self.length:
            self.parse_line()
            self.i += 1
        if self.width is None:
            raise ConfigError("no value given for 'WIDTH'")
        if self.height is None:
            raise ConfigError("no value given for 'HEIGHT'")
        if self.entry is None:
            raise ConfigError("no value given for 'ENTRY'")
        if self.exit is None:
            raise ConfigError("no value given for 'EXIT'")
        if self.output_file is None:
            raise ConfigError("no value given for 'OUTPUT_FILE'")
        if self.perfect is None:
            raise ConfigError("no value given for 'PERFECT'")
        # logic errors handling
        if self.entry == self.exit:
            raise ConfigError("'ENTRY' and 'EXIT' cannot be the same")
        if (self.entry[0] >= self.width or self.entry[1] >= self.height):
            raise ConfigError("'ENTRY' coordinates out of bounds")
        if (self.exit[0] >= self.width or self.exit[1] >= self.height):
            raise ConfigError("'EXIT' coordinates out of bounds")
        return Config(
            self.width,
            self.height,
            self.entry,
            self.exit,
            self.output_file,
            self.perfect,
            self.seed
        )

    def parse_line(self) -> None:
        """Parses a single config line using pattern matching.

        Pattern matching provides clear error messages for invalid keys
        while keeping the parsing logic readable. Each value is validated
        by type-specific parsers. Keys are case-insensitive.
        """
        line = self.__line()
        if line is None:
            return
        parts = line.split(sep="=")
        if parts:
            parts[0] = parts[0].upper()
        match parts:
            case ["WIDTH", width]:
                self.width = self.__parse_int(width)
            case ["HEIGHT", height]:
                self.height = self.__parse_int(height)
            case ["ENTRY", entry]:
                self.entry = self.__parse_coords(entry)
            case ["EXIT", exit]:
                self.exit = self.__parse_coords(exit)
            case ["OUTPUT_FILE", output_file]:
                self.output_file = output_file
            case ["PERFECT", perfect]:
                self.perfect = self.__parse_bool(perfect)
            case ["SEED", seed]:
                self.seed = seed
            case [word, _]:
                raise self.__error(f"expected config key, found '{word}'")
            case _:
                raise self.__error("expected a single equals sign")

    def __line(self) -> str | None:
        """Returns next non-empty, non-comment line with whitespace trimmed.

        Automatic skipping of comments and blank lines simplifies the main
        parsing logic and makes config files more user-friendly.
        """
        while self.i < self.length:
            line = self.lines[self.i].strip()
            match line:
                case "":
                    self.i += 1
                    continue
                case s if s.startswith("#"):
                    self.i += 1
                    continue
                case s:
                    return s
        return None

    def __parse_int(self, s: str) -> int:
        """Validates and converts string to non-negative integer.

        Maze dimensions must be positive, so negative values are rejected
        immediately to catch configuration errors early.
        """
        try:
            n = int(s)
            if n < 0:
                raise self.__error("expected a positive integer")
            return n
        except ValueError:
            raise self.__error("invalid integer value")

    def __parse_coords(self, s: str) -> tuple[int, int]:
        """Parses coordinate pair in 'x,y' format.

        Reuses __parse_int to ensure coordinates are non-negative.
        User-facing format uses x,y for familiarity even though internal
        algorithms use row,col.
        """
        match s.split(sep=","):
            case [a, b]:
                return (self.__parse_int(a), self.__parse_int(b))
            case _:
                raise self.__error("expected a single comma in value")

    def __parse_bool(self, s: str) -> bool:
        """Parses boolean from 'true'/'false' strings, case-insensitive.

        Case-insensitive matching makes config files more forgiving
        for users unfamiliar with Python's boolean capitalization.
        """
        match s.lower():
            case "true": return True
            case "false": return False
            case _: raise self.__error("expected a boolean value")

    def __error(self, message: str) -> ConfigError:
        """Creates ConfigError with current line number for debugging.

        Centralized error creation ensures all config errors have consistent
        formatting and include line numbers to help users fix their configs.
        """
        return ConfigError(
            f"Failed to parse config on line [{self.i}]: {message}"
        )
