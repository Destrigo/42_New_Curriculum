"""
Answer generation using Qwen LLM with extractive fallback.
"""

import re
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.models import MinimalSource


def extractive_answer(question: str, context: str, max_length: int = 300) -> str:
    """
    Extract the most relevant passage from context as answer.
    No LLM needed - runs in milliseconds.

    Scores each sentence by counting query term matches,
    then returns the top sentences up to max_length chars.

    Args:
        question: The question to answer
        context: Retrieved context text
        max_length: Max answer length in characters

    Returns:
        Extracted answer string
    """
    if not context.strip():
        return "No relevant context found."

    # Tokenize question into keywords (remove stopwords)
    stopwords = {
        'what', 'which', 'where', 'when', 'who', 'how', 'why',
        'is', 'are', 'was', 'were', 'the', 'a', 'an', 'in', 'on',
        'at', 'to', 'for', 'of', 'and', 'or', 'does', 'do', 'can',
        'used', 'use', 'with', 'by', 'from', 'this', 'that', 'be'
    }
    question_tokens = set(re.findall(r'\w+', question.lower())) - stopwords

    # Split context into sentences
    sentences = re.split(r'(?<=[.!?])\s+|\n', context)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return context[:max_length].strip()

    # Score each sentence by keyword overlap with question
    def score_sentence(sentence: str) -> float:
        tokens = set(re.findall(r'\w+', sentence.lower()))
        if not tokens:
            return 0.0
        overlap = question_tokens & tokens
        return len(overlap) / (len(question_tokens) + 0.001)

    scored = sorted(enumerate(sentences), key=lambda x: score_sentence(x[1]), reverse=True)

    # Pick top sentences until max_length, preserving order
    selected_indices = set()
    total_len = 0
    for idx, sentence in scored:
        if total_len + len(sentence) > max_length:
            break
        selected_indices.add(idx)
        total_len += len(sentence)
        if total_len >= max_length // 2:
            break

    if not selected_indices:
        # Fallback: return first sentences
        return sentences[0][:max_length].strip()

    # Return in original document order
    result = ' '.join(sentences[i] for i in sorted(selected_indices))
    return result.strip()


class AnswerGenerator:
    """Generate answers using Qwen LLM with retrieved context."""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        device: str | None = None,
        use_llm: bool | None = None  # None = auto-detect
    ) -> None:
        """
        Initialize answer generator.

        Args:
            model_name: HuggingFace model name
            device: Device to use ('cuda', 'cpu', or None for auto)
            use_llm: True = always use LLM, False = extractive only,
                     None = auto (use LLM only if GPU available)
        """
        self.model_name = model_name

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Auto-decide: use LLM only if GPU available (CPU too slow)
        if use_llm is None:
            self.use_llm = self.device == "cuda"
        else:
            self.use_llm = use_llm

        if self.use_llm:
            print(f"Loading model {model_name} on {self.device}...")

            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                dtype=torch.float16 if self.device == "cuda" else torch.float32
            ).to(self.device)
            self.model.eval()
            print("Model loaded successfully!")
        else:
            print(f"No GPU detected. Using fast extractive answers (CPU mode).")
            self.tokenizer = None
            self.model = None

    def load_context_from_sources(
        self,
        sources: List[MinimalSource],
        max_context_length: int = 1500
    ) -> str:
        """
        Load context from retrieved sources.

        Args:
            sources: List of MinimalSource
            max_context_length: Maximum context length in characters

        Returns:
            Combined context string
        """
        contexts = []
        total_length = 0

        for source in sources:
            try:
                with open(source.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(source.first_character_index)
                    chunk_content = f.read(
                        source.last_character_index - source.first_character_index
                    )
                if total_length + len(chunk_content) < max_context_length:
                    contexts.append(chunk_content)
                    total_length += len(chunk_content)
                else:
                    break
            except Exception as e:
                print(f"Error loading context from {source.file_path}: {e}")
                continue

        return "\n\n---\n\n".join(contexts)

    def generate_answer(
        self,
        question: str,
        context: str,
        max_new_tokens: int = 100,
    ) -> str:
        """
        Generate answer given question and context.

        Uses LLM if GPU available, otherwise extractive approach.

        Args:
            question: Question to answer
            context: Retrieved context
            max_new_tokens: Maximum tokens to generate (LLM only)

        Returns:
            Generated or extracted answer
        """
        if not self.use_llm:
            return extractive_answer(question, context)

        # LLM path (GPU only)
        prompt = self._create_prompt(question, context)
        messages = [{"role": "user", "content": prompt}]

        try:
            text = self.tokenizer.apply_chat_template(  # type: ignore
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
        except TypeError:
            text = self.tokenizer.apply_chat_template(  # type: ignore
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        inputs = self.tokenizer(  # type: ignore
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(  # type: ignore
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,  # type: ignore
                num_beams=1,
            )

        input_length = inputs["input_ids"].shape[1]
        generated_tokens = outputs[0][input_length:]
        answer = self.tokenizer.decode(  # type: ignore
            generated_tokens,
            skip_special_tokens=True
        ).strip()

        return answer

    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt for the LLM."""
        return f"""Context:
{context}

Question: {question}

Answer:"""

    def answer_from_sources(
        self,
        question: str,
        sources: List[MinimalSource],
        max_context_length: int = 1500,
        max_new_tokens: int = 100
    ) -> str:
        """
        Generate answer from question and retrieved sources.

        Args:
            question: Question to answer
            sources: Retrieved sources
            max_context_length: Maximum context length
            max_new_tokens: Maximum tokens to generate

        Returns:
            Generated answer
        """
        context = self.load_context_from_sources(sources, max_context_length)
        return self.generate_answer(question, context, max_new_tokens)
