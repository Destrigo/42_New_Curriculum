from typing import TextIO
# import json


class Parser:
    """Parser of the input"""
    def __init__(self, file_input: TextIO) -> None:
        """creates a self.prompt_list that is a list with all the prompts"""
        self.prompt_list: list[str] = []

        line = file_input.readline().strip()
        if line != "[":
            raise Exception("File doesn't start with [")

        line = file_input.readline().strip()
        if line != "{":
            raise Exception("prompt doesn't start with {")

        line = file_input.readline().strip()
        if line[:10] != '"prompt": ':
            raise Exception("Bad start of prompt sintax")
        try:
            self.prompt_list.append(str(line[10:]))
        except Exception:
            raise Exception("Bad prompt string")

        line = file_input.readline().strip()
        while (line == "},"):
            line = file_input.readline().strip()
            if line != "{":
                raise Exception("prompt doesn't start with {")

            line = file_input.readline().strip()
            if line[:10] != '"prompt": ':
                raise Exception("Bad start of prompt sintax")

            try:
                self.prompt_list.append(str(line[10:]))
            except Exception:
                raise Exception("Bad prompt string")
            line = file_input.readline().strip()

        if line != "}":
                raise Exception("Bad end of last prompt sintax")
        line = file_input.readline().strip()
        if line != "]":
            raise Exception("File doesn't end with ]")

    # def _next_line(self, f: TextIO) -> str:
    #     """Return next non-empty, non-comment line"""
    #     line = f.readline()
    #     while line and (line.strip() == "" or line.lstrip().startswith("#")):
    #         line = f.readline()
    #     return line.strip()

with open("../data/input/function_calling_tests.json") as f:
    obj = Parser(f)