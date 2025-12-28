from __future__ import annotations

from typing import List, Dict

import math

from llm_sdk.small_llm_model import Small_LLM_Model
from fsm import JSONFSM, State


class ConstrainedDecoder:
    """
    Token-by-token constrained decoder using an FSM.
    """

    def __init__(self, llm: Small_LLM_Model, fsm: JSONFSM):
        self.llm = llm
        self.fsm = fsm

        # Cache vocabulary once
        vocab_path = llm.get_path_to_vocabulary_json()
        self.id_to_token: Dict[int, str] = self._load_vocab(vocab_path)
        self.token_to_id: Dict[str, int] = {
            tok: idx for idx, tok in self.id_to_token.items()
        }

    # ------------------------------------------------------

    def _load_vocab(self, path: str) -> Dict[int, str]:
        import json

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # HF vocab.json is token -> id, we invert it
        return {int(v): k for k, v in raw.items()}

    # ------------------------------------------------------

    def generate(self, prompt: str) -> str:
        """
        Generate a complete JSON object using constrained decoding.
        """
        input_ids: List[int] = self.llm._encode(prompt)[0].tolist()

        output_tokens: List[str] = []

        while self.fsm.state != State.END:
            logits = self.llm.get_logits_from_input_ids(input_ids)

            allowed = self.fsm.allowed_tokens()
            token_id = self._select_token(logits, allowed)

            token_str = self.id_to_token[token_id]

            self.fsm.advance(token_str)

            input_ids.append(token_id)
            output_tokens.append(token_str)

        return "".join(output_tokens)

    # ------------------------------------------------------

    def _select_token(self,
                      logits: List[float],
                      allowed_tokens: set[str]) -> int:
        """
        Mask logits and select the highest-scoring valid token.
        """
        best_id = None
        best_logit = -math.inf

        for token_str in allowed_tokens:
            if token_str not in self.token_to_id:
                continue

            token_id = self.token_to_id[token_str]
            logit = logits[token_id]

            if logit > best_logit:
                best_logit = logit
                best_id = token_id

        if best_id is None:
            raise RuntimeError(
                f"No valid token found for state {self.fsm.state}"
            )

        return best_id
