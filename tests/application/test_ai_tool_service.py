"""AIToolServiceのテスト。"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.application.data_manager import DataManager
from app.application.services.ai_tool_service import (
    get_ai_tools,
    handle_ai_tool_creation,
    handle_ai_tool_disable,
    handle_ai_tool_enable,
    handle_ai_tool_update,
)
from app.domain.entities import AITool


class TestAIToolService:
    """AIToolServiceのテスト。"""

    @pytest.fixture
    def mock_data_manager(self, mocker: MockerFixture) -> MagicMock:
        """DataManagerのモックを提供するフィクスチャ。"""
        return mocker.MagicMock(spec=DataManager)

    def test_get_ai_tools(self, mock_data_manager: MagicMock) -> None:
        """get_ai_toolsのテスト。"""
        # Arrange
        expected_tools = [
            AITool(id='tool1', name_ja='ツール1'),
            AITool(id='tool2', name_ja='ツール2'),
        ]
        mock_data_manager.get_all_ai_tools.return_value = expected_tools

        # Act
        result = get_ai_tools(mock_data_manager)

        # Assert
        assert result == expected_tools
        mock_data_manager.get_all_ai_tools.assert_called_once()

    def test_handle_ai_tool_creation_成功(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_creation成功のテスト。"""
        # Arrange
        mock_data_manager.create_ai_tool.return_value = True

        # Act
        result = handle_ai_tool_creation(mock_data_manager, 'tool1', 'ツール1', '説明1')

        # Assert
        assert result is True
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', '説明1')

    def test_handle_ai_tool_creation_失敗(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_creation失敗のテスト。"""
        # Arrange
        mock_data_manager.create_ai_tool.return_value = False

        # Act
        result = handle_ai_tool_creation(mock_data_manager, 'tool1', 'ツール1', '説明1')

        # Assert
        assert result is False
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', '説明1')

    def test_handle_ai_tool_creation_説明なし(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_creation説明なしのテスト。"""
        # Arrange
        mock_data_manager.create_ai_tool.return_value = True

        # Act
        result = handle_ai_tool_creation(mock_data_manager, 'tool1', 'ツール1')

        # Assert
        assert result is True
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', None)

    def test_handle_ai_tool_update_成功(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_update成功のテスト。"""
        # Arrange
        mock_data_manager.update_ai_tool.return_value = True

        # Act
        result = handle_ai_tool_update(mock_data_manager, 'tool1', 'ツール1更新', '説明1更新')

        # Assert
        assert result is True
        mock_data_manager.update_ai_tool.assert_called_once_with(
            'tool1', 'ツール1更新', '説明1更新'
        )

    def test_handle_ai_tool_update_失敗(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_update失敗のテスト。"""
        # Arrange
        mock_data_manager.update_ai_tool.return_value = False

        # Act
        result = handle_ai_tool_update(mock_data_manager, 'tool1', 'ツール1更新', '説明1更新')

        # Assert
        assert result is False
        mock_data_manager.update_ai_tool.assert_called_once_with(
            'tool1', 'ツール1更新', '説明1更新'
        )

    def test_handle_ai_tool_disable_成功(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_disable成功のテスト。"""
        # Arrange
        mock_data_manager.disable_ai_tool.return_value = True

        # Act
        result = handle_ai_tool_disable(mock_data_manager, 'tool1')

        # Assert
        assert result is True
        mock_data_manager.disable_ai_tool.assert_called_once_with('tool1')

    def test_handle_ai_tool_disable_失敗(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_disable失敗のテスト。"""
        # Arrange
        mock_data_manager.disable_ai_tool.return_value = False

        # Act
        result = handle_ai_tool_disable(mock_data_manager, 'tool1')

        # Assert
        assert result is False
        mock_data_manager.disable_ai_tool.assert_called_once_with('tool1')

    def test_handle_ai_tool_enable_成功(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_enable成功のテスト。"""
        # Arrange
        mock_data_manager.enable_ai_tool.return_value = True

        # Act
        result = handle_ai_tool_enable(mock_data_manager, 'tool1')

        # Assert
        assert result is True
        mock_data_manager.enable_ai_tool.assert_called_once_with('tool1')

    def test_handle_ai_tool_enable_失敗(self, mock_data_manager: MagicMock) -> None:
        """handle_ai_tool_enable失敗のテスト。"""
        # Arrange
        mock_data_manager.enable_ai_tool.return_value = False

        # Act
        result = handle_ai_tool_enable(mock_data_manager, 'tool1')

        # Assert
        assert result is False
        mock_data_manager.enable_ai_tool.assert_called_once_with('tool1')
