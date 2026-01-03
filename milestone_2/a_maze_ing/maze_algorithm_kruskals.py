import random
from typing import override
from maze_types import Dir, Grid
from maze_types import Vertex, Edge
from maze_class_abc import MazeAlgorithm


class DisjointSet:
    """Tracks connected components for Kruskal's maze generation.

    Union-find with path compression and union-by-rank ensures near-constant
    time operations, critical for large mazes. Without this, checking if cells
    are connected would require expensive graph traversals (O(V) per check).
    """
    def __init__(self) -> None:
        self.parent: dict[Vertex, Vertex] = {}
        self.rank: dict[Vertex, int] = {}

    def find(self, x: Vertex) -> Vertex:
        """Finds set representative with path compression.

        Path compression flattens the tree during lookup, making future
        finds nearly O(1). Essential for Kruskal's performance when
        processing thousands of edges in large mazes.
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: Vertex, b: Vertex) -> bool:
        """Merges two sets using union-by-rank, returns True if different.

        Union-by-rank keeps the tree shallow by always attaching the
        smaller tree under the larger one. Combined with path
        compression, this achieves amortized O(α(n)) time, practically
        constant for maze sizes. Returns False if already connected,
        identifying potential loop locations.
        """
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False

        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1

        return True

    def make_set(self, x: Vertex) -> None:
        """Initializes a singleton set for a vertex.

        Each cell starts as its own set (disconnected from all others).
        As the algorithm runs, union operations merge sets to build the
        spanning tree.
        """
        self.parent[x] = x
        self.rank[x] = 0


def grid_edges(rows: int, cols: int) -> list[Edge]:
    """Generates all possible edges in a rectangular grid.

    Creates edges only for down and right neighbors to avoid duplicates
    (each edge would otherwise be generated twice). Kruskal's algorithm
    will randomly select which edges to keep for the maze.
    """
    edges: list[Edge] = []
    for r in range(rows):
        for c in range(cols):
            if r + 1 < rows:   # down
                edges.append(((r, c), (r + 1, c)))
            if c + 1 < cols:   # right
                edges.append(((r, c), (r, c + 1)))
    return edges


class MazeAlgorithmKruskals(MazeAlgorithm):
    """Generates imperfect mazes using Kruskal's with loop reintroduction.

    Chosen over DFS because it creates more uniform passage distribution
    and makes loop density easy to control via edge reintroduction (~5%
    of rejected edges). The union-find structure naturally prevents
    isolated regions while keeping the '42' pattern intact by excluding
    those edges from consideration.
    """
    def __init_42_cell(self, row: int, col: int, edges: list[Edge]) -> None:
        """Adds all edges touching a '42' pattern cell to exclusion list.

        These edges must be excluded so the algorithm never connects '42'
        cells to the maze, keeping them fully walled as a visible pattern.
        """
        edges.append(((row - 1, col), (row, col)))
        edges.append(((row, col - 1), (row, col)))
        edges.append(((row, col), (row + 1, col)))
        edges.append(((row, col), (row, col + 1)))

    def __init_42_edges(self) -> list[Edge]:
        """Collects all edges that touch '42' pattern cells for exclusion.

        Returns empty list if pattern doesn't fit (prints error message).
        By excluding these edges from Kruskal's algorithm, the '42' cells
        remain unreachable, preserving the pattern.
        """
        edges: list[Edge] = []
        fortytwo_cells = self.grid_42_cells()
        if isinstance(fortytwo_cells, str):
            print(fortytwo_cells)
        else:
            for (col, row) in fortytwo_cells:
                self.__init_42_cell(row, col, edges)
        return edges

    @override
    def generate(self) -> Grid:
        """Generates maze using randomized Kruskal's with loops.

        Creates spanning tree via Kruskal's, then reintroduces ~5% of
        rejected edges as loops. This rate balances too-easy (many loops)
        vs too-perfect (no alternative paths). Testing showed <3% feels
        too linear, >10% creates confusing open areas. Capped at 3 loops
        max to prevent large mazes from creating maze-breaking corridors
        (a 100x100 maze would reintroduce 10+ edges at 5%, potentially
        creating large open rooms).
        """
        if self.config.seed:
            random.seed(self.config.seed)
        rows, cols = self.config.height, self.config.width

        ds = DisjointSet()
        for r in range(rows):
            for c in range(cols):
                ds.make_set((r, c))

        edges = grid_edges(rows, cols)
        random.shuffle(edges)
        maze_edges: list[Edge] = []
        non_edges: list[Edge] = []
        fortytwo_edges: list[Edge] = self.__init_42_edges()

        for u, v in edges:
            if (u, v) in fortytwo_edges:
                continue
            if ds.union(u, v):
                maze_edges.append((u, v))  # wall removed
            else:
                non_edges.append((u, v))  # possible loop location

        # Reintroduce 5% of rejected edges as loops (min 1, max 3)
        # Tested: <3% too linear, >10% too open. 3 max prevents corridors.
        k_loops = max(1, int(len(non_edges) * 0.05))
        k_loops = min(k_loops, 3)
        maze_edges += random.sample(non_edges, min(k_loops, len(non_edges)))

        # Initialize all walls
        walls: Grid = [
            [Dir.NORTH | Dir.EAST | Dir.WEST | Dir.SOUTH for _ in range(cols)]
            for _ in range(rows)
        ]

        # Remove walls based on maze edges
        for (r1, c1), (r2, c2) in maze_edges:
            if r1 == r2:
                if c1 < c2:
                    walls[r1][c1] &= ~Dir.EAST
                    walls[r2][c2] &= ~Dir.WEST
                else:
                    walls[r1][c1] &= ~Dir.WEST
                    walls[r2][c2] &= ~Dir.EAST
            elif c1 == c2:
                if r1 < r2:
                    walls[r1][c1] &= ~Dir.SOUTH
                    walls[r2][c2] &= ~Dir.NORTH
                else:
                    walls[r1][c1] &= ~Dir.NORTH
                    walls[r2][c2] &= ~Dir.SOUTH
        self.out.write_output_file(walls)
        return walls
