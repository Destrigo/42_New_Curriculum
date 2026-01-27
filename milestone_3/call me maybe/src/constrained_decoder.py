# from .small_llm_model import Small_LLM_Model
# import json
# import math


# class Tokenizer:
#     def __init__(self, vocab: dict[str, int]) -> None:
#         self.vocab = vocab
#         self.inv_vocab = {v: k for k, v in vocab.items()}
#         self.vocab_size = len(vocab)
#         # print(self.vocab)

#     def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
#         """Convert text to token IDs using greedy longest-match."""
#         token_ids: list[int] = []
#         i = 0
#         while i < len(text):
#             # Try to match longest possible token starting at i
#             best_match_len = 0
#             best_token_id = None

#             for length in range(len(text) - i, 0, -1):
#                 substring = text[i:i+length]
#                 if substring in self.vocab:
#                     best_match_len = length
#                     best_token_id = self.vocab[substring]
#                     break

#             if best_token_id is not None:
#                 token_ids.append(best_token_id)
#                 i += best_match_len
#                 print(token_ids)
#             # else:
#             #     # If no match found, raise error
#             #     raise ValueError("Cannot tokenize character at"
#             #                      f"position {i}: '{text[i]}' in text '{text}'")

#         return token_ids

#     def decode(self, token_ids: list[int]) -> str:
#         """Decode token IDs back to text - concatenate without spaces"""
#         tokens = [self.inv_vocab[token_id] for token_id in
#                   token_ids if token_id in self.inv_vocab]
#         return ''.join(tokens)

#     def convert_ids_to_tokens(self, token_ids: list[int]) -> list[str]:
#         """Convert token IDs to token strings"""
#         tokens = [self.inv_vocab[token_id] for token_id
#                   in token_ids if token_id in self.inv_vocab]
#         return tokens


# class Decoder:
#     """Decoder representation"""
#     def __init__(self,
#                  prompts: list[str],
#                  functions: list[str]) -> None:
#         self.prompts = prompts
#         self.functions = functions
#         self.model = Small_LLM_Model()

#         # get vocabulary and id_to_token mapping
#         vocab_path = self.model.get_path_to_vocabulary_json()
#         with open(vocab_path) as f:
#             self.vocabulary: dict[str, int] = json.load(f)
#         self.tokenizer = Tokenizer(self.vocabulary)
#         self.matrix = self.build_allowed_token_matrix(functions)
#         self.general_prompt = ("Recreate one of the following functions"
#                                "based on the prompt given at the end: ")
#         for func in self.functions:
#             self.general_prompt += func

#     def build_allowed_token_matrix(self,
#                                    functions: list[str]
#                                    ) -> list[list[int]]:
#         """
#         Build a matrix where each row corresponds to the token IDs
#         of a function string.
#         """

#         matrix: list[list[int]] = []
#         for func in functions:
#             matrix.append(self.encode_text(func))
#         return matrix

#     def get_allowed_token_ids(self, generated_ids: list[int]) -> list[int]:
#         """
#         Docstring for get_allowed_token_ids
#         :param self: Description
#         :param id: Description
#         :type id: int
#         :return: Description
#         :rtype: list[int]
#         """
#         allowed = []
#         prefix_len = len(generated_ids)
#         for line in self.matrix:
#             if line[:prefix_len] == generated_ids and len(line) > prefix_len:
#                 allowed.append(line[prefix_len])
#         return allowed

#     def encode_text(self, text: str) -> list[int]:
#         """Convert text to token IDs using the model's tokenizer."""
#         return self.tokenizer.encode(text, add_special_tokens=False)

#     def decode_token_id(self, token_id: int) -> str:
#         """takes logits give back dictionary equiv."""
#         return self.tokenizer.convert_ids_to_tokens([token_id])[0]

#     def get_token_string(self, token_id: int) -> str:
#         """Gets logits give back human string."""
#         return self.tokenizer.decode([token_id])

