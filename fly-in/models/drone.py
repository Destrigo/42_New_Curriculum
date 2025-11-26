from models.zone import Node


class Drone:
    """Drones"""
    def __init__(self, drone_id: int, start_zone: "Node"):
        """Initialize"""
        self.id = drone_id
        self.current_zone = start_zone
        self.is_arrived = False
        self.path: list[Node] = []
        self.restricted_movement_turns_buffer = 0

    def next_move(self) -> Node | None:
        """Return the next zone the drone wants to move into"""
        if not self.path:
            return None
        return self.path.pop(0)
