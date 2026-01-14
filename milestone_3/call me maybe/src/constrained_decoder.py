from .small_llm_model import Small_LLM_Model
import json


class Decoder:
    """Decoder representation"""
    def __init__(self,
                 prompts: list[str],
                 functions: list[str]) -> None:
        self.prompts = prompts
        self.functions = functions
        self.model = Small_LLM_Model()
        self.tokenizer = self.model._tokenizer

        # get vocabulary and id_to_token mapping
        vocab_path = self.model.get_path_to_vocabulary_json()
        with open(vocab_path) as f:
            self.vocabulary: dict[str, int] = json.load(f)
        self.matrix = self.build_allowed_token_matrix(functions)

    def build_allowed_token_matrix(self,
                                   functions: list[str]
                                   ) -> list[list[int]]:
        """
        Build a matrix where each row corresponds to the token IDs
        of a function string.
        """

        matrix: list[list[int]] = []
        for func in functions:
            matrix.append(self.encode_text(func))
        return matrix

    def get_allowed_token_ids(self, generated_ids: list[int]) -> list[int]:
        """
        Docstring for get_allowed_token_ids
        
        :param self: Description
        :param id: Description
        :type id: int
        :return: Description
        :rtype: list[int]
        """
        allowed = []
        prefix_len = len(generated_ids)
        for line in self.matrix:
            if line[:prefix_len] == generated_ids and len(line) > prefix_len:
                allowed.append(line[prefix_len])
        return allowed

    def encode_text(self, text: str) -> list[int]:
        """Convert text to token IDs using the model's tokenizer."""
        return self.model._tokenizer.encode(text, add_special_tokens=False)

    def decode_token_id(self, token_id: int) -> str:
        """takes logits give back dictionary equiv."""
        return self.model._tokenizer.convert_ids_to_tokens([token_id])[0]

    def get_token_string(self, token_id: int) -> str:
        """Gets logits give back human string."""
        token_str = self.model._tokenizer.decode([token_id])
        return token_str

    def decode(self) -> list[list[int]]:
        """Generate JSON function calls with constrained decoding"""
        # to create and return
        logits_matrix: list[list[int]] = []
        flag_created: bool = False
        for prompt in self.prompts:
            i = 0
            flag_created = False
            input_ids = self.encode_text(prompt)
            generated_ids: list[int] = []
            while flag_created is False:
                logits = self.model.get_logits_from_input_ids(input_ids)
                allowed_ids = self.get_allowed_token_ids(generated_ids)
                import math
                masked_logits = [-math.inf] * len(logits)
                for token_id in allowed_ids:
                    if token_id < len(logits):
                        masked_logits[token_id] = float(logits[token_id])
                next_token_id = masked_logits.index(max(masked_logits))
                input_ids.append(next_token_id)
                generated_ids.append(next_token_id)
                print(self.get_token_string(next_token_id))
                prefix_matches = [line for line in self.matrix if line[:len(generated_ids)] == generated_ids]
                # if len(prefix_matches) == 1:
                #     # Full line matched
                #     flag_created = True
                #     logits_matrix.append(prefix_matches[0])
                i += 1
        return logits_matrix
