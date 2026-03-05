"""Configuration loader with JSON comment support.

Handles loading, validation, and default values for game configuration.
Supports lines starting with # as comments, as well as // and /* */ styles.
"""

import json
import re
import sys
from typing import Any

from src.constants import DEFAULT_CONFIG


def strip_comments(text: str) -> str:
    """Remove comments from JSON-like text.

    Supports:
        - Lines starting with #
        - C-style // single-line comments
        - C-style /* ... */ block comments

    Args:
        text: Raw text content from config file.

    Returns:
        Cleaned text with comments removed.
    """
    lines: list[str] = []
    in_block: bool = False
    for line in text.splitlines():
        if in_block:
            if "*/" in line:
                line = line[line.index("*/") + 2:]
                in_block = False
            else:
                continue
        # Remove block comment starts
        while "/*" in line:
            start = line.index("/*")
            if "*/" in line[start + 2:]:
                end = line.index("*/", start + 2)
                line = line[:start] + line[end + 2:]
            else:
                line = line[:start]
                in_block = True
                break
        # Remove # and // line comments (outside strings)
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        line = re.sub(r'//.*$', '', line)
        lines.append(line)
    return "\n".join(lines)


def _clamp(value: Any, vmin: Any, vmax: Any, default: Any,
           key: str) -> Any:
    """Clamp a value to [vmin, vmax], falling back to default.

    Args:
        value: The value to validate.
        vmin: Minimum allowed value.
        vmax: Maximum allowed value.
        default: Fallback value if invalid.
        key: Config key name for logging.

    Returns:
        Validated value within bounds.
    """
    try:
        val = type(default)(value)
    except (TypeError, ValueError):
        print(f"[config] Invalid value for '{key}': {value!r}, "
              f"using default {default}")
        return default
    if val < vmin or val > vmax:
        clamped = max(vmin, min(vmax, val))
        print(f"[config] '{key}' clamped from {val} to {clamped}")
        return clamped
    return val


def load_config(filepath: str) -> dict[str, Any]:
    """Load and validate game configuration from a JSON file.

    On missing or invalid values, clamps to safe defaults and logs
    a clear message. Unknown keys are ignored.

    Args:
        filepath: Path to the JSON config file.

    Returns:
        Validated configuration dictionary.
    """
    config: dict[str, Any] = dict(DEFAULT_CONFIG)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw: str = f.read()
    except FileNotFoundError:
        print(f"[config] File not found: {filepath}, "
              "using defaults.")
        return config
    except PermissionError:
        print(f"[config] Permission denied: {filepath}, "
              "using defaults.")
        return config
    except OSError as e:
        print(f"[config] Cannot read {filepath}: {e}, "
              "using defaults.")
        return config

    cleaned: str = strip_comments(raw)

    try:
        data: dict[str, Any] = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[config] Invalid JSON in {filepath}: {e}, "
              "using defaults.")
        return config

    if not isinstance(data, dict):
        print("[config] Config root must be an object, "
              "using defaults.")
        return config

    # Validate known keys
    if "highscore_filename" in data:
        val = data["highscore_filename"]
        if isinstance(val, str) and len(val) > 0:
            config["highscore_filename"] = val
        else:
            print("[config] Invalid highscore_filename, "
                  "using default.")

    int_bounds: dict[str, tuple[int, int]] = {
        "lives": (1, 99),
        "points_per_pacgum": (1, 10000),
        "points_per_super_pacgum": (1, 10000),
        "points_per_ghost": (1, 50000),
        "seed": (0, 999999999),
        "level_max_time": (10, 600),
        "frightened_duration": (1, 60),
        "ghost_respawn_time": (1, 60),
        "maze_width": (11, 51),
        "maze_height": (9, 41),
    }

    for key, (lo, hi) in int_bounds.items():
        if key in data:
            config[key] = _clamp(
                data[key], lo, hi, DEFAULT_CONFIG[key], key
            )

    # Validate levels array
    if "levels" in data:
        if isinstance(data["levels"], list) and len(data["levels"]) > 0:
            levels: list[dict[str, int]] = []
            for i, lvl in enumerate(data["levels"]):
                if isinstance(lvl, dict):
                    w = _clamp(
                        lvl.get("width", 19), 11, 51, 19,
                        f"levels[{i}].width"
                    )
                    h = _clamp(
                        lvl.get("height", 15), 9, 41, 15,
                        f"levels[{i}].height"
                    )
                    levels.append({"width": w, "height": h})
                else:
                    print(f"[config] levels[{i}] invalid, skipping.")
            if levels:
                config["levels"] = levels
            else:
                print("[config] No valid levels, using defaults.")
        else:
            print("[config] 'levels' must be a non-empty array, "
                  "using defaults.")

    # Log unknown keys
    known: set[str] = set(DEFAULT_CONFIG.keys())
    for key in data:
        if key not in known:
            print(f"[config] Unknown key '{key}' ignored.")

    return config


def main() -> None:
    """Test config loading from command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.config <config.json>")
        return
    cfg = load_config(sys.argv[1])
    print(json.dumps(cfg, indent=2))


if __name__ == "__main__":
    main()
