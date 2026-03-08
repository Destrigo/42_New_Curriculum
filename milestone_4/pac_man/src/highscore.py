"""Persistent highscore system.

Stores the top 10 scores in a JSON file. Handles file errors,
validates player names and scores, and provides load/save operations.
"""

import json
import os
import re
from typing import Any


MAX_ENTRIES: int = 10
MAX_NAME_LEN: int = 10
NAME_PATTERN: re.Pattern[str] = re.compile(r'^[a-zA-Z0-9 ]+$')


class HighscoreEntry:
    """A single highscore entry."""

    def __init__(self, name: str, score: int) -> None:
        """Initialize a highscore entry."""
        self.name: str = self._sanitize_name(name)
        self.score: int = max(0, int(score))

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Sanitize player name to allowed characters.

        Args:
            name: Raw player name.

        Returns:
            Cleaned name, max 10 characters.
        """
        clean = re.sub(r'[^a-zA-Z0-9 ]', '', str(name))
        clean = clean.strip()[:MAX_NAME_LEN]
        return clean if clean else "Player"

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary."""
        return {"name": self.name, "score": self.score}

    def __repr__(self) -> str:
        """Return string representation."""
        return f"HighscoreEntry({self.name!r}, {self.score})"


class HighscoreManager:
    """Manages the highscore list with persistence."""

    def __init__(self, filepath: str) -> None:
        """Initialize the highscore manager."""
        self.filepath: str = filepath
        self.entries: list[HighscoreEntry] = []
        self.load()

    def load(self) -> None:
        """Load highscores from file."""
        if not os.path.exists(self.filepath):
            print(f"[highscore] No file at {self.filepath}, "
                  "starting fresh.")
            self.entries = []
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data: Any = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[highscore] Error reading {self.filepath}: "
                  f"{e}, starting fresh.")
            self.entries = []
            return

        if not isinstance(data, list):
            print("[highscore] Invalid format, starting fresh.")
            self.entries = []
            return

        entries: list[HighscoreEntry] = []
        for item in data:
            if isinstance(item, dict):
                name = item.get("name", "Player")
                score = item.get("score", 0)
                try:
                    entries.append(HighscoreEntry(str(name),
                                                  int(score)))
                except (TypeError, ValueError):
                    print(f"[highscore] Skipping invalid entry: "
                          f"{item}")

        entries.sort(key=lambda e: e.score, reverse=True)
        self.entries = entries[:MAX_ENTRIES]

    def save(self) -> None:
        """Save highscores to file."""
        data = [e.to_dict() for e in self.entries]
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"[highscore] Error saving to "
                  f"{self.filepath}: {e}")

    def add(self, name: str, score: int) -> bool:
        """Add a new score to the highscore list."""
        entry = HighscoreEntry(name, score)
        self.entries.append(entry)
        self.entries.sort(key=lambda e: e.score, reverse=True)
        self.entries = self.entries[:MAX_ENTRIES]
        self.save()
        return entry in self.entries

    def get_top(self, count: int = MAX_ENTRIES
                ) -> list[HighscoreEntry]:
        """Get top scores."""
        return self.entries[:count]

    def is_high_score(self, score: int) -> bool:
        """Check if a score qualifies for the top 10."""
        if len(self.entries) < MAX_ENTRIES:
            return True
        return score > self.entries[-1].score
