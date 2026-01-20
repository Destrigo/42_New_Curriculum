from .small_llm_model import Small_LLM_Model
import json
import math


class Tokenizer:
    def __init__(self, vocab: dict[str, int]) -> None:
        self.vocab = vocab
        self.inv_vocab = {v: k for k, v in vocab.items()}
        self.vocab_size = len(vocab)
        print(self.vocab)

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        """Convert text to token IDs using greedy longest-match."""
        token_ids: list[int] = []
        i = 0
        while i < len(text):
            # Try to match longest possible token starting at i
            best_match_len = 0
            best_token_id = None

            for length in range(len(text) - i, 0, -1):
                substring = text[i:i+length]
                if substring in self.vocab:
                    best_match_len = length
                    best_token_id = self.vocab[substring]
                    break

            if best_token_id is not None:
                token_ids.append(best_token_id)
                i += best_match_len
                print(token_ids)
            # else:
            #     # If no match found, raise error
            #     raise ValueError("Cannot tokenize character at"
            #                      f"position {i}: '{text[i]}' in text '{text}'")

        return token_ids

    def decode(self, token_ids: list[int]) -> str:
        """Decode token IDs back to text - concatenate without spaces"""
        tokens = [self.inv_vocab[token_id] for token_id in
                  token_ids if token_id in self.inv_vocab]
        return ''.join(tokens)

    def convert_ids_to_tokens(self, token_ids: list[int]) -> list[str]:
        """Convert token IDs to token strings"""
        tokens = [self.inv_vocab[token_id] for token_id
                  in token_ids if token_id in self.inv_vocab]
        return tokens


class Decoder:
    """Decoder representation"""
    def __init__(self,
                 prompts: list[str],
                 functions: list[str]) -> None:
        self.prompts = prompts
        self.functions = functions
        self.model = Small_LLM_Model()

        # get vocabulary and id_to_token mapping
        vocab_path = self.model.get_path_to_vocabulary_json()
        with open(vocab_path) as f:
            self.vocabulary: dict[str, int] = json.load(f)
        self.tokenizer = Tokenizer(self.vocabulary)
        self.matrix = self.build_allowed_token_matrix(functions)
        self.general_prompt = ("Recreate one of the following functions"
                               "based on the prompt given at the end: ")
        for func in self.functions:
            self.general_prompt += func

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
        return self.tokenizer.encode(text, add_special_tokens=False)

    def decode_token_id(self, token_id: int) -> str:
        """takes logits give back dictionary equiv."""
        return self.tokenizer.convert_ids_to_tokens([token_id])[0]

    def get_token_string(self, token_id: int) -> str:
        """Gets logits give back human string."""
        return self.tokenizer.decode([token_id])

    def decode(self) -> list[list[int]]:
        """Generate JSON function calls with constrained decoding"""
        # to create and return
        logits_matrix: list[str] = []
        flag_created: bool = False
        for prompt in self.prompts:
            i = 0
            flag_created = False
            final_prompt = self.general_prompt + prompt
            input_ids = self.encode_text(final_prompt)
            generated_ids: list[int] = []
            while flag_created is False:
                logits = self.model.get_logits_from_input_ids(input_ids)
                allowed_ids = self.get_allowed_token_ids(generated_ids)
                masked_logits = [-math.inf] * len(logits)
                for token_id in allowed_ids:
                    masked_logits[token_id] = float(logits[token_id])
                next_token_id = masked_logits.index(max(masked_logits))
                input_ids.append(next_token_id)
                generated_ids.append(next_token_id)
                # print(self.get_token_string(next_token_id))
                prefix_matches = [line for line in self.matrix
                                  if line[:len(generated_ids)]
                                  == generated_ids]
                if len(prefix_matches) == 1:
                    # Full line matched
                    flag_created = True
                    str_from_logits = ""
                    for int_token in prefix_matches[0]:
                        str_from_logits += self.tokenizer.decode(
                            int_token)
                    logits_matrix.append(str_from_logits)
                i += 1
        return logits_matrix
