from src.constrained_decoder import Decoder
from src.small_llm_model import Small_LLM_Model
import json

# Load vocabulary
model = Small_LLM_Model()
vocab_path = model.get_path_to_vocabulary_json()

with open(vocab_path, 'r') as f:
    vocab = json.load(f)

# Find special characters
special_chars = {}
for token in vocab.keys():
    for char in token:
        if ord(char) > 127:  # Non-ASCII
            special_chars[char] = special_chars.get(char, 0) + 1

# Print findings
print("Special characters found:")
for char, count in sorted(special_chars.items(), key=lambda x: -x[1]):
    print(f"  '{char}' (U+{ord(char):04X}): {count} occurrences")