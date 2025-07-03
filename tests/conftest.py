import tempfile
from collections.abc import Generator

import pytest

from app.model.store import DataManager


@pytest.fixture
def data_manager() -> Generator[DataManager, None, None]:
    """テスト用のDataManagerフィクスチャ。

    一時ディレクトリを作成し、テスト終了後に削除する。
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield DataManager(tmp_dir)
