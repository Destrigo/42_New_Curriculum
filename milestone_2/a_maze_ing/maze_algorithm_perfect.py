import random
from config import Config
from typing import override
from maze_types import Dir, Grid
from maze_class_abc import MazeAlgorithm


class MazeAlgoritm_Perfect(MazeAlgorithm):
    """Generates perfect mazes using recursive backtracking.

    Creates mazes with exactly one path between any two cells. Chosen
    for perfect mazes because it's simpler than adapting Kruskal's to
    avoid loops, and the depth-first nature creates interesting long
    corridors that challenge players.
    """
    def __init__(self, config: Config) -> None:
        super().__init__(config)

    def visited_array_if_42(self) -> list[list[int]]:
        """Pre-marks '42' pattern cells as visited to avoid them.

        By marking these cells before generation starts, they remain
        isolated without scattered special-case checks throughout the
        backtracking logic. The algorithm treats them as already-visited
        walls.
        """
        visited = [[0 for _ in range(self.config.width)]
                   for _ in range(self.config.height)]
        cells = self.grid_42_cells()
        if isinstance(cells, str):
            print(cells)
            return visited
        for (x, y) in cells:
            visited[y][x] = 1
        return visited

    @override
    def generate(self) -> Grid:
        """Generates perfect maze using recursive backtracking.

        Uses iterative backtracking (not recursive) to avoid stack
        overflow on large mazes. Backtracks when at exit even if walls
        remain available (line 61) to ensure complete maze coverage -
        otherwise the algorithm might stop early, leaving unvisited cells.
        """
        # init seed if there is in config
        if self.config.seed:
            random.seed(self.config.seed)
        (x, y) = curr_cell = self.config.entry
        exit = self.config.exit
        sizex = self.config.width
        sizey = self.config.height
        # init grid with all walls
        grid: Grid = [
            [Dir.WEST | Dir.SOUTH | Dir.EAST | Dir.NORTH for _ in range(sizex)]
            for _ in range(sizey)]
        # grid of visited cells
        visited = self.visited_array_if_42()
        visited[y][x] = 1
        visitsum = sum(sum(row) for row in visited)
        # all path from start to backtrack
        visitn = [(x, y)]
        n = 0
        directions = Dir.all()

        # algo
        while visitsum != (sizex * sizey):
            # check which wall can be destroyed
            walls_available = Dir.NONE
            if x != 0 and visited[y][x - 1] == 0:
                walls_available |= Dir.WEST
            if y != (sizey - 1) and visited[y + 1][x] == 0:
                walls_available |= Dir.NORTH
            if x != (sizex - 1) and visited[y][x + 1] == 0:
                walls_available |= Dir.EAST
            if y != 0 and visited[y - 1][x] == 0:
                walls_available |= Dir.SOUTH

            # backtrack if no walls are available or we are in exit
            if walls_available == Dir.NONE or curr_cell == exit and n > 0:
                curr_cell = visitn[n - 1]
                (x, y) = curr_cell
                n -= 1
                continue
            # else, remove wall and move
            while True:
                # choose one random wall, check if destroyable, destroy
                random_dir = random.choice(directions)
                next_cell = (0, 0)
                if not walls_available & random_dir:
                    continue
                match random_dir:
                    case Dir.WEST:
                        next_cell = (x - 1, y)
                        grid[y][x] &= ~Dir.WEST
                        grid[next_cell[1]][next_cell[0]] &= ~Dir.EAST
                    case Dir.NORTH:
                        next_cell = (x, y + 1)
                        grid[y][x] &= ~Dir.SOUTH
                        grid[next_cell[1]][next_cell[0]] &= ~Dir.NORTH
                    case Dir.EAST:
                        next_cell = (x + 1, y)
                        grid[y][x] &= ~Dir.EAST
                        grid[next_cell[1]][next_cell[0]] &= ~Dir.WEST
                    case Dir.SOUTH:
                        next_cell = (x, y - 1)
                        grid[y][x] &= ~Dir.NORTH
                        grid[next_cell[1]][next_cell[0]] &= ~Dir.SOUTH
                    case Dir.NONE:
                        pass
                n += 1
                visitn.insert(n, next_cell)  # insert in lst movements
                curr_cell = next_cell  # move in next one
                (x, y) = curr_cell
                visited[y][x] = 1
                break
            visitsum = sum(sum(row) for row in visited)
        self.out.write_output_file(grid)
        return grid
