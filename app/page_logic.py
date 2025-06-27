import logging
from typing import Tuple
from uuid import UUID

from app.data_manager import DataManager, Project
from app.worker import Worker

logger = logging.getLogger('aiman')
running_workers: dict[UUID, Worker] = {}


def handle_project_creation(
    name: str, source: str, ai_tool: str, data_manager: DataManager
) -> Tuple[Project | None, str]:
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
    """
    if not all([name, source, ai_tool]):
        return None, 'すべてのフィールドを入力してください。'

    try:
        project = data_manager.create_project(name, source, ai_tool)
        return project, f'プロジェクト「{project.name}」を作成しました。'
    except Exception as e:
        logger.error(f'プロジェクト作成中にエラーが発生しました: {e}')
        return None, f'プロジェクトの作成に失敗しました: {e}'


def handle_project_execution(
    project_id: UUID | None,
    data_manager: DataManager,
    running_workers: dict[UUID, Worker],
) -> Tuple[Worker | None, str]:
    """プロジェクト実行ボタンのロジックを処理します。

    プロジェクトIDの検証、多重実行の防止を行い、問題なければワーカースレッドを開始します。

    Args:
        project_id: 実行するプロジェクトのID。
        data_manager: DataManagerのインスタンス。
        running_workers: 現在実行中のワーカーを保持する辞書。

    Returns:
        開始されたワーカーインスタンスと、表示用のメッセージのタプル。
        開始に失敗した場合は、ワーカーインスタンスはNoneになります。
    """
    if not project_id:
        return None, 'プロジェクトを選択してください。'

    if project_id in running_workers:
        return None, 'このプロジェクトは既に実行中です。'

    try:
        worker = Worker(project_id, data_manager)
        running_workers[project_id] = worker
        worker.start()
        return worker, f'プロジェクト {project_id} を実行します。'
    except Exception as e:
        # TODO: より具体的な例外処理
        return None, f'ワーカーの起動に失敗しました: {e}'
