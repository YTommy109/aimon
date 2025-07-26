"""ProjectServiceのテスト。"""

from unittest.mock import Mock, patch

from app.errors import ResourceNotFoundError
from app.models.project import Project
from app.services.ai_tool_service import AIToolService
from app.services.project_service import ProjectService


class TestProjectService:
    """ProjectServiceのテストクラス。"""

    def setup_method(self) -> None:
        """テストメソッドの前処理。"""
        self.mock_repository = Mock()
        self.mock_ai_tool_service = Mock(spec=AIToolService)
        self.project_service = ProjectService(self.mock_repository, self.mock_ai_tool_service)

    def test_プロジェクトが正常に作成される(self) -> None:
        """プロジェクトが正常に作成されることをテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = 'test_tool'

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is not None
        assert result.name == name
        assert result.source == source
        assert result.ai_tool == ai_tool
        self.mock_repository.save.assert_called_once()

    def test_無効な入力でプロジェクト作成が失敗する(self) -> None:
        """無効な入力でプロジェクト作成が失敗することをテストする。"""
        # Arrange
        name = ''
        source = '/path/to/source'
        ai_tool = 'test_tool'

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None
        self.mock_repository.save.assert_not_called()

    def test_空のソースディレクトリでプロジェクト作成が失敗する(self) -> None:
        """空のソースディレクトリでプロジェクト作成が失敗することをテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = ''
        ai_tool = 'test_tool'

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None
        self.mock_repository.save.assert_not_called()

    def test_空のAIツールでプロジェクト作成が失敗する(self) -> None:
        """空のAIツールでプロジェクト作成が失敗することをテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = ''

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None
        self.mock_repository.save.assert_not_called()

    def test_空白文字のみの入力でプロジェクト作成が失敗する(self) -> None:
        """空白文字のみの入力でプロジェクト作成が失敗することをテストする。"""
        # Arrange
        name = '   '
        source = '/path/to/source'
        ai_tool = 'test_tool'

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None
        self.mock_repository.save.assert_not_called()

    def test_プロジェクト作成時に例外が発生する(self) -> None:
        """プロジェクト作成時に例外が発生することをテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = 'test_tool'
        self.mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = self.project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None

    def test_全プロジェクトが正常に取得される(self) -> None:
        """全プロジェクトが正常に取得されることをテストする。"""
        # Arrange
        projects = [
            Project(name='プロジェクト1', source='/path1', ai_tool='tool1'),
            Project(name='プロジェクト2', source='/path2', ai_tool='tool2'),
        ]
        self.mock_repository.find_all.return_value = projects

        # Act
        result = self.project_service.get_all_projects()

        # Assert
        assert result == projects

    def test_IDでプロジェクトが正常に取得される(self) -> None:
        """IDでプロジェクトが正常に取得されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        self.mock_repository.find_by_id.return_value = project

        # Act
        result = self.project_service.get_project_by_id('12345678-1234-1234-1234-123456789012')

        # Assert
        assert result is not None
        assert result.name == 'テストプロジェクト'

    def test_無効なIDでプロジェクト取得が失敗する(self) -> None:
        """無効なIDでプロジェクト取得が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = ResourceNotFoundError(
            'Project', 'invalid-uuid'
        )

        # Act
        result = self.project_service.get_project_by_id('invalid-uuid')

        # Assert
        assert result is None

    def test_ValueErrorでプロジェクト取得が失敗する(self) -> None:
        """ValueErrorでプロジェクト取得が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = ValueError('Invalid UUID')

        # Act
        result = self.project_service.get_project_by_id('invalid-uuid')

        # Assert
        assert result is None

    def test_Exceptionでプロジェクト取得が失敗する(self) -> None:
        """Exceptionでプロジェクト取得が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = Exception('Database error')

        # Act
        result = self.project_service.get_project_by_id('12345678-1234-1234-1234-123456789012')

        # Assert
        assert result is None

    @patch('app.services.project_service.AsyncGenericAIToolExecutor')
    def test_プロジェクトが正常に実行される(self, mock_executor_class: Mock) -> None:
        """プロジェクトが正常に実行されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        self.mock_repository.find_by_id.return_value = project

        # AIツールサービスのモック設定
        mock_ai_tool = Mock()
        mock_ai_tool.id = 'test_tool'
        mock_ai_tool.endpoint_url = 'https://api.example.com/test'
        self.mock_ai_tool_service.get_ai_tool_by_id.return_value = mock_ai_tool

        # AsyncGenericAIToolExecutorのモック設定
        mock_executor = Mock()
        mock_executor.execute.return_value = {
            'success': True,
            'data': {'summary': 'AIツール実行が完了しました。'},
            'project_id': '12345678-1234-1234-1234-123456789012',
            'source_path': '/path/to/source',
            'ai_tool_id': 'test_tool',
            'endpoint_url': 'https://api.example.com/test',
        }
        mock_executor_class.return_value = mock_executor

        # Act
        result, message = self.project_service.execute_project(
            '12345678-1234-1234-1234-123456789012'
        )

        # Assert
        assert result is not None
        assert result.name == 'テストプロジェクト'
        assert message == 'プロジェクトの実行が完了しました。'
        self.mock_repository.save.assert_called_once()
        mock_executor_class.assert_called_once_with('test_tool', 'https://api.example.com/test')
        mock_executor.execute.assert_called_once()

    def test_無効なIDでプロジェクト実行が失敗する(self) -> None:
        """無効なIDでプロジェクト実行が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = ValueError('Invalid UUID')

        # Act
        result, message = self.project_service.execute_project('invalid-uuid')

        # Assert
        assert result is None
        assert message == '無効なプロジェクトIDです。'

    def test_存在しないプロジェクトでプロジェクト実行が失敗する(self) -> None:
        """存在しないプロジェクトでプロジェクト実行が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = ResourceNotFoundError('Project', 'not-found')

        # Act
        result, message = self.project_service.execute_project(
            '12345678-1234-1234-1234-123456789012'
        )

        # Assert
        assert result is None
        assert message == 'プロジェクトが見つかりません。'

    def test_存在しないAIツールでプロジェクト実行が失敗する(self) -> None:
        """存在しないAIツールでプロジェクト実行が失敗することをテストする。"""
        # Arrange
        project = Project(
            name='テストプロジェクト', source='/path/to/source', ai_tool='non-existent'
        )
        self.mock_repository.find_by_id.return_value = project

        # AIツールが見つからない場合のモック設定
        self.mock_ai_tool_service.get_ai_tool_by_id.side_effect = ValueError(
            'AIツールが見つかりません'
        )

        # Act
        result, message = self.project_service.execute_project(
            '12345678-1234-1234-1234-123456789012'
        )

        # Assert
        assert result is None
        assert message == 'AIツール non-existent が見つかりません。'

    def test_Exceptionでプロジェクト実行が失敗する(self) -> None:
        """Exceptionでプロジェクト実行が失敗することをテストする。"""
        # Arrange
        self.mock_repository.find_by_id.side_effect = Exception('Database error')

        # Act
        result, message = self.project_service.execute_project(
            '12345678-1234-1234-1234-123456789012'
        )

        # Assert
        assert result is None
        assert message == 'プロジェクトが見つかりません。'

    def test_プロジェクトが見つからない場合の実行失敗(self) -> None:
        """プロジェクトが見つからない場合の実行失敗をテストする。"""
        # Arrange
        self.mock_repository.find_by_id.return_value = None

        # Act
        result, message = self.project_service.execute_project(
            '12345678-1234-1234-1234-123456789012'
        )

        # Assert
        assert result is None
        assert message == 'プロジェクトが見つかりません。'
