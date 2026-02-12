"""
Evaluation metrics for RAG system.
"""

from src.models import (
    MinimalSource,
    StudentSearchResults,
    RagDataset,
    AnsweredQuestion,
)


def calculate_overlap(
    retrieved: MinimalSource,
    ground_truth: MinimalSource,
    min_overlap: float = 0.05
) -> bool:
    """
    Check if two sources have at least min_overlap (default 5%).
    
    Args:
        retrieved: Retrieved source
        ground_truth: Ground truth source
        min_overlap: Minimum overlap percentage (default 0.05 = 5%)
    
    Returns:
        True if overlap >= min_overlap, False otherwise
    """
    # Must be same file
    if retrieved.file_path != ground_truth.file_path:
        return False
    
    # Calculate intersection
    start = max(
        retrieved.first_character_index,
        ground_truth.first_character_index
    )
    end = min(
        retrieved.last_character_index,
        ground_truth.last_character_index
    )
    
    # Overlap length
    overlap_length = max(0, end - start)
    
    # Ground truth length
    gt_length = (
        ground_truth.last_character_index -
        ground_truth.first_character_index
    )
    
    # Avoid division by zero
    if gt_length == 0:
        return False
    
    # Calculate overlap percentage
    overlap_percentage = overlap_length / gt_length
    
    return overlap_percentage >= min_overlap


def calculate_recall_at_k(
    student_results: StudentSearchResults,
    ground_truth_dataset: RagDataset,
    k: int
) -> float:
    """
    Calculate Recall@k metric.
    
    Args:
        student_results: Student's search results
        ground_truth_dataset: Dataset with ground truth
        k: Number of top results to consider
    
    Returns:
        Average recall@k across all questions
    """
    total_questions = 0
    total_recall = 0.0
    
    # Create mapping of question_id to ground truth
    gt_map = {
        q.question_id: q
        for q in ground_truth_dataset.rag_questions
        if isinstance(q, AnsweredQuestion)
    }
    
    for result in student_results.search_results:
        # Get ground truth for this question
        gt_question = gt_map.get(result.question_id)
        
        if gt_question is None:
            continue
        
        # Only process AnsweredQuestions
        if not isinstance(gt_question, AnsweredQuestion):
            continue
        
        # Take top-k retrieved sources
        top_k_sources = result.retrieved_sources[:k]
        gt_sources = gt_question.sources
        
        # Count how many GT sources were found
        found_count = 0
        for gt_src in gt_sources:
            for retrieved_src in top_k_sources:
                if calculate_overlap(retrieved_src, gt_src):
                    found_count += 1
                    break  # Don't count the same GT source twice
        
        # Calculate recall for this question
        if len(gt_sources) > 0:
            question_recall = found_count / len(gt_sources)
            total_recall += question_recall
            total_questions += 1
    
    # Return average recall
    if total_questions == 0:
        return 0.0
    
    return total_recall / total_questions


def evaluate_search_results(
    student_results: StudentSearchResults,
    ground_truth_dataset: RagDataset
) -> dict[str, float]:
    """
    Evaluate search results at multiple k values.
    
    Args:
        student_results: Student's search results
        ground_truth_dataset: Dataset with ground truth
    
    Returns:
        Dictionary with recall at different k values
    """
    results = {}
    
    for k in [1, 3, 5, 10]:
        recall = calculate_recall_at_k(
            student_results,
            ground_truth_dataset,
            k
        )
        results[f"recall@{k}"] = recall
    
    return results
