from ingest_watcher.domain.entities import SnapshotEntryStats


class InMemorySnapshotState:
    """In-memory snapshot state."""

    def add_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        ...
    
    def remove_file(self, path: str) -> bool:
        ...
    
    def update_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        ...
    
    def add_directory(self, path: str) -> bool:
        ...
    
    def remove_directory(self, path: str) -> list[str]:
        ...