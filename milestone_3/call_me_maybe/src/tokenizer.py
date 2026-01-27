from typing import Dict, List


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
        """Convert text to token IDs using greedy longest-match on
        byte-encoded text.
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

    def decode(self, token_ids: List[int],
               skip_special_tokens: bool = False) -> str:
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
