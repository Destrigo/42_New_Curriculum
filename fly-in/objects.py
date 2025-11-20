class Drone():
    """'Drones"""
    def __init__(self, id: int, position_x: int, position_y: int,
                 is_arrived: bool = False):
        """Initialize"""
        self.id = id
        self.position_x = position_x
        self.position_y = position_y


class Node_Map():
    """Base of every node of every map"""
