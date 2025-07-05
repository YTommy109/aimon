import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from app.infrastructure.persistence import JsonProjectRepository


@pytest.fixture
def project_repository() -> Generator[JsonProjectRepository, None, None]:
    """テスト用のJsonProjectRepositoryフィクスチャ。

    一時ディレクトリを作成し、テスト終了後に削除する。
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield JsonProjectRepository(Path(tmp_dir))
