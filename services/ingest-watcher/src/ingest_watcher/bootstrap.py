from dataclasses import dataclass


@dataclass
class IngestWatcherConfig:
    """Configuration for the ingest watcher."""

    root_path: str

class IngestWatcherApp:
    ...

def build_app(config: IngestWatcherConfig) -> IngestWatcherApp | None:
    ...
