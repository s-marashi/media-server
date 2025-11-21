from typing import Protocol

from ingest_watcher.domain.entities import SnapshotEntryStats


class SnapshotState(Protocol):
    """ It abstracts away state keeping logic from snapshot it self"""

    def add_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        """Add a file to the snapshot."""
        ...

    def remove_file(self, path: str) -> bool:
        """Remove a file from the snapshot."""
        ...

    def update_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        """Update a file in the snapshot."""
        ...
    
    def get_stats(self, path: str) -> SnapshotEntryStats | None:
        """Get the stats of a file in the snapshot."""
        ...

    def add_directory(self, path: str) -> bool:
        """Add a directory to the snapshot."""
        ...

    def remove_directory(self, path: str) -> list[str]:
        """Remove a directory from the snapshot."""
        ...

    def exists(self, path: str) -> bool:
        """Check if a path exists in the snapshot."""
        ...
    
    def get_children(self, path: str) -> list[str]:
        """Get the children of a path in the snapshot."""
        ...
