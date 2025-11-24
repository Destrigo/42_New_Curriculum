class Node():
    """Base of every node of every map"""
    def __init__(self, map_definition: str, name: str, x: int, y: int, type_zone="standard", color="black", max_drone=1):
        """Initialize"""
        self.x = x
        self.y = y
        self.name = name
        self.map_definition = map_definition
        self.type_zone = type_zone
        self.priority_flag = False
        if self.type_zone == "standard":
            self.cost = 1
        if self.type_zone == "restricted":
            self.cost = 2
        if self.type_zone == "blocked":
            self.cost = 1000000
        if self.type_zone == "priority":
            self.cost = 0.99999
            self.priority_flag = True

        self.color = color
        self.max_drone = max_drone
        