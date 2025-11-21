from collections.abc import Callable

from ingest_watcher.domain.entities import SnapshotEntryStats
from ingest_watcher.domain.snapshot_state import SnapshotState

from hashlib import md5

SnapshotStateFactory = Callable[[str], SnapshotState]

def run_common_snapshot_state_tests(make_snapshot_state: SnapshotStateFactory):
    """Return list of common snapshot state tests."""

    def test_file_does_not_exist():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/test.txt"), "File should not exist"

    def test_add_file_and_exists():
        state = make_snapshot_state("/")
        assert not state.exists("/foo/test.txt")

        changed = state.add_file("/foo/test.txt", SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100))
        assert changed, "File should be added"
        assert state.exists("/foo/test.txt"), "File should exist"

    def test_add_file_and_get_stats():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/test.txt", stats)
        assert changed, "File should be added"
        assert state.get_stats("/foo/test.txt") == stats, "Stats should be correct"
    
    def test_remove_file_and_does_not_exist():
        state = make_snapshot_state("/")

        changed = state.remove_file("/foo/test.txt")
        assert not changed, "File should not be removed"
    
    def test_add_file_remove_and_does_not_exist():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/test.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/test.txt"), "File should exist"

        changed = state.remove_file("/foo/test.txt")
        assert changed, "File should be removed"
        assert not state.exists("/foo/test.txt"), "File should not exist"
    
    def test_update_file_and_does_not_exist():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.update_file("/foo/test.txt", stats)
        assert not changed, "File should not be updated"

    def test_add_file_update_and_get_stats():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/test.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/test.txt"), "File should exist"
        assert state.get_stats("/foo/test.txt") == stats

        new_stats = SnapshotEntryStats(md5=md5("test2".encode()).hexdigest(), size=200)
        changed = state.update_file("/foo/test.txt", new_stats)
        assert changed, "File should be updated"
        assert state.exists("/foo/test.txt"), "File should exist"
        assert state.get_stats("/foo/test.txt") == new_stats
    

    def test_directory_does_not_exist():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/bar"), "Directory should not exist"
    
    def test_add_directory_and_exists():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/bar"), "Directory should not exist"
        
        changed = state.add_directory("/foo/bar")
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar"), "Directory should exist"

    def test_remove_directory_and_does_not_exist():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/bar"), "Directory should not exist"

        changed = state.remove_directory("/foo/bar")
        assert changed == [], "Directory should not be removed"

    def test_add_directory_remove_and_does_not_exist():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/bar"), "Directory should not exist"

        changed = state.add_directory("/foo/bar")
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar"), "Directory should exist"

        changed = state.remove_directory("/foo/bar")
        assert changed == [], "Directory should be removed"
        assert not state.exists("/foo/bar"), "Directory should not exist"
    
    def test_directory_does_exist_and_get_children():
        state = make_snapshot_state("/")

        assert not state.exists("/foo/bar"), "Directory should not exist"

        children = state.get_children("/foo/bar")
        assert children == [], "Directory should have no children"
    
    def test_children_of_non_directory_are_empty():
        state = make_snapshot_state("/")

        changed = state.add_file("/foo/bar.txt", SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100))
        assert changed, "File should be added"
        assert state.exists("/foo/bar.txt"), "File should exist"
        assert state.get_children("/foo/bar.txt") == [], "File should have no children"

    def test_children_of_empty_directory_are_empty():
        state = make_snapshot_state("/")

        changed = state.add_directory("/foo/bar")
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar"), "Directory should exist"
        assert state.get_children("/foo/bar") == [], "Directory should have no children"
    
    def test_children_of_directory_with_one_file():
        state = make_snapshot_state("/foo")

        changed = state.add_file("/foo/bar/baz.txt", SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100))
        assert changed, "File should be added"
        assert state.exists("/foo/bar/baz.txt"), "File should exist"
        assert state.get_children("/foo/bar") == ["/foo/bar/baz.txt"], "Directory should have one child"
    
    def test_remove_directory_and_children_are_removed():
        state = make_snapshot_state("/")

        changed = state.add_directory("/foo/bar")
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar"), "Directory should exist"
        assert state.get_children("/foo/bar") == [], "Directory should have no children"
        
        changed = state.add_file("/foo/bar/baz.txt", SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100))
        assert changed, "File should be added"
        assert state.exists("/foo/bar/baz.txt"), "File should exist"
        assert state.get_children("/foo/bar") == ["/foo/bar/baz.txt"], "Directory should have one child"

        removed_files = state.remove_directory("/foo/bar")
        assert removed_files == ["/foo/bar/baz.txt"], "File should be removed"
        assert not state.exists("/foo/bar/baz.txt"), "File should not exist"
        assert not state.exists("/foo/bar"), "Directory should not exist"

    def test_remove_directory_and_children_are_removed_recursively():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/a.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/a.txt"), "File should exist"

        changed = state.add_file("/foo/bar/b.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/b.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/c.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/baz/c.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/d.txt", stats)
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar/baz/d.txt"), "Directory should exist"

        removed_files = state.remove_directory("/foo")
        assert removed_files == ["/foo/a.txt", "/foo/bar/b.txt", "/foo/bar/baz/c.txt", "/foo/bar/baz/d.txt"], "Files should be removed"
        assert not state.exists("/foo/a.txt"), "File should not exist"
        assert not state.exists("/foo/bar/b.txt"), "File should not exist"
        assert not state.exists("/foo/bar/baz/c.txt"), "File should not exist"
        assert not state.exists("/foo/bar/baz/d.txt"), "Directory should not exist"
        assert not state.exists("/foo/bar"), "Directory should not exist"
        assert not state.exists("/foo/bar/baz"), "Directory should not exist"
        assert not state.exists("/foo"), "Directory should not exist"
    

    def test_add_file_to_directory_and_get_children_of_root():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/a.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/a.txt"), "File should exist"

        changed = state.add_file("/foo/bar/b.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/b.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/c.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/baz/c.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/d.txt", stats)
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar/baz/d.txt"), "Directory should exist"

        children = state.get_children("/")
        assert children == ["/foo"], "Directory should have one children"
    
    def test_get_all_files_of_root():
        state = make_snapshot_state("/")
        stats = SnapshotEntryStats(md5=md5("test".encode()).hexdigest(), size=100)

        changed = state.add_file("/foo/a.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/a.txt"), "File should exist"

        changed = state.add_file("/foo/bar/b.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/b.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/c.txt", stats)
        assert changed, "File should be added"
        assert state.exists("/foo/bar/baz/c.txt"), "File should exist"

        changed = state.add_file("/foo/bar/baz/d.txt", stats)
        assert changed, "Directory should be added"
        assert state.exists("/foo/bar/baz/d.txt"), "Directory should exist"

        files = state.get_all_files("/")
        assert files == ["/foo/a.txt", "/foo/bar/b.txt", "/foo/bar/baz/c.txt", "/foo/bar/baz/d.txt"], "Files should be correct"


    return [
        test_file_does_not_exist,
        test_add_file_and_exists,
        test_add_file_and_get_stats,
        test_remove_file_and_does_not_exist,
        test_add_file_remove_and_does_not_exist,
        test_update_file_and_does_not_exist,
        test_add_file_update_and_get_stats,
        test_directory_does_not_exist,
        test_add_directory_and_exists,
        test_remove_directory_and_does_not_exist,
        test_add_directory_remove_and_does_not_exist,
        test_directory_does_exist_and_get_children,
        test_children_of_non_directory_are_empty,
        test_children_of_empty_directory_are_empty,
        test_children_of_directory_with_one_file,
        test_remove_directory_and_children_are_removed,
        test_remove_directory_and_children_are_removed_recursively,
        test_add_file_to_directory_and_get_children_of_root,
        test_get_all_files_of_root,
    ]
