"""AIツールサービスのテスト。"""

from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

from app.errors import ResourceNotFoundError
from app.models.ai_tool import AITool
from app.repositories.ai_tool_repository import JsonAIToolRepository
from app.services.ai_tool_service import AIToolService


class TestAIToolService:
    """AIToolServiceのテストクラス。"""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """モックリポジトリのフィクスチャ。"""
        return Mock(spec=JsonAIToolRepository)

    @pytest.fixture
    def service(self, mock_repository: Mock) -> AIToolService:
        """サービスのフィクスチャ。"""
        return AIToolService(mock_repository)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツールのフィクスチャ。"""
        return AITool(
            id='test-tool-1',
            name_ja='テストツール1',
            description='テスト用のAIツール',
            endpoint_url='https://api.example.com/test1',
        )

    def test_全AIツールを取得できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """全AIツールを取得できることをテスト。"""
        # Arrange
        mock_repository.find_all_tools.return_value = [sample_ai_tool]

        # Act
        tools = service.get_all_ai_tools()

        # Assert
        assert tools == [sample_ai_tool]
        mock_repository.find_all_tools.assert_called_once()

    def test_IDでAIツールを取得できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """IDでAIツールを取得できることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool

        # Act
        tool = service.get_ai_tool_by_id('test-tool-1')

        # Assert
        assert tool == sample_ai_tool
        mock_repository.find_by_id.assert_called_once_with('test-tool-1')

    def test_存在しないIDでAIツールを取得するとValueErrorが発生する(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないIDでAIツールを取得するとValueErrorが発生することをテスト。"""
        # Arrange
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', 'non-existent')

        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            service.get_ai_tool_by_id('non-existent')

    def test_AIツールを作成できる(self, service: AIToolService, mock_repository: Mock) -> None:
        """AIツールを作成できることをテスト。"""
        # Arrange
        mock_repository.save.return_value = None

        # Act
        result = service.create_ai_tool(
            'new-tool', '新規ツール', '新規ツールの説明', 'https://api.example.com/new'
        )

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        saved_tool = mock_repository.save.call_args[0][0]
        assert saved_tool.id == 'new-tool'
        assert saved_tool.name_ja == '新規ツール'
        assert saved_tool.description == '新規ツールの説明'
        assert saved_tool.endpoint_url == 'https://api.example.com/new'

    def test_AIツール作成時にエラーが発生するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """AIツール作成時にエラーが発生するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.create_ai_tool(
            'new-tool', '新規ツール', '新規ツールの説明', 'https://api.example.com/new'
        )

        # Assert
        assert result is False

    def test_AIツールを更新できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツールを更新できることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.return_value = None

        # Act
        result = service.update_ai_tool(
            'test-tool-1', '更新されたツール名', '更新された説明', 'https://api.example.com/updated'
        )

        # Assert
        assert result is True
        mock_repository.find_by_id.assert_called_once_with('test-tool-1')
        mock_repository.save.assert_called_once()

        # 更新されたツールの内容を確認
        saved_tool = mock_repository.save.call_args[0][0]
        assert saved_tool.name_ja == '更新されたツール名'
        assert saved_tool.description == '更新された説明'
        assert saved_tool.endpoint_url == 'https://api.example.com/updated'
        assert saved_tool.updated_at is not None

    def test_存在しないAIツールを更新するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールを更新するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', 'non-existent')

        # Act
        result = service.update_ai_tool(
            'non-existent',
            '更新されたツール名',
            '更新された説明',
            'https://api.example.com/updated',
        )

        # Assert
        assert result is False

    def test_AIツール更新時にエラーが発生するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール更新時にエラーが発生するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.update_ai_tool(
            'test-tool-1', '更新されたツール名', '更新された説明', 'https://api.example.com/updated'
        )

        # Assert
        assert result is False

    def test_AIツールを無効化できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツールを無効化できることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.return_value = None

        # Act
        result = service.disable_ai_tool('test-tool-1')

        # Assert
        assert result is True
        mock_repository.find_by_id.assert_called_once_with('test-tool-1')
        mock_repository.save.assert_called_once()

        # 無効化されたツールの内容を確認
        saved_tool = mock_repository.save.call_args[0][0]
        assert saved_tool.disabled_at is not None
        assert saved_tool.updated_at is not None

    def test_存在しないAIツールを無効化するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールを無効化するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', 'non-existent')

        # Act
        result = service.disable_ai_tool('non-existent')

        # Assert
        assert result is False

    def test_AIツール無効化時にエラーが発生するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール無効化時にエラーが発生するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.disable_ai_tool('test-tool-1')

        # Assert
        assert result is False

    def test_AIツールを有効化できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツールを有効化できることをテスト。"""
        # Arrange
        sample_ai_tool.disabled_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.return_value = None

        # Act
        result = service.enable_ai_tool('test-tool-1')

        # Assert
        assert result is True
        mock_repository.find_by_id.assert_called_once_with('test-tool-1')
        mock_repository.save.assert_called_once()

        # 有効化されたツールの内容を確認
        saved_tool = mock_repository.save.call_args[0][0]
        assert saved_tool.disabled_at is None
        assert saved_tool.updated_at is not None

    def test_存在しないAIツールを有効化するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールを有効化するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', 'non-existent')

        # Act
        result = service.enable_ai_tool('non-existent')

        # Assert
        assert result is False

    def test_AIツール有効化時にエラーが発生するとFalseが返される(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール有効化時にエラーが発生するとFalseが返されることをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.enable_ai_tool('test-tool-1')

        # Assert
        assert result is False
