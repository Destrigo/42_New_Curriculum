# class Display:
#     RESET = "\033[0m"
#     RED = "\033[31m"
#     GREEN = "\033[32m"
#     YELLOW = "\033[33m"
#     BLUE = "\033[34m"
#     CYAN = "\033[36m"
#     MAGENTA = "\033[35m"
#     WHITE = "\033[37m"

#     ZONE_COLORS = {
#         "normal": GREEN,
#         "blocked": RED,
#         "restricted": YELLOW,
#         "priority": CYAN
#     }

#     def __init__(self, nodes, drones):
#         self.nodes = nodes
#         self.drones = drones

#         self.previous_zone = {d.id: d.current_zone for d in drones}

#     def update(self):
#         """Prints one simulation turn in required format."""

#         movements = []

#         for d in self.drones:
#             prev = self.previous_zone[d.id]
#             curr = d.current_zone

#             # Case 1: Drone already arrived → print if first turn
#             if d.is_arrived:
#                 if prev != curr:      # arrival happened this turn
#                     movements.append(f"D{d.id}-{curr.name}")
#                 self.previous_zone[d.id] = curr
#                 continue

#             # Case 2: In-flight toward restricted zone
#             if d.restricted_movement_turns_buffer > 0:
#                 if d.path:
#                     connection = f"{prev.name}-{d.path[0].name}"
#                 else:
#                     connection = f"{prev.name}-?"
#                 movements.append(f"D{d.id}-{connection}")
#                 self.previous_zone[d.id] = curr
#                 continue

#             # Case 3: Normal movement
#             if prev != curr:
#                 movements.append(f"D{d.id}-{curr.name}")

#             # Update stored position
#             self.previous_zone[d.id] = curr

#         if movements:
#             print(" ".join(movements))
#         else:
#             print("")
import os
import time
from typing import Dict, Tuple


