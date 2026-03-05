"""Renderer module for drawing the game with pygame.

Handles all visual rendering: maze walls, items, player,
ghosts, and HUD elements.
"""

import math
from typing import Optional

import pygame

from src.constants import (
    CELL_SIZE, HUD_HEIGHT,
    BLACK, WHITE, YELLOW, BLUE,
    WALL_COLOR, WALL_FILL, PACGUM_COLOR, BG_COLOR,
    FRIGHTENED_BLUE,
    WALL_ALL, WALL_N, WALL_E, WALL_S, WALL_W,
    ITEM_PACGUM, ITEM_SUPER,
    DIR_N, DIR_E, DIR_S, DIR_W,
)
from src.player import Player
from src.ghost import Ghost


class Renderer:
    """Handles all pygame rendering.

    Attributes:
        screen: The pygame display surface.
        font: Font for HUD text.
        small_font: Smaller font for secondary info.
        maze_w: Maze width in cells.
        maze_h: Maze height in cells.
    """

    def __init__(self, maze_w: int, maze_h: int) -> None:
        """Initialize the renderer and create the display.

        Args:
            maze_w: Maze width in cells.
            maze_h: Maze height in cells.
        """
        self.maze_w: int = maze_w
        self.maze_h: int = maze_h
        self.pixel_w: int = maze_w * CELL_SIZE
        self.pixel_h: int = maze_h * CELL_SIZE + HUD_HEIGHT
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.pixel_w, self.pixel_h)
        )
        pygame.display.set_caption("Pac-Man")
        self.font: pygame.font.Font = pygame.font.SysFont(
            "arial", 18, bold=True
        )
        self.small_font: pygame.font.Font = pygame.font.SysFont(
            "arial", 14
        )
        self.title_font: pygame.font.Font = pygame.font.SysFont(
            "arial", 48, bold=True
        )
        self.medium_font: pygame.font.Font = pygame.font.SysFont(
            "arial", 24, bold=True
        )

    def resize(self, maze_w: int, maze_h: int) -> None:
        """Resize display for a new maze size.

        Args:
            maze_w: New maze width.
            maze_h: New maze height.
        """
        self.maze_w = maze_w
        self.maze_h = maze_h
        self.pixel_w = maze_w * CELL_SIZE
        self.pixel_h = maze_h * CELL_SIZE + HUD_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.pixel_w, self.pixel_h)
        )

    def clear(self) -> None:
        """Clear the screen to black."""
        self.screen.fill(BG_COLOR)

    def draw_maze(self, maze: list[list[int]]) -> None:
        """Draw maze walls.

        Args:
            maze: 2D list of wall-encoded cells.
        """
        h = len(maze)
        w = len(maze[0]) if h > 0 else 0

        for y in range(h):
            for x in range(w):
                cell = maze[y][x]
                cx = x * CELL_SIZE
                cy = y * CELL_SIZE

                if cell == WALL_ALL:
                    # Solid block
                    pygame.draw.rect(
                        self.screen, WALL_FILL,
                        (cx + 2, cy + 2,
                         CELL_SIZE - 4, CELL_SIZE - 4)
                    )
                    pygame.draw.rect(
                        self.screen, WALL_COLOR,
                        (cx + 2, cy + 2,
                         CELL_SIZE - 4, CELL_SIZE - 4),
                        1
                    )
                    continue

                # Draw wall edges
                if cell & WALL_N:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (cx, cy), (cx + CELL_SIZE, cy), 2
                    )
                if cell & WALL_S:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (cx, cy + CELL_SIZE),
                        (cx + CELL_SIZE, cy + CELL_SIZE), 2
                    )
                if cell & WALL_W:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (cx, cy), (cx, cy + CELL_SIZE), 2
                    )
                if cell & WALL_E:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (cx + CELL_SIZE, cy),
                        (cx + CELL_SIZE, cy + CELL_SIZE), 2
                    )

    def draw_items(self, items: list[list[int]]) -> None:
        """Draw pacgums and super-pacgums.

        Args:
            items: 2D grid of item types.
        """
        h = len(items)
        w = len(items[0]) if h > 0 else 0

        for y in range(h):
            for x in range(w):
                item = items[y][x]
                if item == ITEM_PACGUM:
                    mx = x * CELL_SIZE + CELL_SIZE // 2
                    my = y * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(
                        self.screen, PACGUM_COLOR,
                        (mx, my), 3
                    )
                elif item == ITEM_SUPER:
                    mx = x * CELL_SIZE + CELL_SIZE // 2
                    my = y * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(
                        self.screen, PACGUM_COLOR,
                        (mx, my), 8
                    )

    def draw_player(self, player: Player) -> None:
        """Draw Pac-Man with animated mouth.

        Args:
            player: The player object.
        """
        if player.dead:
            return

        cx = player.x * CELL_SIZE + CELL_SIZE // 2
        cy = player.y * CELL_SIZE + CELL_SIZE // 2
        r = int(CELL_SIZE * 0.42)
        mouth = player.get_mouth_angle()

        # Base angle based on direction
        base: float = 0.0
        if player.direction == DIR_E:
            base = 0.0
        elif player.direction == DIR_S:
            base = math.pi / 2
        elif player.direction == DIR_W:
            base = math.pi
        elif player.direction == DIR_N:
            base = -math.pi / 2

        # Draw pac-man as a filled arc
        start_angle = base + mouth
        end_angle = base + 2 * math.pi - mouth

        # Use polygon for mouth
        points = [(cx, cy)]
        steps = 30
        for i in range(steps + 1):
            a = start_angle + (end_angle - start_angle) * i / steps
            px = cx + int(r * math.cos(a))
            py = cy + int(r * math.sin(a))
            points.append((px, py))

        if len(points) > 2:
            pygame.draw.polygon(self.screen, YELLOW, points)

        # Eye
        eye_angle = base - 0.6
        ex = cx + int(r * 0.45 * math.cos(eye_angle))
        ey = cy + int(r * 0.45 * math.sin(eye_angle))
        pygame.draw.circle(self.screen, BLACK, (ex, ey), 2)

    def draw_ghost(self, ghost: Ghost, player_x: int,
                   player_y: int) -> None:
        """Draw a single ghost.

        Args:
            ghost: The ghost object.
            player_x: Player x for eye direction.
            player_y: Player y for eye direction.
        """
        if ghost.eaten:
            # Draw just eyes floating back
            self._draw_ghost_eyes(
                ghost.x * CELL_SIZE + CELL_SIZE // 2,
                ghost.y * CELL_SIZE + CELL_SIZE // 2,
                player_x, player_y,
                int(CELL_SIZE * 0.4)
            )
            return

        cx = ghost.x * CELL_SIZE + CELL_SIZE // 2
        cy = ghost.y * CELL_SIZE + CELL_SIZE // 2
        r = int(CELL_SIZE * 0.4)

        color = FRIGHTENED_BLUE if ghost.frightened else ghost.color

        # Blinking when frightened is about to end
        if ghost.frightened and ghost.frighten_timer < 2.0:
            if int(ghost.frighten_timer * 4) % 2 == 0:
                color = WHITE

        # Body - semicircle top + wavy bottom
        # body_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        pygame.draw.circle(self.screen, color, (cx, cy - 2), r)
        pygame.draw.rect(
            self.screen, color,
            (cx - r, cy - 2, r * 2, r)
        )

        # Wavy bottom
        wave_y = cy + r - 4
        seg_w = (r * 2) // 3
        for i in range(3):
            sx = cx - r + i * seg_w
            bump = 4 if i % 2 == 0 else -2
            pygame.draw.circle(
                self.screen, color,
                (sx + seg_w // 2, wave_y + bump),
                seg_w // 2
            )

        # Eyes
        if not ghost.frightened:
            self._draw_ghost_eyes(cx, cy, player_x, player_y, r)
        else:
            # Simple frightened eyes
            pygame.draw.circle(
                self.screen, WHITE,
                (cx - r // 3, cy - r // 4), 3
            )
            pygame.draw.circle(
                self.screen, WHITE,
                (cx + r // 3, cy - r // 4), 3
            )

    def _draw_ghost_eyes(self, cx: int, cy: int,
                         player_x: int, player_y: int,
                         r: int) -> None:
        """Draw ghost eyes looking toward the player.

        Args:
            cx: Ghost center x pixel.
            cy: Ghost center y pixel.
            player_x: Player cell x.
            player_y: Player cell y.
            r: Ghost radius.
        """
        eye_off = r // 3
        eye_r = max(3, r // 4)
        pupil_r = max(1, eye_r // 2)

        # White part
        for dx in [-eye_off, eye_off]:
            pygame.draw.circle(
                self.screen, WHITE,
                (cx + dx, cy - r // 4), eye_r
            )

        # Pupils looking at player
        px_pixel = player_x * CELL_SIZE + CELL_SIZE // 2
        py_pixel = player_y * CELL_SIZE + CELL_SIZE // 2
        angle = math.atan2(py_pixel - cy, px_pixel - cx)
        pd = eye_r * 0.35

        for dx in [-eye_off, eye_off]:
            px = int(cx + dx + math.cos(angle) * pd)
            py = int(cy - r // 4 + math.sin(angle) * pd)
            pygame.draw.circle(
                self.screen, BLUE, (px, py), pupil_r
            )

    def draw_hud(self, score: int, lives: int, level: int,
                 total_levels: int, time_left: int,
                 cheats: dict[str, bool]) -> None:
        """Draw the in-game HUD bar.

        Args:
            score: Current score.
            lives: Remaining lives.
            level: Current level number.
            total_levels: Total number of levels.
            time_left: Seconds remaining.
            cheats: Active cheat flags.
        """
        hud_y = self.maze_h * CELL_SIZE + 4

        # Background bar
        pygame.draw.rect(
            self.screen, (20, 20, 40),
            (0, self.maze_h * CELL_SIZE, self.pixel_w, HUD_HEIGHT)
        )

        score_surf = self.font.render(
            f"Score: {score}", True, WHITE
        )
        self.screen.blit(score_surf, (10, hud_y + 4))

        lives_surf = self.font.render(
            f"Lives: {lives}", True, WHITE
        )
        self.screen.blit(lives_surf,
                         (self.pixel_w // 4, hud_y + 4))

        level_surf = self.font.render(
            f"Lvl: {level}/{total_levels}", True, WHITE
        )
        self.screen.blit(level_surf,
                         (self.pixel_w // 2, hud_y + 4))

        time_color = WHITE if time_left > 15 else (
            (255, 100, 100) if time_left > 5 else (255, 0, 0)
        )
        time_surf = self.font.render(
            f"Time: {time_left}", True, time_color
        )
        self.screen.blit(time_surf,
                         (self.pixel_w * 3 // 4, hud_y + 4))

        # Cheat indicators
        flags: list[str] = []
        if cheats.get("god"):
            flags.append("GOD")
        if cheats.get("freeze"):
            flags.append("FREEZE")
        if cheats.get("speed"):
            flags.append("SPEED")
        if flags:
            cheat_surf = self.small_font.render(
                " | ".join(flags), True, (255, 80, 80)
            )
            self.screen.blit(cheat_surf, (10, hud_y + 26))

    def draw_overlay(self, alpha: int = 200) -> None:
        """Draw a semi-transparent dark overlay.

        Args:
            alpha: Transparency value (0-255).
        """
        overlay = pygame.Surface(
            (self.pixel_w, self.pixel_h)
        )
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

    def draw_text_centered(self, text: str, y: int,
                           color: tuple[int, int, int] = WHITE,
                           font: Optional[pygame.font.Font] = None
                           ) -> None:
        """Draw centered text.

        Args:
            text: Text to render.
            y: Y position for text center.
            color: Text color.
            font: Font to use (defaults to medium_font).
        """
        f = font or self.medium_font
        surf = f.render(text, True, color)
        rect = surf.get_rect(center=(self.pixel_w // 2, y))
        self.screen.blit(surf, rect)

    def draw_menu(self, highscores: list[tuple[str, int]],
                  selected: int = 0) -> None:
        """Draw the main menu screen.

        Args:
            highscores: List of (name, score) tuples.
            selected: Currently selected menu item index.
        """
        self.screen.fill((10, 10, 30))
        self.draw_text_centered(
            "PAC-MAN", self.pixel_h // 6,
            YELLOW, self.title_font
        )
        self.draw_text_centered(
            "Ghosts! More ghosts!",
            self.pixel_h // 6 + 45,
            (150, 150, 150), self.small_font
        )

        options = ["Start Game", "Highscores",
                   "Instructions", "Exit"]
        base_y = self.pixel_h // 3 + 20
        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            prefix = "> " if i == selected else "  "
            self.draw_text_centered(
                prefix + opt, base_y + i * 38, color
            )

        # Display highscores below menu options
        hs_y = base_y + len(options) * 38 + 20
        if highscores:
            self.draw_text_centered(
                "highscores:", hs_y,
                (180, 180, 180), self.small_font
            )
            for i, (name, score) in enumerate(highscores[:5]):
                entry_color = YELLOW if i == 0 else (
                    PACGUM_COLOR if i < 3 else (160, 160, 160)
                )
                self.draw_text_centered(
                    f"{i + 1}. {name} - {score} pts",
                    hs_y + 22 + i * 20,
                    entry_color, self.small_font
                )

    def draw_pause_menu(self, selected: int = 0) -> None:
        """Draw the pause screen overlay.

        Args:
            selected: Currently selected option.
        """
        self.draw_overlay(180)
        self.draw_text_centered(
            "PAUSED", self.pixel_h // 3,
            YELLOW, self.title_font
        )
        options = ["Resume", "Main Menu"]
        base_y = self.pixel_h // 2
        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            prefix = "> " if i == selected else "  "
            self.draw_text_centered(
                prefix + opt, base_y + i * 38, color
            )

    def draw_highscores(self, entries: list[tuple[str, int]]
                        ) -> None:
        """Draw highscores screen.

        Args:
            entries: List of (name, score) tuples.
        """
        self.screen.fill((10, 10, 30))
        self.draw_text_centered(
            "TOP 10 HIGHSCORES", 50,
            YELLOW, self.medium_font
        )
        if not entries:
            self.draw_text_centered(
                "No scores yet", self.pixel_h // 2,
                (128, 128, 128)
            )
        else:
            for i, (name, score) in enumerate(entries[:10]):
                color = YELLOW if i == 0 else (
                    PACGUM_COLOR if i < 3 else (180, 180, 180)
                )
                y = 100 + i * 32
                text = f"{i + 1}. {name:<12} {score:>6} pts"
                self.draw_text_centered(text, y, color, self.font)

        self.draw_text_centered(
            "Press ESCAPE to go back",
            self.pixel_h - 40,
            (100, 100, 100), self.small_font
        )

    def draw_instructions(self) -> None:
        """Draw instructions screen."""
        self.screen.fill((10, 10, 30))
        self.draw_text_centered(
            "HOW TO PLAY", 50, YELLOW, self.medium_font
        )
        lines = [
            ("Arrow Keys / WASD", "Move Pac-Man"),
            ("ESC / P", "Pause game"),
            ("", ""),
            ("Eat all pacgums to clear a level!", ""),
            ("Super-pacgums make ghosts edible!", ""),
            ("", ""),
            ("--- CHEAT KEYS (for review) ---", ""),
            ("1", "God mode (invincible)"),
            ("2", "Freeze ghosts"),
            ("3", "Speed boost"),
            ("4", "Skip level"),
            ("5", "Extra life"),
        ]
        for i, (key, desc) in enumerate(lines):
            y = 100 + i * 28
            if key and desc:
                self.draw_text_centered(
                    f"{key}: {desc}", y, WHITE, self.small_font
                )
            elif key:
                color = (255, 100, 100) if "CHEAT" in key else (
                    PACGUM_COLOR
                )
                self.draw_text_centered(
                    key, y, color, self.small_font
                )

        self.draw_text_centered(
            "Press ESCAPE to go back",
            self.pixel_h - 40,
            (100, 100, 100), self.small_font
        )

    def draw_enter_name(self, final_score: int,
                        player_name: str,
                        is_victory: bool) -> None:
        """Draw the name entry screen after game ends.

        Args:
            final_score: The player's final score.
            player_name: Current name text being entered.
            is_victory: Whether the player won.
        """
        self.draw_overlay(200)
        title = "YOU WIN!" if is_victory else "GAME OVER"
        color = (0, 255, 0) if is_victory else (255, 50, 50)
        self.draw_text_centered(
            title, self.pixel_h // 4, color, self.title_font
        )
        if is_victory:
            self.draw_text_centered(
                "Congratulations! You cleared all levels!",
                self.pixel_h // 4 + 40,
                (200, 255, 200), self.small_font
            )
        self.draw_text_centered(
            f"Final Score: {final_score}",
            self.pixel_h // 4 + 70, YELLOW
        )
        self.draw_text_centered(
            "Enter your name:",
            self.pixel_h // 2 - 20, WHITE, self.font
        )

        # Name input box
        box_w, box_h = 260, 40
        box_x = (self.pixel_w - box_w) // 2
        box_y = self.pixel_h // 2 + 10
        pygame.draw.rect(
            self.screen, (40, 40, 60),
            (box_x, box_y, box_w, box_h)
        )
        pygame.draw.rect(
            self.screen, YELLOW,
            (box_x, box_y, box_w, box_h), 2
        )

        name_surf = self.medium_font.render(
            player_name + "_", True, YELLOW
        )
        name_rect = name_surf.get_rect(
            center=(self.pixel_w // 2, box_y + box_h // 2)
        )
        self.screen.blit(name_surf, name_rect)

        self.draw_text_centered(
            "Press ENTER to save",
            box_y + box_h + 30,
            (150, 150, 150), self.small_font
        )
