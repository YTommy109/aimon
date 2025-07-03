"""AIツール管理のサービス層。"""

from app.model.entities import AITool
from app.model.store import DataManager

# 定数定義
MAX_TOOL_ID_LENGTH = 50
MAX_TOOL_NAME_LENGTH = 100
MAX_TOOL_DESCRIPTION_LENGTH = 500


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
    result = False
    try:
        # バリデーションと重複チェックをまとめて判定
        if not _is_valid_creation_input(tool_id, name, description) or _is_duplicate_tool_id(
            data_manager, tool_id
        ):
            result = False
        else:
            # AIツール作成（descriptionがNoneの場合は空文字）
            description_str = description if description is not None else ''
            data_manager.create_ai_tool(tool_id, name, description_str)
            result = True
    except Exception:
        result = False
    return result


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
    result = False
    try:
        # バリデーション
        if not _is_valid_update_input(name, description):
            result = False
        else:
            # AIツール更新（descriptionがNoneの場合は空文字）
            description_str = description if description is not None else ''
            data_manager.update_ai_tool(tool_id, name, description_str)
            result = True
    except Exception:
        result = False
    return result


def handle_ai_tool_disable(
    data_manager: DataManager,
    tool_id: str,
) -> bool:
    """AIツール無効化処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。

    Returns:
        無効化が成功した場合True、失敗した場合False。
    """
    try:
        # AIツール無効化
        data_manager.disable_ai_tool(tool_id)
        return True
    except Exception:
        return False


def handle_ai_tool_enable(
    data_manager: DataManager,
    tool_id: str,
) -> bool:
    """AIツール有効化処理。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。

    Returns:
        有効化が成功した場合True、失敗した場合False。
    """
    try:
        # AIツール有効化
        data_manager.enable_ai_tool(tool_id)
        return True
    except Exception:
        return False


def get_ai_tools(data_manager: DataManager) -> list[AITool]:
    """有効なAIツールの一覧を取得。

    Args:
        data_manager: データマネージャー。

    Returns:
        有効なAIツールのリスト。
    """
    return data_manager.get_ai_tools()


def get_all_ai_tools(data_manager: DataManager) -> list[AITool]:
    """全てのAIツールの一覧を取得(無効化されたものも含む)。

    Args:
        data_manager: データマネージャー。

    Returns:
        全てのAIツールのリスト。
    """
    return data_manager.get_all_ai_tools()


def _is_valid_creation_input(tool_id: str, name: str, description: str | None) -> bool:
    """作成時の入力値バリデーション。

    Args:
        tool_id: ツールID。
        name: ツール名。
        description: 説明。

    Returns:
        有効な入力の場合True。
    """
    return _is_valid_id(tool_id) and _is_valid_name(name) and _is_valid_description(description)


def _is_valid_update_input(name: str, description: str | None) -> bool:
    """更新時の入力値バリデーション。

    Args:
        name: ツール名。
        description: 説明。

    Returns:
        有効な入力の場合True。
    """
    return _is_valid_name(name) and _is_valid_description(description)


def _is_valid_id(tool_id: str) -> bool:
    """ツールIDの妥当性チェック。

    Args:
        tool_id: ツールID。

    Returns:
        有効な場合True。
    """
    return bool(tool_id and tool_id.strip() and len(tool_id) <= MAX_TOOL_ID_LENGTH)


def _is_valid_name(name: str) -> bool:
    """ツール名の妥当性チェック。

    Args:
        name: ツール名。

    Returns:
        有効な場合True。
    """
    return bool(name and name.strip() and len(name) <= MAX_TOOL_NAME_LENGTH)


def _is_valid_description(description: str | None) -> bool:
    """説明の妥当性チェック。

    Args:
        description: 説明。

    Returns:
        有効な場合True。
    """
    return description is None or len(description) <= MAX_TOOL_DESCRIPTION_LENGTH


def _is_duplicate_tool_id(data_manager: DataManager, tool_id: str) -> bool:
    """重複するツールIDの存在チェック。

    Args:
        data_manager: データマネージャー。
        tool_id: ツールID。

    Returns:
        重複が存在する場合True。
    """
    existing_tools = data_manager.get_ai_tools()
    return any(tool.id == tool_id for tool in existing_tools)
