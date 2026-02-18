from moulinette.models import (
    StudentSearchResultsAndAnswer,
    StudentSearchResults,
    RagDataset,
)
import json
from pathlib import Path
import fire
from moulinette.validate_student_data import validate_student_data
from moulinette.evaluate_retrieval import calculate_recall_at_k_on_dataset

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_student_search_results(student_search_results_path: str):
    return StudentSearchResults(**load_json(student_search_results_path))


def load_student_answers(student_answers_path: str):
    return StudentSearchResultsAndAnswer(**load_json(student_answers_path))


def load_dataset_questions_and_answers(dataset_path: str):
    return RagDataset(**load_json(dataset_path))


class Moulinette:
    def evaluate_student_search_results(
        self, 
        student_answer_path: str, 
        dataset_path: str
    ):
        student_search_results = load_student_search_results(student_answer_path)

        max_context_length = 2000
        k = 10

        is_valid = validate_student_data(
            student_search_results, 
            max_context_length=max_context_length, 
            k=k
        )
        if not is_valid:
            print("Student search results are not valid")
            return False

        recall_results = calculate_recall_at_k_on_dataset(
            student_search_results, 
            load_dataset_questions_and_answers(dataset_path),
            minimal_iou_threshold=0.01,
            k_values=[1, 3, 5, 10],
        )
        print(recall_results)
        if recall_results["recall@5"] < 0.75:
            print("Student search results are not valid")
            return False
        return True

    def evaluate_student_answers(self, student_answer_path: str):
        pass

if __name__ == "__main__":
    fire.Fire(Moulinette)