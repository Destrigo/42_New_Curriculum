from models.drone import Drone
from models.zone import Node


class Display:
    def __init__(self, drones: list, nodes: list):
        self.drones = drones
        self.nodes = nodes

    def show(self) -> None:
        """show stuff"""
        