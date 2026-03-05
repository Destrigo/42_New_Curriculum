"""Constants shared across all game modules."""

from typing import Final

# ── Display ──
CELL_SIZE: Final[int] = 32
FPS: Final[int] = 60
HUD_HEIGHT: Final[int] = 48

# ── Colors ──
BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
YELLOW: Final[tuple[int, int, int]] = (255, 255, 0)
BLUE: Final[tuple[int, int, int]] = (33, 33, 222)
DARK_BLUE: Final[tuple[int, int, int]] = (0, 0, 180)
RED: Final[tuple[int, int, int]] = (255, 0, 0)
GREEN: Final[tuple[int, int, int]] = (0, 255, 0)
ORANGE: Final[tuple[int, int, int]] = (255, 184, 82)
PINK: Final[tuple[int, int, int]] = (255, 184, 255)
CYAN: Final[tuple[int, int, int]] = (0, 255, 255)
GREY: Final[tuple[int, int, int]] = (128, 128, 128)
DARK_GREY: Final[tuple[int, int, int]] = (40, 40, 40)
FRIGHTENED_BLUE: Final[tuple[int, int, int]] = (33, 33, 255)
PACGUM_COLOR: Final[tuple[int, int, int]] = (255, 204, 0)
WALL_COLOR: Final[tuple[int, int, int]] = (33, 33, 200)
WALL_FILL: Final[tuple[int, int, int]] = (25, 25, 180)
BG_COLOR: Final[tuple[int, int, int]] = BLACK
MENU_BG: Final[tuple[int, int, int]] = (10, 10, 30)

GHOST_COLORS: Final[list[tuple[int, int, int]]] = [
    RED, PINK, CYAN, ORANGE,
]
GHOST_NAMES: Final[list[str]] = [
    "Blinky", "Pinky", "Inky", "Clyde",
]

# ── Directions ──
DIR_N: Final[str] = "N"
DIR_E: Final[str] = "E"
DIR_S: Final[str] = "S"
DIR_W: Final[str] = "W"

DIR_DELTA: Final[dict[str, tuple[int, int]]] = {
    DIR_N: (0, -1),
    DIR_E: (1, 0),
    DIR_S: (0, 1),
    DIR_W: (-1, 0), 
}

OPPOSITE: Final[dict[str, str]] = {
    DIR_N: DIR_S,
    DIR_S: DIR_N,
    DIR_E: DIR_W,
    DIR_W: DIR_E,
}

# ── Wall bitmask encoding (matching mazegenerator) ──
WALL_N: Final[int] = 1   # bit 0
WALL_E: Final[int] = 2   # bit 1
WALL_S: Final[int] = 4   # bit 2
WALL_W: Final[int] = 8   # bit 3
WALL_ALL: Final[int] = 15  # solid block

DIR_TO_WALL: Final[dict[str, int]] = {
    DIR_N: WALL_N,
    DIR_E: WALL_E,
    DIR_S: WALL_S,
    DIR_W: WALL_W,
}

# ── Items ──
ITEM_EMPTY: Final[int] = 0
ITEM_PACGUM: Final[int] = 1
ITEM_SUPER: Final[int] = 2

# ── Game states ──
STATE_MENU: Final[str] = "menu"
STATE_PLAYING: Final[str] = "playing"
STATE_PAUSED: Final[str] = "paused"
STATE_GAMEOVER: Final[str] = "gameover"
STATE_VICTORY: Final[str] = "victory"
STATE_ENTER_NAME: Final[str] = "enter_name"
STATE_HIGHSCORES: Final[str] = "highscores"
STATE_INSTRUCTIONS: Final[str] = "instructions"

# ── Default config values ──
DEFAULT_CONFIG: Final[dict[str, object]] = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
    "frightened_duration": 8,
    "ghost_respawn_time": 5,
    "maze_width": 19,
    "maze_height": 15,
    "levels": [
        {"width": 19, "height": 15},
        {"width": 19, "height": 15},
        {"width": 21, "height": 15},
        {"width": 21, "height": 15},
        {"width": 21, "height": 17},
        {"width": 21, "height": 17},
        {"width": 23, "height": 17},
        {"width": 23, "height": 17},
        {"width": 23, "height": 19},
        {"width": 25, "height": 19},
    ],
}
