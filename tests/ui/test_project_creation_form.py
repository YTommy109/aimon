"""プロジェクト作成フォームのテスト。"""

from unittest.mock import Mock
from uuid import UUID

import pytest

from app.errors import ResourceNotFoundError
from app.models import AIToolID
from app.models.ai_tool import AITool
from app.models.project import Project
from app.services.ai_tool_service import AIToolService
from app.services.project_service import ProjectService
from app.ui import project_creation_form


class TestProjectCreationForm:
    """プロジェクト作成フォームのテストクラス。"""

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """モックAIツールサービスを作成する。"""
        return Mock(spec=AIToolService)

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """モックプロジェクトサービスを作成する。"""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def sample_ai_tools(self) -> list[AITool]:
        """サンプルAIツールを作成する。"""
        return [
            AITool(
                name_ja='テストツール1',
                description='テスト用のAIツール',
                command='curl -X GET https://api.example.com/test1',
            ),
            AITool(
                name_ja='テストツール2',
                description='テスト用のAIツール2',
                command='curl -X GET https://api.example.com/test2',
            ),
        ]

    def test_AIツールオプションが正しく作成される(self, sample_ai_tools: list[AITool]) -> None:
        """AIツールオプションが正しく作成されることをテスト。"""
        # Act
        all_options, ai_tool_options = project_creation_form._create_ai_tool_options(
            sample_ai_tools
        )

        # Assert
        assert len(all_options) == 3  # 2つのツール + セパレータ
        assert len(ai_tool_options) == 2
        assert all_options[0] == sample_ai_tools[0].id
        assert all_options[1] == sample_ai_tools[1].id
        assert all_options[2] is None  # セパレータ
        assert ai_tool_options[sample_ai_tools[0].id] == 'テストツール1 (テスト用のAIツール)'
        assert ai_tool_options[sample_ai_tools[1].id] == 'テストツール2 (テスト用のAIツール2)'

    def test_AIツールフォーマットが正しく動作する(self, sample_ai_tools: list[AITool]) -> None:
        """AIツールフォーマットが正しく動作することをテスト。"""
        # Arrange
        _, ai_tool_options = project_creation_form._create_ai_tool_options(sample_ai_tools)

        # Act
        result = project_creation_form._format_ai_tool(sample_ai_tools[0].id, ai_tool_options)

        # Assert
        assert result == 'テストツール1 (テスト用のAIツール)'

    def test_セパレータのフォーマットが正しく動作する(self, sample_ai_tools: list[AITool]) -> None:
        """セパレータのフォーマットが正しく動作することをテスト。"""
        # Arrange
        _, ai_tool_options = project_creation_form._create_ai_tool_options(sample_ai_tools)

        # Act
        result = project_creation_form._format_ai_tool(None, ai_tool_options)

        # Assert
        assert result == '--- 内蔵ツール ---'

    def test_有効な入力値の検証が成功する(self) -> None:
        """有効な入力値の検証が成功することをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is True
        assert error_message == ''

    def test_無効な入力値の検証が失敗する(self) -> None:
        """無効な入力値の検証が失敗することをテスト。"""
        # Arrange
        project_name = ''
        source_dir = '/test/path'
        selected_ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください' in error_message

    def test_AIツールが選択されていない場合の検証が失敗する(self) -> None:
        """AIツールが選択されていない場合の検証が失敗することをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = None

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'AIツールを選択してください' in error_message

    def test_AIツールの存在確認が成功する(self, mock_ai_tool_service: Mock) -> None:
        """AIツールの存在確認が成功することをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.get_ai_tool_by_id.return_value = Mock()

        # Act
        result = project_creation_form._validate_ai_tool_exists(
            AIToolID(ai_tool_id), mock_ai_tool_service
        )

        # Assert
        assert result is True
        mock_ai_tool_service.get_ai_tool_by_id.assert_called_once_with(ai_tool_id)

    def test_AIツールの存在確認が失敗する(self, mock_ai_tool_service: Mock) -> None:
        """AIツールの存在確認が失敗することをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = ResourceNotFoundError(
            'AIツール', AIToolID(ai_tool_id)
        )

        # Act
        result = project_creation_form._validate_ai_tool_exists(
            AIToolID(ai_tool_id), mock_ai_tool_service
        )

        # Assert
        assert result is False

    def test_プロジェクト作成の検証が成功する(
        self, mock_project_service: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """プロジェクト作成の検証が成功することをテスト。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_ai_tool_service.get_ai_tool_by_id.return_value = Mock()
        mock_project_service.create_project.return_value = project

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is True
        assert message == 'プロジェクトを作成しました。'

    def test_AIツールが見つからない場合のプロジェクト作成が失敗する(
        self, mock_project_service: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """AIツールが見つからない場合のプロジェクト作成が失敗することをテスト。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = Exception('AIツールが見つかりません')

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is False
        assert message == '選択されたAIツールが見つかりません。'

    def test_プロジェクト作成が失敗する場合(
        self, mock_project_service: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """プロジェクト作成が失敗する場合をテスト。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_ai_tool_service.get_ai_tool_by_id.return_value = Mock()
        mock_project_service.create_project.return_value = None

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is False
        assert message == 'プロジェクトの作成に失敗しました。'

    def test_ProjectFormInputsが正しく作成される(self) -> None:
        """ProjectFormInputsが正しく作成されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        inputs = project_creation_form.ProjectFormInputs(
            project_name=project_name,
            source_dir=source_dir,
            selected_ai_tool_id=selected_ai_tool_id,
        )

        # Assert
        assert inputs.project_name == project_name
        assert inputs.source_dir == source_dir
        assert inputs.selected_ai_tool_id == selected_ai_tool_id

    def test_AIツールの存在確認で例外が発生した場合(self, mock_ai_tool_service: Mock) -> None:
        """AIツールの存在確認で例外が発生した場合をテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = Exception('予期しないエラー')

        # Act
        result = project_creation_form._validate_ai_tool_exists(
            AIToolID(ai_tool_id), mock_ai_tool_service
        )

        # Assert
        assert result is False

    def test_プロジェクト作成で例外が発生した場合(
        self, mock_project_service: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """プロジェクト作成で例外が発生した場合をテスト。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        mock_ai_tool_service.get_ai_tool_by_id.return_value = Mock()
        mock_project_service.create_project.side_effect = Exception('プロジェクト作成エラー')

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is False
        assert message == 'プロジェクトの作成に失敗しました。'

    def test_空のAIツールリストでオプションが作成される(self) -> None:
        """空のAIツールリストでオプションが作成されることをテスト。"""
        # Act
        all_options, ai_tool_options = project_creation_form._create_ai_tool_options([])

        # Assert
        assert len(all_options) == 0  # 空のリスト
        assert len(ai_tool_options) == 0
