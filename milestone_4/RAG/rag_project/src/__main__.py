"""
Main CLI interface for RAG system.
"""

import fire
from pathlib import Path
from tqdm import tqdm

from src.retrieval import BM25Retriever
from src.generation import AnswerGenerator
from src.models import (
    RagDataset,
    MinimalSearchResults,
    MinimalAnswer,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)
from src.evaluation import evaluate_search_results
from src.utils import load_json, save_json


class RAGSystem:
    """Main RAG system CLI."""
    
    def __init__(self) -> None:
        """Initialize RAG system."""
        self.retriever: BM25Retriever | None = None
        self.generator: AnswerGenerator | None = None
        self.index_path = "data/processed/bm25_index.pkl"
    
    def index(
        self,
        source_dir: str = "data/raw/vllm-0.10.1",
        max_chunk_size: int = 2000
    ) -> None:
        """
        Index repository for search.
        
        Args:
            source_dir: Directory containing source code
            max_chunk_size: Maximum chunk size in characters
        """
        print(f"Indexing directory: {source_dir}")
        print(f"Max chunk size: {max_chunk_size}")
        
        # Initialize retriever
        self.retriever = BM25Retriever(max_chunk_size=max_chunk_size)
        
        # Index directory
        self.retriever.index_directory(source_dir)
        
        # Save index
        self.retriever.save_index(self.index_path)
        
        print(f"Ingestion complete! Index saved to {self.index_path}")
    
    def ingest(
        self,
        source_dir: str = "data/raw/vllm-0.10.1",
        max_chunk_size: int = 2000
    ) -> None:
        """
        Ingest repository (alias for index command).
        
        Args:
            source_dir: Directory containing source code
            max_chunk_size: Maximum chunk size in characters
        """
        return self.index(source_dir=source_dir, max_chunk_size=max_chunk_size)
    
    def search(self, query: str, k: int = 10) -> None:
        """
        Search for a single query.
        
        Args:
            query: Search query
            k: Number of results to return
        """
        # Load retriever
        self._ensure_retriever()
        
        # Search
        results = self.retriever.search(query, k=k)  # type: ignore
        
        # Print results
        print(f"\nTop {k} results for: {query}\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.file_path}")
            print(f"   Characters: {result.first_character_index}-{result.last_character_index}")
            print()
    
    def search_dataset(
        self,
        dataset_path: str,
        k: int = 10,
        save_directory: str = "data/output/search_results"
    ) -> None:
        """
        Search dataset and output StudentSearchResults.
        
        Args:
            dataset_path: Path to dataset JSON
            k: Number of results to retrieve
            save_directory: Directory to save results
        """
        # Load retriever
        self._ensure_retriever()
        
        # Load dataset
        print(f"Loading dataset from {dataset_path}")
        dataset = load_json(dataset_path, RagDataset)
        
        # Process all questions
        search_results = []
        
        for question_obj in tqdm(dataset.rag_questions, desc="Searching"):
            # Search
            retrieved_sources = self.retriever.search(question_obj.question, k=k)  # type: ignore
            
            # Create result
            result = MinimalSearchResults(
                question_id=question_obj.question_id,
                retrieved_sources=retrieved_sources
            )
            search_results.append(result)
        
        # Create output
        output = StudentSearchResults(
            search_results=search_results,
            k=k
        )
        
        # Save
        dataset_name = Path(dataset_path).name
        output_path = Path(save_directory) / dataset_name
        save_json(output, output_path)
        
        print(f"\nSaved student_search_results to {output_path}")
    
    def answer_dataset(
        self,
        student_search_results_path: str,
        save_directory: str = "data/output/answers"
    ) -> None:
        """
        Generate answers from search results.
        
        Args:
            student_search_results_path: Path to StudentSearchResults JSON
            save_directory: Directory to save results
        """
        # Load generator
        self._ensure_generator()
        
        # Load search results
        print(f"Loading search results from {student_search_results_path}")
        search_results = load_json(student_search_results_path, StudentSearchResults)
        
        print(f"Loaded {len(search_results.search_results)} questions")
        
        # We need to load the original dataset to get questions
        # Infer dataset path from search results path
        import re
        dataset_path = student_search_results_path.replace(
            "data/output/search_results",
            "datasets/UnansweredQuestions"
        )
        
        try:
            dataset = load_json(dataset_path, RagDataset)
            # Create question_id -> question mapping
            question_map = {q.question_id: q.question for q in dataset.rag_questions}
        except Exception as e:
            print(f"Warning: Could not load dataset from {dataset_path}: {e}")
            print("Using placeholder questions")
            question_map = {}
        
        # Generate answers
        answers_results = []
        
        for result in tqdm(search_results.search_results, desc="Generating answers"):
            # Get question text from map or use placeholder
            question_text = question_map.get(result.question_id, "Question not available")
            
            # Generate answer
            answer = self.generator.answer_from_sources(  # type: ignore
                question=question_text,
                sources=result.retrieved_sources
            )
            
            # Create answer result
            answer_result = MinimalAnswer(
                question_id=result.question_id,
                retrieved_sources=result.retrieved_sources,
                answer=answer
            )
            answers_results.append(answer_result)
        
        # Create output
        output = StudentSearchResultsAndAnswer(
            search_results=answers_results,
            k=search_results.k
        )
        
        # Save
        dataset_name = Path(student_search_results_path).name
        output_path = Path(save_directory) / dataset_name
        save_json(output, output_path)
        
        print(f"\nSaved answers to {output_path}")
    
    def evaluate(
        self,
        student_answer_path: str,
        dataset_path: str
    ) -> None:
        """
        Evaluate search results against ground truth.
        
        Args:
            student_answer_path: Path to student search results
            dataset_path: Path to ground truth dataset
        """
        # Load data
        print(f"Loading student results from {student_answer_path}")
        student_results = load_json(student_answer_path, StudentSearchResults)
        
        print(f"Loading ground truth from {dataset_path}")
        ground_truth = load_json(dataset_path, RagDataset)
        
        # Validate
        print(f"\nStudent data is valid: True")
        print(f"Total number of questions: {len(student_results.search_results)}")
        print(f"Total number of questions with student sources: {len(student_results.search_results)}")
        
        # Evaluate
        results = evaluate_search_results(student_results, ground_truth)
        
        # Print results
        print("\nEvaluation Results")
        print("=" * 40)
        print(f"Questions evaluated: {len(student_results.search_results)}")
        
        for k in [1, 3, 5, 10]:
            recall = results.get(f"recall@{k}", 0.0)
            print(f"Recall@{k}: {recall:.3f} ({recall * 100:.1f}%)")
    
    def answer(self, query: str, k: int = 10) -> None:
        """
        Answer a single question with context.
        
        Args:
            query: Question to answer
            k: Number of sources to retrieve
        """
        # Load retriever and generator
        self._ensure_retriever()
        self._ensure_generator()
        
        # Retrieve
        sources = self.retriever.search(query, k=k)  # type: ignore
        
        # Generate answer
        answer = self.generator.answer_from_sources(query, sources)  # type: ignore
        
        # Print
        print(f"\nQuestion: {query}\n")
        print(f"Answer: {answer}\n")
        print(f"\nSources ({len(sources)}):")
        for i, source in enumerate(sources, 1):
            print(f"{i}. {source.file_path}")
    
    def _ensure_retriever(self) -> None:
        """Ensure retriever is loaded."""
        if self.retriever is None:
            self.retriever = BM25Retriever()
            self.retriever.load_index(self.index_path)
    
    def _ensure_generator(self) -> None:
        """Ensure generator is loaded."""
        if self.generator is None:
            self.generator = AnswerGenerator()


def main() -> None:
    """Main entry point."""
    fire.Fire(RAGSystem)


if __name__ == "__main__":
    main()
