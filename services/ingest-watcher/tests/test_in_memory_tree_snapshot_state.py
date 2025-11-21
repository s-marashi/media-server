from collections.abc import Callable
from typing import cast

import pytest
from test_contract_snapshot_state import run_common_snapshot_state_tests

from ingest_watcher.domain.snapshot_state import SnapshotState
from ingest_watcher.infrastructure.in_memory_tree_snapshot_state import (
    InMemoryTreeSnapshotState,
)


def make_in_memory_tree_snapshot_state(root_path: str) -> SnapshotState:
    """Make an in-memory tree snapshot state."""
    return cast(SnapshotState, InMemoryTreeSnapshotState(root_path))


@pytest.mark.parametrize(
    "test_func", run_common_snapshot_state_tests(make_in_memory_tree_snapshot_state)
)
def test_snapshot_state_contract(test_func: Callable[[], None]):
    """Test the snapshot state contract."""
    test_func()
