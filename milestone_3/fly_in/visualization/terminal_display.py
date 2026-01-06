from models.zone import Node


class Display:
    """Display class with colored terminal output based on zone colors."""
    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    # Color name to ANSI code mapping
    COLOR_MAP = {
        "green": "\033[32m",
        "red": "\033[31m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "orange": "\033[38;5;208m",
        "purple": "\033[35m",
        "cyan": "\033[36m",
        "magenta": "\033[35m",
        "white": "\033[37m",
        "black": "\033[90m",
        "brown": "\033[38;5;130m",
        "maroon": "\033[38;5;88m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;177m",
        "crimson": "\033[38;5;160m",
        "gold": "\033[38;5;220m",
        "lime": "\033[38;5;154m",
        "rainbow": "\033[38;5;201m",
        "gray": "\033[90m",
        "grey": "\033[90m",
    }
    # Default colors for drone IDs
    DRONE_COLOR = "\033[36m"  # Cyan
    INFLIGHT_COLOR = "\033[38;5;208m"  # Orange
    ARRIVED_COLOR = "\033[32m"  # Green

    def __init__(self, nodes: list, drones: list) -> None:
        """
        Initialize the display.
        Args:
            nodes: List of all nodes in the network
            drones: List of all drones in the simulation
        """
        self.nodes = nodes
        self.drones = drones
        self.previous_zone: dict[int, object] = {d.id: d.current_zone
                                                 for d in drones}
        # Build a quick lookup map: zone_name -> zone_node
        self.zone_map: dict[str, object] = {node.name: node for node in nodes}

    def _get_zone_color(self, zone_name: str) -> str:
        """
        Get the color for a specific zone based on its type.
        Args:
            zone_name: Name of the zone
        Returns:
            ANSI color code string
        """
        # Find the zone in nodes list
        if zone_name in self.zone_map:
            node = self.zone_map[zone_name]
            # Get the color attribute from the node
            color_name = getattr(node, 'color', None)
            if color_name:
                # Look up the ANSI code for this color name
                return self.COLOR_MAP.get(color_name.lower(), self.RESET)
        return self.RESET  # No color if not found

    def update(self) -> None:
        """Prints one simulation turn in required format."""

        movements = []

        for d in self.drones:
            prev: Node = self.previous_zone[d.id]
            curr = d.current_zone

            # Case 1: Drone already arrived → print if first turn
            if d.is_arrived:
                if prev != curr:      # arrival happened this turn
                    zone_color = self._get_zone_color(curr.name)
                    movement = (f"{self.ARRIVED_COLOR}D{d.id}{self.RESET}"
                                f"-"
                                f"{zone_color}{curr.name}{self.RESET}")
                    movements.append(movement)
                self.previous_zone[d.id] = curr
                continue

            # Case 2: In-flight toward restricted zone
            if d.restricted_movement_turns_buffer > 0:
                if d.path:
                    connection = f"{prev.name}-{d.path[0].name}"
                    # Color the connection in orange to show in-flight
                    movement = (f"{self.INFLIGHT_COLOR}D{d.id}{self.RESET}"
                                f"-"
                                f"{self.INFLIGHT_COLOR}{connection}{self.RESET}")
                else:
                    connection = f"{prev.name}-?"
                    movement = (f"{self.INFLIGHT_COLOR}D{d.id}{self.RESET}"
                                f"-"
                                f"{self.INFLIGHT_COLOR}{connection}{self.RESET}")
                movements.append(movement)
                self.previous_zone[d.id] = curr
                continue

            # Case 3: Normal movement
            if prev != curr:
                zone_color = self._get_zone_color(curr.name)
                # Drone ID in cyan, zone name in its specific color
                movement = (f"{self.DRONE_COLOR}D{d.id}{self.RESET}"
                            f"-"
                            f"{zone_color}{curr.name}{self.RESET}")
                movements.append(movement)

            # Update stored position
            self.previous_zone[d.id] = curr

        if movements:
            print(" ".join(movements))
        else:
            print("")
