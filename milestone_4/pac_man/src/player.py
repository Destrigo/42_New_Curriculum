"""Player module for Pac-Man."""

from src.constants import DIR_E, DIR_DELTA
from src.maze import can_move


class Player:
    """Represents the Pac-Man player.

    Attributes:
        x: Current x position in maze coordinates.
        y: Current y position in maze coordinates.
        direction: Current facing direction.
        start_x: Spawn x position.
        start_y: Spawn y position.
        lives: Remaining lives.
        score: Current score.
        mouth_timer: Animation timer for mouth opening/closing.
        dead: Whether player is in death animation.
        dead_timer: Countdown for death animation.
    """

    def __init__(self, x: int, y: int, lives: int) -> None:
        """Initialize the player.

        Args:
            x: Starting x position.
            y: Starting y position.
            lives: Number of starting lives.
        """
        self.x: int = x
        self.y: int = y
        self.start_x: int = x
        self.start_y: int = y
        self.direction: str = DIR_E
        self.lives: int = lives
        self.score: int = 0
        self.mouth_timer: float = 0.0
        self.dead: bool = False
        self.dead_timer: float = 0.0

    def respawn(self) -> None:
        """Reset player to starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.direction = DIR_E
        self.dead = False
        self.dead_timer = 0.0

    def try_move(self, direction: str,
                 maze: list[list[int]]) -> bool:
        """Attempt to move in a given direction."""
        if can_move(maze, self.x, self.y, direction):
            dx, dy = DIR_DELTA[direction]
            self.x += dx
            self.y += dy
            self.direction = direction
            return True
        return False

    def update_animation(self, dt: float) -> None:
        """Update mouth animation timer."""
        self.mouth_timer += dt * 8.0
        if self.mouth_timer > 2.0:
            self.mouth_timer -= 2.0

    def get_mouth_angle(self) -> float:
        """Get the current mouth opening angle."""
        t = self.mouth_timer
        if t > 1.0:
            t = 2.0 - t
        return t * 0.8 + 0.05
