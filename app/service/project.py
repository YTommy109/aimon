"""プロジェクト作成に関するビジネスロジックを提供するモジュール。"""

import logging

from app.errors import RequiredFieldsEmptyError
from app.model import DataManager, Project

logger = logging.getLogger('aiman')


def handle_project_creation(
    name: str,
    source: str,
    ai_tool: str,
    data_manager: DataManager,
) -> tuple[Project | None, str]:
    """プロジェクト作成フォームのロジックを処理します。

    入力値を検証し、問題なければプロジェクトを作成します。

    Args:
        name: プロジェクト名。
        source: 処理対象のディレクトリパス。
        ai_tool: 使用するAIツールのID。
        data_manager: DataManagerのインスタンス。

    Returns:
        作成されたプロジェクトオブジェクトと、表示用のメッセージのタプル。
        作成に失敗した場合は、プロジェクトオブジェクトはNoneになります。

    Raises:
        RequiredFieldsEmptyError: 必須フィールドが入力されていない場合。
    """
    if not all([name, source, ai_tool]):
        raise RequiredFieldsEmptyError()

    try:
        project = data_manager.create_project(name, source, ai_tool)
        return project, f'プロジェクト「{project.name}」を作成しました。'
    except Exception as e:
        logger.error(f'プロジェクト作成中にエラーが発生しました: {e}')
        return None, f'プロジェクトの作成に失敗しました: {e}'