#     def decode(self) -> list[list[int]]:
#         """Generate JSON function calls with constrained decoding"""
#         # to create and return
#         logits_matrix: list[str] = []
#         flag_created: bool = False
#         for prompt in self.prompts:
#             i = 0
#             flag_created = False
#             final_prompt = self.general_prompt + prompt
#             input_ids = self.encode_text(final_prompt)
#             generated_ids: list[int] = []
#             while flag_created is False:
#                 logits = self.model.get_logits_from_input_ids(input_ids)
#                 allowed_ids = self.get_allowed_token_ids(generated_ids)
#                 masked_logits = [-math.inf] * len(logits)
#                 for token_id in allowed_ids:
#                     masked_logits[token_id] = float(logits[token_id])
#                 next_token_id = masked_logits.index(max(masked_logits))
#                 input_ids.append(next_token_id)
#                 generated_ids.append(next_token_id)
#                 # print(self.get_token_string(next_token_id))
#                 prefix_matches = [line for line in self.matrix
#                                   if line[:len(generated_ids)]
#                                   == generated_ids]
#                 if len(prefix_matches) == 1:
#                     # Full line matched
#                     flag_created = True
#                     str_from_logits = ""
#                     for int_token in prefix_matches[0]:
#                         str_from_logits += self.tokenizer.decode(
#                             int_token)
#                     logits_matrix.append(str_from_logits)
#                 i += 1
#         return logits_matrix
"""Decoder module for constrained decoding with LLM."""
from typing import List, Dict, Any
import json
import math
from .small_llm_model import Small_LLM_Model


