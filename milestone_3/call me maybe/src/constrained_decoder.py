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
        self.model = Small_LLM_Model()
        self.tokenizer = self.model._tokenizer

        # get vocabulary and id_to_token mapping
        vocab_path = self.model.get_path_to_vocabulary_json()
        with open(vocab_path) as f:
            self.vocabulary: dict[str, int] = json.load(f)

        # Get actual vocab size from a test run
        test_logits = self.model.get_logits_from_input_ids([0])
        self.vocab_size = len(test_logits)
        print(f"Vocabulary from JSON: {len(self.vocabulary)} tokens")
        print(f"Model logits size: {self.vocab_size} tokens")
        # Build id_to_token mapping using the tokenizer's convert_ids_to_tokens
        self.id_to_token: dict[int, str] = {}
        if self.vocab_size != len(self.vocabulary):
            print(f"NOTE: Model has {self.vocab_size - len(self.vocabulary)} additional tokens beyond vocabulary")

        # tokenize all function components
        for func in self.functions:
            # Tokenize function name as a quoted string
            func.tkname = self.encode_text(f'"{func.name}"')
            print(f"Function {func.name} tokenized to {len(func.tkname)} tokens")
            # Tokenize each argument name as a quoted string
            for arg in func.args:
                func.tkargs.append(self.encode_text(f'"{arg}"'))
            # Tokenize type descriptions (if needed)
            for type_name, type_desc in func.types.items():
                func.tktypes[type_name] = self.encode_text(type_desc)
            func.tkreturn_type = self.encode_text(func.return_type)

    def encode_text(self, text: str) -> list[int]:
        """Convert text to token IDs using the model's tokenizer."""
        # Use the model's tokenizer directly
        return self.model._tokenizer.encode(text, add_special_tokens=False)

    def decode_token_id(self, token_id: int) -> str:
        """Convert a single token ID back to its string representation."""
        return self.model._tokenizer.convert_ids_to_tokens([token_id])[0]

    def get_token_string(self, token_id: int) -> str:
        """Get the actual string that a token represents (for matching)."""
        # Decode the token to get its string form
        token_str = self.model._tokenizer.decode([token_id])
        return token_str

    def decode(self) -> list[str]:
        """Genera direttamente JSON valido come risposta dal modello"""
        outputs = []
        for prompt in self.prompts:
            fsm = FSM(self.functions, self.tokenizer)
            input_ids = self.encode_text(prompt)
            output_token_ids = []
            max_iter = 1000
            iter_count = 0
            while fsm.get_current_state().name != "END" and iter_count < max_iter:
                iter_count += 1
                logits = self.model.get_logits_from_input_ids(input_ids)
                allowed_ids = fsm.get_allowed_token_ids()
                if not allowed_ids:
                    raise Exception(f"No allowed tokens in state {fsm.get_current_state()}")
                # Seleziona miglior token consentito
                best_token_id = max(
                    allowed_ids,
                    key=lambda tid: logits[tid] if tid < len(logits) else float("-inf")
                )
                # Aggiorna FSM
                fsm.consume_token_id(best_token_id)
                # Aggiorna input e output
                input_ids.append(best_token_id)
                output_token_ids.append(best_token_id)
            if iter_count >= max_iter:
                raise Exception(f"Max iterations reached for prompt: {prompt}")
            # Decodifica direttamente il JSON generato dal modello
            json_output = self.tokenizer.decode(output_token_ids)
            # Optional: verifica che sia un JSON valido
            try:
                parsed_json = json.loads(json_output)
            except json.JSONDecodeError:
                print(f"Warning: modello non ha generato JSON valido per il prompt: {prompt}")
                parsed_json = {"error": "Invalid JSON", "raw_output": json_output}

            outputs.append(json.dumps(parsed_json, indent=2))
            print(f"\nPrompt: {prompt}")
            print(f"Output JSON: {json.dumps(parsed_json, indent=2)}\n")
        return outputs
