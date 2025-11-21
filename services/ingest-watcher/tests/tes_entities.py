import pytest
from pydantic import ValidationError

from ingest_watcher.domain.entities import FileEntry


class TestFileEntry:
    """Tests for FileEntry value object validation."""

    def test_md5_normalization(self):
        """MD5 is normalized: uppercase converted to lowercase, whitespace trimmed."""
        entry = FileEntry(
            path="test.mp4",
            md5="  5D41402ABC4B2A76B9719D911017C592  "
        )
        
        assert entry.md5 == "5d41402abc4b2a76b9719d911017c592"
        assert len(entry.md5) == 32

    def test_invalid_md5_rejected(self):
        """Invalid MD5 hashes are rejected."""
        with pytest.raises(ValidationError):
            FileEntry(path="test.mp4", md5="too-short")
        
        with pytest.raises(ValidationError):
            FileEntry(path="test.mp4", md5="5d41402abc4b2a76b9719d911017c59g")
