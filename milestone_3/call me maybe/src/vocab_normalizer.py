"""Vocabulary normalization utilities for tokenization."""
from typing import Dict, Tuple
import json


class VocabularyNormalizer:
    """Normalizes vocabulary by replacing special tokens with actual characters.
    
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
        
        for token, token_id in vocab.items():
            # Apply known replacements
            normalized_token = token
            for special, replacement in VocabularyNormalizer.REPLACEMENTS.items():
                normalized_token = normalized_token.replace(special, replacement)
            
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


def create_manual_replacements(vocab_path: str) -> Dict[str, str]:
    """Analyze vocabulary and suggest manual replacements.
    
    Args:
        vocab_path: Path to vocabulary JSON file
        
    Returns:
        Dictionary of suggested replacements for special characters
    """
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    
    special_chars = VocabularyNormalizer.analyze_vocabulary(vocab)
    
    print("Special characters found in vocabulary:")
    print("=" * 60)
    
    suggestions: Dict[str, str] = {}
    for char, count in sorted(special_chars.items(), key=lambda x: -x[1]):
        char_repr = repr(char)
        print(f"Character: {char_repr:20} Count: {count:6} Unicode: U+{ord(char):04X}")
        
        # Suggest replacement
        if char == 'Ġ':
            suggestions[char] = ' '
            print(f"  → Suggested: ' ' (space)")
        elif char == 'Ċ':
            suggestions[char] = '\n'
            print(f"  → Suggested: '\\n' (newline)")
        elif char == 'ĉ':
            suggestions[char] = '\t'
            print(f"  → Suggested: '\\t' (tab)")
        elif char == '▁':
            suggestions[char] = ' '
            print(f"  → Suggested: ' ' (space)")
        else:
            print(f"  → Need manual mapping!")
    
    print("=" * 60)
    return suggestions


# Example usage function
def example_normalize_and_test() -> None:
    """Example of how to use the normalizer."""
    from .small_llm_model import Small_LLM_Model
    
    # Get vocabulary path
    model = Small_LLM_Model()
    vocab_path = model.get_path_to_vocabulary_json()
    
    print(f"Original vocabulary path: {vocab_path}")
    
    # Analyze vocabulary
    print("\nAnalyzing vocabulary...")
    suggestions = create_manual_replacements(vocab_path)
    
    # Load and normalize
    print("\nNormalizing vocabulary...")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        original_vocab = json.load(f)
    
    normalized_vocab = VocabularyNormalizer.normalize_vocabulary(original_vocab)
    
    # Save normalized version
    output_path = vocab_path.replace('.json', '_normalized.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(normalized_vocab, f, ensure_ascii=False, indent=2)
    
    print(f"Normalized vocabulary saved to: {output_path}")
    
    # Test tokenization
    print("\nTesting tokenization with normalized vocabulary...")
    from .constrained_decoder import Tokenizer
    
    tokenizer = Tokenizer(normalized_vocab)
    
    test_strings = [
        '{"prompt": "test"}',
        'hello world',
        'fn_add_numbers',
        '{"fn_name": "test", "args": {}}',
    ]
    
    for test_str in test_strings:
        try:
            token_ids = tokenizer.encode(test_str)
            decoded = tokenizer.decode(token_ids)
            match = "✓" if decoded == test_str else "✗"
            print(f"{match} '{test_str}' → {len(token_ids)} tokens → '{decoded}'")
        except ValueError as e:
            print(f"✗ '{test_str}' → FAILED: {e}")


# if __name__ == "__main__":
#     example_normalize_and_test()