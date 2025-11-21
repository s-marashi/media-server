from pathlib import Path
from ingest_watcher.domain.entities import Snapshot
from ingest_watcher.domain.repositories import Watcher

def file_watcher(path: Path) -> Snapshot:
    """Watch a path and return a snapshot on its change.."""

    return Snapshot(root=path, files={})