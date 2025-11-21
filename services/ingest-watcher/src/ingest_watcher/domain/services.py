from collections.abc import Callable

from ingest_watcher.domain.entities import Snapshot
from ingest_watcher.domain.events import SnapshotEvent, SnapshotEventType


def diff_snapshots(old: Snapshot, new: Snapshot) -> list[SnapshotEvent]:
    """Compare two snapshots and return the differences."""
    events: list[SnapshotEvent] = []

    # Find added files
    for path in new.files:
        if path not in old.files:
            events.append(
                SnapshotEvent(event_type=SnapshotEventType.FILE_ADDED, path=path)
            )

    # Find removed files
    for path in old.files:
        if path not in new.files:
            events.append(
                SnapshotEvent(event_type=SnapshotEventType.FILE_REMOVED, path=path)
            )

    # Find modified files (same path but different md5)
    for path in new.files:
        if path in old.files:
            if new.files[path].md5 != old.files[path].md5:
                events.append(
                    SnapshotEvent(event_type=SnapshotEventType.FILE_MODIFIED, path=path)
                )

    return events


def dummy_event_processor(event: SnapshotEvent) -> None:
    """Dummy event processor that prints the event."""
    print(event)


def process_snapshot_events(
    events: list[SnapshotEvent],
    processor: Callable[[SnapshotEvent], None] = dummy_event_processor,
) -> None:
    """Process snapshot events."""
    for event in events:
        processor(event)
