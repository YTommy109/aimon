"""プロジェクト実行に関するビジネスロジックを提供するモジュール。"""

import logging
from collections.abc import Mapping
from typing import Final
from uuid import UUID

from app.errors import ProjectAlreadyRunningError, WorkerError
from app.model import DataManager
from app.worker import Worker

logger = logging.getLogger('aiman')
running_workers: Final[dict[UUID, Worker]] = {}


def handle_project_execution(
    project_id: UUID,
    data_manager: DataManager,
    running_workers: Mapping[UUID, Worker],
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
        running_workers[project_id] = worker  # type: ignore[index]
        worker.start()
        return worker, f'プロジェクト {project_id} を実行します。'
    except WorkerError as e:
        logger.error(f'ワーカーの起動に失敗しました: {e}')
        return None, f'ワーカーの起動に失敗しました: {e}'
    except Exception as e:
        logger.error(f'予期せぬエラーが発生しました: {e}')
        return None, f'予期せぬエラーが発生しました: {e}'
