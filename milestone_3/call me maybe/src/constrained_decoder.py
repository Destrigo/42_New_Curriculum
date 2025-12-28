from __future__ import annotations

from typing import List, Dict, Set
import math
import json

from llm_sdk.small_llm_model import Small_LLM_Model
from fsm import JSONFSM, State


class ConstrainedDecoder:
    """
    Token-by-token constrained decoder using an FSM.
    
    This decoder masks invalid tokens at each step based on:
    - FSM state (JSON structure)
    - Schema constraints (valid functions and arguments)
    """

    def __init__(self, llm: Small_LLM_Model, fsm: JSONFSM):
        self.llm = llm
        self.fsm = fsm

        # Load and cache vocabulary
        vocab_path = llm.get_path_to_vocabulary_json()
        self.id_to_token: Dict[int, str] = self._load_vocab(vocab_path)
        self.token_to_id: Dict[str, int] = {
            tok: idx for idx, tok in self.id_to_token.items()
        }
        
        # Build reverse lookup for multi-char tokens
        self.tokens_by_content: Dict[str, List[int]] = {}
        for token_id, token_str in self.id_to_token.items():
            if token_str not in self.tokens_by_content:
                self.tokens_by_content[token_str] = []
            self.tokens_by_content[token_str].append(token_id)

    # ------------------------------------------------------

    def _load_vocab(self, path: str) -> Dict[int, str]:
        """Load vocabulary from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # HF vocab.json is token -> id, we invert it
        return {int(v): k for k, v in raw.items()}

    # ------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a complete JSON object using constrained decoding.
        
        Args:
            prompt: The natural language prompt
            max_tokens: Maximum tokens to generate (safety limit)
            
        Returns:
            Complete JSON string
        """
        # Start with the prompt as context
        input_ids: List[int] = self.llm._encode(prompt)[0].tolist()
        output_tokens: List[str] = []
        
        steps = 0
        while self.fsm.state != State.END and steps < max_tokens:
            steps += 1
            
            # Get logits from the model
            logits = self.llm.get_logits_from_input_ids(input_ids)
            
            # Get allowed tokens from FSM
            allowed_strings = self.fsm.allowed_tokens()
            
            if not allowed_strings:
                raise RuntimeError(
                    f"No allowed tokens at state {self.fsm.state}"
                )
            
            # Select best valid token
            token_id, token_str = self._select_token(logits, allowed_strings)
            
            # Advance FSM with the selected token
            self.fsm.advance(token_str)
            
            # Append to context and output
            input_ids.append(token_id)
            output_tokens.append(token_str)
        
        if self.fsm.state != State.END:
            raise RuntimeError(
                f"Generation exceeded max_tokens ({max_tokens}) "
                f"without reaching END state"
            )
        
        return "".join(output_tokens)

    # ------------------------------------------------------

    def _select_token(
        self,
        logits: List[float],
        allowed_strings: Set[str]
    ) -> tuple[int, str]:
        """
        Mask logits and select the highest-scoring valid token.
        
        Args:
            logits: Raw logits for all tokens in vocabulary
            allowed_strings: Set of allowed string values from FSM
            
        Returns:
            Tuple of (token_id, token_string) for the selected token
        """
        best_id = None
        best_logit = -math.inf
        best_str = None
        
        # Check each allowed string
        for allowed_str in allowed_strings:
            # Find token IDs that match this string
            if allowed_str in self.tokens_by_content:
                token_ids = self.tokens_by_content[allowed_str]
            else:
                # String might not be in vocabulary as single token
                # Try to find it character by character
                token_ids = self._find_matching_tokens(allowed_str)
            
            # Pick the best token ID for this allowed string
            for token_id in token_ids:
                if token_id < len(logits):
                    logit = logits[token_id]
                    if logit > best_logit:
                        best_logit = logit
                        best_id = token_id
                        best_str = allowed_str
        
        if best_id is None:
            # Fall back: try partial matching or character-level
            best_id, best_str = self._fallback_selection(logits, allowed_strings)
        
        if best_id is None:
            raise RuntimeError(
                f"No valid token found for state {self.fsm.state}. "
                f"Allowed strings: {allowed_strings}"
            )
        
        return best_id, best_str

    # ------------------------------------------------------

    def _find_matching_tokens(self, target: str) -> List[int]:
        """Find token IDs that could represent the target string."""
        matches = []
        
        # Exact match
        if target in self.tokens_by_content:
            return self.tokens_by_content[target]
        
        # Partial matches (tokens that start with target or vice versa)
        for token_str, token_ids in self.tokens_by_content.items():
            if token_str.startswith(target) or target.startswith(token_str):
                matches.extend(token_ids)
        
        return matches

    # ------------------------------------------------------

    def _fallback_selection(
        self,
        logits: List[float],
        allowed_strings: Set[str]
    ) -> tuple[int, str]:
        """
        Fallback selection when no exact token match is found.
        Tries to find tokens that partially match allowed strings.
        """
        best_id = None
        best_logit = -math.inf
        best_str = None
        
        # Try to find any token that contains or is contained by allowed strings
        for token_id, token_str in self.id_to_token.items():
            if token_id >= len(logits):
                continue
            
            for allowed_str in allowed_strings:
                # Check if token matches or could be part of the allowed string
                if (allowed_str in token_str or 
                    token_str in allowed_str or
                    token_str.strip() == allowed_str):
                    
                    logit = logits[token_id]
                    if logit > best_logit:
                        best_logit = logit
                        best_id = token_id
                        best_str = allowed_str
                        break
        
        return best_id, best_str