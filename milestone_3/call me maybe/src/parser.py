from .models import Function
import json


class Parser:
    """Parser of the input"""
    def __init__(self,
                 file_input_prompt: str,
                 file_input_func: str) -> None:
        """creates a self.prompt_list that is a list with all the prompts"""
        self.prompt_list: list[str] = self.__parse_prompts(file_input_prompt)
        self.func_list: list[Function] = self.__parse_func(file_input_func)

    def __parse_func(self, file_input_func: str) -> list[Function]:
        """
        takes the input file and parses the functions from it,
        returning list of functions
        """
        func_list: list[Function] = []
        try:
            with open(file_input_func, "r") as file_func:
                d = json.load(file_func)
                for func in d:
                    try:
                        func_list.append(
                            Function(
                                name=str(func["fn_name"]),
                                args=list(func["args_names"]),
                                types=dict(func["args_types"]),
                                return_type=str(func["return_type"])
                            )
                        )
                    except Exception:
                        raise Exception("Bad function sintax")
        except FileNotFoundError:
            raise Exception("File functions not found")
        return func_list

    def __parse_prompts(self, file_input_prompt: str) -> list[str]:
        """parses the prompts from the input file and returns
        them as a list of strings"""
        prompt_list: list[str] = []
        try:
            with open(file_input_prompt, "r") as file_prompt:
                d = json.load(file_prompt)
                for prompt in d:
                    prompt_list.append(str(prompt))
        except FileNotFoundError:
            raise FileNotFoundError("File prompts not found")

        for prompt in prompt_list:
            if not isinstance(prompt, str):
                raise Exception("Bad prompt sintax")
            if prompt.strip() == "":
                raise Exception("Empty prompt found")
            if prompt.count('"') % 2 != 0:
                raise Exception("Unbalanced quotes in prompt")
            if len(prompt) > 1000:
                raise Exception("Prompt too long")
            if prompt.count("{") != prompt.count("}"):
                raise Exception("Unbalanced braces in prompt")
            if prompt.count("(") != prompt.count(")"):
                raise Exception("Unbalanced parentheses in prompt")
            if prompt.count("[") != prompt.count("]"):
                raise Exception("Unbalanced brackets in prompt")
            if "\n" in prompt:
                raise Exception("Newline character in prompt")
            if "\t" in prompt:
                raise Exception("Tab character in prompt")
            if prompt.startswith(" ") or prompt.endswith(" "):
                raise Exception("Prompt starts or ends with whitespace")
            if "  " in prompt:
                raise Exception("Prompt contains consecutive spaces")
            if any(ord(c) < 32 or ord(c) > 126 for c in prompt):
                raise Exception("Prompt contains non-ASCII characters")
            if prompt in prompt_list[:prompt_list.index(prompt)]:
                raise Exception("Duplicate prompt found")
        return prompt_list
