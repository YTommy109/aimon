"""AIツール実行の抽象インターフェース。"""

from abc import ABC, abstractmethod

from PIL import Image


class AIToolExecutor(ABC):
    """AIツール実行の抽象インターフェース。"""

    @abstractmethod
    def execute(self, content: str, images: list[Image.Image]) -> str:
        """AIツールを実行して結果を取得します。

        Args:
            content: 処理対象のテキスト内容。
            images: 処理対象の画像リスト。

        Returns:
            AIツールの実行結果。

        Raises:
            APIConfigurationError: API設定エラーが発生した場合。
            APICallFailedError: API呼び出しに失敗した場合。
        """
