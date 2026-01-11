from .models import Function, FSM
from .small_llm_model import Small_LLM_Model
import json


class Decoder:
    """Decoder representation"""
    def __init__(self,
                 prompts: list[str],
                 functions: list[Function]) -> None:
        self.prompts = prompts
        self.functions = functions
        self.fsm = FSM()  # to implement
        self.model = Small_LLM_Model()

        # get vocabulary and id_to_token mapping
        vocab_path = self.model.get_path_to_vocabulary_json()
        with open(vocab_path) as f:
            self.vocabulary: dict[str, int] = json.load(f)
        self.id_to_token: dict[int, str] = {
            v: k for k, v in self.vocabulary.items()
        }

        # tokenize all function components
        for func in self.functions:
            # Tokenize function name, description, and parameters
            func.tkname = self.encode_text(func.name)
            for arg in func.args:
                func.tkargs.append(self.encode_text(arg))
            for type_name, type_desc in func.types.items():
                func.tktypes[type_name] = self.encode_text(type_desc)
            func.tkreturn_type = self.encode_text(func.return_type)

    def encode_text(self, text: str) -> list[int]:
        """Convert text to token IDs using greedy longest-match."""
        i = 0
        token_ids: list[int] = []
        while i < len(text):
            if text[:i] in self.vocabulary:
                token_ids.append(self.vocabulary[text[:i]])
                text = text[i:]
                i = 1
            else:
                i += 1
        return token_ids

    def decode(self) -> list[str]:
        """Run constrained decoding or all prompts"""
        outputs: list[str] = []
        for prompt in self.prompts:
            input_ids = self.encode_text(prompt)
            output = ""
            while self.fsm.get_current_state().name != "END":
                logits = self.model.get_logits_from_input_ids(input_ids)
                allowed_tokens = self.fsm.get_allowed_tokens()
                # Mask logits
                for token, token_id in self.vocabulary.items():
                    if token not in allowed_tokens:
                        logits[token_id] = float("-inf")
                # select best token
                best_token_id = logits.index(max(logits))
                best_token = self.id_to_token[best_token_id]
                # Update FSM
                self.fsm.consume(best_token)
                # Append
                input_ids.append(best_token_id)
                output += best_token
            outputs.append(output)
        return outputs
