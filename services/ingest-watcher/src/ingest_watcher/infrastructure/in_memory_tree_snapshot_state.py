from ingest_watcher.domain.entities import SnapshotEntryStats
from pathlib import PurePosixPath


class InMemoryTreeSnapshotState:
    """In-memory tree snapshot state."""

    def __init__(self, root_path: str) -> None:
        # it would be none when the path is deleted
        self._paths: list[str | None] = []
        self._is_dir: list[bool | None] = []
        self._stats: list[SnapshotEntryStats | None] = []
        self._children: dict[int, list[int]] = {}
        self._path_to_id: dict[str, int] = {}

        self._root_path = self._normalize_path(root_path, check_in_root=False)
        self._add_entry(self._root_path, True, None)

    def _add_entry(
        self, path: str, is_dir: bool, stats: SnapshotEntryStats | None
    ) -> int:
        self._paths.append(path)
        idx = len(self._paths) - 1
        self._is_dir.append(is_dir)
        self._stats.append(stats)

        self._children[idx] = []
        self._path_to_id[path] = idx

        return idx

    def _add_parents(self, path: str) -> int:
        """Add parents of an entry to the snapshot."""

        parent = path.rsplit("/", 1)[0]

        return self._add_missing_parents(parent)

    def _add_missing_parents(self, path: str) -> int:
        """Add missing parents of a path to the snapshot."""

        idx = self._path_to_id.get(path, None)
        if idx is not None:
            return idx

        parent = path.rsplit("/", 1)[0] or "/"
        parent_idx = self._add_missing_parents(parent)

        idx = self._add_entry(path, True, None)
        self._children[parent_idx].append(idx)

        return idx

    def _normalize_path(self, path: str, check_in_root: bool = True) -> str:
        """Normalize a path."""
        p = PurePosixPath(path)
        if not p.is_absolute():
            raise ValueError(f"Path must be absolute, got {path}")

        if check_in_root and not str(p).startswith(self._root_path):
            raise ValueError(f"Path must be in root, got {path}")

        return str(p)

    def exists(self, path: str) -> bool:
        """Check if a path exists in the snapshot."""
        return self._normalize_path(path) in self._path_to_id

    def add_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        """Add a file to the snapshot."""
        p = self._normalize_path(path)
        if p in self._path_to_id:
            return False

        parent_idx = self._add_parents(p)
        idx = self._add_entry(p, False, stats)
        self._children[parent_idx].append(idx)

        return True

    def get_stats(self, path: str) -> SnapshotEntryStats | None:
        """Get the stats of a path in the snapshot."""
        p = self._normalize_path(path)
        idx = self._path_to_id.get(p, None)
        if idx is None:
            return None

        return self._stats[idx]

    def remove_file(self, path: str) -> bool:
        """Remove a file from the snapshot."""
        p = self._normalize_path(path)
        idx = self._path_to_id.get(p, None)
        if idx is None:
            return False

        self._paths[idx] = None
        self._is_dir[idx] = None
        self._stats[idx] = None

        del self._path_to_id[p]
        del self._children[idx]

        return True

    def update_file(self, path: str, stats: SnapshotEntryStats) -> bool:
        """Update a file in the snapshot."""
        p = self._normalize_path(path)
        idx = self._path_to_id.get(p, None)
        if idx is None:
            return False

        old_stats = self._stats[idx]
        if old_stats == stats:
            return False

        self._stats[idx] = stats
        return True

    def add_directory(self, path: str) -> bool:
        """Add a directory to the snapshot."""
        p = self._normalize_path(path)
        if p in self._path_to_id:
            return False

        parent_idx = self._add_parents(p)
        idx = self._add_entry(p, True, None)
        self._children[parent_idx].append(idx)

        return True

    def remove_directory(self, path: str) -> list[str]:
        """Remove a directory from the snapshot."""
        p = self._normalize_path(path)
        idx = self._path_to_id.get(p, None)
        if idx is None:
            return []

        self._paths[idx] = None
        self._is_dir[idx] = None
        self._stats[idx] = None

        del self._path_to_id[p]
        del self._children[idx]
        return []

    def get_children(self, path: str) -> list[str]:
        """Get the children of a path in the snapshot."""
        p = self._normalize_path(path)
        idx = self._path_to_id.get(p, None)
        if idx is None:
            return []

        children = [self._paths[i] for i in self._children[idx]]

        return [c for c in children if c is not None]
