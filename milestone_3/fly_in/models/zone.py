class Node():
    """Base of every node of every map"""
    def __init__(self, map_definition: str,
                 name: str,
                 x: int, y: int,
                 zone: str = "normal",
                 color: str | None = None,
                 max_drone: int = 1) -> None:
        """Initialize"""
        valid_zone_list = [
            "normal",
            "blocked,"
            "restricted",
            "priority"
        ]

        self.x = x
        self.y = y

        self.name = name
        if '-' in name or ' ' in name:
            raise Exception("Invalid Node name")
        self.map_definition = map_definition

        self.zone = zone
        if zone not in valid_zone_list:
            raise Exception("Invalid Node zone")
        self.cost: float
        if self.zone == "normal":
            self.cost = 1
        if self.zone == "restricted":
            self.cost = 1
        if self.zone == "blocked":
            self.cost = 1000000
        if self.zone == "priority":
            self.cost = 0.99999

        self.connections: list = []
        self.color = color
        if max_drone > 0:
            self.max_drone = max_drone
        else:
            raise Exception("Invalid Node max_drones metadata")
        if self.map_definition == "w":
            self.max_drones = 999999
