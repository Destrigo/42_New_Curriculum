---
title: "Pac-Man — Project Roadmap & Architecture"
---

# Pac-Man — How It Works

## 1. Startup Flow

Everything begins at `pac-man.py`. The entry point validates the command-line argument (a `.json` config file), then hands control to the `Game` class.

1. **Argument parsing** — Checks exactly one `.json` argument is provided. Any error prints a clear message and exits with code 84 (no traceback ever).
2. **Config loading** (`config.py`) — Reads the JSON file, strips `#`, `//`, and `/* */` comments, then validates every key. Invalid or missing values get clamped to safe defaults and logged. Unknown keys are silently ignored.
3. **Pygame initialization** — Creates the display window sized to the first level's maze dimensions.
4. **Highscore loading** (`highscore.py`) — Reads `highscores.json` from disk. If the file is missing or corrupt, starts fresh without crashing.
5. **State machine starts at `MENU`** — The game loop begins.

---

## 2. The Game Loop

The `Game.run()` method drives a classic **fixed-timestep game loop** at 60 FPS:

```
while running:
    dt = clock.tick(60) / 1000.0   # delta time in seconds
    handle_events()                 # process keyboard input
    update(dt)                      # advance game logic
    render()                        # draw everything
```

Each of the three phases behaves differently depending on the current **state**. The state machine has 6 screens: Menu, Playing, Paused, Highscores, Instructions, and Enter Name (covers both game-over and victory).

---

## 3. State Machine

| State           | Input Handling              | Update Logic       | Renders                   |
|-----------------|-----------------------------|--------------------|---------------------------|
| **Menu**        | Arrow keys navigate, Enter selects | None         | Menu + top 5 highscores   |
| **Playing**     | WASD/Arrows move, ESC pauses, 1-5 cheats | Full game logic | Maze, player, ghosts, HUD |
| **Paused**      | Arrow keys navigate, Enter selects, ESC resumes | None | Game view + dark overlay + pause options |
| **Highscores**  | ESC returns to menu         | None               | Top 10 scores list        |
| **Instructions**| ESC returns to menu         | None               | Controls & cheat keys     |
| **Enter Name**  | Type name, Enter saves      | None               | Game view + overlay + name input |

Transitions:
- Menu → Playing (start game), Highscores, Instructions, or Exit
- Playing → Paused (ESC), Enter Name (all lives lost or all levels cleared)
- Paused → Playing (resume) or Menu (quit to menu)
- Enter Name → Menu (after saving highscore)
- Highscores/Instructions → Menu (ESC)

---

## 4. Level Initialization (`start_level`)

When a level begins (either from menu "Start Game" or after completing the previous level):

1. **Get level config** — Reads `width` and `height` from the `levels` array for the current level number. Mazes grow progressively.
2. **Generate maze** — Calls the external `mazegenerator` package via `maze.py`:
   - Level 1 uses the fixed seed from config (default 42) for reproducibility.
   - Levels 2+ use a random seed.
   - `perfect=False` produces imperfect mazes with loops (Pac-Man-compatible corridors).
   - If the package fails, a fallback generator kicks in.
3. **Resize renderer** — Adjusts the Pygame window to the new maze dimensions.
4. **Place entities**:
   - Player spawns at the nearest walkable cell to the maze center.
   - 4 ghosts spawn near the 4 corners.
   - Pacgums are placed on every walkable cell (except player/ghost positions).
   - Super-pacgums replace the pacgum nearest to each corner.
5. **Reset timers** — Level countdown, movement accumulators, and direction queue are all reset.
6. **Carry state** — Score and lives are carried from the previous level.

---

## 5. Update Tick (each frame during Playing)

The `update(dt)` method runs every frame (~16ms) and processes in this order:

### 5.1 Death Pause
If the player just died, a 1-second pause plays. After it expires, player respawns at center, ghosts reset to corners.

### 5.2 Level Timer
A wall-clock timer counts down `level_max_time` seconds. When it reaches 0, the player loses a life. If lives remain, the level resets (player/ghosts respawn, timer restarts). If no lives remain → Game Over.

### 5.3 Player Movement
Uses a **tick accumulator** (default: every 160ms, halved with speed cheat). Each tick:
1. Try the **queued direction** first (the last arrow key pressed).
2. If that's blocked by a wall, continue in the **current direction**.
3. If that's also blocked, stand still.
4. On successful move → check item collection.

