"""Ghost module with AI behaviors.

Each ghost has a personality affecting how aggressively it chases:
    - Blinky (red): Direct chaser, rarely random.
    - Pinky (pink): Slightly random.
    - Inky (cyan): More unpredictable.
    - Clyde (orange): Very random, often wanders.
"""

import random
from typing import Optional

from src.constants import (
    DIR_N, DIR_DELTA, OPPOSITE, GHOST_COLORS, GHOST_NAMES,
)
from src.maze import can_move


# Personality: chance of making a random move instead of optimal
RANDOM_CHANCE: list[float] = [0.10, 0.20, 0.35, 0.50]


class Ghost:
    """Represents a ghost enemy.

    Attributes:
        id: Ghost index (0-3).
        name: Ghost name.
        color: RGB color tuple.
        x: Current x position.
        y: Current y position.
        home_x: Home corner x (respawn target).
        home_y: Home corner y (respawn target).
        direction: Current movement direction.
        frightened: Whether ghost is in frightened state.
        frighten_timer: Remaining frightened time in seconds.
        eaten: Whether ghost has been eaten.
        respawn_timer: Remaining respawn cooldown in seconds.
    """

    def __init__(self, ghost_id: int, x: int, y: int) -> None:
        """Initialize a ghost.

        Args:
            ghost_id: Index 0-3 determining personality/color.
            x: Starting x position.
            y: Starting y position.
        """
        self.id: int = ghost_id
        self.name: str = GHOST_NAMES[ghost_id]
        self.color: tuple[int, int, int] = GHOST_COLORS[ghost_id]
        self.x: int = x
        self.y: int = y
        self.home_x: int = x
        self.home_y: int = y
        self.direction: str = DIR_N
        self.frightened: bool = False
        self.frighten_timer: float = 0.0
        self.eaten: bool = False
        self.respawn_timer: float = 0.0

    def reset(self) -> None:
        """Reset ghost to home position and clear states."""
        self.x = self.home_x
        self.y = self.home_y
        self.direction = DIR_N
        self.frightened = False
        self.frighten_timer = 0.0
        self.eaten = False
        self.respawn_timer = 0.0

    def make_frightened(self, duration: float) -> None:
        """Put ghost into frightened state.

        Args:
            duration: How long the ghost stays frightened (seconds).
        """
        if not self.eaten:
            self.frightened = True
            self.frighten_timer = duration

    def eat(self, respawn_time: float) -> None:
        """Mark ghost as eaten.

        Args:
            respawn_time: Seconds until ghost respawns at home.
        """
        self.eaten = True
        self.frightened = False
        self.frighten_timer = 0.0
        self.respawn_timer = respawn_time

    def update(self, dt: float, player_x: int, player_y: int,
               maze: list[list[int]], frozen: bool = False) -> None:
        """Update ghost state and position.

        Args:
            dt: Delta time in seconds.
            player_x: Player's current x position.
            player_y: Player's current y position.
            maze: The maze grid.
            frozen: If True, ghost doesn't move (cheat).
        """
        # Update timers
        if self.frightened:
            self.frighten_timer -= dt
            if self.frighten_timer <= 0:
                self.frightened = False
                self.frighten_timer = 0.0

        if self.eaten:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.eaten = False
                self.respawn_timer = 0.0
                self.x = self.home_x
                self.y = self.home_y
            return  # Don't move while eaten

        if frozen:
            return

    def move(self, player_x: int, player_y: int,
             maze: list[list[int]]) -> None:
        """Execute one movement step.

        Args:
            player_x: Player x position for chase/flee logic.
            player_y: Player y position for chase/flee logic.
            maze: The maze grid.
        """
        if self.eaten:
            return

        # Get valid moves
        moves: list[tuple[str, int, int]] = []
        for d, (dx, dy) in DIR_DELTA.items():
            if can_move(maze, self.x, self.y, d):
                moves.append((d, self.x + dx, self.y + dy))

        if not moves:
            return

        # Filter out reverse unless it's the only option
        if len(moves) > 1:
            opp = OPPOSITE.get(self.direction, "")
            filtered = [(d, nx, ny) for d, nx, ny in moves
                        if d != opp]
            if filtered:
                moves = filtered

        pick: Optional[tuple[str, int, int]] = None

        if self.frightened:
            # Flee: maximize distance from player
            best_dist = -1
            for d, nx, ny in moves:
                dist = abs(nx - player_x) + abs(ny - player_y)
                if dist > best_dist:
                    best_dist = dist
                    pick = (d, nx, ny)
            # Add randomness to flee behavior
            if random.random() < 0.25:
                pick = random.choice(moves)
        else:
            # Chase: minimize distance to player
            best_d = float("inf")
            for d, nx, ny in moves:
                dist = abs(nx - player_x) + abs(ny - player_y)
                if dist < best_d:
                    best_d = dist
                    pick = (d, nx, ny)
            # Personality randomness
            chance = RANDOM_CHANCE[self.id] if self.id < 4 else 0.2
            if random.random() < chance:
                pick = random.choice(moves)

        if pick:
            self.direction, self.x, self.y = pick
