from visualization.terminal_display import Display


class Turns:
    """Turns"""
    def __init__(self, drones: list, nodes: list) -> int:
        turns = 0
        #d = Display(drones, nodes)
        #d.show()
        while not all(Drone.is_arrived for Drone in drones):
            turns += 1
            for d in drones:
                if d.is_arrived is False:
                    d.action(drones)
            #d.show()
        print(turns)
