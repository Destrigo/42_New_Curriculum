from abc import ABC, abstractmethod
from config import Config
from maze_types import Grid, Vertex
from output_writer import OutputWriter


class MazeAlgorithm(ABC):
    """Abstract base class for maze generation algorithms.

    Enforces the contract that all algorithms must implement generate()
    while providing shared functionality like the '42' pattern. This
    abstraction enables the factory pattern in MazeGenerator, making it
    easy to add new algorithms without changing client code.
    """
    config: Config

    def __init__(self, config: Config) -> None:
        """Initializes algorithm with config and output writer.

        Output writer is initialized here so all algorithms automatically
        write their results, ensuring consistent behavior across algorithms.
        """
        self.config = config
        self.out = OutputWriter(config)

    @abstractmethod
    def generate(self) -> Grid:
        """Must create and return a valid maze grid.

        Subclasses implement specific algorithms (Kruskal's, recursive
        backtracking, etc.) but all must return a grid where walls are
        properly removed to create paths. Output file writing happens
        automatically via the base class's OutputWriter.
        """
        pass

    def grid_42_cells(self) -> str | list[Vertex]:
        """Returns '42' pattern cells or error message if pattern won't fit.

        Returns string instead of raising exception because '42' is a visual
        flourish, not essential to maze generation. Callers can print the
        error and continue with a valid maze. Coordinates are in (x, y) format
        matching the user-facing config, not internal (row, col) format.
        """
        if (self.config.width < 10 or self.config.height < 7):
            return "map too small for the 42 to be shown"

        mid_y = self.config.height // 2
        mid_x = self.config.width // 2
        if (self.config.width % 2) == 0:
            mid_x -= 1
        # insert 4
        cells = [
            (mid_x - 1, mid_y),
            (mid_x - 1, mid_y + 1),
            (mid_x - 1, mid_y + 2),
            (mid_x - 2, mid_y),
            (mid_x - 3, mid_y),
            (mid_x - 3, mid_y - 1),
            (mid_x - 3, mid_y - 2),
        ]
        if (self.config.width % 2) == 1:
            mid_x -= 1
        # insert 2
        cells = cells + [
            (mid_x + 2, mid_y),
            (mid_x + 2, mid_y + 1),
            (mid_x + 2, mid_y + 2),
            (mid_x + 3, mid_y + 2),
            (mid_x + 4, mid_y + 2),
            (mid_x + 3, mid_y),
            (mid_x + 4, mid_y),
            (mid_x + 4, mid_y - 1),
            (mid_x + 4, mid_y - 2),
            (mid_x + 3, mid_y - 2),
            (mid_x + 2, mid_y - 2),
        ]
        if self.config.entry in cells or self.config.exit in cells:
            return "entry or exit in the 42 area, cannot draw it"
        return cells
