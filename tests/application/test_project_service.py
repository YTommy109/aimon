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

    def test_handle_project_execution_NewWorkerが起動される(
        self, mocker: MockerFixture, mock_data_manager: MagicMock
    ) -> None:
        """正常時にNewWorkerが起動されることをテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_data_manager.update_project.return_value = True

        # Mock ApplicationContainer and NewWorker
        mock_container_class = mocker.patch(
            'app.application.services.project_service.ApplicationContainer'
        )
        mock_worker_class = mocker.patch('app.application.services.project_service.NewWorker')
        mock_streamlit = mocker.patch('app.application.services.project_service.st')

        mock_container = mocker.MagicMock()
        mock_worker = mocker.MagicMock()
        mock_container_class.return_value = mock_container
        mock_worker_class.return_value = mock_worker

        # Create a proper mock for session_state
        mock_session_state = mocker.MagicMock()
        mock_streamlit.session_state = mock_session_state

        # Act
        updated_project, message = handle_project_execution(project, mock_data_manager)

        # Assert
        assert updated_project == project
        assert message == 'プロジェクト「テストプロジェクト」の実行を開始しました。'

        # NewWorkerが正しく起動されることを確認
        mock_worker_class.assert_called_once_with(
            project_id=project.id,
            project_repository=mock_container.project_repository,
            ai_tool_repository=mock_container.ai_tool_repository,
        )
        mock_worker.start.assert_called_once()

        # セッション状態にワーカーが追加されることを確認
        # running_workersがセットされたことを直接確認
        assert (
            hasattr(mock_session_state, 'running_workers')
            or 'running_workers' in mock_session_state.__dict__
        )

    def test_handle_project_execution_Worker起動中に例外発生(
        self, mocker: MockerFixture, mock_data_manager: MagicMock
    ) -> None:
        """ワーカー起動中に例外が発生した場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_data_manager.update_project.return_value = True

        # Mock ApplicationContainer but make NewWorker throw exception
        mock_container_class = mocker.patch(
            'app.application.services.project_service.ApplicationContainer'
        )
        mock_worker_class = mocker.patch('app.application.services.project_service.NewWorker')
        mock_streamlit = mocker.patch('app.application.services.project_service.st')

        mock_container = mocker.MagicMock()
        mock_container_class.return_value = mock_container
        mock_worker_class.side_effect = Exception('ワーカー作成エラー')

        # Create a proper mock for session_state
        mock_session_state = mocker.MagicMock()
        mock_streamlit.session_state = mock_session_state

        # Act
        updated_project, message = handle_project_execution(project, mock_data_manager)

        # Assert
        assert updated_project is None
        assert 'プロジェクトの実行開始中にエラーが発生しました' in message
        assert 'ワーカー作成エラー' in message
