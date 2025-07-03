"""プロジェクト実行サービスのテスト。"""

from typing import Never
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.errors import ProjectAlreadyRunningError, WorkerError
from app.model import Project, ProjectStatus
from app.service.execution import handle_project_execution
from app.worker import Worker


@pytest.fixture
def mock_data_manager() -> MagicMock:
    """DataManagerのモックを提供するフィクスチャ"""
    return MagicMock()


@pytest.fixture
def mock_worker() -> MagicMock:
    """Workerのモックを提供するフィクスチャ"""
    worker_mock = MagicMock(spec=Worker)
    worker_mock.start = MagicMock()
    # モックされたworkerのproject_idが、後で代入されるように設定
    worker_mock.project_id = None
    return worker_mock


def test_プロジェクト実行が正常に成功する(
    mock_data_manager: MagicMock,
    mock_worker: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    project_id = uuid4()
    # `Worker`クラスのコンストラクタが、モックされたworkerインスタンスを
    # 返すように差し替える
    monkeypatch.setattr('app.service.execution.Worker', lambda *args: mock_worker)
    mock_worker.project_id = project_id

    # Project インスタンスを作成し、必要な属性を設定
    project = Project(
        id=project_id,
        name='Test Project',
        source='/path',
        ai_tool='test_tool',
    )
    mock_data_manager.get_project.return_value = project

    # Act
    worker, message = handle_project_execution(project_id, mock_data_manager, running_workers={})

    # Assert
    assert worker is mock_worker
    assert '実行します' in message
    mock_worker.start.assert_called_once()
    assert project.status == ProjectStatus.PENDING  # 実行前は Pending 状態


def test_プロジェクトが既に実行中の場合にエラーメッセージを返す(
    mock_data_manager: MagicMock,
) -> None:
    # Arrange
    project_id = uuid4()
    mock_worker = MagicMock(spec=Worker)
    running_workers = {project_id: mock_worker}

    # Act & Assert
    with pytest.raises(
        ProjectAlreadyRunningError,
        match=f'プロジェクト {project_id} は既に実行中です',
    ):
        handle_project_execution(
            project_id,
            mock_data_manager,
            running_workers,
        )


def test_ワーカーエラーが発生した場合にNoneとエラーメッセージを返す(
    mock_data_manager: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    project_id = uuid4()
    error_message = 'ワーカー初期化に失敗しました'

    def failing_worker(*args: object) -> Never:
        raise WorkerError(error_message)

    monkeypatch.setattr('app.service.execution.Worker', failing_worker)

    # Act
    worker, message = handle_project_execution(project_id, mock_data_manager, running_workers={})

    # Assert
    assert worker is None
    assert 'ワーカーの起動に失敗しました' in message
    assert error_message in message


def test_予期せぬエラーが発生した場合にNoneとエラーメッセージを返す(
    mock_data_manager: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    project_id = uuid4()
    error_message = '予期しない例外が発生'

    def failing_worker(*args: object) -> Never:
        raise RuntimeError(error_message)

    monkeypatch.setattr('app.service.execution.Worker', failing_worker)

    # Act
    worker, message = handle_project_execution(project_id, mock_data_manager, running_workers={})

    # Assert
    assert worker is None
    assert '予期せぬエラーが発生しました' in message
    assert error_message in message
