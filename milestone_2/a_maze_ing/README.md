# A-Maze-ing

*This project has been created as part of the 42 curriculum by rploeger and mtaranti.*

## Description

A-Maze-ing is a Python-based maze generation and visualization tool that creates procedurally generated mazes with customizable parameters. The project implements multiple maze generation algorithms and provides an interactive graphical interface using the MiniLibX library. Generated mazes can be either perfect (containing exactly one path between entry and exit) or imperfect (containing multiple possible paths and loops), and all mazes feature a hidden "42" pattern formed by fully closed cells.

The project emphasizes code reusability by packaging the core maze generation logic as a standalone module that can be installed and used in other projects. It demonstrates practical applications of graph theory, pathfinding algorithms, and procedural generation techniques.

## Instructions

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/robbplo/ft-a-maze-ing
cd a-maze-ing
```

2. **Install dependencies:**
```bash
make install
```

This will install all required dependencies including the MiniLibX library and development tools.

### Building the Reusable Package

To build the maze generator package from source:

```bash
make build
```

This creates a distributable wheel file (`mazegen-*.whl`) in the project root that can be installed with pip in other projects.

### Running the Program

Execute the maze generator with a configuration file:

```bash
make run
# or
python3 a_maze_ing.py config.txt
```

You can create custom configuration files following the format described below.

### Development Commands

- **Run tests:** `make test`
- **Code linting:** `make lint`
- **Strict linting:** `make lint-strict`
- **Debug mode:** `make debug`
- **Clean temporary files:** `make clean`

## Configuration File Format

The configuration file uses a simple `KEY=VALUE` format with one setting per line. Lines starting with `#` are treated as comments.

### Required Keys

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width in cells (integer > 0) | `WIDTH=20` |
| `HEIGHT` | Maze height in cells (integer > 0) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates as x,y | `ENTRY=0,0` |
| `EXIT` | Exit coordinates as x,y | `EXIT=19,14` |
| `OUTPUT_FILE` | Path to output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Generate perfect maze (True/False) | `PERFECT=True` |

### Optional Keys

| Key       | Description                       | Example |
|-----      |-------------                      |---------|
| `SEED`    | Random seed for reproducibility   | `SEED=42` |

### Example Configuration

```ini
# Maze Configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
```

## Maze Generation Algorithms

### Algorithm Selection

The project implements two maze generation algorithms that are automatically selected based on the `PERFECT` configuration parameter:

1. **Backtracking** (Perfect mazes when `PERFECT=True`)
2. **Randomized Kruskal's Algorithm** (Imperfect mazes when `PERFECT=False`)

### Backtracking (Perfect Maze)

**How it works:**
- Starts from the entry point and performs a depth-first traversal
- At each cell, randomly selects an unvisited neighbor and removes the wall between them
- When no unvisited neighbors exist, backtracks to the previous cell
- Continues until all cells have been visited
- Reserves cells for the "42" pattern by marking them as visited before generation

**Why we chose this algorithm:**
- **Guarantees perfect mazes:** Creates exactly one path between any two points with no loops
- **Efficient:** Linear time complexity O(n) where n is the number of cells
- **Long corridors:** Tends to create long, winding passages that make interesting mazes
- **Simple implementation:** Easy to understand and debug
- **Natural-looking:** Produces organic-looking maze structures

### Randomized Kruskal's Algorithm (Imperfect Maze)

**How it works:**
- Treats the maze as a graph where each cell is a vertex
- Creates a list of all possible edges (walls between adjacent cells)
- Uses a disjoint-set (union-find) data structure to track connected components
- Randomly processes edges, removing walls that would connect separate components
- Reintroduces approximately 5% of rejected edges to create loops
- Avoids the "42" pattern cells during edge creation

**Why we chose this algorithm:**
- **Creates loops:** Generates multiple paths between entry and exit for more complex exploration
- **Uniform distribution:** Produces more evenly distributed passages than recursive backtracking
- **Controlled complexity:** The 5% loop reintroduction parameter allows fine-tuning maze difficulty
- **Graph theory foundation:** Demonstrates practical application of minimum spanning trees
- **Flexible:** Easy to adjust parameters to control maze characteristics

### Maze Requirements

All generated mazes satisfy these constraints:
- Entry and exit points are different and within maze bounds
- No isolated cells (all cells are reachable, except the "42" pattern)
- Proper wall coherence (neighboring cells share wall states)
- No large open areas (corridors limited to 2 cells wide)
- External borders are always walled
- Contains a visible "42" pattern (if maze is large enough: minimum 10×7)

## Interactive Visualization

The program provides an interactive graphical interface with the following features:

### Controls

- **Key 1:** Regenerate a new random maze with the same configuration
- **Key 2:** Toggle display of the shortest path from entry to exit
- **Key 3:** Cycle through color palettes (3 different themes)
- **Key 4:** Quit the application

