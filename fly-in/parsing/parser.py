from models.drone import Drone
from models.zone import Node


class Parser:
    """Parser of the input"""
    def __init__(self, file_obj):
        """initialize"""
        self.nodes: list[Node] = []
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
            self._parse_connection(line, self.nodes)
            line = self._next_line(f)

        for i in range(1, self.num_drones + 1):
            dr = self._parse_drone(i, start_zone)
            self.drones.append(dr)

    def _next_line(self, f):
        """Return next non-empty, non-comment line"""
        line = f.readline()
        while line and (line.strip() == "" or line.lstrip().startswith("#")):
            line = f.readline()
        return line.strip()

    def _parse_node(self, line: str) -> Node:
        """Parse a node"""
        parseddata = line.replace("[", ""
                                  ).replace("]", ""
                                            ).replace(":", ""
                                                      ).replace("=", " "
                                                                ).split(" ")
        n = Node(parseddata[0], parseddata[1],
                 int(parseddata[2]), int(parseddata[3]))
        if len(parseddata) > 4:
            setattr(n, parseddata[4], parseddata[5])
        if len(parseddata) > 6:
            setattr(n, parseddata[6], parseddata[7])
        if len(parseddata) > 8:
            setattr(n, parseddata[8], parseddata[9])
        return n

    def _parse_connection(self, line: str, drone: list) -> None:
        """Parse connection"""
        line = line[11:]
        parsed = line.replace("[", "-").replace("]", "-"
                                                ).replace(" ", "").split("-")
        for dr in drone:
            if parsed[0] == dr.name:
                dr.connections.append(parsed[1])
                # if len(parsed > 2):
                #    dr.connections.append(parsed[1], int(parsed[3]))
                # else:
                #    dr.connections.append(parsed[1], 1)
        for dr in drone:
            if parsed[1] == dr.name:
                dr.connections.append(parsed[0])
                # if len(parsed > 2):
                #    dr.connections.append(parsed[1], int(parsed[3]))
                # else:
                #    dr.connections.append(parsed[1], 1)

    def _parse_drone(self, i: int, start_zone: Node) -> Drone:
        """parse drones"""
        n = Drone(i, start_zone)
        return n
