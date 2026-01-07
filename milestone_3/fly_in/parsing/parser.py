from models.drone import Drone
from models.zone import Node
from typing import TextIO


class Parser:
    """Parser of the input"""
    def __init__(self, file_obj: TextIO) -> None:
        """initialize"""
        self.nodes: list[Node] = []
        self.drones: list[Drone] = []
        self.num_drones = 0
        start_zone = None
        end_zone = None

        line = self._next_line(file_obj)

        if not line.lower().startswith("nb_drones"):
            raise ValueError("Missing nb_drones")
        try:
            self.num_drones = int(line.split(":")[1].strip())
        except Exception:
            raise TypeError("number of drones not int")
        if self.num_drones <= 0:
            raise ValueError("Invalid drones num")

        line = self._next_line(file_obj)
        if not line.startswith("start_hub"):
            raise ValueError("Wrong hubs input")
        start_zone = self._parse_node(line)
        self.nodes.append(start_zone)

        line = self._next_line(file_obj)
        while line.startswith("hub:"):
            node = self._parse_node(line)
            self.nodes.append(node)
            line = self._next_line(file_obj)

        if not line.startswith("end_hub"):
            raise ValueError("Wrong hubs input")
        end_zone = self._parse_node(line)
        self.nodes.append(end_zone)

        line = self._next_line(file_obj)
        if not line.startswith("connection:"):
            raise Exception("Connections not inputted correctly")
        while line.startswith("connection:"):
            self._parse_connection(line, self.nodes)
            line = self._next_line(file_obj)
        # check for dup
        for nd in self.nodes:
            if len(nd.connections) != len(set(nd.connections)):
                raise Exception("Duplicated connection")

        for i in range(1, self.num_drones + 1):
            drone = self._parse_drone(i, start_zone)
            self.drones.append(drone)

    def _next_line(self, f: TextIO) -> str:
        """Return next non-empty, non-comment line"""
        line = f.readline()
        while line and (line.strip() == "" or line.lstrip().startswith("#")):
            line = f.readline()
        return line.strip()

    def _parse_node(self, line: str) -> Node:
        """Parse a node"""
        parseddata = line.split("[")
        metadata: list = []
        gen_data: list = []
        if len(parseddata) == 2:
            metadata = parseddata[1].replace("[", ""
                                             ).replace("]", ""
                                                       ).replace(":", ""
                                                                 ).split(" ")
        gen_data = parseddata[0].replace("[", ""
                                         ).replace(
                                             "]", "").replace(
                                                       ":", "").replace(
                                                                 "=",
                                                                 " ").split(
                                                                           " ")
        hub = gen_data[0]
        name = gen_data[1]
        x = int(gen_data[2])
        y = int(gen_data[3])
        node = Node(hub, name, x, y)
        for data in metadata:
            if data.startswith("color"):
                setattr(node, data[5:], node.color)
            elif data.startswith("zone"):
                setattr(node, data[4:], node.zone)
            elif data.startswith("max_drones"):
                try:
                    setattr(node, data[11:], node.max_drone)
                except ValueError:
                    raise Exception("wrong number input parcing max_drones")
            else:
                raise Exception("wrong metadata")
        return node

    def _parse_connection(self, line: str, nodes: list) -> None:
        """Parse connection"""
        line = line[12:]
        line = line.replace("[", "").replace("]", "")
        parsed: list = []
        metadata: str
        link_capacity = 1
        tmp = line.split(" ")
        if len(tmp) > 2:
            raise Exception("Wrong connection input str")
        elif len(tmp) == 2:
            metadata = tmp[1]
            if metadata.startswith("max_link_capacity="):
                link_capacity = int(metadata[18])
                if link_capacity < 1:
                    raise Exception("Link Capacity can't be < 1")
            else:
                raise Exception("Bad connection metadata")

        parsed = tmp[0].split("-")
        for check in parsed:
            if '-' in check:
                raise Exception("Bad zone connection names")
        flag_left: int = 0
        flag_right: int = 0
        for node in nodes:
            if parsed[0] == node.name:
                node.connections.append((parsed[1], link_capacity))
                flag_left += 1
            if parsed[1] == node.name:
                node.connections.append((parsed[0], link_capacity))
                flag_right += 1
        if flag_left != 1 or flag_right != 1:
            raise Exception("Invalid Connection")

    def _parse_drone(self, i: int, start_zone: Node) -> Drone:
        """parse drones"""
        n = Drone(i, start_zone)
        return n
