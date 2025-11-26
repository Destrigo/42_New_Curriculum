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

    def action(self, drones: list) -> None:
        """do something"""
        if self.is_arrived is True:
            return
        if self.restricted_movement_turns_buffer != 0:
            self.restricted_movement_turns_buffer -= 1
            self.path.pop(0)
            return
        if self.current_zone == self.path[0]:
            self.path.pop(0)
            return
        else:
            self.current_zone = self.path.pop(0)
            if self.current_zone.zone == "restricted":
                self.restricted_movement_turns_buffer = 1
        # if here it moved, check if it finished
        if self.restricted_movement_turns_buffer == 0 and not self.path:
            self.is_arrived = True
