from typing import List, Dict
import json
import math
from .small_llm_model import Small_LLM_Model
from .tokenizer import Tokenizer


class Decoder:
    """Decoder for constrained generation using LLM.
    This decoder uses a matrix-based approach to constrain the LLM's
    output to match one of the predefined function call strings.
    """

    def __init__(self, prompts: List[str], functions: List[str]) -> None:
        """Initialize decoder with prompts and allowed functions.
        Args:
            prompts: List of user prompts to process
            functions: List of valid function call JSON strings
        Raises:
            FileNotFoundError: If vocabulary file not found
            json.JSONDecodeError: If vocabulary file is invalid JSON
        """
        self.prompts = prompts
        self.functions = functions
        self.model = Small_LLM_Model()

        # Load vocabulary
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

        # Create tokenizer (handles byte-level encoding internally)
        self.tokenizer = Tokenizer(self.vocabulary)
        # Build matrix of allowed token sequences
        self.matrix = self.build_allowed_token_matrix(functions)
        # Build general prompt
        self.general_prompt = (
            "Recreate one of the following functions "
            "based on the prompt given at the end: "
        )
        for func in self.functions:
            self.general_prompt += func + " "

    def build_allowed_token_matrix(
        self,
        functions: List[str]
    ) -> List[List[int]]:
        """Build matrix of allowed token sequences.
        Each row in the matrix represents the token IDs for one
        valid function call string.
        Args:
            functions: List of function call JSON strings
        Returns:
            Matrix where each row is a list of token IDs
        Raises:
            ValueError: If any function cannot be tokenized
        """
        matrix: List[List[int]] = []

        for i, func in enumerate(functions):
            try:
                token_ids = self.encode_text(func)
                matrix.append(token_ids)
                # print(
                #     f"Function {i+1} tokenized to {len(token_ids)} tokens: "
                #     f"{func[:50]}..."
                # )
            except ValueError as e:
                raise ValueError(
                    f"Failed to tokenize function {i+1}: {func[:50]}..."
                ) from e
        return matrix

    def get_allowed_token_ids(self, generated_ids: List[int]) -> List[int]:
        """Get allowed next token IDs based on generated prefix.
        Args:
            generated_ids: List of token IDs generated so far
        Returns:
            List of token IDs that can follow the current prefix
        """
        allowed = set()
        prefix_len = len(generated_ids)

        for line in self.matrix:
            # Check if this line matches our prefix so far
            if line[:prefix_len] == generated_ids and len(line) > prefix_len:
                # Add the next token from this line
                allowed.add(line[prefix_len])
        return list(allowed)

    def check_substring_match(self,
                              generated_ids: List[int]) -> tuple[bool,
                                                                 List[int]]:
        """Check if generated sequence is a substring of exactly one function.
        Args:
            generated_ids: List of token IDs generated so far
        Returns:
            Tuple of (is_unique_match, matched_function_ids)
            - is_unique_match: True if exactly one function
            contains this substring
            - matched_function_ids: The full token sequence of
            the matched function
        """
        matches = []
        for line in self.matrix:
            # Check if generated_ids appears anywhere in this line
            for i in range(len(line) - len(generated_ids) + 1):
                if line[i:i+len(generated_ids)] == generated_ids:
                    matches.append(line)
                    break  # Found in this line, move to next line
        # Return True only if exactly one function matches
        if len(matches) == 1:
            return True, matches[0]
        else:
            return False, []

    def encode_text(self, text: str) -> List[int]:
        """Convert text to token IDs.
        Args:
            text: Text to encode
        Returns:
            List of token IDs
        Raises:
            ValueError: If text cannot be tokenized
        """
        return self.tokenizer.encode(text, add_special_tokens=False)

    def decode_token_ids(self, token_ids: List[int]) -> str:
        """Convert token IDs to human-readable string.
        Args:
            token_ids: List of token IDs
        Returns:
            Decoded string
        """
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

    def _refactor_args(self, func_obj: dict, prompt: str) -> str:
        """
        Given a function object with empty 'args', generate the
        filled 'args' JSON using the LLM.
        Stops when a valid JSON object is produced.
        """
        # --- setup -------------------------------------------------
        remaining_args = set(func_obj["args_names"])

        prompt_token_ids = set(self.encode_text(prompt))
        structural_token_ids = set(self.encode_text(' {}[]":,'))
        colon_ids = set(self.encode_text(':'))
        comma_ids = set(self.encode_text(','))
        brace_close_ids = set(self.encode_text('}'))

        system_prompt = (
            "Fill the function arguments using ONLY values copied "
            "from the user prompt. Return ONLY valid JSON."
        )
        llm_prompt = (
            "User prompt:\n"
            f"{prompt}\n\n"
            "Argument names:\n"
            f"{func_obj['args_names']}\n\n"
            "Fill the arguments as JSON:\n"
        )
        llm_prompt = system_prompt + llm_prompt
        input_ids = self.encode_text(llm_prompt)
        generated_ids: List[int] = []

        # --- helper ------------------------------------------------
        def current_text() -> str:
            return self.decode_token_ids(generated_ids)

        # --- decoding loop ----------------------------------------
        max_steps = 300
        for _ in range(max_steps):
            logits = self.model.get_logits_from_input_ids(input_ids)

            text = current_text()
            allowed_ids = set()

            # ---- STATE 1: start or after comma → expect key or } ----
            if text.strip() == "" or text.strip().endswith(","):
                # allow remaining arg names
                for arg in remaining_args:
                    allowed_ids |= set(self.encode_text(f'"{arg}"'))

                # allow closing brace only if no args left
                if not remaining_args:
                    allowed_ids |= brace_close_ids

            # ---- STATE 2: after key → expect colon -----------------
            elif text.rstrip().endswith('"'):
                allowed_ids |= colon_ids

            # ---- STATE 3: after colon → expect value ----------------
            elif text.rstrip().endswith(":"):
                allowed_ids |= prompt_token_ids

            # ---- STATE 4: after value → expect comma or } -----------
            else:
                # allow comma if more args remain
                if remaining_args:
                    allowed_ids |= comma_ids
                allowed_ids |= brace_close_ids

            # always allow structural tokens
            allowed_ids |= structural_token_ids

            # mask logits
            masked_logits = [-math.inf] * len(logits)
            for tid in allowed_ids:
                if tid < len(logits):
                    masked_logits[tid] = logits[tid]

            if max(masked_logits) == -math.inf:
                raise Exception(
                    f"No valid tokens.\nGenerated so far:\n{text}"
                )

            next_id = masked_logits.index(max(masked_logits))
            input_ids.append(next_id)
            generated_ids.append(next_id)

            text = current_text()
            print(f"ARGS GEN: {text}")

            # ---- update remaining args -----------------------------
            for arg in list(remaining_args):
                if f'"{arg}"' in text:
                    remaining_args.remove(arg)

            # ---- stop condition ------------------------------------
            try:
                parsed = json.loads(text)
                return json.dumps(parsed)
            except json.JSONDecodeError:
                continue

        raise RuntimeError(
            "Failed to generate valid args JSON.\n"
            f"Last output:\n{current_text()}"
        )

    def decode(self) -> List[str]:
        """Generate function calls with constrained decoding.
        For each prompt, uses the LLM to generate a function call
        that matches one of the predefined function strings.
        Returns:
            List of generated function call strings
        Raises:
            Exception: If generation fails or no valid tokens available
        """
        outputs: List[str] = []

        for prompt in self.prompts:
            output = self._decode_single_prompt(prompt)
            output = self._refactor_args(json.loads(output), prompt)
            outputs.append(output)
        return outputs

    def _decode_single_prompt(self, prompt: str) -> str:
        """Decode a single prompt to a function call.
        Args:
            prompt: User prompt to process
        Returns:
            Generated function call string
        Raises:
            Exception: If generation fails
        """
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
            # Get allowed token IDs
            allowed_ids = self.get_allowed_token_ids(generated_ids)
            if not allowed_ids:
                raise Exception(
                    f"No allowed tokens "
                    f"Generated so far: "
                    f"{self.decode_token_ids(generated_ids)}"
                )
            # Mask logits
            masked_logits = [-math.inf] * len(logits)
            for token_id in allowed_ids:
                if token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            # Check if any valid logits exist
            max_logit = max(masked_logits)
            if max_logit == -math.inf:
                raise Exception(
                    f"All allowed token logits are -inf. "
                    f"Allowed IDs: {allowed_ids}"
                )
            # Select best token
            next_token_id = masked_logits.index(max_logit)
            print(
                f"Next token ID: {next_token_id} "
                f"('{self.tokenizer.decode([next_token_id])}')"
            )
            # Append to sequences
            input_ids.append(next_token_id)
            generated_ids.append(next_token_id)

            # Debug output for first few iterations
            # if iteration <= 10:
            #     token_str = self.tokenizer.decode([next_token_id])
            #     print(
            #         f"Iter {iteration}: Token {next_token_id} = "
            #         f"'{token_str}'"
            #     )
            #     print(
            #         f"  Generated: "
            #         f"{self.decode_token_ids(generated_ids)}"
            #     )

            # Check if generated sequence is a substring of exactly one
            is_unique_match, matched_function = self.check_substring_match(
                generated_ids)
            if is_unique_match:
                # Found unique substring match - return the full function
                flag_created = True
                str_from_tokens = self.decode_token_ids(matched_function)
                print(f"Matched function: {str_from_tokens}")
                return str_from_tokens

            # Also check prefix matching (original behavior as fallback)
            prefix_matches = [
                line for line in self.matrix
                if line[:len(generated_ids)] == generated_ids
            ]
            if not prefix_matches:
                # No matches at all - something went wrong
                raise Exception(
                    f"No prefix matches. "
                    f"Generated: {self.decode_token_ids(generated_ids)}"
                )
