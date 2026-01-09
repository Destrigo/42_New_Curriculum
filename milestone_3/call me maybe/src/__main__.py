from .small_llm_model import Small_LLM_Model
import json

# Initialize model
model = Small_LLM_Model()

vocab_path = model.get_path_to_vocabulary_json()
with open(vocab_path) as f:
    vocabulary = json.load(f)

id_to_token = {v: k for k, v in vocabulary.items()}


def encode_text(text: str, vocab: dict) -> list[int]:
    """Convert text to token IDs using greedy longest-match."""
    i = 0
    token_ids = []
    while i < len(text):
        if text[:i] in vocab:
            token_ids.append(vocab[text[:i]])
            text = text[i:]
            i = 1
        else:
            i += 1
    return token_ids


# Start with a prompt
prompt = "who is call me maybe?"
input_ids = encode_text(prompt, vocabulary)  # You need to implement this!

print(f"Starting prompt: {prompt}")
print(f"Token IDs: {input_ids}\n")

# Generate tokens one by one
max_new_tokens = 20
for i in range(max_new_tokens):
    # Get logits from model
    logits = model.get_logits_from_input_ids(input_ids)

    # Select next token (highest probability)
    next_token_id = max(range(len(logits)), key=lambda i: logits[i])

    # Add to sequence
    input_ids.append(next_token_id)

    # Get the token text
    next_token_text = id_to_token.get(next_token_id, "<UNKNOWN>")

    print(f"Step {i+1}:")
    print(f"  Token ID: {next_token_id}")
    print(f"  Token text: {repr(next_token_text)}")

    # Optional: stop if we hit end-of-sequence token
    # (you'll need to find what the EOS token ID is)
    # if next_token_id == EOS_TOKEN_ID:
    #     print("Hit EOS token, stopping")
    #     break

print("\n--- Final Generated Text ---")
# Decode all IDs back to text
generated_text = "".join([id_to_token.get(id, "") for id in input_ids])
print(generated_text.replace("Ġ", " "))
