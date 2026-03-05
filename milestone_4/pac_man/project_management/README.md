# Project Management

## Timeline

| Phase              | Duration   | Status     |
|--------------------|-----------|------------|
| Architecture design | Day 1-2   | Complete   |
| Config & maze integration | Day 2-3 | Complete |
| Core game logic     | Day 3-6   | Complete   |
| Ghost AI            | Day 5-7   | Complete   |
| UI & rendering      | Day 6-8   | Complete   |
| Highscore system    | Day 7-8   | Complete   |
| Cheat mode          | Day 8     | Complete   |
| Testing & polish    | Day 8-10  | Complete   |
| Packaging           | Day 10    | Complete   |

## Architecture Choices

- **Pygame** was chosen as the graphical library for its simplicity, cross-platform support, and extensive documentation.
- **Modular design**: Each component (player, ghost, maze, config, highscore, renderer) is in its own module to enable independent testing and clear responsibility boundaries.
- **State machine**: Game flow is managed through explicit state constants, avoiding complex conditional logic.

## Risk Analysis

| Risk                          | Mitigation                                    |
|-------------------------------|-----------------------------------------------|
| mazegenerator API changes     | Fallback generator, defensive coding          |
| Pygame not available          | Clear install instructions, requirements.txt  |
| Config file corruption        | Robust defaults, graceful error handling       |
| Highscore file corruption     | Auto-recovery, fresh start on invalid data    |
| Performance with large mazes  | Cell-based rendering, capped FPS              |

## Acceptance Tests

- [x] Game launches with valid config
- [x] Game handles missing/invalid config gracefully
- [x] Maze generates correctly from mazegenerator package
- [x] Player moves through corridors, blocked by walls
- [x] Pacgums collected, score increases
- [x] Super-pacgums frighten ghosts
- [x] Frightened ghosts can be eaten
- [x] Ghost respawn after being eaten
- [x] Player loses life on ghost collision
- [x] Game over when all lives lost
- [x] Level completes when all pacgums eaten
- [x] Level progression with carried score/lives
- [x] Timer counts down, triggers level restart
- [x] Highscore saved and loaded
- [x] Name entry on game end
- [x] Main menu navigation
- [x] Pause/resume works
- [x] All cheat modes functional
- [x] No crashes on any error condition
