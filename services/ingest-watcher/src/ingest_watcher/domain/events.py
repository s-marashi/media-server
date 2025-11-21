from enum import Enum

from pydantic import BaseModel, Field


class SnapshotEventType(Enum):
    FILE_ADDED = "file_added"
    FILE_REMOVED = "file_removed"
    FILE_MODIFIED = "file_modified"


class SnapshotEvent(BaseModel):
    """Domain event representing a change in a snapshot."""

    event_type: SnapshotEventType = Field(
        ..., description="Event type: FILE_ADDED, FILE_REMOVED, or FILE_MODIFIED"
    )
    path: str = Field(..., description="Path of the file that changed", min_length=1)

    model_config = {"frozen": True}

    def __str__(self) -> str:
        return f"{self.event_type.value}: {self.path}"
