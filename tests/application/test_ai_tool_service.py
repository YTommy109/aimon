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
            AITool(id='tool1', name_ja='ツール1', endpoint_url='dummy'),
            AITool(id='tool2', name_ja='ツール2', endpoint_url='dummy'),
        ]
        mock_data_manager.get_all_ai_tools.return_value = expected_tools

        # Act
        result = get_ai_tools(mock_data_manager)

        # Assert
        assert result == expected_tools
        mock_data_manager.get_all_ai_tools.assert_called_once()

    def test_handle_ai_tool_creation_成功(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.create_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'tool1',
            'name': 'ツール1',
            'description': '説明1',
            'endpoint_url': None,
        }
        result = handle_ai_tool_creation(mock_data_manager, tool_info)
        assert result is True
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', '説明1', None)

    def test_handle_ai_tool_creation_失敗(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.create_ai_tool.return_value = False
        tool_info = {
            'tool_id': 'tool1',
            'name': 'ツール1',
            'description': '説明1',
            'endpoint_url': None,
        }
        result = handle_ai_tool_creation(mock_data_manager, tool_info)
        assert result is False
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', '説明1', None)

    def test_handle_ai_tool_creation_説明なし(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.create_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'tool1',
            'name': 'ツール1',
            'description': None,
            'endpoint_url': None,
        }
        result = handle_ai_tool_creation(mock_data_manager, tool_info)
        assert result is True
        mock_data_manager.create_ai_tool.assert_called_once_with('tool1', 'ツール1', None, None)

    def test_handle_ai_tool_creation_endpoint_url(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.create_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'tool_ep',
            'name': 'ツールEP',
            'description': '説明EP',
            'endpoint_url': 'http://localhost:8080/ep',
        }
        result = handle_ai_tool_creation(mock_data_manager, tool_info)
        assert result is True
        mock_data_manager.create_ai_tool.assert_called_once_with(
            'tool_ep', 'ツールEP', '説明EP', 'http://localhost:8080/ep'
        )

    def test_handle_ai_tool_update_成功(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.update_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'tool1',
            'name': 'ツール1更新',
            'description': '説明1更新',
            'endpoint_url': None,
        }
        result = handle_ai_tool_update(mock_data_manager, tool_info)
        assert result is True
        mock_data_manager.update_ai_tool.assert_called_once_with(
            'tool1', 'ツール1更新', '説明1更新', None
        )

    def test_handle_ai_tool_update_失敗(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.update_ai_tool.return_value = False
        tool_info = {
            'tool_id': 'tool1',
            'name': 'ツール1更新',
            'description': '説明1更新',
            'endpoint_url': None,
        }
        result = handle_ai_tool_update(mock_data_manager, tool_info)
        assert result is False
        mock_data_manager.update_ai_tool.assert_called_once_with(
            'tool1', 'ツール1更新', '説明1更新', None
        )

    def test_handle_ai_tool_update_endpoint_url(self, mock_data_manager: MagicMock) -> None:
        mock_data_manager.update_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'tool_ep',
            'name': 'ツールEP更新',
            'description': '説明EP更新',
            'endpoint_url': 'http://localhost:8080/ep2',
        }
        result = handle_ai_tool_update(mock_data_manager, tool_info)
        assert result is True
        mock_data_manager.update_ai_tool.assert_called_once_with(
            'tool_ep', 'ツールEP更新', '説明EP更新', 'http://localhost:8080/ep2'
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

    def test_aitool_endpoint_urlフィールド(self) -> None:
        """AIToolのendpoint_urlフィールドが正しくセット・取得できることをテストする。"""
        # Arrange
        tool = AITool(id='tool3', name_ja='ツール3', endpoint_url='http://localhost:8080/test')
        # Act & Assert
        assert tool.endpoint_url == 'http://localhost:8080/test'
        # Noneの場合もテスト
        tool2 = AITool(id='tool4', name_ja='ツール4', endpoint_url='dummy')
        assert tool2.endpoint_url == 'dummy'
