from typing import List, Dict, Set, Tuple
import json
import math
import re
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
        Fill function arguments by extracting values from prompt.
        
        Uses constrained LLM generation to extract each argument value
        individually, then constructs valid JSON programmatically.
        
        This approach guarantees 100% valid JSON output.
        
        Args:
            func_obj: Function object with fn_name, args_names, etc.
            prompt: User's natural language prompt
            
        Returns:
            JSON string with filled arguments
        """
        arg_names = func_obj.get("args_names", [])
        arg_types = func_obj.get("args_types", {})
        
        if not arg_names:
            func_obj["args"] = {}
            return json.dumps(func_obj)
        
        print(f"\n=== Extracting {len(arg_names)} arguments ===")
        
        args_dict = {}
        
        # Extract each argument value one by one
        for arg_name in arg_names:
            arg_type = arg_types.get(arg_name, "string")
            print(f"Extracting '{arg_name}' (type: {arg_type})...")
            
            value = self._extract_single_argument(arg_name, arg_type, prompt)
            args_dict[arg_name] = value
            
            print(f"  → '{value}'")
        
        # Build valid JSON programmatically (guaranteed correct)
        func_obj["args"] = args_dict
        result = json.dumps(func_obj)
        
        print(f"\n✓ Result: {result}\n")
        return result

    def _extract_single_argument(
        self,
        arg_name: str,
        arg_type: str,
        prompt: str
    ) -> str:
        """
        Extract a single argument value from prompt using constrained LLM.
        
        Constrains generation to only tokens that appear in the prompt,
        ensuring values are extracted rather than hallucinated.
        
        Args:
            arg_name: Name of argument to extract
            arg_type: Type of the argument
            prompt: User prompt containing the value
            
        Returns:
            Extracted value as string
        """
        # First try regex-based extraction (fast, reliable)
        regex_value = self._extract_with_regex(arg_name, prompt)
        if regex_value:
            return self._convert_type(regex_value, arg_type)
        
        # Fallback to LLM-based extraction
        return self._extract_with_llm(arg_name, arg_type, prompt)
    
    def _extract_with_regex(self, arg_name: str, prompt: str) -> str:
        """
        Try to extract argument value using regex patterns.
        
        Args:
            arg_name: Name of argument
            prompt: User prompt
            
        Returns:
            Extracted value or empty string if not found
        """
        # Pattern 1: "arg_name: value" or "arg_name = value"
        patterns = [
            rf'{re.escape(arg_name)}\s*[:=]\s*["\']?([^"\'\s,\.]+)["\']?',
            rf'{re.escape(arg_name)}\s+is\s+["\']?([^"\'\s,\.]+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Pattern 2: Extract quoted strings
        quoted = re.findall(r'["\']([^"\']+)["\']', prompt)
        if quoted:
            # Return first quoted string that's not the arg name
            for q in quoted:
                if q.lower() != arg_name.lower():
                    return q
        
        # Pattern 3: Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        if numbers:
            return numbers[0]
        
        return ""
    
    def _extract_with_llm(
        self,
        arg_name: str,
        arg_type: str,
        prompt: str
    ) -> str:
        """
        Extract argument value using LLM with constrained generation.
        
        Constrains generation to only prompt tokens to prevent hallucination.
        
        Args:
            arg_name: Name of argument
            arg_type: Type of argument
            prompt: User prompt
            
        Returns:
            Extracted value
        """
        # Tokenize prompt to get allowed tokens
        prompt_tokens = self.encode_text(prompt)
        prompt_token_set = set(prompt_tokens)
        
        # Build prompt subsequences for smart matching
        prompt_subsequences = self._build_prompt_subsequences(prompt_tokens)
        
        # Create extraction prompt
        extraction_prompt = (
            f"Extract the {arg_name} from this text. "
            f"Return ONLY the {arg_name} value.\n"
            f"Text: {prompt}\n"
            f"{arg_name}:"
        )
        
        input_ids = self.encode_text(extraction_prompt)
        generated_ids: List[int] = []
        
        # Generate value with constraints
        max_tokens = 20
        
        for step in range(max_tokens):
            logits = self.model.get_logits_from_input_ids(input_ids)
            
            # Get allowed tokens
            allowed = self._get_allowed_tokens_for_value(
                generated_ids=generated_ids,
                prompt_token_set=prompt_token_set,
                prompt_subsequences=prompt_subsequences
            )
            
            if not allowed:
                break
            
            # Mask logits
            masked_logits = [-math.inf] * len(logits)
            for tid in allowed:
                if 0 <= tid < len(logits):
                    masked_logits[tid] = logits[tid]
            
            if max(masked_logits) == -math.inf:
                break
            
            next_token_id = masked_logits.index(max(masked_logits))
            next_token_str = self.decode_token_ids([next_token_id])
            
            # Stop on newline or if value is getting too long
            if '\n' in next_token_str or step > 15:
                break
            
            input_ids.append(next_token_id)
            generated_ids.append(next_token_id)
        
        # Decode and clean the value
        value = self.decode_token_ids(generated_ids).strip()
        value = self._clean_extracted_value(value)
        
        return self._convert_type(value, arg_type)
    
    def _build_prompt_subsequences(
        self,
        prompt_tokens: List[int]
    ) -> Dict[Tuple[int, ...], str]:
        """
        Build all contiguous token subsequences from prompt.
        
        Args:
            prompt_tokens: Token IDs from prompt
            
        Returns:
            Dict mapping token tuples to decoded strings
        """
        subsequences = {}
        max_length = 10
        
        for start in range(len(prompt_tokens)):
            for length in range(1, min(max_length + 1, len(prompt_tokens) - start + 1)):
                subseq = tuple(prompt_tokens[start:start + length])
                decoded = self.decode_token_ids(list(subseq))
                if decoded.strip():  # Only meaningful text
                    subsequences[subseq] = decoded
        
        return subsequences
    
    def _get_allowed_tokens_for_value(
        self,
        generated_ids: List[int],
        prompt_token_set: Set[int],
        prompt_subsequences: Dict[Tuple[int, ...], str]
    ) -> List[int]:
        """
        Get allowed tokens for value generation.
        
        Constrains to prompt tokens and uses smart subsequence matching.
        
        Args:
            generated_ids: Tokens generated so far
            prompt_token_set: Set of all prompt token IDs
            prompt_subsequences: Map of token subsequences
            
        Returns:
            List of allowed token IDs
        """
        allowed = prompt_token_set.copy()
        
        # Add newline to allow stopping
        try:
            newline_tokens = self.encode_text('\n')
            allowed.update(newline_tokens)
        except:
            pass
        
        # Smart subsequence matching
        if generated_ids:
            current_tuple = tuple(generated_ids)
            
            # Find subsequences that start with current tokens
            matching = [
                subseq for subseq in prompt_subsequences.keys()
                if len(subseq) >= len(current_tuple) and
                   subseq[:len(current_tuple)] == current_tuple
            ]
            
            if matching:
                # Constrain to tokens that continue these subsequences
                next_candidates = set()
                for subseq in matching:
                    if len(subseq) > len(current_tuple):
                        next_candidates.add(subseq[len(current_tuple)])
                
                if next_candidates:
                    # Only allow continuation tokens
                    allowed = next_candidates
                    # Keep newline for stopping
                    try:
                        newline_tokens = self.encode_text('\n')
                        allowed.update(newline_tokens)
                    except:
                        pass
        
        return list(allowed)
    
    def _clean_extracted_value(self, value: str) -> str:
        """
        Clean up extracted value.
        
        Args:
            value: Raw extracted value
            
        Returns:
            Cleaned value
        """
        # Take only first line
        value = value.split('\n')[0].strip()
        
        # Remove common prefixes
        value = re.sub(
            r'^(value|result|answer|output):\s*',
            '',
            value,
            flags=re.IGNORECASE
        )
        
        # Remove quotes
        value = value.strip('"\'')
        
        # Remove trailing punctuation
        value = value.rstrip('.,!?;: ')
        
        return value.strip()
    
    def _convert_type(self, value: str, arg_type: str) -> any:
        """
        Convert value to appropriate type.
        
        Args:
            value: String value
            arg_type: Target type
            
        Returns:
            Converted value
        """
        if not value:
            return ""
        
        arg_type_lower = str(arg_type).lower()
        
        # Handle numeric types
        if 'float' in arg_type_lower or 'number' in arg_type_lower:
            # Extract number from value
            match = re.search(r'-?\d+\.?\d*', value)
            if match:
                try:
                    return float(match.group())
                except:
                    pass
        
        if 'int' in arg_type_lower:
            match = re.search(r'-?\d+', value)
            if match:
                try:
                    return int(match.group())
                except:
                    pass
        
        # Handle boolean
        if 'bool' in arg_type_lower:
            value_lower = value.lower()
            if value_lower in ['true', 'yes', '1']:
                return True
            if value_lower in ['false', 'no', '0']:
                return False
        
        # Default: return as string
        return value

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
