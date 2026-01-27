"""Vocabulary normalization utilities for tokenization."""
from typing import Dict, Tuple
import json


class VocabularyNormalizer:
    """Normalizes vocabulary by replacing special
    tokens with actual characters.
    This handles common special tokens found in tokenizer vocabularies:
    - Ġ (space in GPT-style tokenizers)
    - Ċ (newline)
    - ĉ (tab)
    - Ā, ā, Ă, ă, etc. (various unicode representations)
    """
    # Common special token replacements
    REPLACEMENTS = {
        'Ġ': ' ',      # GPT-style space
        'Ċ': '\n',     # Newline
        'ĉ': '\t',     # Tab
        '▁': ' ',      # SentencePiece space
        '</w>': '',    # End of word marker
        '<unk>': '',   # Unknown token
        '<s>': '',     # Start token
        '</s>': '',    # End token
        '<pad>': '',   # Padding token
        '<mask>': '',  # Mask token
    }

    @staticmethod
    def normalize_vocabulary(vocab: Dict[str, int]) -> Dict[str, int]:
        """Normalize vocabulary by replacing special tokens.
        Args:
            vocab: Original vocabulary dictionary
        Returns:
            Normalized vocabulary with special tokens replaced
        """
        normalized: Dict[str, int] = {}
        plho = VocabularyNormalizer.REPLACEMENTS
        for token, token_id in vocab.items():
            # Apply known replacements
            normalized_token = token
            for special, replacement in plho.items():
                normalized_token = normalized_token.replace(special,
                                                            replacement)
            # Store normalized version
            normalized[normalized_token] = token_id
        return normalized

    @staticmethod
    def analyze_vocabulary(vocab: Dict[str, int]) -> Dict[str, int]:
        """Analyze vocabulary to find special characters.
        Args:
            vocab: Vocabulary dictionary
        Returns:
            Dictionary of special characters and their counts
        """
        special_chars: Dict[str, int] = {}
        for token in vocab.keys():
            for char in token:
                # Check for non-ASCII or special characters
                if ord(char) > 127 or char in ['\n', '\t', '\r']:
                    special_chars[char] = special_chars.get(char, 0) + 1
        return special_chars

    @staticmethod
    def save_normalized_vocab(
        original_path: str,
        output_path: str
    ) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Load, normalize, and save vocabulary.
        Args:
            original_path: Path to original vocabulary JSON
            output_path: Path to save normalized vocabulary
        Returns:
            Tuple of (original_vocab, normalized_vocab)
        Raises:
            FileNotFoundError: If original vocabulary not found
            json.JSONDecodeError: If vocabulary file is invalid
        """
        # Load original
        with open(original_path, 'r', encoding='utf-8') as f:
            original_vocab = json.load(f)
        # Normalize
        normalized_vocab = VocabularyNormalizer.normalize_vocabulary(
            original_vocab
        )

        # Save normalized
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_vocab, f, ensure_ascii=False, indent=2)
        return original_vocab, normalized_vocab
