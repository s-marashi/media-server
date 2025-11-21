from pydantic import BaseModel, Field, field_validator

from ingest_watcher.domain.events import SnapshotEvent, SnapshotEventType
from ingest_watcher.domain.snapshot_state import SnapshotState


class SnapshotEntryStats(BaseModel):
    """Value object representing the stats of a file entry in a snapshot."""

    md5: str = Field(..., min_length=1, description="MD5 hash of the file")
    size: int = Field(..., ge=0, description="File size in bytes")
    mime: str = Field(default="", description="MIME type of the file")

    model_config = {"frozen": True}

    @field_validator("md5")
    @classmethod
    def validate_md5_format(cls, v: str) -> str:
        """Validate and normalize MD5 hash format."""
        v = v.strip()
        if len(v) != 32:
            raise ValueError(f"MD5 hash must be exactly 32 characters, got {len(v)}")
        if not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("MD5 hash must contain only hexadecimal characters")
        return v.lower()

    def __eq__(self, other: object) -> bool:
        """Check if two SnapshotEntryStats are equal."""
        if not isinstance(other, SnapshotEntryStats):
            return False
        return (
            self.md5 == other.md5
            and self.size == other.size
            and self.mime == other.mime
        )


class Snapshot:
    """Entity representing a snapshot of a directory."""

    def __init__(self, id: str, state_store: SnapshotState):
        self._id: str = id
        self._state_store = state_store
        self._events: list[SnapshotEvent] = []

    def add_file(self, path: str, stats: SnapshotEntryStats):
        """Add an entry to the snapshot."""

        changed = self._state_store.add_file(path, stats)
        if changed:
            self._events.append(
                SnapshotEvent(event_type=SnapshotEventType.FILE_ADDED, path=path)
            )

    def remove_file(self, path: str):
        """Remove a file from the snapshot."""

        changed = self._state_store.remove_file(path)
        if changed:
            self._events.append(
                SnapshotEvent(event_type=SnapshotEventType.FILE_REMOVED, path=path)
            )

    def update_file(self, path: str, stats: SnapshotEntryStats):
        """Update a file in the snapshot."""

        changed = self._state_store.update_file(path, stats)
        if changed:
            self._events.append(
                SnapshotEvent(event_type=SnapshotEventType.FILE_MODIFIED, path=path)
            )

    def add_directory(self, path: str):
        """Add a directory to the snapshot."""

        changed = self._state_store.add_directory(path)
        if changed:
            self._events.append(
                SnapshotEvent(event_type=SnapshotEventType.DIRECTORY_ADDED, path=path)
            )

    def remove_directory(self, path: str):
        """Remove a directory from the snapshot."""

        removed_files = self._state_store.remove_directory(path)
        if len(removed_files) > 0:
            for removed_file in removed_files:
                self._events.append(
                    SnapshotEvent(
                        event_type=SnapshotEventType.FILE_REMOVED, path=removed_file
                    )
                )

    def pull_events(self) -> list[SnapshotEvent]:
        """Pull events from the snapshot."""

        events = self._events
        self._events = []

        return events

    # @classmethod
    # def from_entries(self, entries: list[SnapshotEntry]) -> Snapshot:
    #     ...
