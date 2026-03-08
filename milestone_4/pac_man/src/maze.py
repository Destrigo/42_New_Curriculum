"""Maze integration module.

Wraps the external A-Maze-ing (mazegenerator) package and provides
helper functions for wall-checking and item placement.
"""

import random
from typing import Any

from src.constants import (
    WALL_ALL, WALL_N, WALL_E, WALL_S, WALL_W,
    DIR_TO_WALL, DIR_DELTA,
    ITEM_EMPTY, ITEM_PACGUM, ITEM_SUPER,
)


def generate_maze(width: int, height: int, seed: int,
                  perfect: bool = False) -> Any:
    """Generate a maze using the mazegenerator package."""
    try:
        from mazegenerator.mazegenerator import MazeGenerator
        mg: Any = MazeGenerator(
            size=(width, height),
            perfect=perfect,
            entry_cell=(0, 0),
            exit_cell=(width - 1, height - 1),
            seed=seed,
        )
        return mg.maze
    except ImportError:
        print("[maze] mazegenerator package not found, "
              "using fallback generator.")
        return _fallback_maze(width, height, seed)
    except Exception as e:
        print(f"[maze] Maze generation failed: {e}, "
              "using fallback.")
        return _fallback_maze(width, height, seed)


def _fallback_maze(width: int, height: int,
                   seed: int) -> list[list[int]]:
    """Simple fallback maze generator if external package fails."""
    rng = random.Random(seed if seed > 0 else None)

    maze: list[list[int]] = []
    for y in range(height):
        row: list[int] = []
        for x in range(width):
            cell = 0
            if y == 0:
                cell |= WALL_N
            if y == height - 1:
                cell |= WALL_S
            if x == 0:
                cell |= WALL_W
            if x == width - 1:
                cell |= WALL_E
            row.append(cell)
        maze.append(row)

    visited = [[False] * width for _ in range(height)]
    stack: list[tuple[int, int]] = [(0, 0)]
    visited[0][0] = True

    dirs = [(0, -1, WALL_N, WALL_S), (1, 0, WALL_E, WALL_W),
            (0, 1, WALL_S, WALL_N), (-1, 0, WALL_W, WALL_E)]

    # Mark all internal walls
    for y in range(height):
        for x in range(width):
            maze[y][x] = WALL_ALL

    while stack:
        cx, cy = stack[-1]
        neighbors: list[tuple[int, int, int, int, int, int]] = []
        shuffled = list(dirs)
        rng.shuffle(shuffled)
        for dx, dy, wall, opp in shuffled:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not visited[ny][nx]:
                    neighbors.append((nx, ny, dx, dy, wall, opp))
        if not neighbors:
            stack.pop()
            continue
        nx, ny, _, _, wall, opp = neighbors[0]
        visited[ny][nx] = True
        maze[cy][cx] &= ~wall
        maze[ny][nx] &= ~opp
        stack.append((nx, ny))

    # Add extra passages for imperfect maze
    for _ in range(width * height // 4):
        x = rng.randint(1, width - 2)
        y = rng.randint(1, height - 2)
        d = rng.choice(list(dirs))
        dx, dy, wall, opp = d
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            maze[y][x] &= ~wall
            maze[ny][nx] &= ~opp

    return maze


def has_wall(maze: list[list[int]], x: int, y: int,
             direction: str) -> bool:
    """Check if a cell has a wall in the given direction."""
    h = len(maze)
    w = len(maze[0]) if h > 0 else 0
    if x < 0 or x >= w or y < 0 or y >= h:
        return True
    cell = maze[y][x]
    if cell == WALL_ALL:
        return True
    return bool(cell & DIR_TO_WALL[direction])


def can_move(maze: list[list[int]], x: int, y: int,
             direction: str) -> bool:
    """Check if movement from (x, y) in direction is possible."""
    h = len(maze)
    w = len(maze[0]) if h > 0 else 0
    if x < 0 or x >= w or y < 0 or y >= h:
        return False
    if maze[y][x] == WALL_ALL:
        return False
    if has_wall(maze, x, y, direction):
        return False
    dx, dy = DIR_DELTA[direction]
    nx, ny = x + dx, y + dy
    if nx < 0 or nx >= w or ny < 0 or ny >= h:
        return False
    if maze[ny][nx] == WALL_ALL:
        return False
    return True


def is_walkable(maze: list[list[int]], x: int, y: int) -> bool:
    """Check if a cell is walkable (not a solid wall)."""
    h = len(maze)
    w = len(maze[0]) if h > 0 else 0
    if x < 0 or x >= w or y < 0 or y >= h:
        return False
    return maze[y][x] != WALL_ALL


def find_nearest_walkable(maze: list[list[int]], cx: int, cy: int,
                          max_radius: int = 10) -> tuple[int, int]:
    """Find the nearest walkable cell to (cx, cy)"""
    if is_walkable(maze, cx, cy):
        return cx, cy
    for r in range(1, max_radius + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                nx, ny = cx + dx, cy + dy
                if is_walkable(maze, nx, ny):
                    return nx, ny
    return cx, cy


def place_items(maze: list[list[int]],
                player_pos: tuple[int, int],
                ghost_positions: list[tuple[int, int]]
                ) -> tuple[list[list[int]], int]:
    """Place pacgums and super-pacgums on the maze."""
    h = len(maze)
    w = len(maze[0]) if h > 0 else 0
    items: list[list[int]] = [
        [ITEM_EMPTY] * w for _ in range(h)
    ]

    # Place pacgums
    count = 0
    for y in range(h):
        for x in range(w):
            if maze[y][x] != WALL_ALL:
                items[y][x] = ITEM_PACGUM
                count += 1

    # Place super-pacgums near corners
    corners = [
        (1, 1),
        (1, w - 2),
        (h - 2, 1),
        (h - 2, w - 2),
    ]
    occupied: set[tuple[int, int]] = set()
    occupied.add(player_pos)
    for gp in ghost_positions:
        occupied.add(gp)

    for cy, cx in corners:
        # Search outward for a walkable cell not occupied
        placed = False
        for r in range(0, 8):
            if placed:
                break
            for dy in range(-r, r + 1):
                if placed:
                    break
                for dx in range(-r, r + 1):
                    nx, ny = cx + dx, cy + dy
                    if (0 <= ny < h and 0 <= nx < w
                            and maze[ny][nx] != WALL_ALL
                            and items[ny][nx] == ITEM_PACGUM
                            and (nx, ny) not in occupied):
                        items[ny][nx] = ITEM_SUPER
                        placed = True
                        break

    # Clear player and ghost positions
    px, py = player_pos
    if 0 <= py < h and 0 <= px < w:
        if items[py][px] != ITEM_EMPTY:
            items[py][px] = ITEM_EMPTY
            count -= 1
    for gx, gy in ghost_positions:
        if 0 <= gy < h and 0 <= gx < w:
            if items[gy][gx] != ITEM_EMPTY:
                items[gy][gx] = ITEM_EMPTY
                count -= 1

    return items, count
