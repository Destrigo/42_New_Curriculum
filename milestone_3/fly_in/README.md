# Fly-in: Drone Routing System

*This project has been created as part of the 42 curriculum by mtaranti.*

## Description

Fly-in is an efficient drone routing system that navigates multiple autonomous drones through a network of connected zones while minimizing simulation turns and respecting complex movement constraints. The system implements sophisticated pathfinding algorithms to route drones from a central hub to a target destination while handling:

- Zone capacity constraints (maximum drones per zone)
- Connection capacity limits (maximum simultaneous traversals)
- Variable movement costs (normal, restricted, priority, and blocked zones)
- Multi-turn movements through restricted zones
- Deadlock avoidance and conflict resolution
- Real-time visual feedback through terminal animation

The project demonstrates advanced algorithmic thinking, graph theory application, and optimization techniques in a challenging pathfinding scenario.

## Instructions

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)

### Installation

```bash
# Install dependencies
make install
```

### Execution

```bash
# Run the simulation with default map (map.txt)
make run

# Run in debug mode
make debug

# Clean temporary files
make clean

# Run code quality checks
make lint

# Run strict type checking (recommended)
make lint-strict
```

### Map File Format

Create or modify map files following this format:

```
nb_drones: 5
start_hub: start 0 0 [color=green max_drones=5]
hub: waypoint1 1 0 [zone=normal color=blue]
hub: waypoint2 2 0 [zone=restricted color=red max_drones=2]
end_hub: goal 3 0 [color=yellow]

connection: start-waypoint1
connection: waypoint1-waypoint2 [max_link_capacity=2]
connection: waypoint2-goal
```

**Zone Types:**
- `normal` - Standard zone (1 turn movement cost)
- `restricted` - Slow zone (2 turn movement cost)
- `priority` - Preferred zone (1 turn, prioritized in pathfinding)
- `blocked` - Inaccessible zone

**Optional Metadata:**
- `color=<name>` - Visual color for terminal display
- `max_drones=<number>` - Maximum concurrent drone occupancy
- `max_link_capacity=<number>` - Maximum simultaneous connection traversals (connections only)

### Running with Different Maps

Edit `main.py` to change the map file:

```python
with open("maps/easy/01_linear_path.txt") as f:
    parsed_data = Parser(f)
```

Or modify the code to accept command-line arguments.

## Algorithm Implementation

### Pathfinding Strategy

The implementation uses a depth-first search (DFS) approach to generate all possible paths from start to goal, then intelligently assigns drones to paths based on several optimization criteria:

1. **Path Generation**: DFS explores the graph to find all valid paths, automatically avoiding blocked zones
2. **Cost Calculation**: Each path is evaluated based on cumulative zone costs (priority zones are cheaper, restricted zones are more expensive)
3. **Path Selection**: Drones are assigned to the lowest-cost available path iteratively
4. **Conflict Resolution**: When zone capacity constraints are detected, wait nodes are inserted to prevent collisions
5. **Multi-turn Handling**: Restricted zones automatically generate two-turn movements by duplicating nodes in the path

### Key Features

- **Dynamic Path Adjustment**: Paths are modified in real-time to handle capacity constraints
- **Greedy Assignment**: Drones select the best available path at assignment time
- **Capacity Management**: Tracks zone occupancy across all simulation turns
- **Visual Feedback**: Animated terminal display shows real-time drone movements, zone states, and capacity utilization

### Complexity Analysis

- **Path Generation**: O(V + E) per path where V is vertices and E is edges, with exponential worst-case for all paths
- **Path Assignment**: O(N * P * T) where N is drones, P is paths, T is average path length
- **Memory**: O(N * T) for storing all drone paths plus O(P * T) for path cache

The algorithm prioritizes finding valid solutions over optimal performance on extremely complex maps (e.g., "The Impossible Dream" challenger map).

### Performance Optimizations

- Path caching to avoid redundant calculations
- Zone capacity tracking with O(1) lookup
- Greedy path selection to reduce search space
- Early termination when all drones are assigned

## Visual Representation

The system provides an enhanced terminal visualization featuring:

- **Animated Grid Display**: Real-time 2D representation of the drone network
- **Color-Coded Zones**: Visual distinction between zone types (normal, restricted, priority, blocked)
- **Capacity Indicators**: Shows zone capacity limits and current occupancy
- **Drone Tracking**: Individual drone positions marked with symbols
- **Movement Highlighting**: Current turn movements displayed with special formatting
- **Status Panel**: Live statistics on drone arrivals and transit status
- **Legend**: Clear explanation of symbols and colors

The visualization can be toggled between animated mode (with delay) and text-only mode for faster execution and log capture.

## Project Structure

```
fly-in/
├── main.py                    # Entry point
├── map.txt                    # Default map file
├── Makefile                   # Build automation
├── README.md                  # This file
├── models/
│   ├── drone.py              # Drone class and behavior
│   └── zone.py               # Node/Zone definitions
├── parsing/
│   └── parser.py             # Map file parser
├── pathfinding/
│   └── routing.py            # Pathfinding algorithms
├── execution/
│   └── turns.py              # Simulation turn manager
└── visualization/
    └── terminal_display.py   # Terminal visualization
```

## Resources

### Graph Theory and Pathfinding
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) - Comprehensive coverage of graph algorithms
- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) - Shortest path algorithm foundation
- [A* Search Algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) - Heuristic pathfinding
- [Graph Theory Tutorial](https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/) - Practical implementation guide

### Python Best Practices
- [PEP 8 – Style Guide](https://peps.python.org/pep-0008/) - Python code style
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/) - Documentation standards
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Static typing in Python
- [mypy Documentation](https://mypy.readthedocs.io/) - Type checking tool

### Problem-Solving Techniques
- [Multi-Agent Path Finding](https://en.wikipedia.org/wiki/Multi-agent_pathfinding) - Coordinating multiple agents
- [Constraint Satisfaction Problems](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem) - Handling complex constraints
- [Flow Network Algorithms](https://en.wikipedia.org/wiki/Flow_network) - Capacity-constrained routing

### AI Tool Usage

AI tools (Claude, ChatGPT, GitHub Copilot) were used strategically in this project for:

**Code Generation Assistance:**
- Initial parser structure and regex pattern suggestions
- Boilerplate code for class definitions and type hints
- Terminal color code reference and ANSI escape sequences

**Debugging Support:**
- Type hint error resolution with mypy
- Logic error identification in pathfinding algorithm
- Suggestions for handling edge cases (dead ends, loops, capacity constraints)

**Documentation:**
- README structure and formatting
- Docstring templates following PEP 257
- Algorithm complexity analysis verification

**Not Used For:**
- Core pathfinding algorithm logic (designed independently)
- Simulation turn mechanics (implemented from scratch)
- Overall project architecture decisions

All AI-generated content was thoroughly reviewed, tested, and modified to ensure full understanding and project compliance. Peer review was conducted to validate correctness and identify potential issues.

## Known Limitations

- The current implementation prioritizes finding valid solutions over optimal turn count for complex maps
- Very large maps (50+ nodes) with many drones may experience slower path generation
- The greedy path assignment doesn't guarantee global optimality
- No dynamic path recalculation during simulation (paths are pre-computed)

## Future Improvements

- Implement A* or Dijkstra's algorithm for more efficient pathfinding
- Add dynamic path recalculation to handle unexpected blockages
- Optimize path assignment using flow network algorithms
- Implement parallel path generation for better performance
- Add command-line arguments for map selection and visualization options
- Create a graphical interface using pygame or tkinter

## License

This project is part of the 42 school curriculum and follows the school's academic policies.