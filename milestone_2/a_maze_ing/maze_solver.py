from heapq import heapify, heappop, heappush
from math import inf
from config import Config
from maze_types import Dir, Grid, Vertex


class MazeSolver:
    """Finds shortest path through maze using Dijkstra's algorithm.

    Uses Dijkstra over A* because all edge weights are 1 (uniform cost),
    making Manhattan distance heuristic provide minimal benefit. Simpler
    implementation without heuristic tuning, with negligible performance
    difference for typical maze sizes (<100x100).
    """
    config: Config
    grid: Grid
    distances: dict[Vertex, float] = {}
    previous: dict[Vertex, tuple[Vertex | None, Dir | None]] = {}

    def __init__(self, config: Config, grid: Grid) -> None:
        """Initializes solver and immediately computes shortest path.

        Eager computation ensures path is always available for output
        and visualization without requiring explicit solve() call.
        """
        self.config = config
        self.grid = grid
        self.__pathfind()

    def __pathfind(self) -> None:
        """Computes shortest paths from entry to all reachable cells.

        Calculates distances to all cells, not just exit, to enable future
        features like heatmaps or difficulty analysis. Entry/exit coordinates
        are swapped from (x, y) config format to internal (row, col) format.
        """
        # swap entry and exit because they are in x,y and we use row/col
        entry = (self.config.entry[1], self.config.entry[0])
        pq: list[tuple[float, Vertex]] = []
        for r in range(self.config.height):
            for c in range(self.config.width):
                self.distances[(r, c)] = inf
                self.previous[(r, c)] = (None, None)
        pq.append((0, entry))
        self.distances[entry] = 0
        heapify(pq)

        while len(pq) > 0:
            curr = (r, c) = heappop(pq)[1]
            for dir in Dir.all():
                if self.grid[r][c] & dir:
                    continue
                (dr, dc) = dir.rc_offset()
                next = (r + dr, c + dc)
                if (r + dr < 0 or r + dr >= self.config.height or c + dc < 0
                   or c + dc >= self.config.width):
                    continue
                new_dist = self.distances[curr] + 1
                if new_dist < self.distances[next]:
                    self.distances[next] = new_dist
                    self.previous[next] = (curr, dir)
                    heappush(pq, (new_dist, next))

    def shortest_path(self) -> str:
        """Returns shortest path as direction string for compact output format.

        String format (e.g., "NNESWW") matches the output file specification
        and provides a compact representation. Returns "no path found" if
        exit is unreachable (shouldn't happen in valid mazes).
        """
        target = (self.config.exit[1], self.config.exit[0])
        if self.previous[target] == (None, None):
            return "no path found"
        dirs: list[Dir] = []
        while target:
            match self.previous[target]:
                case (next_target, Dir(dir)) if next_target is not None:
                    target = next_target
                    dirs.append(dir)
                case _:
                    break
        dirs.reverse()
        return "".join(map(Dir.to_string, dirs))
