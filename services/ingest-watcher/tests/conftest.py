from pathlib import Path

import pytest


@pytest.fixture
def media_root(tmp_path: Path) -> Path:
    root = tmp_path / "media_root"
    root.mkdir(parents=True, exist_ok=True)

    return root


@pytest.fixture
def media_file(media_root: Path):
    def _make_file(tree: dict[str, bytes]) -> None:
        for rel_path, content in tree.items():
            full_path = media_root / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)

    return _make_file