class Display:
    """Enhanced terminal visualizer for drone pathfinding simulation."""

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    ORANGE = "\033[38;5;208m"
    PURPLE = "\033[38;5;141m"
    LIME = "\033[38;5;154m"
    GOLD = "\033[38;5;220m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_DARK = "\033[48;5;236m"

    # Zone type colors
    ZONE_COLORS = {
        "normal": GREEN,
        "blocked": RED,
        "restricted": ORANGE,
        "priority": CYAN
    }

    # Named colors from map definitions
    NAMED_COLORS = {
        "green": GREEN,
        "red": RED,
        "yellow": YELLOW,
        "blue": BLUE,
        "orange": ORANGE,
        "purple": PURPLE,
        "cyan": CYAN,
        "magenta": MAGENTA,
        "lime": LIME,
        "gold": GOLD,
        "white": WHITE,
        "brown": "\033[38;5;130m",
        "maroon": "\033[38;5;88m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;177m",
        "crimson": "\033[38;5;160m",
        "rainbow": "\033[38;5;201m",
        "black": DIM + WHITE
    }

    def __init__(self, nodes, drones, animate=True, delay=0.3):
        """
        Initialize the display.
        Args:
            nodes: List of Node objects representing the map
            drones: List of Drone objects
            animate: Whether to animate the visualization
            delay: Delay between frames (seconds)
        """
        self.nodes = nodes
        self.drones = drones
        self.animate = animate
        self.delay = delay

        self.previous_zone = {d.id: d.current_zone for d in drones}
        self.turn_count = 0

        # Build map grid for visualization
        self.grid = self._build_grid()
        self.start_node = nodes[0]
        self.end_node = nodes[-1]

    def _build_grid(self) -> Dict[Tuple[int, int], 'Node']:
        """Build a coordinate grid from nodes."""
        grid = {}
        for node in self.nodes:
            grid[(node.x, node.y)] = node
        return grid

    def _get_node_color(self, node) -> str:
        """Get the appropriate color for a node."""
        # First check if node has a named color attribute
        if hasattr(node, 'color') and node.color:
            return self.NAMED_COLORS.get(node.color.lower(), self.WHITE)

        # Fall back to zone type color
        zone_type = getattr(node, 'zone', 'normal')
        return self.ZONE_COLORS.get(zone_type, self.WHITE)

    def _get_drone_symbol(self, count: int) -> str:
        """Get symbol for drone count."""
        if count == 0:
            return "  "
        elif count == 1:
            return "●"
        elif count <= 9:
            return f"{count}"
        else:
            return "+"

    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _draw_map(self):
        """Draw the entire map with current drone positions."""
        if not self.grid:
            return
        # Get map boundaries
        xs = [x for x, y in self.grid.keys()]
        ys = [y for x, y in self.grid.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # Count drones at each position
        drone_positions = {}
        for drone in self.drones:
            pos = (drone.current_zone.x, drone.current_zone.y)
            drone_positions[pos] = drone_positions.get(pos, 0) + 1
        # Draw the map
        print(f"\n{self.BOLD}╔═══ DRONE PATHFINDING SIMULATION ═══╗{self.RESET}")
        print(f"{self.BOLD}║ Turn: {self.turn_count:<3}                         ║{self.RESET}")
        print(f"{self.BOLD}╚═════════════════════════════════════╝{self.RESET}\n")
        for y in range(max_y, min_y - 1, -1):
            row = []
            for x in range(min_x, max_x + 1):
                if (x, y) in self.grid:
                    node = self.grid[(x, y)]
                    color = self._get_node_color(node)
                    # Get drone count at this position
                    drone_count = drone_positions.get((x, y), 0)
                    symbol = self._get_drone_symbol(drone_count)
                    # Special markers for start/end
                    if node == self.start_node:
                        cell = f"{self.BG_GREEN}{self.BOLD} S{symbol}{self.RESET}"
                    elif node == self.end_node:
                        cell = f"{self.BG_MAGENTA}{self.BOLD} G{symbol}{self.RESET}"
                    else:
                        # Show capacity if limited
                        capacity = getattr(node, 'max_drones', None)
                        if capacity and (int(capacity) < 10):
                            cap_str = f"{capacity}"
                        else:
                            cap_str = " "
                        if drone_count > 0:
                            cell = f"{color}{self.BOLD}[{symbol}]{self.RESET}"
                        else:
                            cell = f"{color}{self.DIM}[{cap_str} ]{self.RESET}"
                    row.append(cell)
                else:
                    row.append("    ")
            print("  ".join(row))
        print()

    def _draw_status(self):
        """Draw status panel with drone information."""
        arrived = sum(1 for d in self.drones if d.is_arrived)
        in_transit = len(self.drones) - arrived

        print(f"{self.BOLD}╔═══ STATUS ═══════════════════════════╗{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} Total Drones:   {len(self.drones):<3}                  {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.GREEN}Arrived:{self.RESET}        {arrived:<3}                  {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.YELLOW}In Transit:{self.RESET}     {in_transit:<3}                  {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}╚══════════════════════════════════════╝{self.RESET}\n")

    def _draw_legend(self):
        """Draw legend for the map."""
        print(f"{self.BOLD}╔═══ LEGEND ═══════════════════════════╗{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.BG_GREEN} S  {self.RESET} Start Hub                     {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.BG_MAGENTA} G  {self.RESET} Goal Hub                      {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.GREEN}[●]{self.RESET}  Normal Zone (1 turn)         {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.ORANGE}[●]{self.RESET}  Restricted Zone (2 turns)    {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.CYAN}[●]{self.RESET}  Priority Zone (fast)         {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} {self.RED}[●]{self.RESET}  Blocked/Dead End             {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}║{self.RESET} [3]  Capacity Limit (max drones)  {self.BOLD}║{self.RESET}")
        print(f"{self.BOLD}╚══════════════════════════════════════╝{self.RESET}\n")

    def _draw_movements(self):
        """Draw current turn movements."""
        movements = []

        for d in self.drones:
            prev = self.previous_zone[d.id]
            curr = d.current_zone

            if d.is_arrived:
                if prev != curr:
                    movements.append(f"{self.GREEN}D{d.id}→{curr.name}{self.RESET}")
            elif d.restricted_movement_turns_buffer > 0:
                if d.path:
                    movements.append(f"{self.ORANGE}D{d.id}⟳{prev.name}→{d.path[0].name}{self.RESET}")
                else:
                    movements.append(f"{self.ORANGE}D{d.id}⟳{prev.name}{self.RESET}")
            elif prev != curr:
                movements.append(f"{self.CYAN}D{d.id}→{curr.name}{self.RESET}")

        if movements:
            print(f"{self.BOLD}Movements this turn:{self.RESET}")
            # Print in columns
            for i in range(0, len(movements), 3):
                print("  " + "  ".join(movements[i:i+3]))
            print()

    def update(self):
        """Update the display for the current turn."""
        self.turn_count += 1

        if self.animate:
            self._clear_screen()
            self._draw_map()
            self._draw_status()

            # Only show legend on first turn
            if self.turn_count == 1:
                self._draw_legend()

            self._draw_movements()

            # Update previous positions
            for d in self.drones:
                self.previous_zone[d.id] = d.current_zone

            # Pause for animation
            if not all(d.is_arrived for d in self.drones):
                time.sleep(self.delay)
        else:
            # Non-animated mode: just print movements
            movements = []
            for d in self.drones:
                prev = self.previous_zone[d.id]
                curr = d.current_zone

                if d.is_arrived:
                    if prev != curr:
                        movements.append(f"D{d.id}-{curr.name}")
                elif d.restricted_movement_turns_buffer > 0:
                    if d.path:
                        connection = f"{prev.name}-{d.path[0].name}"
                    else:
                        connection = f"{prev.name}-?"
                    movements.append(f"D{d.id}-{connection}")
                elif prev != curr:
                    movements.append(f"D{d.id}-{curr.name}")

                self.previous_zone[d.id] = curr

            if movements:
                print(" ".join(movements))
            else:
                print("")

    def show_final_summary(self):
        """Show final summary after simulation completes."""
        if self.animate:
            print(f"\n{self.BOLD}{'='*42}{self.RESET}")
            print(f"{self.BOLD}{self.GREEN}✓ SIMULATION COMPLETE!{self.RESET}")
            print(f"{self.BOLD}{'='*42}{self.RESET}")
            print(f"  Total Turns:     {self.turn_count}")
            print(f"  Drones Arrived:  {len(self.drones)}/{len(self.drones)}")
            print(f"{self.BOLD}{'='*42}{self.RESET}\n")
