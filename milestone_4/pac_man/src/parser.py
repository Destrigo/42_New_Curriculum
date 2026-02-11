import json


class Parser:
    """Parser of the input"""
    def __init__(self,
                 file_input: str) -> None:
        """???"""
        self.input = self.__parse_input(file_input)
        self.scoreboard = self.__parse_scores()
        
    def __parse_scores(self):
        try:
            with open("../scoreboard.json", "r") as f:
                json_scores = json.load(f)
                return json_scores
        except FileNotFoundError:
            return "no scoreboard file found"

    def __parse_input(self, file_input: str) -> list[str]:
        """
        takes the input file and parses the functions from it,
        returning list of functions
        """
        # placeholder
        dict_config = {
            "map": list,
            "pacman": dict,
            "ghosts": list,
            "points_per_ghost": int,
            "lives": int,
            "seed": int,
            "level_max_time": int
        }

        with open(file_input, "r") as config:
            config = json.load(config)
            #
            #
            # parse keys, first decide keys
            # match perfectly, if no match go to default, no extra keys
            #
            #
            if len(config) != 5:
                raise Exception("Invalid input file")
            for key in dict_config.keys():
                if key not in config:
                    raise Exception("Invalid input file")
                if not isinstance(config[key], dict_config[key]):
                    raise Exception("Invalid input file")
            return config
