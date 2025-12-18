class Display:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"

    ZONE_COLORS = {
        "normal": GREEN,
        "blocked": RED,
        "restricted": YELLOW,
        "priority": CYAN
    }

    def __init__(self, nodes, drones):
        self.nodes = nodes
        self.drones = drones

        self.previous_zone = {d.id: d.current_zone for d in drones}

    # Really cool def
    # def update(self):
    #     """Print current state of all zones and drones in the terminal."""
    #     print("\033[H\033[J", end="")  # clear terminal
    #     for node in self.nodes:
    #         color = self.ZONE_COLORS.get(getattr(node,
    # "zone", "normal"), self.WHITE)
    #         # Find drones in this zone by name comparison
    #         drones_here = [f"D{d.id}" for d in self.drones
    # if d.current_zone.name == node.name]
    #         drones_display = " ".join(drones_here) if drones_here else "--"
    #         print(f"{color}{node.
    # name:<12} [{drones_display:<5}]{self.RESET}")
    #     print("\n")

    def update(self):
        """Prints one simulation turn in required format."""

        movements = []

        for d in self.drones:
            prev = self.previous_zone[d.id]
            curr = d.current_zone

            # Case 1: Drone already arrived → print if first turn
            if d.is_arrived:
                if prev != curr:      # arrival happened this turn
                    movements.append(f"D{d.id}-{curr.name}")
                self.previous_zone[d.id] = curr
                continue

            # Case 2: In-flight toward restricted zone
            if d.restricted_movement_turns_buffer > 0:
                if d.path:
                    connection = f"{prev.name}-{d.path[0].name}"
                else:
                    connection = f"{prev.name}-?"
                movements.append(f"D{d.id}-{connection}")
                self.previous_zone[d.id] = curr
                continue

            # Case 3: Normal movement
            if prev != curr:
                movements.append(f"D{d.id}-{curr.name}")

            # Update stored position
            self.previous_zone[d.id] = curr

        if movements:
            print(" ".join(movements))
        else:
            print("")
