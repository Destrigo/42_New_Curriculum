from typing import List, Dict
from moulinette.models import (
    MinimalSource,
    StudentSearchResults,
    RagDataset,
)
from pydantic import BaseModel


def compare_sources(s1: MinimalSource, s2: MinimalSource) -> float:
    if s1.file_path != s2.file_path:
        return 0.0

    assert s1.first_character_index != -1
    assert s1.last_character_index != -1
    assert s2.first_character_index != -1
    assert s2.last_character_index != -1

    s1_len = s1.last_character_index - s1.first_character_index
    s2_len = s2.last_character_index - s2.first_character_index

    s1_intersection_s2 = max(
        0,
        (
            min(s1.last_character_index, s2.last_character_index)
            - max(s1.first_character_index, s2.first_character_index)
        ),
    )

    s2_intersection_s1 = max(
        0,
        (
            min(s2.last_character_index, s1.last_character_index)
            - max(s2.first_character_index, s1.first_character_index)
        ),
    )

    return max(s1_intersection_s2, s2_intersection_s1) / (
        s1_len + s2_len - max(s1_intersection_s2, s2_intersection_s1)
    )


def calculate_recall_at_k_for_one_question(
    pred_sources: List[MinimalSource],
    true_sources: List[MinimalSource],
    minimal_iou_threshold: float = 0.05,
) -> float:
    """
    Calculate recall@k by checking if any search result contains lines from cited sources.

    Returns 1.0 if at least one cited source is found, 0.0 otherwise.
    """
    if not true_sources:
        return 1.0
    if not pred_sources:
        return 0.0

    # Create set of cited source locations for efficient lookup
    found_sources = {i: 0 for i in range(len(true_sources))}
    for i, true_source in enumerate(true_sources):
        for pred_source in pred_sources:
            if compare_sources(true_source, pred_source) > minimal_iou_threshold:
                found_sources[i] += 1.
                break

    return sum(found_sources.values()) / len(true_sources)


class EvalObject(BaseModel):
    true_sources: List[MinimalSource]
    pred_sources: List[MinimalSource]

def calculate_recall_at_k_on_dataset(
    student_search_results: StudentSearchResults,
    rag_dataset: RagDataset,
    minimal_iou_threshold: float = 0.05,
    k_values: List[int] = [1, 3, 5, 10],
) -> float:

    total_questions = len(rag_dataset.rag_questions)
    eval_objects: Dict[str, EvalObject] = {}

    for question in rag_dataset.rag_questions:
        eval_objects[question.question_id] = EvalObject(
            true_sources=question.sources,
            pred_sources=[]
        )

    for student_search_result in student_search_results.search_results:
        eval_objects[student_search_result.question_id].pred_sources = student_search_result.retrieved_sources

    print(f"Total number of questions: {total_questions}")
    print(f"Total number of questions with sources: {len(eval_objects)}")
    print(f"Total number of questions with student sources: {len([eval_object for eval_object in eval_objects.values() if eval_object.pred_sources])}")

    results = {f"recall@{k}": [] for k in k_values}
    for eval_object in eval_objects.values():
        for k in k_values:
            recall = calculate_recall_at_k_for_one_question(
                eval_object.pred_sources[:k],
                eval_object.true_sources,
                minimal_iou_threshold
            )
            results[f"recall@{k}"].append(recall)

    avg_results = {}
    for k in k_values:
        scores = results[f"recall@{k}"]
        avg_recall = sum(scores) / len(scores) if scores else 0.0
        avg_results[f"recall@{k}"] = avg_recall

    # Display results
    print(f"\n🎯 Evaluation Results")
    print("=" * 40)
    print(f"📊 Questions evaluated: {total_questions}")

    for k in k_values:
        recall = avg_results[f"recall@{k}"]
        print(f"📈 Recall@{k}: {recall:.3f} ({recall*100:.1f}%)")

    return avg_results
