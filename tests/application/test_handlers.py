"""アプリケーション層のハンドラーテスト。"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.application.handlers import AIToolHandler
from app.domain.entities import AITool
from app.domain.repositories import AIToolRepository
from app.errors import ResourceNotFoundError


class TestAIToolHandler:
    """AIToolHandlerのテスト。"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> MagicMock:
        """モックリポジトリを作成します。"""
        return mocker.MagicMock(spec=AIToolRepository)

    @pytest.fixture
    def handler(self, mock_repository: MagicMock) -> AIToolHandler:
        """テスト用のAIToolHandlerを作成します。"""
        return AIToolHandler(mock_repository)

    def test_有効なAIツールの作成(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """有効なAIツールの作成をテストします。"""
        # Arrange
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AI Tool', 'test-tool')

        # Act
        result = handler.create_ai_tool('test-tool', 'テストツール', 'テスト用ツール')

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        saved_tool = mock_repository.save.call_args[0][0]
        assert isinstance(saved_tool, AITool)
        assert saved_tool.id == 'test-tool'
        assert saved_tool.name_ja == 'テストツール'
        assert saved_tool.description == 'テスト用ツール'

    def test_重複IDでのAIツール作成失敗(
        self, handler: AIToolHandler, mock_repository: MagicMock
    ) -> None:
        """重複IDでのAIツール作成失敗をテストします。"""
        # Arrange
        existing_tool = AITool(id='test-tool', name_ja='既存ツール', endpoint_url='dummy')
        mock_repository.find_by_id.return_value = existing_tool

        # Act
        result = handler.create_ai_tool('test-tool', 'テストツール')

        # Assert
        assert result is False
        mock_repository.save.assert_not_called()

    def test_無効な入力でのAIツール作成失敗(
        self, handler: AIToolHandler, mock_repository: MagicMock
    ) -> None:
        """無効な入力でのAIツール作成失敗をテストします。"""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act
        result = handler.create_ai_tool('', 'テストツール')  # 空のID

        # Assert
        assert result is False
        mock_repository.save.assert_not_called()

    def test_AIツールの更新(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """AIツールの更新をテストします。"""
        # Arrange
        existing_tool = AITool(id='test-tool', name_ja='元の名前', endpoint_url='dummy')
        mock_repository.find_by_id.return_value = existing_tool

        # Act
        result = handler.update_ai_tool('test-tool', '新しい名前', '新しい説明')

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        assert existing_tool.name_ja == '新しい名前'
        assert existing_tool.description == '新しい説明'

    def test_存在しないAIツールの更新失敗(
        self, handler: AIToolHandler, mock_repository: MagicMock
    ) -> None:
        """存在しないAIツールの更新失敗をテストします。"""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act
        result = handler.update_ai_tool('non-existent', '新しい名前')

        # Assert
        assert result is False
        mock_repository.save.assert_not_called()

    def test_AIツールの無効化(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """AIツールの無効化をテストします。"""
        # Act
        result = handler.disable_ai_tool('test-tool')

        # Assert
        assert result is True
        mock_repository.disable.assert_called_once_with('test-tool')

    def test_AIツールの有効化(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """AIツールの有効化をテストします。"""
        # Act
        result = handler.enable_ai_tool('test-tool')

        # Assert
        assert result is True
        mock_repository.enable.assert_called_once_with('test-tool')

    def test_有効なAIツールの取得(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """有効なAIツールの取得をテストします。"""
        # Arrange
        tools = [
            AITool(id='tool1', name_ja='ツール1', endpoint_url='dummy'),
            AITool(id='tool2', name_ja='ツール2', endpoint_url='dummy'),
        ]
        mock_repository.find_active_tools.return_value = tools

        # Act
        result = handler.get_active_ai_tools()

        # Assert
        assert result == tools
        mock_repository.find_active_tools.assert_called_once()

    def test_全AIツールの取得(self, handler: AIToolHandler, mock_repository: MagicMock) -> None:
        """全AIツールの取得をテストします。"""
        # Arrange
        tools = [
            AITool(id='tool1', name_ja='ツール1', endpoint_url='dummy'),
            AITool(id='tool2', name_ja='ツール2', endpoint_url='dummy'),
        ]
        mock_repository.find_all_tools.return_value = tools

        # Act
        result = handler.get_all_ai_tools()

        # Assert
        assert result == tools
        mock_repository.find_all_tools.assert_called_once()
