"""
Intelligent chunking strategies for different file types.
"""

import ast
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a chunk of text with metadata."""
    file_path: str
    content: str
    first_character_index: int
    last_character_index: int
    chunk_type: str = "text"  # "code", "text", "function", "class"


class PythonChunker:
    """Chunks Python code using AST for intelligent splitting."""
    def __init__(self, max_chunk_size: int = 2000) -> None:
        """
        Initialize Python chunker.
        Args:
            max_chunk_size: Maximum chunk size in characters
        """
        self.max_chunk_size = max_chunk_size

    def chunk(self, content: str, file_path: str) -> List[Chunk]:
        """
        Chunk Python code into logical units.
        Args:
            content: Python source code
            file_path: Path to the file
        Returns:
            List of chunks
        """
        chunks: List[Chunk] = []
        try:
            # Parse AST
            tree = ast.parse(content)
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Get source segment
                    start_line = node.lineno - 1
                    if node.end_lineno:
                        end_line = node.end_lineno
                    else:
                        end_line = start_line + 1
                    # Get character indices
                    lines = content.split('\n')
                    start_char = sum(len(line) + 1
                                     for line in lines[:start_line])
                    end_char = sum(len(line) + 1 for line in lines[:end_line])
                    chunk_content = content[start_char:end_char]
                    # If chunk is too large, split it
                    if len(chunk_content) > self.max_chunk_size:
                        # Fall back to simple splitting
                        sub_chunks = self._split_large_chunk(
                            chunk_content,
                            start_char,
                            file_path
                        )
                        chunks.extend(sub_chunks)
                    else:
                        chunk_type = "function" if isinstance(node, ast.FunctionDef) else "class"
                        chunks.append(Chunk(
                            file_path=file_path,
                            content=chunk_content,
                            first_character_index=start_char,
                            last_character_index=end_char,
                            chunk_type=chunk_type
                        ))

            # If no functions/classes found, use simple chunking
            if not chunks:
                chunks = self._simple_chunk(content, file_path)

        except SyntaxError:
            # If parsing fails, fall back to simple chunking
            chunks = self._simple_chunk(content, file_path)
        return chunks

    def _split_large_chunk(
        self,
        content: str,
        start_offset: int,
        file_path: str
    ) -> List[Chunk]:
        """Split a large chunk into smaller pieces."""
        chunks: List[Chunk] = []
        current_pos = 0

        while current_pos < len(content):
            end_pos = min(current_pos + self.max_chunk_size, len(content))

            # Try to break at newline
            if end_pos < len(content):
                newline_pos = content.rfind('\n', current_pos, end_pos)
                if newline_pos > current_pos:
                    end_pos = newline_pos + 1

            chunk_content = content[current_pos:end_pos]
            chunks.append(Chunk(
                file_path=file_path,
                content=chunk_content,
                first_character_index=start_offset + current_pos,
                last_character_index=start_offset + end_pos,
                chunk_type="code"
            ))
            # overlap = 200  # 200 caratteri di overlap
            # current_pos = max(current_pos, end_pos - overlap)
            current_pos = end_pos
        return chunks

    def _simple_chunk(self, content: str, file_path: str) -> List[Chunk]:
        """Simple chunking by size."""
        chunks: List[Chunk] = []
        current_pos = 0

        while current_pos < len(content):
            end_pos = min(current_pos + self.max_chunk_size, len(content))

            # Try to break at newline
            if end_pos < len(content):
                newline_pos = content.rfind('\n', current_pos, end_pos)
                if newline_pos > current_pos:
                    end_pos = newline_pos + 1

            chunk_content = content[current_pos:end_pos]
            chunks.append(Chunk(
                file_path=file_path,
                content=chunk_content,
                first_character_index=current_pos,
                last_character_index=end_pos,
                chunk_type="code"
            ))
            current_pos = end_pos
        return chunks


class TextChunker:
    """Chunks text/markdown files by semantic units."""
    def __init__(self, max_chunk_size: int = 2000) -> None:
        """
        Initialize text chunker.
        Args:
            max_chunk_size: Maximum chunk size in characters
        """
        self.max_chunk_size = max_chunk_size

    def chunk(self, content: str, file_path: str) -> List[Chunk]:
        """
        Chunk text by paragraphs and sections.
        Args:
            content: Text content
            file_path: Path to the file
        Returns:
            List of chunks
        """
        chunks: List[Chunk] = []

        # Try to split by markdown headers first
        if self._is_markdown(file_path):
            chunks = self._chunk_markdown(content, file_path)
        else:
            chunks = self._chunk_paragraphs(content, file_path)
        return chunks

    def _is_markdown(self, file_path: str) -> bool:
        """Check if file is markdown."""
        return Path(file_path).suffix.lower() in ['.md', '.markdown']

    def _chunk_markdown(self, content: str, file_path: str) -> List[Chunk]:
        """Chunk markdown by headers."""
        chunks: List[Chunk] = []
        lines = content.split('\n')

        current_chunk = []
        current_start = 0
        current_pos = 0

        for line in lines:
            line_len = len(line) + 1  # +1 for newline

            # Check if header
            is_header = line.startswith('#')

            # Check if we should start new chunk
            chunk_content = '\n'.join(current_chunk)
            should_break = (
                is_header and
                len(chunk_content) > 0 and
                len(chunk_content) > self.max_chunk_size // 2
            )

            if should_break:
                # Save current chunk
                chunks.append(Chunk(
                    file_path=file_path,
                    content=chunk_content,
                    first_character_index=current_start,
                    last_character_index=current_pos,
                    chunk_type="text"
                ))

                # Start new chunk
                current_chunk = [line]
                current_start = current_pos
            else:
                current_chunk.append(line)

            # Check if chunk is too large
            if len('\n'.join(current_chunk)) > self.max_chunk_size:
                chunks.append(Chunk(
                    file_path=file_path,
                    content='\n'.join(current_chunk),
                    first_character_index=current_start,
                    last_character_index=current_pos + line_len,
                    chunk_type="text"
                ))
                current_chunk = []
                current_start = current_pos + line_len

            current_pos += line_len

        # Add remaining chunk
        if current_chunk:
            chunks.append(Chunk(
                file_path=file_path,
                content='\n'.join(current_chunk),
                first_character_index=current_start,
                last_character_index=current_pos,
                chunk_type="text"
            ))
        return chunks if chunks else self._chunk_paragraphs(content, file_path)

    def _chunk_paragraphs(self, content: str, file_path: str) -> List[Chunk]:
        """Chunk by paragraphs (double newline)."""
        chunks: List[Chunk] = []
        paragraphs = content.split('\n\n')

        current_chunk = []
        current_start = 0
        current_pos = 0

        for para in paragraphs:
            para_len = len(para) + 2  # +2 for double newline

            # Check if adding this paragraph would exceed limit
            combined = '\n\n'.join(current_chunk + [para])

            if len(combined) > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append(Chunk(
                    file_path=file_path,
                    content=chunk_content,
                    first_character_index=current_start,
                    last_character_index=current_pos,
                    chunk_type="text"
                ))

                # Start new chunk
                current_chunk = [para]
                current_start = current_pos
            else:
                current_chunk.append(para)

            current_pos += para_len

        # Add remaining chunk
        if current_chunk:
            chunks.append(Chunk(
                file_path=file_path,
                content='\n\n'.join(current_chunk),
                first_character_index=current_start,
                last_character_index=current_pos,
                chunk_type="text"
            ))
        return chunks


class AdaptiveChunker:
    """Chooses appropriate chunker based on file type."""
    def __init__(self, max_chunk_size: int = 2000) -> None:
        """
        Initialize adaptive chunker.
        Args:
            max_chunk_size: Maximum chunk size in characters
        """
        self.python_chunker = PythonChunker(max_chunk_size)
        self.text_chunker = TextChunker(max_chunk_size)

    def chunk_file(self, file_path: str | Path) -> List[Chunk]:
        """
        Chunk a file using appropriate strategy.
        Args:
            file_path: Path to file
        Returns:
            List of chunks
        """
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        file_path_str = str(file_path)

        # Choose chunker based on file extension
        if file_path.suffix == '.py':
            return self.python_chunker.chunk(content, file_path_str)
        else:
            return self.text_chunker.chunk(content, file_path_str)
