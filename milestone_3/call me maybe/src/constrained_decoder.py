from typing import List, Dict
import json
import math
import re
from .small_llm_model import Small_LLM_Model
from .tokenizer import Tokenizer


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
        self.general_prompt = (
            "You are a function selector. Choose the MOST SPECIFIC function that matches the task. "
            "If the prompt mentions 'substitute', 'replace', or 'regex', choose fn_substitute_string_with_regex. "
            "If it only mentions 'reverse', choose fn_reverse_string. "
            "Available functions: "
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
        """Check if generated sequence is a substring of exactly one function."""
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

    def _refactor_args(self, func_obj: dict, prompt: str) -> str:
        """
        Fill function arguments by extracting values from prompt.
        
        Uses smart pattern matching tailored to each function type.
        """
        arg_names = func_obj.get("args_names", [])
        arg_types = func_obj.get("args_types", {})
        fn_name = func_obj.get("fn_name", "")
        
        if not arg_names:
            func_obj["args"] = {}
            return json.dumps(func_obj)
        
        print(f"\n=== Extracting args for {fn_name} ===")
        print(f"Prompt: {prompt}")
        
        args_dict = {}
        
        # Use function-specific extraction logic
        if fn_name == "fn_substitute_string_with_regex":
            args_dict = self._extract_substitute_args(prompt, arg_names)
        elif fn_name == "fn_add_numbers" or fn_name == "fn_multiply_numbers":
            args_dict = self._extract_binary_op_args(prompt, arg_names, arg_types)
        elif fn_name == "fn_is_even":
            args_dict = self._extract_is_even_args(prompt, arg_names, arg_types)
        elif fn_name == "fn_greet":
            args_dict = self._extract_greet_args(prompt, arg_names)
        elif fn_name == "fn_reverse_string":
            args_dict = self._extract_reverse_args(prompt, arg_names)
        elif fn_name == "fn_get_square_root":
            args_dict = self._extract_sqrt_args(prompt, arg_names, arg_types)
        else:
            # Generic extraction
            args_dict = self._extract_generic_args(prompt, arg_names, arg_types)
        
        for arg_name, value in args_dict.items():
            print(f"  {arg_name}: {value}")
        
        func_obj["args"] = args_dict
        result = json.dumps(func_obj)
        print(f"✓ Result: {result}\n")
        return result

    def _extract_substitute_args(
        self,
        prompt: str,
        arg_names: List[str]
    ) -> Dict[str, str]:
        """
        Extract args for fn_substitute_string_with_regex.
        
        Patterns:
        - "Substitute X with Y in Z"
        - "Replace X in Z with Y"
        
        Args: source_string, regex, replacement
        """
        args = {}
        
        # Pattern 1: "Substitute/Replace X with Y in 'Z'"
        match = re.search(
            r"(?:substitute|replace)\s+(?:the\s+)?(?:word\s+)?['\"]?(\w+)['\"]?\s+with\s+['\"]?(\w+)['\"]?\s+in\s+['\"]([^'\"]+)['\"]",
            prompt,
            re.IGNORECASE
        )
        if match:
            args["regex"] = match.group(1)
            args["replacement"] = match.group(2)
            args["source_string"] = match.group(3)
            return args
        
        # Pattern 2: "Replace X in 'Z' with Y"
        match = re.search(
            r"(?:replace|substitute)\s+(?:all\s+)?['\"]?(\w+)['\"]?\s+in\s+['\"]([^'\"]+)['\"]\s+with\s+['\"]?(\w+)['\"]?",
            prompt,
            re.IGNORECASE
        )
        if match:
            args["regex"] = match.group(1)
            args["source_string"] = match.group(2)
            args["replacement"] = match.group(3)
            return args
        
        # Pattern 3: "Substitute X in 'Z' with 'Y'"
        match = re.search(
            r"(?:substitute|replace)\s+(?:the\s+)?(\w+)\s+in\s+(?:the\s+string\s+)?['\"]([^'\"]+)['\"]\s+with\s+['\"]([^'\"]+)['\"]",
            prompt,
            re.IGNORECASE
        )
        if match:
            args["regex"] = match.group(1)
            args["source_string"] = match.group(2)
            args["replacement"] = match.group(3)
            return args
        
        # Fallback: extract quoted strings in order
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
        if len(quoted) >= 2:
            args["source_string"] = quoted[0] if len(quoted) > 0 else ""
            args["regex"] = quoted[1] if len(quoted) > 1 else ""
            args["replacement"] = quoted[2] if len(quoted) > 2 else ""
        
        return args

    def _extract_binary_op_args(
        self,
        prompt: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Extract args for binary operations (add, multiply).
        
        Pattern: "What is the X of A and B"
        """
        args = {}
        
        # Pattern: "X of A and B"
        match = re.search(
            r"(?:sum|product|difference)\s+of\s+(\d+\.?\d*)\s+and\s+(\d+\.?\d*)",
            prompt,
            re.IGNORECASE
        )
        if match:
            args[arg_names[0]] = float(match.group(1))
            args[arg_names[1]] = float(match.group(2))
            return args
        
        # Fallback: extract all numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        if len(numbers) >= 2:
            args[arg_names[0]] = float(numbers[0])
            args[arg_names[1]] = float(numbers[1])
        
        return args

    def _extract_is_even_args(
        self,
        prompt: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, int]:
        """
        Extract args for fn_is_even.
        
        Pattern: "Is X an even number?"
        """
        args = {}
        
        # Pattern: "Is X an even/odd number"
        match = re.search(r"is\s+(\d+)\s+an?\s+(?:even|odd)", prompt, re.IGNORECASE)
        if match:
            args[arg_names[0]] = int(match.group(1))
            return args
        
        # Fallback: extract first number
        numbers = re.findall(r'\b\d+\b', prompt)
        if numbers:
            args[arg_names[0]] = int(numbers[0])
        
        return args

    def _extract_greet_args(
        self,
        prompt: str,
        arg_names: List[str]
    ) -> Dict[str, str]:
        """
        Extract args for fn_greet.
        
        Pattern: "Greet X"
        """
        args = {}
        
        # Pattern: "Greet X"
        match = re.search(r"greet\s+(\w+)", prompt, re.IGNORECASE)
        if match:
            args[arg_names[0]] = match.group(1)
            return args
        
        # Fallback: last word
        words = prompt.split()
        if words:
            args[arg_names[0]] = words[-1].strip('.,!?')
        
        return args

    def _extract_reverse_args(
        self,
        prompt: str,
        arg_names: List[str]
    ) -> Dict[str, str]:
        """
        Extract args for fn_reverse_string.
        
        Pattern: "Reverse the string 'X'"
        """
        args = {}
        
        # Pattern: "Reverse 'X'" or "Reverse the string 'X'"
        match = re.search(r"reverse\s+(?:the\s+)?(?:string\s+)?['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if match:
            args[arg_names[0]] = match.group(1)
            return args
        
        # Fallback: extract quoted string
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
        if quoted:
            args[arg_names[0]] = quoted[0]
        
        return args

    def _extract_sqrt_args(
        self,
        prompt: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Extract args for fn_get_square_root.
        
        Pattern: "What is the square root of X"
        """
        args = {}
        
        # Pattern: "square root of X"
        match = re.search(r"square\s+root\s+of\s+(\d+\.?\d*)", prompt, re.IGNORECASE)
        if match:
            args[arg_names[0]] = float(match.group(1))
            return args
        
        # Fallback: extract number
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        if numbers:
            args[arg_names[0]] = float(numbers[0])
        
        return args

    def _extract_generic_args(
        self,
        prompt: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, any]:
        """
        Generic extraction for any function.
        """
        args = {}
        
        # Extract quoted strings and numbers
        quoted_strings = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        
        string_idx = 0
        number_idx = 0
        
        for arg_name in arg_names:
            arg_type = arg_types.get(arg_name, "str")
            arg_type_lower = str(arg_type).lower()
            
            if 'int' in arg_type_lower:
                if number_idx < len(numbers):
                    args[arg_name] = int(numbers[number_idx])
                    number_idx += 1
            elif 'float' in arg_type_lower:
                if number_idx < len(numbers):
                    args[arg_name] = float(numbers[number_idx])
                    number_idx += 1
            else:
                if string_idx < len(quoted_strings):
                    args[arg_name] = quoted_strings[string_idx]
                    string_idx += 1
        
        return args

    def decode(self) -> List[str]:
        """Generate function calls with constrained decoding."""
        outputs: List[str] = []

        for prompt in self.prompts:
            output = self._decode_single_prompt(prompt)
            output = self._refactor_args(json.loads(output), prompt)
            outputs.append(output)
        return outputs

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
            print(
                f"Next token ID: {next_token_id} "
                f"('{self.tokenizer.decode([next_token_id])}')"
            )
            input_ids.append(next_token_id)
            generated_ids.append(next_token_id)

            is_unique_match, matched_function = self.check_substring_match(
                generated_ids)
            if is_unique_match:
                flag_created = True
                str_from_tokens = self.decode_token_ids(matched_function)
                print(f"Matched function: {str_from_tokens}")
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