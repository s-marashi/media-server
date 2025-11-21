from typing import Protocol

from ingest_watcher.domain.entities import SnapshotEntryStats
from ingest_watcher.domain.snapshot_state import SnapshotState

from hashlib import md5

class SnapshotStateFactory(Protocol):
    """Factory for creating snapshot states."""

    def __call__(self) -> SnapshotState:
        """Create a snapshot state."""
        ...

def run_common_snapshot_state_tests(make_snapshot_state: SnapshotStateFactory):
    """Return list of common snapshot state tests."""

    def test_add_file_and_exists():
        state = make_snapshot_state()
        assert not state.exists("/foo/test.txt")

        changed = state.add_file("/foo/test.txt", SnapshotEntryStats(md5=md5("test").hexdigest(), size=100))
        assert changed, "File should be added"
        assert state.exists("/foo/test.txt"), "File should exist"