### Visual Elements

- **Green cell:** Entry point
- **Red cell:** Exit point
- **Magenta cells:** The "42" pattern (fully closed cells)
- **Yellow/colored path:** Shortest path when toggled on
- **Customizable colors:** Wall and path colors change with palette selection

## Reusable Code Structure

### What Part is Reusable

The entire maze generation logic is packaged as a reusable module that includes:

- **Core Classes:**
  - `MazeGenerator`: Main interface for maze generation
  - `MazeAlgorithm`: Abstract base class for algorithms
  - `MazeAlgorithmKruskals`: Kruskal's algorithm implementation
  - `MazeAlgoritm_Perfect`: Recursive backtracking implementation
  - `MazeSolver`: Dijkstra-based pathfinding for shortest path calculation
  - `OutputWriter`: Handles maze output in hexadecimal format

- **Supporting Modules:**
  - `Config`: Configuration parsing and validation
  - `maze_types`: Type definitions (Grid, Vertex, Edge, Dir enum)

### How to Use the Reusable Module

**Installation:**

```bash
pip install mazegen-0.1.0-py3-none-any.whl
```

**Basic Usage:**

```python
from config import Config
from maze_generator import MazeGenerator

# Create a configuration
config = Config(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    output_file="maze.txt",
    perfect=True,
    seed="optional_seed"
)

# Generate the maze
generator = MazeGenerator(config)

# Access the maze grid (2D list of Dir flags)
maze_grid = generator.grid

# The output file is automatically written
# It contains the hexadecimal representation and shortest path
```

**Advanced Usage:**

```python
from maze_solver import MazeSolver
from maze_types import Dir

# Use the solver to find paths
solver = MazeSolver(config, maze_grid)
shortest_path = solver.shortest_path()  # Returns string like "EESSNNEEW"

# Access individual cell walls
cell = maze_grid[y][x]  # Note: row, column indexing
has_north_wall = bool(cell & Dir.NORTH)
has_east_wall = bool(cell & Dir.EAST)
has_south_wall = bool(cell & Dir.SOUTH)
has_west_wall = bool(cell & Dir.WEST)
```

## Team and Project Management

### Team Roles

- **[rploeger]:** Input parsing, validation, Kruskal's Algorithm and package definition
- **[mtaranti]:** DFS for "perfect" algorithm, Visualization and user interface (MLX integration)

### Planning

**Initial Planning:**
- Research maze generation algorithms
- Design configuration file format
- Set up project structure and testing framework
- Implement basic grid representation

**Development Phase (Week 2-3):**
- Implement recursive backtracking algorithm
- Implement Kruskal's algorithm
- Develop visualization system
- Implement pathfinding (Dijkstra's algorithm)
- Create output file writer

**Final Phase:**
- Add interactive features (regeneration, path toggle, color palettes)
- Package as distributable wheel
- Write documentation and tests

**Evolution:**
- Original plan included only one algorithm; expanded to two for flexibility
- Added color palette feature based on user feedback during development
- Moved from terminal-based to graphical visualization for better user experience

### What Worked Well

- **Test-driven development:** Writing tests first helped catch bugs early
- **Modular design:** Separating concerns made the codebase easy to extend
- **Algorithm abstraction:** Using an abstract base class made adding new algorithms straightforward
- **Configuration system:** Flexible config format accommodated new features without breaking changes

### What Could Be Improved

- **Performance:** Large mazes (100×100+) could benefit from optimization
- **Documentation:** More inline code comments would improve maintainability
- **Error messages:** Could provide more specific guidance when configuration is invalid
- **Testing coverage:** More edge cases could be covered in the test suite
- **Visualisation:** Strings of options should scale with the window

### Tools Used

- **uv:** Fast Python package manager for dependency management
- **pytest:** Testing framework with coverage reporting
- **mypy:** Static type checker for Python
- **flake8:** Code linting and style checking
- **Git:** Version control and collaboration
- **MiniLibX:** Graphics library for visualization

## Resources

### Classic References

- **Documentation:**
  - [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
  - [MiniLibX Documentation](https://harm-smits.github.io/42docs/libs/minilibx)

- **Online Resources:**
  - [Stack-Overflow: Maze Generation Algorithm](https://stackoverflow.com/questions/38502/whats-a-good-algorithm-to-generate-a-maze)

### AI Usage

AI tools were used in the following areas of the project:

**Documentation:**
- Used AI to help structure the README and ensure all required sections were included

**Code Review:**
- AI assisted in identifying potential type hint improvements
- AI writing of docs for functions

**Important Note:** All AI-generated content was thoroughly reviewed, tested, and modified by team members. We take full responsibility for the final implementation and can explain every part of the codebase.

## License

This project is part of the 42 school curriculum.

---

For questions or contributions, please refer to the project repository.
