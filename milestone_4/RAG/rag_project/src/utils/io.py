"""
Utility functions for file I/O and data handling.
"""

import json
from pathlib import Path
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def load_json(filepath: str | Path, model_class: Type[T]) -> T:
    """
    Load and validate JSON file using Pydantic model.
    Args:
        filepath: Path to JSON file
        model_class: Pydantic model class to validate with
    Returns:
        Validated Pydantic model instance
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return model_class(**data)


def save_json(data: BaseModel, filepath: str | Path) -> None:
    """
    Save Pydantic model to JSON file.

    Args:
        data: Pydantic model instance
        filepath: Path to save JSON file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            data.model_dump(),
            f,
            indent=2,
            ensure_ascii=False
        )


def ensure_dir(dirpath: str | Path) -> Path:
    """
    Ensure directory exists, create if necessary.
    Args:
        dirpath: Directory path
    Returns:
        Path object
    """
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    return dirpath
