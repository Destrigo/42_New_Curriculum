import json


class Parser:
    """Parser of the input"""
    def __init__(self,
                 file_input_prompt: str,
                 file_input_func: str) -> None:
        """creates a self.prompt_list that is a list with all the prompts"""
        self.prompt_list: list[str] = self.__parse_prompts(file_input_prompt)
        self.func_list: list[str] = self.__parse_func(file_input_func)

    def __parse_func(self, file_input_func: str) -> list[str]:
        """
        takes the input file and parses the functions from it,
        returning list of functions
        """
        func_list: list[str] = []
        try:
            with open(file_input_func, "r") as file_func:
                d = json.load(file_func)
                for func_obj in d:
                    func_string = json.dumps(func_obj,
                                             separators=(",", ":"))
                    required_keys = {"fn_name",
                                     "args_names",
                                     "args_types",
                                     "return_type"}
                    if not required_keys.issubset(func_obj):
                        raise ValueError("Invalid function "
                                         f"schema: {func_obj}")
                    func_list.append(func_string)
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
                for prompt_obj in d:
                    # Extract just the prompt string from the dictionary
                    if isinstance(prompt_obj, dict) and "prompt" in prompt_obj:
                        prompt_list.append(str(prompt_obj["prompt"]))
                    elif isinstance(prompt_obj, str):
                        prompt_list.append(prompt_obj)
                    else:
                        raise Exception("Bad prompt format")
        except FileNotFoundError:
            raise FileNotFoundError("File prompts not found")

        for prompt in prompt_list:
            if not isinstance(prompt, str):
                raise Exception("Bad prompt sintax")
            if prompt.strip() == "":
                raise Exception("Empty prompt found")
            if len(prompt) > 1000:
                raise Exception("Prompt too long")
        return prompt_list