### 5.4 Item Collection
When the player enters a cell:
- **Pacgum**: +10 points, decrement pacgums remaining.
- **Super-pacgum**: +50 points, decrement pacgums remaining, all non-eaten ghosts enter **frightened** state for 8 seconds.

### 5.5 Ghost Movement
Uses a separate accumulator (default: every 260ms). Each ghost independently:
1. Gets valid moves (cells reachable through open walls).
2. Filters out the reverse direction (ghosts don't U-turn unless forced).
3. **Chase mode** (normal): picks the move minimizing Manhattan distance to player.
4. **Flee mode** (frightened): picks the move maximizing distance from player.
5. **Personality**: each ghost has a random-move probability (Blinky 10%, Pinky 20%, Inky 35%, Clyde 50%).

### 5.6 Ghost Timers
Each frame updates:
- **Frighten timer**: counts down. When expired, ghost returns to chase mode.
- **Respawn timer** (if eaten): counts down. When expired, ghost respawns at home corner.

### 5.7 Collision Detection
Checks every ghost against the player's position:
- **Ghost frightened** → ghost gets eaten: +200 points, ghost enters "eaten" state, starts respawn timer.
- **Ghost normal + no god mode** → player loses a life. If lives remain, enter death pause. If no lives → Game Over.
- **Ghost normal + god mode** → nothing happens.

### 5.8 Level Completion
If `pacgums_left == 0`:
- If current level is the last → Victory screen.
- Otherwise → load next level with carried score and lives.

---

## 6. Rendering Pipeline

The `render()` method draws in strict layer order:

1. **Clear screen** to black.
2. **Maze walls** — Each cell is inspected. Solid blocks (value 15) draw a filled blue square. Other cells draw blue lines for each wall bit that is set (N=1, E=2, S=4, W=8).
3. **Items** — Small yellow circles for pacgums, larger ones for super-pacgums.
4. **Ghosts** — Colored body with semicircle + wavy bottom. Eyes track the player's position. Frightened ghosts turn blue and blink white when about to expire. Eaten ghosts show only floating eyes.
5. **Pac-Man** — Yellow polygon with animated mouth (opens/closes using a sine-based timer). Eye drawn relative to facing direction.
6. **HUD bar** — Score, lives, level, and countdown timer. Cheat indicators in red if active.
7. **Overlays** — Pause menu, name entry, etc. drawn on top with semi-transparent black background.

---

## 7. Module Responsibilities

| Module          | Role                                                              |
|-----------------|-------------------------------------------------------------------|
| `pac-man.py`    | Entry point: argument validation, error wrapping                  |
| `constants.py`  | All shared constants: colors, sizes, wall encoding, state names   |
| `config.py`     | JSON config loading with comment stripping and validation         |
| `maze.py`       | Wraps `mazegenerator` package, provides wall-checking helpers     |
| `player.py`     | Player state: position, direction, lives, movement, animation     |
| `ghost.py`      | Ghost AI: chase/flee behavior, frightened/eaten states, timers    |
| `highscore.py`  | Persistent top-10 storage: load/save JSON, name validation        |
| `renderer.py`   | All Pygame drawing: maze, sprites, HUD, menus, overlays           |
| `game.py`       | Orchestrator: state machine, game loop, collision, level loading  |

---

## 8. Cheat Mode

Activated by pressing number keys during gameplay (designed for peer review):

| Key | Effect              | Toggle |
|-----|---------------------|--------|
| 1   | God mode (invincible) | On/Off |
| 2   | Freeze ghosts       | On/Off |
| 3   | Speed boost (2×)    | On/Off |
| 4   | Skip level instantly| One-shot |
| 5   | Add extra life      | One-shot |

Active cheats are shown in red on the HUD bar.

---

## 9. Wall Encoding (from mazegenerator)

Each cell is an integer where the 4 low bits represent walls:

```
  Bit 0 (1) = North wall     ───
  Bit 1 (2) = East wall        │ right
  Bit 2 (4) = South wall     ───
  Bit 3 (8) = West wall      │ left
  Value 15  = Solid block (all walls / impassable)
```

Movement from cell `(x, y)` in direction `D` is allowed when `cell & DIR_TO_WALL[D] == 0` and the destination cell is not a solid block (value 15).
