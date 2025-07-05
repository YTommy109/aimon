"""AIツール関連のサービス関数群。"""

from app.application.data_manager import DataManager
from app.domain.entities import AITool


def get_ai_tools(data_manager: DataManager) -> list[AITool]:
    """有効なAIツールの一覧を取得。

    Args:
        data_manager: データマネージャー。

    Returns:
        有効なAIツールのリスト。
    """
    return data_manager.get_all_ai_tools()


def handle_ai_tool_creation(
    data_manager: DataManager,
    tool_id: str,
    name: str,
    description: str | None = None,
) -> bool:
    """AIツール作成処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。
        name: ツール名。
        description: 説明(オプション)。

    Returns:
        作成が成功した場合True、失敗した場合False。
    """
    return data_manager.create_ai_tool(tool_id, name, description)


def handle_ai_tool_update(
    data_manager: DataManager,
    tool_id: str,
    name: str,
    description: str | None = None,
) -> bool:
    """AIツール更新処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。
        name: ツール名。
        description: 説明(オプション)。

    Returns:
        更新が成功した場合True、失敗した場合False。
    """
    return data_manager.update_ai_tool(tool_id, name, description)


def handle_ai_tool_disable(data_manager: DataManager, tool_id: str) -> bool:
    """AIツール無効化処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。

    Returns:
        無効化が成功した場合True、失敗した場合False。
    """
    return data_manager.disable_ai_tool(tool_id)


def handle_ai_tool_enable(data_manager: DataManager, tool_id: str) -> bool:
    """AIツール有効化処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。

    Returns:
        有効化が成功した場合True、失敗した場合False。
    """
    return data_manager.enable_ai_tool(tool_id)
