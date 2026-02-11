from pydantic import BaseModel
from typing import List


class data_input(BaseModel):
    """placeholder"""
    map: List[str]
    pacman: dict
    ghosts: List[dict]
    points_per_ghost: int
    lives: int
    seed: int
    level_max_time: int