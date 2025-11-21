import hashlib
import os
from pathlib import Path

import pytest

from ingest_watcher.domain.entities import Snapshot, SnapshotEntryStats
from ingest_watcher.domain.events import SnapshotEventType
from ingest_watcher.domain.services import diff_snapshots


@pytest.fixture
def make_snapshot():
    """Factory fixture to create snapshots from a files dictionary."""

    def _make_snapshot(root: Path, files_dict: dict[str, dict]) -> Snapshot:
        files = {
            path: SnapshotEntryStats(
                md5=info["md5"],
                size=info.get("size", 0),
                mime=info.get("mime", ""),
            )
            for path, info in files_dict.items()
        }
        return Snapshot(root=root, files=files)

    return _make_snapshot


@pytest.fixture
def root_path():
    """Fixture providing a root path for snapshots."""
    return Path("/root")


@pytest.fixture
def md5_hash():
    """Fixture providing a MD5 hash for a given or random content."""

    def _md5_hash(content: bytes | None = None) -> str:
        if content is None:
            content = os.urandom(1024)
        return hashlib.md5(content).hexdigest()

    return _md5_hash


# Test scenarios for snapshot diffing
SNAPSHOT_DIFF_TEST_CASES = [
    pytest.param(
        {},
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        [
            (SnapshotEventType.FILE_ADDED, "a.mp4"),
            (SnapshotEventType.FILE_ADDED, "b.mp4"),
        ],
        id="first_run_with_files_produces_added_events",
    ),
    pytest.param(
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        [],
        id="no_changes_produces_empty_events",
    ),
    pytest.param(
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
            "c.mp4": {"md5": "7d41402abc4b2a76b9719d911017c592", "size": 30},
        },
        [(SnapshotEventType.FILE_ADDED, "c.mp4")],
        id="file_addition_produces_added_event",
    ),
    pytest.param(
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
            "b.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
        },
        [(SnapshotEventType.FILE_REMOVED, "b.mp4")],
        id="file_removal_produces_removed_event",
    ),
    pytest.param(
        {
            "a.mp4": {"md5": "5d41402abc4b2a76b9719d911017c592", "size": 10},
        },
        {
            "a.mp4": {"md5": "098f6bcd4621d373cade4e832627b4f6", "size": 20},
        },
        [(SnapshotEventType.FILE_MODIFIED, "a.mp4")],
        id="file_modification_produces_modified_event",
    ),
]


@pytest.mark.parametrize(
    "old_files,new_files,expected_events", SNAPSHOT_DIFF_TEST_CASES
)
def test_diff_snapshots(
    make_snapshot, root_path, old_files, new_files, expected_events
):
    """Test snapshot diffing produces correct events for various scenarios."""
    old = make_snapshot(root_path, old_files)
    new = make_snapshot(root_path, new_files)

    events = diff_snapshots(old, new)

    assert len(events) == len(expected_events)
    actual_events = {(e.event_type, e.path) for e in events}
    expected_set = set(expected_events)
    assert actual_events == expected_set
