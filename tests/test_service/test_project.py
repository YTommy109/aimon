"""プロジェクト作成サービスのテスト。"""

from unittest.mock import MagicMock

import pytest

from app.errors import RequiredFieldsEmptyError
from app.model import Project, ProjectStatus
from app.service.project import handle_project_creation


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
    with pytest.raises(RequiredFieldsEmptyError, match='すべてのフィールドを入力してください'):
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
