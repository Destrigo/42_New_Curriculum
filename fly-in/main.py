from parsing.parser import Parser
from pathfinding.routing import Pathfinder
from execution.turns import Turns


class Solution:
    def main():
        """main"""
        f = open("map.txt")
        parsed_data = []
        parsed_data = Parser(f)
        # close(f)
        drones = [parsed_data[0]]
        nodes = [parsed_data[1]]
        Pathfinder(drones, nodes)
        Turns(drones, nodes)
