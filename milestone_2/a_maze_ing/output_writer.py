from maze_solver import MazeSolver
from maze_types import Grid
from config import Config


class OutputWriter:
    """Writes maze in hexadecimal format required by 42 project validator.

    The hex encoding (0-F representing wall bitmasks) provides a compact,
    human-readable format that the provided validator can parse. Including
    the solved path allows visualization tools to show the solution.
    """
    def __init__(self, config: Config) -> None:
        self.config = config

    def write_output_file(self, grid: Grid) -> None:
        """Writes maze, entry/exit coordinates, and solution path to file.

        Format is hex grid + entry coords + exit coords + direction string.
        Path is included so visualization tools can highlight the solution
        without re-solving. The +1 offset in hex conversion maps Dir flags
        (0-15) to printable hex digits (1-16 mod 16 = 1-F, 0).
        """
        hex = "0123456789ABCDEF"
        string = ""
        for y in range(self.config.height):
            for x in range(self.config.width):
                string += hex[grid[y][x] % 16]
            string += "\n"
        string += "\n"
        (x, y) = self.config.entry
        string += f"{x}, {y}\n"
        (x, y) = self.config.exit
        string += f"{x}, {y}\n"
        solver = MazeSolver(self.config, grid)
        string += f"{solver.shortest_path()}"
        string += "\n"
        try:
            with open(self.config.output_file, "w") as fd:
                _ = fd.write(string)
        except Exception as e:
            print(f"failed to write output file: {type(e).__name__} {e.args}")
