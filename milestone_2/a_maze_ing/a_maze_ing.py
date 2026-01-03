import sys
from pathlib import Path
from config import ConfigError, ConfigParser
from visualisation import Visualizator


def main() -> None:
    """Entry point that parses config and launches visualization.

    Requires config file path as single argument to ensure users explicitly
    configure maze parameters rather than relying on defaults. Config errors
    are caught and displayed without stack traces to provide user-friendly
    error messages for invalid config files.
    """
    if len(sys.argv) != 2:
        print("usage: python3 a_maze_ing.py [CONFIG_FILE]")
        return
    try:
        config = ConfigParser.from_file(Path(sys.argv[1]))
    except ConfigError as err:
        print(err)
        return
    visualizator = Visualizator(config)
    visualizator.start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"maze generator failed: {type(e).__name__} {e.args}")
