"""プロジェクト作成フォームのテスト。"""

from unittest.mock import Mock

import pytest

from app.models.project import Project
from app.services.project_service import ProjectService
from app.types import ToolType
from app.ui import project_creation_form


class TestProjectCreationForm:
    """プロジェクト作成フォームのテストクラス。"""

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """モックプロジェクトサービスを作成する。"""
        return Mock(spec=ProjectService)

    def test_有効な入力値の検証が成功する(self) -> None:
        # Arrange
        project_name = 'テストプロジェクト'
        source = '/test/path'
        tool = ToolType.OVERVIEW

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source, tool
        )

        # Assert
        assert is_valid is True
        assert error_message == ''

    def test_内蔵ツールが選択されている場合の検証が成功する(self) -> None:
        # Arrange
        project_name = 'テストプロジェクト'
        source = '/test/path'
        selected_tool_type = ToolType.OVERVIEW

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source, selected_tool_type
        )

        # Assert
        assert is_valid is True
        assert error_message == ''

    def test_無効な入力値の検証が失敗する(self) -> None:
        # Arrange
        project_name = ''  # 空の名前
        source = '/test/path'
        selected_tool_type = ToolType.OVERVIEW

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source, selected_tool_type
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください' in error_message

    def test_内蔵ツールが選択されていない場合の検証が失敗する(self) -> None:
        # Arrange
        project_name = 'テストプロジェクト'
        source = '/test/path'
        selected_tool_type = None  # 内蔵ツールが選択されていない

        # Act
        is_valid, error_message = project_creation_form._validate_project_inputs(
            project_name, source, selected_tool_type
        )

        # Assert
        assert is_valid is False
        assert '内蔵ツールを選択してください' in error_message

    def test_プロジェクト作成の検証が成功する(self, mock_project_service: Mock) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service.create_project.return_value = project

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service
        )

        # Assert
        assert success is True
        assert message == 'プロジェクトを作成しました。'
        mock_project_service.create_project.assert_called_once_with(
            project.name, project.source, project.tool
        )

    def test_プロジェクト作成が失敗する場合(self, mock_project_service: Mock) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service.create_project.return_value = None

        # Act
        success, message = project_creation_form._create_project_with_validation(
            project, mock_project_service
        )

        # Assert
        assert success is False
        assert message == 'プロジェクトの作成に失敗しました。'

    def test_ProjectFormInputsが正しく作成される(self) -> None:
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_tool_type = ToolType.OVERVIEW

        # Act
        inputs = project_creation_form.ProjectFormInputs(
            project_name=project_name,
            source_dir=source_dir,
            selected_tool_type=selected_tool_type,
        )

        # Assert
        assert inputs.project_name == project_name
        assert inputs.source_dir == source_dir
        assert inputs.selected_tool_type == selected_tool_type
