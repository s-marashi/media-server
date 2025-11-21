from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from ingest_watcher.domain.entities import Snapshot

WatcherFn = Callable[[Path], Snapshot]

class SnapshotRepository(Protocol):
    """Repository for snapshots."""

    def load(self, path: Path) -> Snapshot:
        """Load a snapshot by path."""
        ...

    def save(self, snapshot: Snapshot) -> None:
        """Save a snapshot."""
        ...
