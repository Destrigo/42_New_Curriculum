"""
Answer generation using Qwen LLM.
"""

from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.models import MinimalSource


class AnswerGenerator:
    """Generate answers using Qwen LLM with retrieved context."""
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        device: str | None = None
    ) -> None:
        """
        Initialize answer generator.
        
        Args:
            model_name: HuggingFace model name
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.model_name = model_name
        
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"Loading model {model_name} on {self.device}...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)
        
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def load_context_from_sources(
        self,
        sources: List[MinimalSource],
        max_context_length: int = 2000
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
                
                # Add to contexts if we have space
                if total_length + len(chunk_content) < max_context_length:
                    contexts.append(f"## Source: {source.file_path}\n{chunk_content}")
                    total_length += len(chunk_content)
                else:
                    break
            
            except Exception as e:
                print(f"Error loading context from {source.file_path}: {e}")
                continue
        
        return "\n\n".join(contexts)
    
    def generate_answer(
        self,
        question: str,
        context: str,
        max_new_tokens: int = 200,
        temperature: float = 0.7
    ) -> str:
        """
        Generate answer given question and context.
        
        Args:
            question: Question to answer
            context: Retrieved context
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated answer
        """
        # Create prompt
        prompt = self._create_prompt(question, context)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the answer part (after the prompt)
        answer = full_output[len(prompt):].strip()
        
        return answer
    
    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create prompt for the LLM.
        
        Args:
            question: Question to answer
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful assistant that answers questions about code and documentation.

Context:
{context}

Question: {question}

Answer: """
        
        return prompt
    
    def answer_from_sources(
        self,
        question: str,
        sources: List[MinimalSource],
        max_context_length: int = 2000,
        max_new_tokens: int = 200
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
        # Load context
        context = self.load_context_from_sources(sources, max_context_length)
        
        # Generate answer
        answer = self.generate_answer(
            question,
            context,
            max_new_tokens=max_new_tokens
        )
        
        return answer
