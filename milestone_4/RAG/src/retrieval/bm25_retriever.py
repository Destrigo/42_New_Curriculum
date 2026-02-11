"""
BM25-based retrieval system for code and documentation search.
"""

import pickle
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from rank_bm25 import BM25Okapi
from tqdm import tqdm

from src.indexing.chunking import Chunk, AdaptiveChunker
from src.models import MinimalSource


@dataclass
class IndexedChunk:
    """Chunk with additional index metadata."""
    
    chunk: Chunk
    doc_id: int
    tokens: List[str]


class BM25Retriever:
    """BM25-based retrieval system."""
    
    def __init__(self, max_chunk_size: int = 2000) -> None:
        """
        Initialize BM25 retriever.
        
        Args:
            max_chunk_size: Maximum chunk size for chunking
        """
        self.chunker = AdaptiveChunker(max_chunk_size)
        self.indexed_chunks: List[IndexedChunk] = []
        self.bm25: BM25Okapi | None = None
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization.
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of tokens
        """
        # Simple whitespace + lowercase tokenization
        # Could be improved with better tokenizer
        return text.lower().split()
    
    def index_directory(
        self,
        directory: str | Path,
        extensions: List[str] | None = None
    ) -> None:
        """
        Index all files in a directory.
        
        Args:
            directory: Directory to index
            extensions: File extensions to index (default: ['.py', '.md'])
        """
        if extensions is None:
            extensions = ['.py', '.md', '.txt', '.rst']
        
        directory = Path(directory)
        
        # Find all files
        files = []
        for ext in extensions:
            files.extend(directory.rglob(f'*{ext}'))
        
        print(f"Found {len(files)} files to index")
        
        # Chunk all files
        all_chunks: List[Chunk] = []
        for file_path in tqdm(files, desc="Chunking files"):
            chunks = self.chunker.chunk_file(file_path)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks")
        
        # Create indexed chunks with tokens
        self.indexed_chunks = []
        corpus_tokens = []
        
        for doc_id, chunk in enumerate(tqdm(all_chunks, desc="Tokenizing")):
            tokens = self.tokenize(chunk.content)
            
            indexed_chunk = IndexedChunk(
                chunk=chunk,
                doc_id=doc_id,
                tokens=tokens
            )
            
            self.indexed_chunks.append(indexed_chunk)
            corpus_tokens.append(tokens)
        
        # Build BM25 index
        print("Building BM25 index...")
        self.bm25 = BM25Okapi(corpus_tokens)
        print("Indexing complete!")
    
    def search(self, query: str, k: int = 5) -> List[MinimalSource]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of MinimalSource results
        """
        if self.bm25 is None:
            raise ValueError("Index not built. Call index_directory first.")
        
        # Tokenize query
        query_tokens = self.tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top k
        top_k_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]
        
        # Convert to MinimalSource
        results: List[MinimalSource] = []
        for idx in top_k_indices:
            indexed_chunk = self.indexed_chunks[idx]
            chunk = indexed_chunk.chunk
            
            result = MinimalSource(
                file_path=chunk.file_path,
                first_character_index=chunk.first_character_index,
                last_character_index=chunk.last_character_index
            )
            results.append(result)
        
        return results
    
    def save_index(self, save_path: str | Path) -> None:
        """
        Save index to disk.
        
        Args:
            save_path: Path to save index
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        index_data = {
            'indexed_chunks': self.indexed_chunks,
            'bm25': self.bm25
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        print(f"Index saved to {save_path}")
    
    def load_index(self, load_path: str | Path) -> None:
        """
        Load index from disk.
        
        Args:
            load_path: Path to load index from
        """
        load_path = Path(load_path)
        
        if not load_path.exists():
            raise FileNotFoundError(f"Index file not found: {load_path}")
        
        with open(load_path, 'rb') as f:
            index_data = pickle.load(f)
        
        self.indexed_chunks = index_data['indexed_chunks']
        self.bm25 = index_data['bm25']
        
        print(f"Index loaded from {load_path}")
        print(f"Loaded {len(self.indexed_chunks)} chunks")
