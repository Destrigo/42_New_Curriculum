#!/usr/bin/env python3
"""Pac-Man game entry point.

Usage:
    python3 pac-man.py config.json

Launches the Pac-Man game with the given configuration file.
Any errors in the config are handled gracefully with defaults.
"""

import sys


def main() -> None:
    """Parse arguments and launch the game.

    Validates that exactly one argument (config file) is provided,
    then initializes and runs the game. All errors are caught and
    reported cleanly without tracebacks.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>")
        print("  config.json: path to a JSON configuration file")
        sys.exit()

    config_path: str = sys.argv[1]

    if not config_path.endswith(".json"):
        print(f"Error: '{config_path}' is not a .json file.")
        sys.exit()

    try:
        from src.game import Game
        game = Game(config_path)
        game.run()
    except ImportError as e:
        print(f"Error: Missing dependency: {e}")
        print("Run 'make install' to install dependencies.")
        sys.exit()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()


if __name__ == "__main__":
    main()
