class Node():
    """Base of every node of every map"""
    def __init__(self, map_definition: str,
                 name: str,
                 x: int, y: int,
                 zone: str = "normal",
                 color: str | None = None,
                 max_drone: int = 1) -> None:
        """Initialize"""
        self.x = x
        self.y = y
        self.name = name
        self.map_definition = map_definition
        self.zone = zone
        self.cost: float
        if self.zone == "normal":
            self.cost = 1
        if self.zone == "restricted":
            self.cost = 1
        if self.zone == "blocked":
            self.cost = 1000000
        if self.zone == "priority":
            self.cost = 0.99999
        if self.map_definition == "w":
            self.max_drones = 999999

        self.connections: list = []
        self.color = color
        self.max_drone = max_drone
