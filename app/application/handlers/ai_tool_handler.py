"""AIツール管理のハンドラー。"""

from app.domain.entities import AITool
from app.domain.repositories import AIToolRepository

# 定数定義
MAX_TOOL_ID_LENGTH = 50
MAX_TOOL_NAME_LENGTH = 100
MAX_TOOL_DESCRIPTION_LENGTH = 500


class AIToolHandler:
    """AIツール管理のハンドラー。"""

    def __init__(self, ai_tool_repository: AIToolRepository) -> None:
        """ハンドラーを初期化します。

        Args:
            ai_tool_repository: AIツールリポジトリ。
        """
        self.ai_tool_repository = ai_tool_repository

    def create_ai_tool(self, tool_id: str, name: str, description: str | None = None) -> bool:
        """AIツール作成処理。

        Args:
            tool_id: ツールID。
            name: ツール名。
            description: 説明(オプション)。

        Returns:
            作成が成功した場合True、失敗した場合False。
        """
        if not self._is_valid_creation_input(tool_id, name, description):
            return False

        if self._is_duplicate_tool_id(tool_id):
            return False

        try:
            description_str = description if description is not None else ''
            ai_tool = AITool(id=tool_id, name_ja=name, description=description_str)
            self.ai_tool_repository.save(ai_tool)
            return True
        except Exception:
            return False

    def update_ai_tool(self, tool_id: str, name: str, description: str | None = None) -> bool:
        """AIツール更新処理。

        Args:
            tool_id: ツールID。
            name: ツール名。
            description: 説明(オプション)。

        Returns:
            更新が成功した場合True、失敗した場合False。
        """
        if not self._is_valid_update_input(name, description):
            return False

        try:
            ai_tool = self.ai_tool_repository.find_by_id(tool_id)
            if ai_tool is None:
                return False

            ai_tool.name_ja = name
            if description is not None:
                ai_tool.description = description

            self.ai_tool_repository.save(ai_tool)
            return True
        except Exception:
            return False

    def disable_ai_tool(self, tool_id: str) -> bool:
        """AIツール無効化処理。

        Args:
            tool_id: ツールID。

        Returns:
            無効化が成功した場合True、失敗した場合False。
        """
        try:
            self.ai_tool_repository.disable(tool_id)
            return True
        except Exception:
            return False

    def enable_ai_tool(self, tool_id: str) -> bool:
        """AIツール有効化処理。

        Args:
            tool_id: ツールID。

        Returns:
            有効化が成功した場合True、失敗した場合False。
        """
        try:
            self.ai_tool_repository.enable(tool_id)
            return True
        except Exception:
            return False

    def get_active_ai_tools(self) -> list[AITool]:
        """有効なAIツールの一覧を取得。

        Returns:
            有効なAIツールのリスト。
        """
        return self.ai_tool_repository.find_active_tools()

    def get_all_ai_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得(無効化されたものも含む)。

        Returns:
            全てのAIツールのリスト。
        """
        return self.ai_tool_repository.find_all_tools()

    def _is_valid_creation_input(self, tool_id: str, name: str, description: str | None) -> bool:
        """作成時の入力値バリデーション。"""
        return (
            self._is_valid_id(tool_id)
            and self._is_valid_name(name)
            and self._is_valid_description(description)
        )

    def _is_valid_update_input(self, name: str, description: str | None) -> bool:
        """更新時の入力値バリデーション。"""
        return self._is_valid_name(name) and self._is_valid_description(description)

    def _is_valid_id(self, tool_id: str) -> bool:
        """ツールIDの妥当性チェック。"""
        return bool(tool_id and tool_id.strip() and len(tool_id) <= MAX_TOOL_ID_LENGTH)

    def _is_valid_name(self, name: str) -> bool:
        """ツール名の妥当性チェック。"""
        return bool(name and name.strip() and len(name) <= MAX_TOOL_NAME_LENGTH)

    def _is_valid_description(self, description: str | None) -> bool:
        """説明の妥当性チェック。"""
        return description is None or len(description) <= MAX_TOOL_DESCRIPTION_LENGTH

    def _is_duplicate_tool_id(self, tool_id: str) -> bool:
        """重複するツールIDの存在チェック。"""
        existing_tool = self.ai_tool_repository.find_by_id(tool_id)
        return existing_tool is not None
