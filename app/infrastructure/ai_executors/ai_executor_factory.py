"""AIツール実行のファクトリクラス。"""

from app.domain.ai_tool_executor import AIToolExecutor
from app.domain.entities import AITool

from .azure_functions_executor import GenericAIToolExecutor


class AIExecutorFactory:
    """AIツール実行のファクトリクラス。"""

    @staticmethod
    def create_executor(ai_tool: AITool) -> AIToolExecutor:
        """AIツールエンティティに基づいてAIツール実行クラスを作成します。

        Args:
            ai_tool: AIツールエンティティ。

        Returns:
            AIツール実行クラスのインスタンス。

        Raises:
            ValueError: 未知のAIツールIDの場合。
        """
        return GenericAIToolExecutor(ai_tool.id, ai_tool.endpoint_url)
