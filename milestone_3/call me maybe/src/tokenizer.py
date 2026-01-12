class Tokenizer:
    def __init__(self, vocab: dict[str, int]) -> None:
        self.vocab = vocab
        self.inv_vocab = {v: k for k, v in vocab.items()}

    def encode_text(self, text: str) -> list[int]:
        """Convert text to token IDs using greedy longest-match."""
        token_ids: list[int] = []
        i = 0
        while i < len(text):
            # Try to match longest possible token starting at i
            best_match_len = 0
            best_token_id = None
            
            for length in range(len(text) - i, 0, -1):
                substring = text[i:i+length]
                if substring in self.vocabulary:
                    best_match_len = length
                    best_token_id = self.vocabulary[substring]
                    break
            
            if best_token_id is not None:
                token_ids.append(best_token_id)
                i += best_match_len
            else:
                # If no match found, skip this character (or raise error)
                raise ValueError(f"Cannot tokenize character at position {i}: '{text[i]}' in text '{text}'")
        
        return token_ids

    def decode(self, token_ids: list[int]) -> str:
        tokens = [self.inv_vocab[token_id] for token_id
                  in token_ids if token_id in self.inv_vocab]
        return ' '.join(tokens)

    def convert_ids_to_tokens(self, token_ids: list[int]) -> list[str]:
        tokens = [self.inv_vocab[token_id] for token_id
                  in token_ids if token_id in self.inv_vocab]
        return tokens