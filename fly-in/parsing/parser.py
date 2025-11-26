from models.drone import Drone
from models.zone import Node
from models.connection import Connection


class Map_Parser:
    """Parser of the input"""
    def __init__(self, file_obj):
        """initialize"""
        self.nodes: list[Node] = []
        self.connections: list[Connection] = []
        self.drones: list[Drone] = []
        self.num_drones = 0
        self.parse(file_obj)

    def parse(self, f):
        """the actual function that parses"""
        line = self._next_line(f)

        if not line.lower().startswith("nb_drones"):
            raise ValueError("Missing nb_drones")
        self.num_drones = int(line.split(":")[1].strip())

        line = self._next_line(f)
        if not line.startswith("start_hub"):
            raise ValueError("Missing start_hub")
        start_zone = self._parse_node(line)
        self.nodes.append(start_zone)

        line = self._next_line(f)
        while line.startswith("hub:"):
            node = self._parse_node(line)
            self.nodes.append(node)
            line = self._next_line(f)

        if not line.startswith("end_hub"):
            raise ValueError("Missing end_hub")
        end_zone = self._parse_node(line)
        self.nodes.append(end_zone)

        line = self._next_line(f)
        while line.startswith("connection:"):
            conn = self._parse_connection(line)
            self.connections.append(conn)
            line = self._next_line(f)

        for i in range(1, self.num_drones + 1):
            self.drones.append(Drone(i, start_zone))

    def _next_line(self, f):
        """Return next non-empty, non-comment line"""
        line = f.readline()
        while line and (line.strip() == "" or line.lstrip().startswith("#")):
            line = f.readline()
        return line.strip()

    def _parse_node(self, line: str) -> Node:
        """Parse a node"""
        # TODO: actual extraction of name, x, y, metadata
        return Node("exampleName", 0, 0)

    def _parse_connection(self, line: str) -> Connection:
        """Parse connection"""
        _, rest = line.split(":")
        left, right = rest.strip().split("-")
        return Connection(left.strip(), right.strip())
