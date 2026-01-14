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
        self.max = len(self.matrix)

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

    def decode(self) -> list[str]:
        """Generate JSON function calls with constrained decoding"""
        # to create and return
        logits_matrix: list[list[int]] = []
        i = 0
        flag_match: bool = False
        flag_created: bool = False
        for prompt in self.prompts:
            flag_created = False
            i = 0
            while not flag_created:
                flag_match = False
            
                input_ids = self.encode_text(prompt)
                logits = self.model.get_logits_from_input_ids(input_ids)
                next_logit = get_next_logit(logits)
                for token, token_id in next_logit:
                    for lst in self.matrix:
                        if token_id == lst[i]:
                            flag_match = True
                        else:
                            next_logit[token] = float(-inf)
                if not flag_match:
                    raise Exception("No tokens found")
                logits.append(index(max(next_logit)))
                for lst in self.matrix:
                    if logits == lst:
                        flag_created = True
                        logits_matrix.append(logits)
                i += 1
        return logits_matrix
