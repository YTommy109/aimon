"""ProjectServiceのテスト。"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.application.data_manager import DataManager
from app.application.services.project_service import (
    _validate_project_input,
    handle_project_creation,
    handle_project_execution,
)
from app.domain.entities import Project


class TestProjectService:
    """ProjectServiceのテスト。"""

    @pytest.fixture
    def mock_data_manager(self, mocker: MockerFixture) -> MagicMock:
        """DataManagerのモックを提供するフィクスチャ。"""
        return mocker.MagicMock(spec=DataManager)

    # _validate_project_inputのテスト

    def test_validate_project_input_すべて有効(self) -> None:
        """すべての入力が有効な場合のテスト。"""
        # Act
        result = _validate_project_input('プロジェクト名', '/source/path', 'ai-tool')

        # Assert
        assert result is None

    def test_validate_project_input_名前が空(self) -> None:
        """名前が空の場合のテスト。"""
        # Act
        result = _validate_project_input('', '/source/path', 'ai-tool')

        # Assert
        assert result == 'プロジェクト名を入力してください。'

    def test_validate_project_input_名前が空白のみ(self) -> None:
        """名前が空白のみの場合のテスト。"""
        # Act
        result = _validate_project_input('   ', '/source/path', 'ai-tool')

        # Assert
        assert result == 'プロジェクト名を入力してください。'

    def test_validate_project_input_ソースが空(self) -> None:
        """ソースが空の場合のテスト。"""
        # Act
        result = _validate_project_input('プロジェクト名', '', 'ai-tool')

        # Assert
        assert result == 'ソースディレクトリパスを入力してください。'

    def test_validate_project_input_ソースが空白のみ(self) -> None:
        """ソースが空白のみの場合のテスト。"""
        # Act
        result = _validate_project_input('プロジェクト名', '   ', 'ai-tool')

        # Assert
        assert result == 'ソースディレクトリパスを入力してください。'

    def test_validate_project_input_AIツールが空(self) -> None:
        """AIツールが空の場合のテスト。"""
        # Act
        result = _validate_project_input('プロジェクト名', '/source/path', '')

        # Assert
        assert result == 'AIツールを選択してください。'

    def test_validate_project_input_AIツールが空白のみ(self) -> None:
        """AIツールが空白のみの場合のテスト。"""
        # Act
        result = _validate_project_input('プロジェクト名', '/source/path', '   ')

        # Assert
        assert result == 'AIツールを選択してください。'

    # handle_project_creationのテスト

    def test_handle_project_creation_成功(self, mock_data_manager: MagicMock) -> None:
        """プロジェクト作成が成功する場合のテスト。"""
        # Arrange
        expected_project = Project(
            name='テストプロジェクト', source='/test/path', ai_tool='test-tool'
        )
        mock_data_manager.create_project.return_value = expected_project

        # Act
        project, message = handle_project_creation(
            'テストプロジェクト', '/test/path', 'test-tool', mock_data_manager
        )

        # Assert
        assert project == expected_project
        assert message == 'プロジェクト「テストプロジェクト」を作成しました。'
        mock_data_manager.create_project.assert_called_once_with(
            'テストプロジェクト', '/test/path', 'test-tool'
        )

    def test_handle_project_creation_名前が空(self, mock_data_manager: MagicMock) -> None:
        """名前が空の場合のテスト。"""
        # Act
        project, message = handle_project_creation('', '/test/path', 'test-tool', mock_data_manager)

        # Assert
        assert project is None
        assert message == 'プロジェクト名を入力してください。'
        mock_data_manager.create_project.assert_not_called()

    def test_handle_project_creation_ソースが空(self, mock_data_manager: MagicMock) -> None:
        """ソースが空の場合のテスト。"""
        # Act
        project, message = handle_project_creation(
            'テストプロジェクト', '', 'test-tool', mock_data_manager
        )

        # Assert
        assert project is None
        assert message == 'ソースディレクトリパスを入力してください。'
        mock_data_manager.create_project.assert_not_called()

    def test_handle_project_creation_AIツールが空(self, mock_data_manager: MagicMock) -> None:
        """AIツールが空の場合のテスト。"""
        # Act
        project, message = handle_project_creation(
            'テストプロジェクト', '/test/path', '', mock_data_manager
        )

        # Assert
        assert project is None
        assert message == 'AIツールを選択してください。'
        mock_data_manager.create_project.assert_not_called()

    def test_handle_project_creation_空白を含む入力(self, mock_data_manager: MagicMock) -> None:
        """空白を含む入力の場合のテスト(空白が除去される)。"""
        # Arrange
        expected_project = Project(
            name='テストプロジェクト', source='/test/path', ai_tool='test-tool'
        )
        mock_data_manager.create_project.return_value = expected_project

        # Act
        project, message = handle_project_creation(
            '  テストプロジェクト  ', '  /test/path  ', 'test-tool', mock_data_manager
        )

        # Assert
        assert project == expected_project
        assert message == 'プロジェクト「テストプロジェクト」を作成しました。'
        mock_data_manager.create_project.assert_called_once_with(
            'テストプロジェクト', '/test/path', 'test-tool'
        )

    def test_handle_project_creation_作成失敗(self, mock_data_manager: MagicMock) -> None:
        """プロジェクト作成が失敗する場合のテスト。"""
        # Arrange
        mock_data_manager.create_project.return_value = None

        # Act
        project, message = handle_project_creation(
            'テストプロジェクト', '/test/path', 'test-tool', mock_data_manager
        )

        # Assert
        assert project is None
        assert message == 'プロジェクトの作成に失敗しました。'
        mock_data_manager.create_project.assert_called_once_with(
            'テストプロジェクト', '/test/path', 'test-tool'
        )

    # handle_project_executionのテスト

    def test_handle_project_execution_成功(self, mock_data_manager: MagicMock) -> None:
        """プロジェクト実行が成功する場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_data_manager.update_project.return_value = True

        # Act
        updated_project, message = handle_project_execution(project, mock_data_manager)

        # Assert
        assert updated_project == project
        assert message == 'プロジェクト「テストプロジェクト」の実行を開始しました。'
        assert project.executed_at is not None  # start_processingが呼ばれた証拠
        mock_data_manager.update_project.assert_called_once_with(project)

    def test_handle_project_execution_更新失敗(self, mock_data_manager: MagicMock) -> None:
        """プロジェクト更新が失敗する場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_data_manager.update_project.return_value = False

        # Act
        updated_project, message = handle_project_execution(project, mock_data_manager)

        # Assert
        assert updated_project is None
        assert message == 'プロジェクトの実行開始に失敗しました。'
        mock_data_manager.update_project.assert_called_once_with(project)

    def test_handle_project_execution_例外発生(self, mock_data_manager: MagicMock) -> None:
        """例外が発生する場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_data_manager.update_project.side_effect = Exception('データベースエラー')

        # Act
        updated_project, message = handle_project_execution(project, mock_data_manager)

        # Assert
        assert updated_project is None
        assert 'プロジェクトの実行開始中にエラーが発生しました' in message
        assert 'データベースエラー' in message
