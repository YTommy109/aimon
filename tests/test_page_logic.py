"""ページロジックのテスト。"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.model import Project, ProjectStatus
from app.page_logic import handle_project_creation, handle_project_execution


@pytest.fixture
def mock_data_manager() -> MagicMock:
    """DataManagerのモックを提供するフィクスチャ"""
    return MagicMock()


def test_プロジェクト作成が正常に成功する(mock_data_manager: MagicMock) -> None:
    # Arrange
    name = 'Test Project'
    source = '/path'
    ai_tool = 'test_tool'
    mock_project = Project(name=name, source=source, ai_tool=ai_tool)
    mock_data_manager.create_project.return_value = mock_project

    # Act
    project, message = handle_project_creation(name, source, ai_tool, mock_data_manager)

    # Assert
    assert project is not None
    assert project.name == name
    assert project.status == ProjectStatus.PENDING  # 作成直後は Pending 状態
    assert '作成しました' in message
    mock_data_manager.create_project.assert_called_once_with(name, source, ai_tool)


def test_プロジェクト作成時に入力が不足している場合にエラーメッセージを返す(
    mock_data_manager: MagicMock,
) -> None:
    # Arrange
    name = ''
    source = '/path'
    ai_tool = 'test_tool'

    # Act & Assert
    with pytest.raises(ValueError, match='すべてのフィールドを入力してください'):
        handle_project_creation(name, source, ai_tool, mock_data_manager)

    mock_data_manager.create_project.assert_not_called()


def test_データマネージャが例外を発生させた場合にエラーメッセージを返す(
    mock_data_manager: MagicMock,
) -> None:
    # Arrange
    name = 'Test Project'
    source = '/path'
    ai_tool = 'test_tool'
    error_message = 'DB connection failed'
    mock_data_manager.create_project.side_effect = Exception(error_message)

    # Act
    project, message = handle_project_creation(name, source, ai_tool, mock_data_manager)

    # Assert
    assert project is None
    assert '作成に失敗しました' in message
    assert error_message in message
    mock_data_manager.create_project.assert_called_once_with(name, source, ai_tool)


@pytest.fixture
def mock_worker() -> MagicMock:
    """Workerのモックを提供するフィクスチャ"""
    worker_mock = MagicMock()
    worker_mock.start = MagicMock()
    # モックされたworkerのproject_idが、後で代入されるように設定
    worker_mock.project_id = None
    return worker_mock


def test_プロジェクト実行が正常に成功する(
    mock_data_manager: MagicMock, mock_worker: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    project_id = uuid4()
    # `Worker`クラスのコンストラクタが、モックされたworkerインスタンスを
    # 返すように差し替える
    monkeypatch.setattr('app.page_logic.Worker', lambda *args: mock_worker)
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
    worker.start.assert_called_once()  # type: ignore[attr-defined]
    assert project.status == ProjectStatus.PENDING  # 実行前は Pending 状態


def test_プロジェクトIDが未選択の場合にエラーメッセージを返す(
    mock_data_manager: MagicMock,
) -> None:
    # Act & Assert
    with pytest.raises(ValueError, match='プロジェクトを選択してください'):
        handle_project_execution(None, mock_data_manager, running_workers={})


def test_プロジェクトが既に実行中の場合にエラーメッセージを返す(
    mock_data_manager: MagicMock,
) -> None:
    # Arrange
    project_id = uuid4()
    running_workers = {project_id: MagicMock()}

    # Act & Assert
    with pytest.raises(RuntimeError, match='このプロジェクトは既に実行中です'):
        handle_project_execution(
            project_id,
            mock_data_manager,
            running_workers,  # type: ignore
        )
