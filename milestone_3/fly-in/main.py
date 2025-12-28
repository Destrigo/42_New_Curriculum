from parsing.parser import Parser
from pathfinding.routing import Pathfinder
from execution.turns import Turns


class Solution:
    def main():
        """main"""
        with open("map.txt") as f:
            parsed_data = Parser(f)
        Pathfinder(parsed_data.drones, parsed_data.nodes)
        Turns(parsed_data.drones, parsed_data.nodes)


if __name__ == "__main__":
    Solution.main()
