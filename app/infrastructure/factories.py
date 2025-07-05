"""ファクトリークラス群。"""

from pathlib import Path

from app.application.data_manager import DataManager
from app.application.handlers.ai_tool_handler import AIToolHandler
from app.application.handlers.project_handler import ProjectHandler
from app.infrastructure.persistence import JsonAIToolRepository, JsonProjectRepository


def create_data_manager(data_dir_path: str | Path) -> DataManager:
    """データマネージャーインスタンスを生成します。

    Args:
        data_dir_path: データディレクトリのパス。

    Returns:
        DataManagerインスタンス。
    """
    # Path型に変換
    path = Path(data_dir_path)

    # リポジトリの作成
    ai_tool_repository = JsonAIToolRepository(path)
    project_repository = JsonProjectRepository(path)

    # ハンドラーの作成
    ai_tool_handler = AIToolHandler(ai_tool_repository)
    project_handler = ProjectHandler(project_repository)

    # データマネージャーの作成
    return DataManager(ai_tool_handler, project_handler)
