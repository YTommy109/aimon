"""プロジェクトサービスのテストモジュール。"""

from unittest.mock import Mock
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from app.errors import ResourceNotFoundError
from app.models import AIToolID
from app.models.ai_tool import AITool
from app.models.project import Project
from app.services.project_service import ProjectService


class TestProjectService:
    """プロジェクトサービスのテストクラス。"""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """プロジェクトリポジトリのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """AIツールサービスのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def project_service(self, mock_repository: Mock, mock_ai_tool_service: Mock) -> ProjectService:
        """プロジェクトサービスを作成する。"""
        return ProjectService(mock_repository, mock_ai_tool_service)

    def test_プロジェクトを作成できる(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """プロジェクトを作成できることをテスト。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        created_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_repository.save.return_value = created_project

        # Act
        result = project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is not None
        assert result.name == 'テストプロジェクト'
        assert result.source == '/path/to/source'
        mock_repository.save.assert_called_once()

    def test_無効な入力でプロジェクト作成が失敗する(self, project_service: ProjectService) -> None:
        """無効な入力でプロジェクト作成が失敗することをテスト。"""
        # Arrange
        name = ''  # 空の名前
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        result = project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None

    def test_空のAIツールでプロジェクト作成が成功する(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """空のAIツールでプロジェクト作成が成功することをテスト。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('00000000-0000-0000-0000-000000000000'))  # 空のUUID

        # Act
        result = project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is not None
        assert result.name == name
        assert result.source == source
        assert result.ai_tool == ai_tool
        mock_repository.save.assert_called_once_with(result)

    def test_プロジェクト作成でエラーが発生した場合はNoneを返す(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """プロジェクト作成でエラーが発生した場合はNoneを返すことをテスト。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.save.side_effect = Exception('データベースエラー')

        # Act
        result = project_service.create_project(name, source, ai_tool)

        # Assert
        assert result is None

    def test_全プロジェクトを取得できる(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """全プロジェクトを取得できることをテスト。"""
        # Arrange
        projects = [
            Project(
                name='プロジェクト1',
                source='/path/to/source1',
                ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
            ),
            Project(
                name='プロジェクト2',
                source='/path/to/source2',
                ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345679')),
            ),
        ]
        mock_repository.find_all.return_value = projects

        # Act
        result = project_service.get_all_projects()

        # Assert
        assert len(result) == 2
        assert result[0].name == 'プロジェクト1'
        assert result[1].name == 'プロジェクト2'

    def test_プロジェクトが存在しない場合は空のリストを返す(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """プロジェクトが存在しない場合は空のリストを返すことをテスト。"""
        # Arrange
        mock_repository.find_all.return_value = []

        # Act
        result = project_service.get_all_projects()

        # Assert
        assert len(result) == 0

    def test_IDでプロジェクトを取得できる(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """IDでプロジェクトを取得できることをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_repository.find_by_id.return_value = project

        # Act
        result = project_service.get_project_by_id(str(project_id))

        # Assert
        assert result is not None
        assert result.name == 'テストプロジェクト'

    def test_無効なIDでプロジェクトを取得するとNoneを返す(
        self, project_service: ProjectService
    ) -> None:
        """無効なIDでプロジェクトを取得するとNoneを返すことをテスト。"""
        # Arrange
        invalid_id = 'invalid-uuid'

        # Act
        result = project_service.get_project_by_id(invalid_id)

        # Assert
        assert result is None

    def test_存在しないIDでプロジェクトを取得するとNoneを返す(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """存在しないIDでプロジェクトを取得するとNoneを返すことをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_repository.find_by_id.side_effect = ResourceNotFoundError(
            'プロジェクト', str(project_id)
        )

        # Act
        result = project_service.get_project_by_id(str(project_id))

        # Assert
        assert result is None

    def test_プロジェクトを実行できる(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
        mock_ai_tool_service: Mock,
    ) -> None:
        """プロジェクトを実行できることをテスト。"""
        # Arrange
        mock_executor_class = mocker.patch('app.services.project_service.CommandExecutor')
        project_id = UUID('12345678-1234-5678-1234-567812345678')
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        ai_tool = AITool(name_ja='テストツール', command='curl -X GET https://api.example.com/test')

        mock_repository.find_by_id.return_value = project
        mock_ai_tool_service.get_ai_tool_by_id.return_value = ai_tool
        mock_repository.save.return_value = None

        # エグゼキューターのモック
        mock_executor = Mock()
        mock_executor.execute.return_value = {'result': 'success'}
        mock_executor_class.return_value = mock_executor

        # Act
        result_project, message = project_service.execute_project(str(project_id))

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました。'
        mock_repository.save.assert_called()

    def test_存在しないプロジェクトの実行は失敗する(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        """存在しないプロジェクトの実行は失敗することをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_repository.find_by_id.side_effect = ResourceNotFoundError(
            'プロジェクト', str(project_id)
        )

        # Act
        result_project, message = project_service.execute_project(str(project_id))

        # Assert
        assert result_project is None
        assert 'プロジェクトが見つかりません' in message

    def test_存在しないAIツールの実行は失敗する(
        self, project_service: ProjectService, mock_repository: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """存在しないAIツールの実行は失敗することをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        mock_repository.find_by_id.return_value = project
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = ResourceNotFoundError(
            'AIツール', str(UUID('12345678-1234-5678-1234-567812345678'))
        )

        # Act
        result_project, message = project_service.execute_project(str(project_id))

        # Assert
        assert result_project is None
        assert 'AIツール' in message
