from enum import IntFlag


class Dir(IntFlag):
    """Wall directions using bit flags for efficient set operations.

    IntFlag allows bitwise operations (|, &, ~) to combine/remove walls
    in a single cell. Power-of-2 values enable representing any wall
    combination (0-15) as a single integer for compact storage.
    """
    NONE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @staticmethod
    def all() -> list['Dir']:
        """Returns all four cardinal directions for iteration.

        Excludes NONE to simplify random direction selection in algorithms.
        """
        return [Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]

    def to_string(self) -> str:
        """Converts direction to single-letter format for compact output."""
        match self:
            case Dir.NONE: return ""
            case Dir.NORTH: return "N"
            case Dir.EAST: return "E"
            case Dir.SOUTH: return "S"
            case Dir.WEST: return "W"

    def rc_offset(self) -> tuple[int, int]:
        """Returns direction offset in (row, col) format for grid navigation.

        Uses row/col order to match Python's grid[row][col] indexing,
        preventing the common bug of accessing grid[x][y] when Python
        expects grid[y][x].
        """
        match self:
            case Dir.NONE: return (0, 0)
            case Dir.NORTH: return (-1, 0)
            case Dir.EAST: return (0, 1)
            case Dir.SOUTH: return (1, 0)
            case Dir.WEST: return (0, -1)


type Grid = list[list[Dir]]  # 2D array of wall bitmasks, indexed [row][col]
type Vertex = tuple[int, int]  # (row, col) position in grid
type Edge = tuple[Vertex, Vertex]  # Connection between two adjacent cells
