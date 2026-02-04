import json


class Parser:
    """Parser of the input"""
    def __init__(self,
                 file_input: str) -> None:
        """???"""
        self.input: ??? = self.__parse_input(file_input)
        
    def __parse_func(self, file_input: str) -> list[str]:
        """
        takes the input file and parses the functions from it,
        returning list of functions
        """
        with open(file_input, "r") as config:
            d = json.load(config)
            #
            #
            # parse keys, first decide keys
            # match perfectly, if no match go to default, no extra keys
            #
            #
            
        
