"""
Constrained Decoder con estrazione argomenti via Constrained Decoding.

MODIFICHE rispetto all'originale:
- Rimossi tutti i metodi _extract_*_args basati su regex
- Aggiunto ConstrainedArgumentExtractor
- _refactor_args ora usa constrained decoding
"""

from typing import Any, List, Dict
import json
import math
from llm_sdk import Small_LLM_Model
from .tokenizer import Tokenizer
from .constrained_arg_extractor import ConstrainedArgumentExtractor


class Decoder:
    """Decoder for constrained generation using LLM."""

    def __init__(self, prompts: List[str], functions: List[str]) -> None:
        """Initialize decoder with prompts and allowed functions."""
        self.prompts = prompts
        self.functions = functions
        self.model = Small_LLM_Model()

        vocab_path = self.model.get_path_to_vocabulary_json()
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                self.vocabulary: Dict[str, int] = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Vocabulary file not found at {vocab_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in vocabulary file: {vocab_path}",
                e.doc,
                e.pos
            ) from e

        self.tokenizer = Tokenizer(self.vocabulary)
        self.matrix = self.build_allowed_token_matrix(functions)

        # ═══════════════════════════════════════════════════════════════
        # NUOVO: Inizializza l'estrattore di argomenti con constrained decoding
        # ═══════════════════════════════════════════════════════════════
        self.arg_extractor = ConstrainedArgumentExtractor(
            model=self.model,
            tokenizer=self.tokenizer,
            vocabulary=self.vocabulary
        )

        self.general_prompt = (
            "Select the most appropriate function based on the task. "
            "Pay close attention to keywords: "
            "'sum' or 'add' means fn_add_numbers, "
            "'product' or 'multiply' means fn_multiply_numbers, "
            "'substitute' or 'replace' means fn_substitute_string_with_regex, "
            "'reverse' means fn_reverse_string. "
            "Functions: "
        )
        for func in self.functions:
            self.general_prompt += func + " "

    def build_allowed_token_matrix(
        self,
        functions: List[str]
    ) -> List[List[int]]:
        """Build matrix of allowed token sequences."""
        matrix: List[List[int]] = []
        for i, func in enumerate(functions):
            try:
                token_ids = self.encode_text(func)
                matrix.append(token_ids)
            except ValueError as e:
                raise ValueError(
                    f"Failed to tokenize function {i+1}: {func[:50]}..."
                ) from e
        return matrix

    def get_allowed_token_ids(self, generated_ids: List[int]) -> List[int]:
        """Get allowed next token IDs based on generated prefix."""
        allowed = set()
        prefix_len = len(generated_ids)
        for line in self.matrix:
            if line[:prefix_len] == generated_ids and len(line) > prefix_len:
                allowed.add(line[prefix_len])
        return list(allowed)

    def check_substring_match(self,
                              generated_ids: List[int]) -> tuple[bool,
                                                                 List[int]]:
        """Check if generated sequence is a substring
        of exactly one function."""
        matches = []
        for line in self.matrix:
            for i in range(len(line) - len(generated_ids) + 1):
                if line[i:i+len(generated_ids)] == generated_ids:
                    matches.append(line)
                    break
        if len(matches) == 1:
            return True, matches[0]
        else:
            return False, []

    def encode_text(self, text: str) -> List[int]:
        """Convert text to token IDs."""
        return self.tokenizer.encode(text, add_special_tokens=False)

    def decode_token_ids(self, token_ids: List[int]) -> str:
        """Convert token IDs to human-readable string."""
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    # ═══════════════════════════════════════════════════════════════════════
    # METODO MODIFICATO: Usa constrained decoding invece di regex
    # ═══════════════════════════════════════════════════════════════════════
    def _refactor_args(self, func_obj: dict, prompt: str) -> str:
        """
        Fill function arguments using CONSTRAINED DECODING.
        L'LLM genera i valori token-per-token, guidato dallo schema.
        Niente più regex!
        """
        arg_names = func_obj.get("args_names", [])
        arg_types = func_obj.get("args_types", {})
        fn_name = func_obj.get("fn_name", "")

        if not arg_names:
            func_obj["args"] = {}
            return json.dumps(func_obj)

        # Usa constrained decoding per estrarre gli argomenti
        args_dict = self.arg_extractor.extract_arguments(
            prompt=prompt,
            fn_name=fn_name,
            arg_names=arg_names,
            arg_types=arg_types
        )

        # Log per debug
        print(f"[Constrained Extraction] {fn_name}")
        for arg_name, value in args_dict.items():
            print(f"  {arg_name}: {value} ({type(value).__name__})")

        func_obj["args"] = args_dict
        return json.dumps(func_obj)

    def decode(self) -> List[str]:
        """Generate function calls with constrained decoding."""
        outputs: List[str] = []

        for prompt in self.prompts:
            output = self._decode_single_prompt(prompt)
            func_obj = json.loads(output)
            func_obj = self._validate_function_selection(func_obj, prompt)
            output = json.dumps(func_obj)
            output = self._refactor_args(json.loads(output), prompt)
            outputs.append(output)
        return outputs

    def _validate_function_selection(self,
                                     func_obj: dict,
                                     prompt: str) -> Any:
        """Validate and correct function selection based on prompt keywords."""
        fn_name = func_obj.get("fn_name", "")
        prompt_lower = prompt.lower()

        if 'sum' in prompt_lower or 'add' in prompt_lower:
            if fn_name != 'fn_add_numbers':
                for func_str in self.functions:
                    if '"fn_name":"fn_add_numbers"' in func_str:
                        return json.loads(func_str)
        if ('multiply' in prompt_lower or
           'product' in prompt_lower) and 'sum' not in prompt_lower:
            if fn_name != 'fn_multiply_numbers':
                for func_str in self.functions:
                    if '"fn_name":"fn_multiply_numbers"' in func_str:
                        return json.loads(func_str)

        if ('substitute' in prompt_lower or 'replace' in prompt_lower):
            if fn_name == 'fn_reverse_string':
                for func_str in self.functions:
                    if ('"fn_name":"'
                       'fn_substitute_string_with_regex"') in func_str:
                        return json.loads(func_str)
        return func_obj

    def _decode_single_prompt(self, prompt: str) -> str:
        """Decode a single prompt to a function call."""
        flag_created = False
        final_prompt = self.general_prompt + prompt

        try:
            input_ids = self.encode_text(final_prompt)
        except ValueError as e:
            raise Exception(
                f"Failed to encode prompt: {str(e)}"
            ) from e

        generated_ids: List[int] = []

        while not flag_created:
            logits = self.model.get_logits_from_input_ids(input_ids)
            allowed_ids = self.get_allowed_token_ids(generated_ids)
            if not allowed_ids:
                raise Exception(
                    f"No allowed tokens "
                    f"Generated so far: "
                    f"{self.decode_token_ids(generated_ids)}"
                )
            masked_logits = [-math.inf] * len(logits)
            for token_id in allowed_ids:
                if token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            max_logit = max(masked_logits)
            if max_logit == -math.inf:
                raise Exception(
                    f"All allowed token logits are -inf. "
                    f"Allowed IDs: {allowed_ids}"
                )
            next_token_id = masked_logits.index(max_logit)
            input_ids.append(next_token_id)
            generated_ids.append(next_token_id)

            is_unique_match, matched_function = self.check_substring_match(
                generated_ids)
            if is_unique_match:
                flag_created = True
                str_from_tokens = self.decode_token_ids(matched_function)
                return str_from_tokens

            prefix_matches = [
                line for line in self.matrix
                if line[:len(generated_ids)] == generated_ids
            ]
            if not prefix_matches:
                raise Exception(
                    f"No prefix matches. "
                    f"Generated: {self.decode_token_ids(generated_ids)}"
                )
        raise Exception("Decoding failed to produce a function call.")
