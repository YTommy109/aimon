"""executorsモジュールの__init__.pyのテスト。"""

from app.utils.executors import AsyncGenericAIToolExecutor
from app.utils.executors.azure_functions_executor import (
    AsyncGenericAIToolExecutor as OriginalClass,
)


class TestExecutorsInit:
    """executorsモジュールの__init__.pyのテストクラス。"""

    def test_AsyncGenericAIToolExecutorがインポートできる(self) -> None:
        """AsyncGenericAIToolExecutorがインポートできることをテスト。"""
        # Act & Assert
        assert AsyncGenericAIToolExecutor is not None

    def test_AsyncGenericAIToolExecutorが正しいクラスである(self) -> None:
        """AsyncGenericAIToolExecutorが正しいクラスであることをテスト。"""
        # Act & Assert
        assert AsyncGenericAIToolExecutor == OriginalClass
