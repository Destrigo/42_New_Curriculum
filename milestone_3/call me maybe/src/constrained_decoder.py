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
        """Initialize decoder with prompts and allowed functions."""
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

        # Create tokenizer
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
        
        IMPROVED: Better handling of multiple arguments and quoted strings.
        """
        arg_names = func_obj.get("args_names", [])
        arg_types = func_obj.get("args_types", {})
        
        if not arg_names:
            func_obj["args"] = {}
            return json.dumps(func_obj)
        
        print(f"\n=== Extracting {len(arg_names)} arguments ===")
        print(f"Prompt: {prompt}")
        
        args_dict = {}
        
        # Extract all values at once using smart pattern matching
        extracted_values = self._extract_all_values(prompt, arg_names, arg_types)
        
        # Assign values to arguments
        for i, arg_name in enumerate(arg_names):
            arg_type = arg_types.get(arg_name, "string")
            
            if i < len(extracted_values):
                value = extracted_values[i]
            else:
                # Fallback: try individual extraction
                value = self._extract_single_value(arg_name, arg_type, prompt)
            
            # Convert to appropriate type
            value = self._convert_type(value, arg_type)
            args_dict[arg_name] = value
            
            print(f"  {arg_name}: {value}")
        
        # Build valid JSON programmatically
        func_obj["args"] = args_dict
        result = json.dumps(func_obj)
        
        print(f"✓ Result: {result}\n")
        return result

    def _extract_all_values(
        self,
        prompt: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> List[str]:
        """
        Extract all argument values from prompt using smart pattern matching.
        
        Returns list of values in order of arg_names.
        """
        values = []
        
        # Strategy 1: Extract quoted strings (for string arguments)
        quoted_strings = re.findall(r"'([^']+)'", prompt)
        if not quoted_strings:
            quoted_strings = re.findall(r'"([^"]+)"', prompt)
        
        # Strategy 2: Extract numbers (for numeric arguments)
        numbers = re.findall(r'\b\d+\.?\d*\b', prompt)
        
        # Strategy 3: Extract words after common patterns
        # Pattern: "arg_name is value" or "arg_name: value"
        pattern_matches = {}
        for arg_name in arg_names:
            patterns = [
                rf'{re.escape(arg_name)}\s+(?:is|:)\s+([^\s,\.]+)',
                rf'(?:the\s+)?{re.escape(arg_name)}(?:\s+is)?\s+([^\s,\.]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    pattern_matches[arg_name] = match.group(1).strip('"\'')
                    break
        
        # Assign values based on argument types and what we found
        quoted_idx = 0
        number_idx = 0
        
        for arg_name in arg_names:
            arg_type = arg_types.get(arg_name, "str")
            arg_type_lower = str(arg_type).lower()
            
            value = ""
            
            # First, check if we have a pattern match for this arg
            if arg_name in pattern_matches:
                value = pattern_matches[arg_name]
            
            # If not, assign based on type
            elif 'float' in arg_type_lower or 'int' in arg_type_lower or 'number' in arg_type_lower:
                # Need a number
                if number_idx < len(numbers):
                    value = numbers[number_idx]
                    number_idx += 1
            
            elif 'str' in arg_type_lower or 'string' in arg_type_lower:
                # Need a string
                if quoted_idx < len(quoted_strings):
                    value = quoted_strings[quoted_idx]
                    quoted_idx += 1
            
            # If still no value, try to extract from prompt based on position
            if not value:
                value = self._extract_by_position(prompt, arg_name, arg_type)
            
            values.append(value)
        
        return values

    def _extract_by_position(
        self,
        prompt: str,
        arg_name: str,
        arg_type: str
    ) -> str:
        """
        Extract value by analyzing prompt structure and position.
        """
        arg_type_lower = str(arg_type).lower()
        
        # Common patterns in function calling prompts
        patterns = [
            # "what is X of A and B"
            r'(?:sum|product|difference)\s+of\s+(\S+)\s+and\s+(\S+)',
            # "X the string 'value'"
            r'(?:reverse|greet|process)\s+(?:the\s+)?(?:string\s+)?["\']([^"\']+)["\']',
            # "substitute X with Y in Z"
            r'substitute\s+(?:the\s+)?(\S+)\s+(?:with|in)\s+(\S+)',
            # "replace X in Y with Z"
            r'replace\s+(?:all\s+)?(\S+)\s+in\s+["\']([^"\']+)["\']\s+with\s+(\S+)',
            # "is X an Y"
            r'is\s+(\d+)\s+an?\s+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                # Return first captured group that makes sense
                for group in match.groups():
                    if group and group.strip():
                        return group.strip('"\'')
        
        # Fallback: extract words
        words = prompt.split()
        filtered = [w for w in words if len(w) > 1 and w.lower() not in 
                   ['the', 'a', 'an', 'is', 'are', 'of', 'and', 'with', 'in', 'to', 'for']]
        
        if filtered:
            if 'int' in arg_type_lower or 'float' in arg_type_lower:
                # Return first number
                for word in filtered:
                    if re.match(r'^\d+\.?\d*$', word):
                        return word
            else:
                # Return first non-number
                for word in filtered:
                    if not re.match(r'^\d+\.?\d*$', word):
                        return word.strip('"\'')
        
        return ""

    def _extract_single_value(
        self,
        arg_name: str,
        arg_type: str,
        prompt: str
    ) -> str:
        """
        Extract a single value using LLM with constrained generation.
        
        This is the fallback when regex extraction fails.
        """
        # Try regex patterns specific to this argument
        patterns = [
            rf'{re.escape(arg_name)}\s*[:=]\s*["\']?([^"\'\s,]+)["\']?',
            rf'{re.escape(arg_name)}\s+is\s+["\']?([^"\'\s,]+)["\']?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1).strip('"\'')
        
        # Fallback to LLM extraction
        prompt_tokens = self.encode_text(prompt)
        prompt_token_set = set(prompt_tokens)
        prompt_subsequences = self._build_prompt_subsequences(prompt_tokens)
        
        extraction_prompt = (
            f"Extract {arg_name} from: {prompt}\n"
            f"{arg_name}:"
        )
        
        input_ids = self.encode_text(extraction_prompt)
        generated_ids: List[int] = []
        
        max_tokens = 15
        
        for step in range(max_tokens):
            logits = self.model.get_logits_from_input_ids(input_ids)
            
            allowed = self._get_allowed_tokens_for_value(
                generated_ids=generated_ids,
                prompt_token_set=prompt_token_set,
                prompt_subsequences=prompt_subsequences
            )
            
            if not allowed:
                break
            
            masked_logits = [-math.inf] * len(logits)
            for tid in allowed:
                if 0 <= tid < len(logits):
                    masked_logits[tid] = logits[tid]
            
            if max(masked_logits) == -math.inf:
                break
            
            next_token_id = masked_logits.index(max(masked_logits))
            next_token_str = self.decode_token_ids([next_token_id])
            
            if '\n' in next_token_str or step > 10:
                break
            
            input_ids.append(next_token_id)
            generated_ids.append(next_token_id)
        
        value = self.decode_token_ids(generated_ids).strip()
        return self._clean_value(value)
    
    def _build_prompt_subsequences(
        self,
        prompt_tokens: List[int]
    ) -> Dict[Tuple[int, ...], str]:
        """Build all contiguous token subsequences from prompt."""
        subsequences = {}
        max_length = 10
        
        for start in range(len(prompt_tokens)):
            for length in range(1, min(max_length + 1, len(prompt_tokens) - start + 1)):
                subseq = tuple(prompt_tokens[start:start + length])
                decoded = self.decode_token_ids(list(subseq))
                if decoded.strip():
                    subsequences[subseq] = decoded
        
        return subsequences
    
    def _get_allowed_tokens_for_value(
        self,
        generated_ids: List[int],
        prompt_token_set: Set[int],
        prompt_subsequences: Dict[Tuple[int, ...], str]
    ) -> List[int]:
        """Get allowed tokens for value generation."""
        allowed = prompt_token_set.copy()
        
        try:
            newline_tokens = self.encode_text('\n')
            allowed.update(newline_tokens)
        except:
            pass
        
        if generated_ids:
            current_tuple = tuple(generated_ids)
            matching = [
                subseq for subseq in prompt_subsequences.keys()
                if len(subseq) >= len(current_tuple) and
                   subseq[:len(current_tuple)] == current_tuple
            ]
            
            if matching:
                next_candidates = set()
                for subseq in matching:
                    if len(subseq) > len(current_tuple):
                        next_candidates.add(subseq[len(current_tuple)])
                
                if next_candidates:
                    allowed = next_candidates
                    try:
                        newline_tokens = self.encode_text('\n')
                        allowed.update(newline_tokens)
                    except:
                        pass
        
        return list(allowed)
    
    def _clean_value(self, value: str) -> str:
        """Clean up extracted value."""
        value = value.split('\n')[0].strip()
        value = re.sub(r'^(value|result|answer|output):\s*', '', value, flags=re.IGNORECASE)
        value = value.strip('"\'')
        value = value.rstrip('.,!?;: ')
        return value.strip()
    
    def _convert_type(self, value: str, arg_type: str) -> any:
        """Convert value to appropriate type."""
        if not value:
            return ""
        
        arg_type_lower = str(arg_type).lower()
        
        if 'float' in arg_type_lower or 'number' in arg_type_lower:
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
        
        if 'bool' in arg_type_lower:
            value_lower = value.lower()
            if value_lower in ['true', 'yes', '1']:
                return True
            if value_lower in ['false', 'no', '0']:
                return False
        
        return value

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