class Node():
    """Base of every node of every map"""
    def __init__(self, map_definition: str, name: str, x: int, y: int,
                 zone="standard", color="black", max_drone=1):
        """Initialize"""
        self.x = x
        self.y = y
        self.name = name
        self.map_definition = map_definition
        self.zone = zone
        self.priority_flag = False
        if self.zone == "standard":
            self.cost = 1
        if self.zone == "restricted":
            self.cost = 2
        if self.zone == "blocked":
            self.cost = 1000000
        if self.zone == "priority":
            self.cost = 0.99999
            self.priority_flag = True

        self.connections = []
        self.color = color
        self.max_drone = max_drone
