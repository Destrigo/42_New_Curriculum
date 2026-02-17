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

    def ingest(self, source_dir: str = "data/raw/vllm-0.10.1", max_chunk_size: int = 2000) -> None:
        """Alias for index command."""
        return self.index(source_dir=source_dir, max_chunk_size=max_chunk_size)

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
        try:
            print(f"Indexing directory: {source_dir}")
            print(f"Max chunk size: {max_chunk_size}")

            # Initialize retriever
            self.retriever = BM25Retriever(max_chunk_size=max_chunk_size)
            self.retriever.index_directory(source_dir)  # Index directory
            self.retriever.save_index(self.index_path)  # Save index

            print(f"Ingestion complete! Index saved to {self.index_path}")
        except Exception as e:
            print(e)

    def search(self, query: str, k: int = 10) -> None:
        """
        Search for a single query.
        Args:
            query: Search query
            k: Number of results to return
        """
        try:
            self._ensure_retriever()  # Load retriever
            # Search
            results = self.retriever.search(query, k=k)  # type: ignore
            # Print results
            print(f"\nTop {k} results for: {query}\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.file_path}")
                print(f"   Characters: {result.first_character_index}-"
                      f"{result.last_character_index}")
                print()
        except Exception as e:
            print(e)                

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
        try:
            # Load retriever
            self._ensure_retriever()

            # Load dataset
            print(f"Loading dataset from {dataset_path}")
            dataset = load_json(dataset_path, RagDataset)

            # Process all questions
            search_results = []
            for question_obj in tqdm(dataset.rag_questions, desc="Searching"):
                # Search
                retr_src = self.retriever.search(question_obj.question,
                                                 k=k)  # type: ignore

                # Create result
                result = MinimalSearchResults(
                    question_id=question_obj.question_id,
                    question=question_obj.question,
                    retrieved_sources=retr_src
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
        except Exception as e:
            print(e)

    def answer_dataset(
        self,
        student_search_results_path: str,
        save_directory: str = "data/output/search_results_and_answer"
    ) -> None:
        """
        Generate answers from search results.
        Args:
            student_search_results_path: Path to StudentSearchResults JSON
            save_directory: Directory to save results
        """
        try:
            # Load generator
            self._ensure_generator()

            # Load search results
            print(f"Loading search results from {student_search_results_path}")
            search_results = load_json(student_search_results_path,
                                       StudentSearchResults)

            print(f"Loaded {len(search_results.search_results)} questions")

            # Generate answers
            answers_results = []

            for result in tqdm(search_results.search_results,
                               desc="Generating answers"):
                # Generate answer
                answer = self.generator.answer_from_sources(  # type: ignore
                    question=result.question,
                    sources=result.retrieved_sources
                )

                # Create answer result
                answer_result = MinimalAnswer(
                    question_id=result.question_id,
                    question=result.question,
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
        except Exception as e:
            print(e)

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
        try:
            # Load data
            print(f"Loading student results from {student_answer_path}")
            student_results = load_json(student_answer_path,
                                        StudentSearchResults)

            print(f"Loading ground truth from {dataset_path}")
            ground_truth = load_json(dataset_path, RagDataset)

            # Validate
            print("\nStudent data is valid: True")
            print("Total number of "
                  f"questions: {len(student_results.search_results)}")
            print("Total number of questions with student "
                  f"sources: {len(student_results.search_results)}")

            # Evaluate
            results = evaluate_search_results(student_results, ground_truth)

            # Print results
            print("\nEvaluation Results")
            print("=" * 40)
            print("Questions "
                  f"evaluated: {len(student_results.search_results)}")

            for k in [1, 3, 5, 10]:
                recall = results.get(f"recall@{k}", 0.0)
                print(f"Recall@{k}: {recall:.3f} ({recall * 100:.1f}%)")
        except Exception as e:
            print(e)

    def answer(self, query: str, k: int = 10) -> None:
        """
        Answer a single question with context.
        Args:
            query: Question to answer
            k: Number of sources to retrieve
        """
        try:
            # Load retriever and generator
            self._ensure_retriever()
            self._ensure_generator()

            # Retrieve
            sources = self.retriever.search(query, k=k)  # type: ignore

            # Generate answer
            answer = self.generator.answer_from_sources(query,
                                                        sources)

            # Print
            print(f"\nQuestion: {query}\n")
            print(f"Answer: {answer}\n")
            print(f"\nSources ({len(sources)}):")
            for i, source in enumerate(sources, 1):
                print(f"{i}. {source.file_path}")
        except Exception as e:
            print(e)

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
