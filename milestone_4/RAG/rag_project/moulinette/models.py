from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import uuid
from enum import Enum


# ---------------------------------------------------------------------------- #
#                                    Source                                    #
# ---------------------------------------------------------------------------- #
class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


# ---------------------------------------------------------------------------- #
#                                   Question                                   #
# ---------------------------------------------------------------------------- #


class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    sources: List[MinimalSource]
    answer: str


# ---------------------------------------------------------------------------- #
#                               Dataset Retrieval                              #
# ---------------------------------------------------------------------------- #


class RagDataset(BaseModel):
    rag_questions: List[AnsweredQuestion] | List[UnansweredQuestion]


# ---------------------------------------------------------------------------- #
#                               Students Outputs                               #
# ---------------------------------------------------------------------------- #

# ------------------------------ search results ------------------------------ #

class MinimalSearchResults(BaseModel):
    question_id: str
    retrieved_sources: List[MinimalSource]

class MinimalAnswer(MinimalSearchResults):
    answer: str


# ------------------------------- dataset level ------------------------------ #

class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]
