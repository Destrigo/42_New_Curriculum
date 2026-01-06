from parsing.parser import Parser
from pathfinding.routing import Pathfinder
from execution.turns import Turns


class Solution:
    def main(self) -> None:
        """main"""
        try:
            with open("map.txt") as f:
                parsed_data = Parser(f)
        except FileNotFoundError:
            raise FileNotFoundError("File not found")
        Pathfinder(parsed_data.drones, parsed_data.nodes)
        Turns(parsed_data.drones, parsed_data.nodes)


if __name__ == "__main__":
    sol = Solution()
    sol.main()
