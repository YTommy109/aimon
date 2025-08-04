"""executorsモジュールの__init__.pyのテスト。"""

from app.utils.executors import CommandExecutor
from app.utils.executors.command_executor import (
    CommandExecutor as OriginalClass,
)


class TestExecutorsInit:
    """executorsモジュールの__init__.pyのテストクラス。"""

    def test_CommandExecutorがインポートできる(self) -> None:
        """CommandExecutorがインポートできることをテスト。"""
        # Act & Assert
        assert CommandExecutor is not None

    def test_CommandExecutorが正しいクラスである(self) -> None:
        """CommandExecutorが正しいクラスであることをテスト。"""
        # Act & Assert
        assert CommandExecutor == OriginalClass
