"""DataManagerクラスのテスト。"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.application.data_manager import DataManager
from app.application.handlers.ai_tool_handler import AIToolHandler
from app.application.handlers.project_handler import ProjectHandler
from app.domain.entities import AITool, Project


class TestDataManager:
    """DataManagerクラスのテスト。"""

    @pytest.fixture
    def mock_ai_tool_handler(self, mocker: MockerFixture) -> MagicMock:
        """AIToolHandlerのモックを提供するフィクスチャ。"""
        return mocker.MagicMock(spec=AIToolHandler)

    @pytest.fixture
    def mock_project_handler(self, mocker: MockerFixture) -> MagicMock:
        """ProjectHandlerのモックを提供するフィクスチャ。"""
        return mocker.MagicMock(spec=ProjectHandler)

    @pytest.fixture
    def data_manager(
        self,
        mock_ai_tool_handler: MagicMock,
        mock_project_handler: MagicMock,
    ) -> DataManager:
        """DataManagerインスタンスを提供するフィクスチャ。"""
        return DataManager(mock_ai_tool_handler, mock_project_handler)

    # AIツール関連のテスト

    def test_get_ai_tools(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """get_ai_toolsメソッドのテスト。"""
        # Arrange
        expected_tools = [
            AITool(id='tool1', name_ja='ツール1', endpoint_url='dummy'),
            AITool(id='tool2', name_ja='ツール2', endpoint_url='dummy'),
        ]
        mock_ai_tool_handler.get_active_ai_tools.return_value = expected_tools

        # Act
        result = data_manager.get_ai_tools()

        # Assert
        assert result == expected_tools
        mock_ai_tool_handler.get_active_ai_tools.assert_called_once()

    def test_get_all_ai_tools(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """get_all_ai_toolsメソッドのテスト。"""
        # Arrange
        expected_tools = [
            AITool(id='tool1', name_ja='ツール1', endpoint_url='dummy'),
            AITool(id='tool2', name_ja='ツール2', endpoint_url='dummy'),
        ]
        mock_ai_tool_handler.get_all_ai_tools.return_value = expected_tools

        # Act
        result = data_manager.get_all_ai_tools()

        # Assert
        assert result == expected_tools
        mock_ai_tool_handler.get_all_ai_tools.assert_called_once()

    def test_create_ai_tool(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """create_ai_toolメソッドのテスト。"""
        # Arrange
        mock_ai_tool_handler.create_ai_tool.return_value = True

        # Act
        result = data_manager.create_ai_tool('tool1', 'ツール1', '説明1')

        # Assert
        assert result is True
        mock_ai_tool_handler.create_ai_tool.assert_called_once_with(
            'tool1', 'ツール1', '説明1', None
        )

    def test_update_ai_tool(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """update_ai_toolメソッドのテスト。"""
        # Arrange
        mock_ai_tool_handler.update_ai_tool.return_value = True

        # Act
        result = data_manager.update_ai_tool('tool1', 'ツール1更新', '説明1更新')

        # Assert
        assert result is True
        mock_ai_tool_handler.update_ai_tool.assert_called_once_with(
            'tool1', 'ツール1更新', '説明1更新', None
        )

    def test_disable_ai_tool(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """disable_ai_toolメソッドのテスト。"""
        # Arrange
        mock_ai_tool_handler.disable_ai_tool.return_value = True

        # Act
        result = data_manager.disable_ai_tool('tool1')

        # Assert
        assert result is True
        mock_ai_tool_handler.disable_ai_tool.assert_called_once_with('tool1')

    def test_enable_ai_tool(
        self,
        data_manager: DataManager,
        mock_ai_tool_handler: MagicMock,
    ) -> None:
        """enable_ai_toolメソッドのテスト。"""
        # Arrange
        mock_ai_tool_handler.enable_ai_tool.return_value = True

        # Act
        result = data_manager.enable_ai_tool('tool1')

        # Assert
        assert result is True
        mock_ai_tool_handler.enable_ai_tool.assert_called_once_with('tool1')

    # プロジェクト関連のテスト

    def test_get_projects(
        self,
        data_manager: DataManager,
        mock_project_handler: MagicMock,
    ) -> None:
        """get_projectsメソッドのテスト。"""
        # Arrange
        expected_projects = [
            Project(name='プロジェクト1', source='/path1', ai_tool='tool1'),
            Project(name='プロジェクト2', source='/path2', ai_tool='tool2'),
        ]
        mock_project_handler.get_all_projects.return_value = expected_projects

        # Act
        result = data_manager.get_projects()

        # Assert
        assert result == expected_projects
        mock_project_handler.get_all_projects.assert_called_once()

    def test_create_project(
        self,
        data_manager: DataManager,
        mock_project_handler: MagicMock,
    ) -> None:
        """create_projectメソッドのテスト。"""
        # Arrange
        expected_project = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        mock_project_handler.create_project.return_value = expected_project

        # Act
        result = data_manager.create_project('プロジェクト1', '/path1', 'tool1')

        # Assert
        assert result == expected_project
        mock_project_handler.create_project.assert_called_once_with(
            'プロジェクト1', '/path1', 'tool1'
        )

    def test_get_project_by_id(
        self,
        data_manager: DataManager,
        mock_project_handler: MagicMock,
    ) -> None:
        """get_project_by_idメソッドのテスト。"""
        # Arrange
        expected_project = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        mock_project_handler.get_project_by_id.return_value = expected_project

        # Act
        result = data_manager.get_project_by_id('project-id')

        # Assert
        assert result == expected_project
        mock_project_handler.get_project_by_id.assert_called_once_with('project-id')

    def test_update_project(
        self,
        data_manager: DataManager,
        mock_project_handler: MagicMock,
    ) -> None:
        """update_projectメソッドのテスト。"""
        # Arrange
        project = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        mock_project_handler.update_project.return_value = True

        # Act
        result = data_manager.update_project(project)

        # Assert
        assert result is True
        mock_project_handler.update_project.assert_called_once_with(project)
