from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from sans_indexer.models import IndexEntry


class BaseStorage(ABC):
    """Abstract interface for index data storage."""

    @abstractmethod
    def load_all(self) -> Iterator[IndexEntry]:
        """Yields all IndexEntry records from storage."""
        pass

    @abstractmethod
    def add(self, entry: IndexEntry) -> None:
        """Persists a new IndexEntry to storage."""
        pass