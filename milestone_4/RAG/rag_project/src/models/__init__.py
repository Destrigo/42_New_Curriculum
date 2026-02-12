"""
Pydantic models for RAG system data structures.
"""

import uuid
from typing import List, Union
from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """Represents a source location in a file."""
    
    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """Represents a question without ground truth."""
    
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """Represents a question with ground truth sources and answer."""
    
    sources: List[MinimalSource]
    answer: str
    difficulty: str | None = None
    is_valid: bool | None = None


class RagDataset(BaseModel):
    """Represents a dataset of RAG questions."""
    
    rag_questions: List[Union[AnsweredQuestion, UnansweredQuestion]]


class MinimalSearchResults(BaseModel):
    """Represents search results for a single question."""
    
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Represents search results with generated answer."""
    
    answer: str


class StudentSearchResults(BaseModel):
    """Represents complete search results for a dataset."""
    
    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    """Represents search results with answers for a dataset."""
    
    search_results: List[MinimalAnswer]  # type: ignore[assignment]
