from typing import TextIO


class Function:
    """Function representation"""
    def __init__(self,
                 name: str,
                 description: str,
                 parameters: dict) -> None:
        self.name = name
        self.description = description
        self.parameters = parameters


class Parser:
    """Parser of the input"""
    def __init__(self,
                 file_input_prompt: str,
                 file_input_func: str) -> None:
        """creates a self.prompt_list that is a list with all the prompts"""
        self.prompt_list: list[str] = self.__parse_prompts(file_input_prompt)
        self.func_list: list[Function] = self.__parse_func(file_input_func)

    def __parse_func(self, file_input_func: TextIO) -> list[Function]:
        """
        takes the input file and parses the functions from it,
        returning list of functions
        """
        func_list: list[Function] = []
        try:
            with open(file_input_func, "r") as file_input_func:
                line = file_input_func.readline().strip()
                if line != "[":
                    raise Exception("File doesn't start with [")

                line = file_input_func.readline().strip()
                if line != "{":
                    raise Exception("function doesn't start with {")

                line = file_input_func.readline().strip()
                if line[:8] != '"name": ':
                    raise Exception("Bad start of name sintax")
                try:
                    name = str(line[8:])
                except Exception:
                    raise Exception("Bad name string")

                line = file_input_func.readline().strip()
                if line[:15] != '"description": ':
                    raise Exception("Bad start of description sintax")
                try:
                    description = str(line[15:])
                except Exception:
                    raise Exception("Bad description string")

                line = file_input_func.readline().strip()
                if line[:14] != '"parameters": ':
                    raise Exception("Bad start of parameters sintax")
                try:
                    parameters = eval(line[14:])
                except Exception:
                    raise Exception("Bad parameters dict")

                func_list.append(Function(name, description, parameters))
        except FileNotFoundError:
            raise Exception("File functions not found")
        return func_list

    def __parse_prompts(self, file_input_prompt: TextIO) -> list[str]:
        """parses the prompts from the input file and returns
        them as a list of strings"""
        prompt_list: list[str] = []
        try:
            with open(file_input_prompt, "r") as file_input_prompt:
                line = file_input_prompt.readline().strip()
                if line != "[":
                    raise Exception("File doesn't start with [")

                line = file_input_prompt.readline().strip()
                if line != "{":
                    raise Exception("prompt doesn't start with {")

                line = file_input_prompt.readline().strip()
                if line[:10] != '"prompt": ':
                    raise Exception("Bad start of prompt sintax")
                try:
                    prompt_list.append(str(line[10:]))
                except Exception:
                    raise Exception("Bad prompt string")

                line = file_input_prompt.readline().strip()
                while (line == "},"):
                    line = file_input_prompt.readline().strip()
                    if line != "{":
                        raise Exception("prompt doesn't start with {")

                    line = file_input_prompt.readline().strip()
                    if line[:10] != '"prompt": ':
                        raise Exception("Bad start of prompt sintax")

                    try:
                        self.prompt_list.append(str(line[10:]))
                    except Exception:
                        raise Exception("Bad prompt string")
                    line = file_input_prompt.readline().strip()

                if line != "}":
                    raise Exception("Bad end of last prompt sintax")
                line = file_input_prompt.readline().strip()
                if line != "]":
                    raise Exception("File doesn't end with ]")
        except FileNotFoundError:
            raise Exception("File prompts not found")
        return prompt_list

    # def _next_line(self, f: TextIO) -> str:
    #     """Return next non-empty, non-comment line"""
    #     line = f.readline()
    #     while line and (line.strip() == "" or line.lstrip().startswith("#")):
    #         line = f.readline()
    #     return line.strip()
