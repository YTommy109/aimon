"""ページのビジネスロジックを定義するモジュール。"""

import logging
from typing import Final
from uuid import UUID

from app.errors import (
    ProjectAlreadyRunningError,
    RequiredFieldsEmptyError,
    WorkerError,
)
from app.model import DataManager, Project
from app.worker import Worker

logger = logging.getLogger('aiman')
running_workers: Final[dict[UUID, Worker]] = {}


def handle_project_creation(
    name: str, source: str, ai_tool: str, data_manager: DataManager
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


def handle_project_execution(
    project_id: UUID,
    data_manager: DataManager,
    running_workers: dict[UUID, Worker],
) -> tuple[Worker | None, str]:
    """プロジェクト実行ボタンのロジックを処理します。

    プロジェクトIDの検証、多重実行の防止を行い、問題なければワーカースレッドを開始します。

    Args:
        project_id: 実行するプロジェクトのID。
        data_manager: DataManagerのインスタンス。
        running_workers: 現在実行中のワーカーを保持する辞書。

    Returns:
        開始されたワーカーインスタンスと、表示用のメッセージのタプル。
        開始に失敗した場合は、ワーカーインスタンスはNoneになります。

    Raises:
        ProjectAlreadyRunningError: プロジェクトが既に実行中の場合。
        WorkerError: ワーカーの起動に失敗した場合。
    """
    if project_id in running_workers:
        raise ProjectAlreadyRunningError(project_id)

    try:
        worker = Worker(project_id, data_manager)
        running_workers[project_id] = worker
        worker.start()
        return worker, f'プロジェクト {project_id} を実行します。'
    except WorkerError as e:
        logger.error(f'ワーカーの起動に失敗しました: {e}')
        return None, f'ワーカーの起動に失敗しました: {e}'
    except Exception as e:
        logger.error(f'予期せぬエラーが発生しました: {e}')
        return None, f'予期せぬエラーが発生しました: {e}'


class PageLogic:
    """ページの表示ロジックを管理するクラス。"""

    def __init__(self, data_manager: DataManager) -> None:
        """
        PageLogicを初期化します。

        Args:
            data_manager: データマネージャーのインスタンス。
        """
        self.data_manager = data_manager

    def validate_project_form(self, name: str, source: str, ai_tool: str) -> None:
        """
        プロジェクトフォームの入力値を検証します。

        Args:
            name: プロジェクト名。
            source: ソースディレクトリのパス。
            ai_tool: 使用するAIツール。

        Raises:
            RequiredFieldsEmptyError: 必須フィールドが入力されていない場合。
        """
        if not all([name, source, ai_tool]):
            raise RequiredFieldsEmptyError()
