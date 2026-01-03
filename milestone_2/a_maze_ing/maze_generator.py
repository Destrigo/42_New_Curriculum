from maze_algorithm_kruskals import MazeAlgorithmKruskals
from config import Config
from maze_types import Dir, Grid
from maze_algorithm_perfect import MazeAlgoritm_Perfect
from maze_class_abc import MazeAlgorithm


class MazeGenerator:
    """Selects and runs the appropriate maze algorithm based on config.

    Factory pattern that delegates to Kruskal's for imperfect mazes
    (with loops) or recursive backtracking for perfect mazes (single path).
    This design allows easy addition of new algorithms without changing
    client code.
    """
    config: Config
    grid: Grid
    algo: MazeAlgorithm

    def __init__(self, config: Config) -> None:
        """Selects algorithm based on config.perfect and generates maze.

        Algorithm selection happens at construction to fail fast if config
        is invalid. Generation is also immediate to ensure the grid is
        always available for visualization or output.
        """
        self.config = config
        if self.config.perfect:
            self.algo = MazeAlgoritm_Perfect(self.config)
        else:
            self.algo = MazeAlgorithmKruskals(self.config)
        self.grid = self.algo.generate()

    def print_maze_bitmask(self) -> None:
        """Prints maze as hexadecimal wall bitmask for debugging.

        Single-digit hex representation (0-F) provides a compact view
        of the maze structure for debugging without ASCII art overhead.
        Useful for quickly verifying wall patterns in large mazes.
        """
        for r in range(self.config.height):
            line = ""
            for c in range(self.config.width):
                # get the digit after 0x from hex()
                line += hex(self.grid[r][c])[2]
            print(line)

    def print_maze_pretty(self) -> None:
        """Prints maze as ASCII art for visualization without GUI.

        Provides a human-readable representation for debugging and testing.
        Complements the hex output by showing the actual maze structure
        visually, making it easier to verify algorithm correctness.
        """
        rows, cols = self.config.height, self.config.width
        # Top border
        print("+" + "---+" * cols)

        for r in range(rows):
            # Cell row (vertical walls)
            line1 = "|"
            for c in range(cols):
                line1 += "   "
                line1 += "|" if self.grid[r][c] & Dir.EAST else " "
            print(line1)

            # Wall row (horizontal walls)
            line2 = "+"
            for c in range(cols):
                line2 += "---+" if self.grid[r][c] & Dir.SOUTH else "   +"
            print(line2)
