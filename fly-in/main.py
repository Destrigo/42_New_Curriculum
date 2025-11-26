from parsing.parser import Parser
from pathfinding.routing import Pathfinder
from execution.turns import Turns


class Solution:
    def main():
        """main"""
        with open("map.txt") as f:
            parsed_data = Parser(f)
        drones = parsed_data.drones
        nodes = parsed_data.nodes
        Pathfinder(drones, nodes)
        Turns(drones, nodes)

if __name__ == "__main__":
    Solution.main()