class Tokenizer:
    """Custom tokenizer using vocabulary JSON with byte-level encoding.
    
    This tokenizer handles the byte-level BPE encoding used by GPT-2/Qwen,
    where text is first converted to bytes, then those bytes are encoded
    using special unicode characters.
    """
    
    def __init__(self, vocab: Dict[str, int]) -> None:
        """Initialize tokenizer with vocabulary.
        
        Args:
            vocab: Dictionary mapping token strings to token IDs
        """
        self.vocab = vocab
        self.inv_vocab = {v: k for k, v in vocab.items()}
        self.vocab_size = len(vocab)
        
        # Create byte encoder (text → special unicode for BPE)
        self.byte_encoder = self._bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
    
    @staticmethod
    def _bytes_to_unicode() -> Dict[int, str]:
        """Create byte-to-unicode mapping (GPT-2 style).
        
        Returns:
            Dictionary mapping byte values to unicode characters
        """
        bs = (
            list(range(ord("!"), ord("~") + 1))
            + list(range(ord("¡"), ord("¬") + 1))
            + list(range(ord("®"), ord("ÿ") + 1))
        )
        cs = bs[:]
        n = 0
        for b in range(2**8):
            if b not in bs:
                bs.append(b)
                cs.append(2**8 + n)
                n += 1
        return {b: chr(c) for b, c in zip(bs, cs)}
    
    def _encode_bytes(self, text: str) -> str:
        """Convert text to byte-level representation.
        
        Args:
            text: Text to encode
            
        Returns:
            Text with bytes encoded as special unicode characters
        """
        return ''.join(self.byte_encoder[b] for b in text.encode('utf-8'))
    
    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        """Convert text to token IDs using greedy longest-match on byte-encoded text.
        
        Args:
            text: Text to encode
            add_special_tokens: Whether to add special tokens (ignored)
            
        Returns:
            List of token IDs
            
        Raises:
            ValueError: If text cannot be fully tokenized
        """
        # First convert text to byte-level representation
        byte_text = self._encode_bytes(text)
        
        token_ids: List[int] = []
        i = 0
        
        while i < len(byte_text):
            best_match_len = 0
            best_token_id = None
            
            # Try to match longest possible token starting at i
            for length in range(min(len(byte_text) - i, 100), 0, -1):
                substring = byte_text[i:i+length]
                if substring in self.vocab:
                    best_match_len = length
                    best_token_id = self.vocab[substring]
                    break
            
            if best_token_id is not None:
                token_ids.append(best_token_id)
                i += best_match_len
            else:
                raise ValueError(
                    f"Cannot tokenize at position {i}: "
                    f"byte_text='{byte_text[i:i+10]}...' "
                    f"original='{text[:50]}...'"
                )
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = False) -> str:
        """Decode token IDs back to text.
        
        Args:
            token_ids: List of token IDs to decode
            skip_special_tokens: Whether to skip special tokens (ignored)
            
        Returns:
            Decoded text string
        """
        # Get tokens
        tokens = [
            self.inv_vocab[token_id] 
            for token_id in token_ids 
            if token_id in self.inv_vocab
        ]
        
        # Join tokens
        byte_text = ''.join(tokens)
        
        # Decode bytes back to text
        try:
            text_bytes = bytearray([
                self.byte_decoder[c] for c in byte_text
            ])
            return text_bytes.decode('utf-8', errors='replace')
        except (KeyError, UnicodeDecodeError):
            # Fallback: return as-is
            return byte_text
    
    def convert_ids_to_tokens(self, token_ids: List[int]) -> List[str]:
        """Convert token IDs to token strings.
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            List of token strings
        """
        return [
            self.inv_vocab[token_id] 
            for token_id in token_ids 
            if token_id in self.inv_vocab
        ]


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
                print(
                    f"Function {i+1} tokenized to {len(token_ids)} tokens: "
                    f"{func[:50]}..."
                )
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
    
    def check_substring_match(self, generated_ids: List[int]) -> tuple[bool, List[int]]:
        """Check if generated sequence is a substring of exactly one function.
        
        Args:
            generated_ids: List of token IDs generated so far
            
        Returns:
            Tuple of (is_unique_match, matched_function_ids)
            - is_unique_match: True if exactly one function contains this substring
            - matched_function_ids: The full token sequence of the matched function
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
        
        for prompt_idx, prompt in enumerate(self.prompts):
            try:
                print(f"\n{'='*60}")
                print(f"Processing prompt {prompt_idx+1}/{len(self.prompts)}: {prompt}")
                print(f"{'='*60}")
                
                output = self._decode_single_prompt(prompt)
                outputs.append(output)
                
            except Exception as e:
                raise Exception(
                    f"Failed to decode prompt {prompt_idx+1} "
                    f"('{prompt}'): {str(e)}"
                ) from e
        
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
        max_iterations = 1000
        iteration = 0
        
        while not flag_created and iteration < max_iterations:
            iteration += 1
            
            try:
                # Get logits from model (using public method only)
                logits = self.model.get_logits_from_input_ids(input_ids)
                
                # Get allowed token IDs
                allowed_ids = self.get_allowed_token_ids(generated_ids)
                
                if not allowed_ids:
                    raise Exception(
                        f"No allowed tokens at iteration {iteration}. "
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
                
                # Append to sequences
                input_ids.append(next_token_id)
                generated_ids.append(next_token_id)
                
                # Debug output for first few iterations
                if iteration <= 10:
                    token_str = self.tokenizer.decode([next_token_id])
                    print(
                        f"Iter {iteration}: Token {next_token_id} = "
                        f"'{token_str}'"
                    )
                    print(
                        f"  Generated: "
                        f"{self.decode_token_ids(generated_ids)}"
                    )
                
                # Check if generated sequence is a substring of exactly one function
                is_unique_match, matched_function = self.check_substring_match(generated_ids)
                
                if is_unique_match:
                    # Found unique substring match - return the full function
                    flag_created = True
                    str_from_tokens = self.decode_token_ids(matched_function)
                    print(f"\n✓ Substring match found in {iteration} iterations")
                    print(f"Generated substring: {self.decode_token_ids(generated_ids)}")
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
                        f"No prefix matches at iteration {iteration}. "
                        f"Generated: {self.decode_token_ids(generated_ids)}"
                    )
                    
            except Exception as e:
                raise Exception(
                    f"Error at iteration {iteration}: {str(e)}"
                ) from e
        
        raise Exception(
            f"Max iterations ({max_iterations}) reached for prompt"
        )