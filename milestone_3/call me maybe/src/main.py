from small_llm_model import Small_LLM_Model
import json

# Initialize model
model = Small_LLM_Model()

# You need to load and understand the vocabulary yourself
vocab_path = model.get_path_to_vocabulary_json()
with open(vocab_path, 'r') as f:
    vocabulary = json.load(f)

# The vocabulary maps tokens (strings) to IDs (numbers)
# Example: {"hello": 123, " world": 456, ...}

print(f"Vocabulary has {len(vocabulary)} tokens")
print(f"Sample tokens: {list(vocabulary.items())[:5]}")

# For this simple example, let's manually create some input_ids
# In reality, you'd tokenize your prompt properly
example_input_ids = [123, 456, 789]  # Pretend these are real token IDs

# Get logits from the model
logits = model.get_logits_from_input_ids(example_input_ids)

print(f"Number of logits returned: {len(logits)}")
print(f"These are scores for each possible next token")

# Find the token with highest score
best_token_id = logits.index(max(logits))
print(f"Token ID with highest probability: {best_token_id}")

# To know what this token is, reverse-lookup in vocabulary
# (you'll need to create an inverse mapping: ID -> token)
id_to_token = {v: k for k, v in vocabulary.items()}
if best_token_id in id_to_token:
    best_token = id_to_token[best_token_id]
    print(f"That corresponds to token: '{best_token}'")
