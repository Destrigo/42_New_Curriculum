"""Main game module coordinating all Pac-Man components.

Manages game state transitions, the main loop, level loading,
input handling, and collision detection.
"""

import random
import time
from typing import Any, Optional

import pygame

from src.constants import (
    FPS,
    DIR_N, DIR_E, DIR_S, DIR_W,
    ITEM_EMPTY, ITEM_PACGUM, ITEM_SUPER,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_ENTER_NAME,
    STATE_HIGHSCORES, STATE_INSTRUCTIONS,
    DEFAULT_CONFIG,
)
from src.config import load_config
from src.maze import generate_maze, find_nearest_walkable, place_items
from src.player import Player
from src.ghost import Ghost
from src.highscore import HighscoreManager
from src.renderer import Renderer


class Game:
    """Main game class managing the full Pac-Man game.

    Attributes:
        config: Loaded configuration dictionary.
        state: Current game state string.
        clock: Pygame clock for FPS management.
        renderer: Renderer instance.
        highscores: Highscore manager.
        player: Current player instance.
        ghosts: List of ghost instances.
        maze: Current maze grid.
        items: Current items grid.
        level: Current level number.
        time_left: Seconds remaining in current level.
        cheats: Dictionary of active cheat flags.
        running: Whether the game loop is running.
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the game.

        Args:
            config_path: Path to the JSON configuration file.
        """
        self.config: dict[str, Any] = load_config(config_path)
        self.state: str = STATE_MENU
        self.menu_selection: int = 0
        self.pause_selection: int = 0
        self.running: bool = True

        # Pygame init
        pygame.init()
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # Use first level's dimensions for initial display
        levels = self.config.get("levels", DEFAULT_CONFIG["levels"])
        first = levels[0] if levels else {"width": 19, "height": 15}
        self.renderer: Renderer = Renderer(
            first["width"], first["height"]
        )

        # Highscores
        self.highscores: HighscoreManager = HighscoreManager(
            self.config["highscore_filename"]
        )

        # Game objects (initialized on level start)
        self.maze: list[list[int]] = []
        self.items: list[list[int]] = []
        self.maze_w: int = 0
        self.maze_h: int = 0
        self.player: Optional[Player] = None
        self.ghosts: list[Ghost] = []
        self.level: int = 1
        self.time_left: float = 0.0
        self.last_timer_tick: float = 0.0
        self.pacgums_left: int = 0
        self.is_victory: bool = False

        # Movement timing
        self.player_move_acc: float = 0.0
        self.ghost_move_acc: float = 0.0
        self.player_move_interval: float = 0.16
        self.ghost_move_interval: float = 0.26

        # Cheats
        self.cheats: dict[str, bool] = {
            "god": False,
            "freeze": False,
            "speed": False,
        }

        # Input
        self.player_name: str = ""
        self.queued_direction: Optional[str] = None

    def _get_level_config(self, level_num: int
                          ) -> dict[str, int]:
        """Get maze dimensions for a given level.

        Args:
            level_num: Level number (1-based).

        Returns:
            Dict with 'width' and 'height' keys.
        """
        levels = self.config.get("levels",
                                 DEFAULT_CONFIG["levels"])
        idx = min(level_num - 1, len(levels) - 1)
        if idx < 0:
            idx = 0
        return levels[idx]

    def _total_levels(self) -> int:
        """Get total number of levels.

        Returns:
            Number of levels defined in config.
        """
        levels = self.config.get("levels",
                                 DEFAULT_CONFIG["levels"])
        return len(levels)

    def start_level(self, level_num: int,
                    carry_score: int = 0,
                    carry_lives: int = -1) -> None:
        """Initialize a new level.

        Args:
            level_num: Level number to start.
            carry_score: Score carried from previous level.
            carry_lives: Lives carried (-1 uses config default).
        """
        self.level = level_num
        lc = self._get_level_config(level_num)
        self.maze_w = lc["width"]
        self.maze_h = lc["height"]

        # Generate maze
        seed = (self.config["seed"]
                if level_num == 1
                else random.randint(1, 999999))
        self.maze = generate_maze(
            self.maze_w, self.maze_h, seed, perfect=False
        )

        # Resize renderer
        self.renderer.resize(self.maze_w, self.maze_h)

        # Find player start (center)
        cx = self.maze_w // 2
        cy = self.maze_h // 2
        px, py = find_nearest_walkable(self.maze, cx, cy)

        # Find ghost starts (corners)
        corner_targets = [
            (1, 1),
            (self.maze_w - 2, 1),
            (1, self.maze_h - 2),
            (self.maze_w - 2, self.maze_h - 2),
        ]
        ghost_positions: list[tuple[int, int]] = []
        for gx, gy in corner_targets:
            sx, sy = find_nearest_walkable(self.maze, gx, gy)
            # Avoid overlap with player
            if sx == px and sy == py:
                sx, sy = find_nearest_walkable(
                    self.maze, gx + 1, gy + 1
                )
            ghost_positions.append((sx, sy))

        # Place items
        self.items, self.pacgums_left = place_items(
            self.maze, (px, py), ghost_positions
        )

        # Create player
        lives = (carry_lives if carry_lives >= 0
                 else self.config["lives"])
        self.player = Player(px, py, lives)
        self.player.score = carry_score

        # Create ghosts
        self.ghosts = []
        for i, (gx, gy) in enumerate(ghost_positions):
            self.ghosts.append(Ghost(i, gx, gy))

        # Timing
        self.time_left = float(self.config["level_max_time"])
        self.last_timer_tick = time.time()
        self.player_move_acc = 0.0
        self.ghost_move_acc = 0.0
        self.queued_direction = None
        self.is_victory = False

    def handle_events(self) -> None:
        """Process pygame events and input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

    def _handle_keydown(self, key: int) -> None:
        """Handle a key press based on current state.

        Args:
            key: Pygame key constant.
        """
        if self.state == STATE_MENU:
            self._handle_menu_key(key)
        elif self.state == STATE_PLAYING:
            self._handle_playing_key(key)
        elif self.state == STATE_PAUSED:
            self._handle_pause_key(key)
        elif self.state == STATE_HIGHSCORES:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
        elif self.state == STATE_INSTRUCTIONS:
            if key == pygame.K_ESCAPE:
                self.state = STATE_MENU
        elif self.state == STATE_ENTER_NAME:
            self._handle_name_entry_key(key)

    def _handle_menu_key(self, key: int) -> None:
        """Handle key in main menu.

        Args:
            key: Pygame key constant.
        """
        if key in (pygame.K_UP, pygame.K_w):
            self.menu_selection = (self.menu_selection - 1) % 4
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu_selection = (self.menu_selection + 1) % 4
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.menu_selection == 0:
                # Start game
                self.cheats = {
                    "god": False, "freeze": False, "speed": False
                }
                self.start_level(1)
                self.state = STATE_PLAYING
            elif self.menu_selection == 1:
                self.state = STATE_HIGHSCORES
            elif self.menu_selection == 2:
                self.state = STATE_INSTRUCTIONS
            elif self.menu_selection == 3:
                self.running = False

    def _handle_playing_key(self, key: int) -> None:
        """Handle key during gameplay.

        Args:
            key: Pygame key constant.
        """
        # Movement
        if key in (pygame.K_UP, pygame.K_w):
            self.queued_direction = DIR_N
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.queued_direction = DIR_S
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.queued_direction = DIR_W
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.queued_direction = DIR_E

        # Pause
        if key in (pygame.K_ESCAPE, pygame.K_p):
            self.state = STATE_PAUSED
            self.pause_selection = 0

        # Cheats
        if key == pygame.K_1:
            self.cheats["god"] = not self.cheats["god"]
        elif key == pygame.K_2:
            self.cheats["freeze"] = not self.cheats["freeze"]
        elif key == pygame.K_3:
            self.cheats["speed"] = not self.cheats["speed"]
        elif key == pygame.K_4:
            # Skip level
            self.pacgums_left = 0
        elif key == pygame.K_5:
            # Extra life
            if self.player:
                self.player.lives += 1

    def _handle_pause_key(self, key: int) -> None:
        """Handle key in pause menu.

        Args:
            key: Pygame key constant.
        """
        if key in (pygame.K_ESCAPE, pygame.K_p):
            self.state = STATE_PLAYING
            self.last_timer_tick = time.time()
        elif key in (pygame.K_UP, pygame.K_w):
            self.pause_selection = (
                (self.pause_selection - 1) % 2
            )
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.pause_selection = (
                (self.pause_selection + 1) % 2
            )
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.pause_selection == 0:
                self.state = STATE_PLAYING
                self.last_timer_tick = time.time()
            elif self.pause_selection == 1:
                self.state = STATE_MENU

    def _handle_name_entry_key(self, key: int) -> None:
        """Handle key in name entry screen.

        Args:
            key: Pygame key constant.
        """
        if key == pygame.K_RETURN:
            name = self.player_name.strip() or "Player"
            score = self.player.score if self.player else 0
            self.highscores.add(name, score)
            self.player_name = ""
            self.state = STATE_MENU
        elif key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        else:
            char = pygame.key.name(key)
            if len(char) == 1 and char.isalnum():
                if len(self.player_name) < 10:
                    self.player_name += char
            elif key == pygame.K_SPACE:
                if len(self.player_name) < 10:
                    self.player_name += " "

    def update(self, dt: float) -> None:
        """Update game logic for one frame.

        Args:
            dt: Delta time in seconds.
        """
        if self.state != STATE_PLAYING:
            return
        if not self.player:
            return

        # ── Death pause ──
        if self.player.dead:
            self.player.dead_timer -= dt
            if self.player.dead_timer <= 0:
                self.player.respawn()
                for g in self.ghosts:
                    g.reset()
            return

        # ── Timer ──
        now = time.time()
        elapsed = now - self.last_timer_tick
        if elapsed >= 1.0:
            self.time_left -= int(elapsed)
            self.last_timer_tick = now
            if self.time_left <= 0:
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self._end_game(victory=False)
                    return
                else:
                    # Restart level
                    self.time_left = float(
                        self.config["level_max_time"]
                    )
                    self.player.respawn()
                    for g in self.ghosts:
                        g.reset()

        # ── Player animation ──
        self.player.update_animation(dt)

        # ── Player movement ──
        speed_mult = 0.5 if self.cheats["speed"] else 1.0
        self.player_move_acc += dt
        if self.player_move_acc >= self.player_move_interval * speed_mult:
            self.player_move_acc = 0.0
            moved = False
            if self.queued_direction:
                moved = self.player.try_move(
                    self.queued_direction, self.maze
                )
                if moved:
                    pass  # queued dir stays as new dir
                else:
                    moved = self.player.try_move(
                        self.player.direction, self.maze
                    )
            else:
                moved = self.player.try_move(
                    self.player.direction, self.maze
                )

            if moved:
                self._check_item_collection()

        # ── Ghost movement ──
        if not self.cheats["freeze"]:
            self.ghost_move_acc += dt
            if self.ghost_move_acc >= self.ghost_move_interval:
                self.ghost_move_acc = 0.0
                for g in self.ghosts:
                    g.move(self.player.x, self.player.y,
                           self.maze)

        # ── Ghost timers ──
        for g in self.ghosts:
            g.update(dt, self.player.x, self.player.y,
                     self.maze, self.cheats["freeze"])

        # ── Collision detection ──
        self._check_collisions()

        # ── Level complete? ──
        if self.pacgums_left <= 0:
            if self.level >= self._total_levels():
                self._end_game(victory=True)
            else:
                self.start_level(
                    self.level + 1,
                    self.player.score,
                    self.player.lives
                )

    def _check_item_collection(self) -> None:
        """Check if player collected an item at current position."""
        if not self.player:
            return
        px, py = self.player.x, self.player.y
        if py < 0 or py >= self.maze_h or px < 0 or px >= self.maze_w:
            return

        item = self.items[py][px]
        if item == ITEM_PACGUM:
            self.items[py][px] = ITEM_EMPTY
            self.player.score += self.config["points_per_pacgum"]
            self.pacgums_left -= 1
        elif item == ITEM_SUPER:
            self.items[py][px] = ITEM_EMPTY
            self.player.score += self.config[
                "points_per_super_pacgum"
            ]
            self.pacgums_left -= 1
            # Frighten all ghosts
            dur = float(self.config["frightened_duration"])
            for g in self.ghosts:
                g.make_frightened(dur)

    def _check_collisions(self) -> None:
        """Check player-ghost collisions."""
        if not self.player:
            return

        for g in self.ghosts:
            if g.eaten:
                continue
            if g.x == self.player.x and g.y == self.player.y:
                if g.frightened:
                    # Eat the ghost
                    self.player.score += self.config[
                        "points_per_ghost"
                    ]
                    g.eat(float(
                        self.config["ghost_respawn_time"]
                    ))
                elif not self.cheats["god"]:
                    # Player dies
                    self.player.lives -= 1
                    if self.player.lives <= 0:
                        self._end_game(victory=False)
                        return
                    self.player.dead = True
                    self.player.dead_timer = 1.0

    def _end_game(self, victory: bool) -> None:
        """Transition to end-game screen.

        Args:
            victory: Whether the player won.
        """
        self.is_victory = victory
        self.state = STATE_ENTER_NAME
        self.player_name = ""

    def render(self) -> None:
        """Render the current frame based on game state."""
        if self.state == STATE_MENU:
            entries = [
                (e.name, e.score)
                for e in self.highscores.get_top(5)
            ]
            self.renderer.draw_menu(entries, self.menu_selection)

        elif self.state == STATE_HIGHSCORES:
            entries = [
                (e.name, e.score)
                for e in self.highscores.get_top(10)
            ]
            self.renderer.draw_highscores(entries)

        elif self.state == STATE_INSTRUCTIONS:
            self.renderer.draw_instructions()

        elif self.state in (STATE_PLAYING, STATE_PAUSED,
                            STATE_ENTER_NAME):
            self.renderer.clear()
            self.renderer.draw_maze(self.maze)
            self.renderer.draw_items(self.items)

            if self.player:
                for g in self.ghosts:
                    self.renderer.draw_ghost(
                        g, self.player.x, self.player.y
                    )
                self.renderer.draw_player(self.player)
                self.renderer.draw_hud(
                    self.player.score,
                    self.player.lives,
                    self.level,
                    self._total_levels(),
                    max(0, int(self.time_left)),
                    self.cheats,
                )

            if self.state == STATE_PAUSED:
                self.renderer.draw_pause_menu(
                    self.pause_selection
                )
            elif self.state == STATE_ENTER_NAME:
                score = self.player.score if self.player else 0
                self.renderer.draw_enter_name(
                    score, self.player_name, self.is_victory
                )

        pygame.display.flip()

    def run(self) -> None:
        """Run the main game loop until exit."""
        while self.running:
            dt: float = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()
