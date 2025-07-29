"""AIツールサービスのテスト。"""

from unittest.mock import Mock
from uuid import UUID

import pytest

from app.errors import ResourceNotFoundError
from app.models import AIToolID
from app.models.ai_tool import AITool
from app.services.ai_tool_service import AIToolService


class TestAIToolService:
    """AIツールサービスのテストクラス。"""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """モックリポジトリを作成する。"""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository: Mock) -> AIToolService:
        """AIツールサービスを作成する。"""
        return AIToolService(mock_repository)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツールを作成する。"""
        return AITool(
            name_ja='テストツール',
            description='テスト用のAIツール',
            endpoint_url='https://api.example.com/test',
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
        tool_id = sample_ai_tool.id
        mock_repository.find_by_id.return_value = sample_ai_tool

        # Act
        tool = service.get_ai_tool_by_id(tool_id)

        # Assert
        assert tool == sample_ai_tool
        mock_repository.find_by_id.assert_called_once_with(tool_id)

    def test_存在しないIDでAIツールを取得するとValueErrorが発生する(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないIDでAIツールを取得するとValueErrorが発生することをテスト。"""
        # Arrange
        tool_id = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', str(tool_id))

        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            service.get_ai_tool_by_id(tool_id)

    def test_AIツールを作成できる(self, service: AIToolService, mock_repository: Mock) -> None:
        """AIツールを作成できることをテスト。"""
        # Arrange
        mock_repository.save.return_value = None

        # Act
        result = service.create_ai_tool(
            '新規ツール', '新規ツールの説明', 'https://api.example.com/new'
        )

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        saved_tool = mock_repository.save.call_args[0][0]
        assert isinstance(saved_tool.id, UUID)  # NewTypeは内部的にはUUID
        assert saved_tool.name_ja == '新規ツール'
        assert saved_tool.description == '新規ツールの説明'
        assert saved_tool.endpoint_url == 'https://api.example.com/new'

    def test_AIツール作成でエラーが発生した場合はFalseを返す(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """AIツール作成でエラーが発生した場合はFalseを返すことをテスト。"""
        # Arrange
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.create_ai_tool(
            '新規ツール', '新規ツールの説明', 'https://api.example.com/new'
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
            sample_ai_tool.id,
            '更新されたツール名',
            '更新された説明',
            'https://api.example.com/updated',
        )

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        updated_tool = mock_repository.save.call_args[0][0]
        assert updated_tool.name_ja == '更新されたツール名'
        assert updated_tool.description == '更新された説明'
        assert updated_tool.endpoint_url == 'https://api.example.com/updated'

    def test_存在しないAIツールの更新は失敗する(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールの更新は失敗することをテスト。"""
        # Arrange
        tool_id = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', str(tool_id))

        # Act
        result = service.update_ai_tool(
            tool_id,
            '更新されたツール名',
            '更新された説明',
            'https://api.example.com/updated',
        )

        # Assert
        assert result is False

    def test_AIツール更新でエラーが発生した場合はFalseを返す(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール更新でエラーが発生した場合はFalseを返すことをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.update_ai_tool(
            sample_ai_tool.id,
            '更新されたツール名',
            '更新された説明',
            'https://api.example.com/updated',
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
        result = service.disable_ai_tool(sample_ai_tool.id)

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        disabled_tool = mock_repository.save.call_args[0][0]
        assert disabled_tool.disabled_at is not None

    def test_存在しないAIツールの無効化は失敗する(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールの無効化は失敗することをテスト。"""
        # Arrange
        tool_id = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', str(tool_id))

        # Act
        result = service.disable_ai_tool(tool_id)

        # Assert
        assert result is False

    def test_AIツール無効化でエラーが発生した場合はFalseを返す(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール無効化でエラーが発生した場合はFalseを返すことをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.disable_ai_tool(sample_ai_tool.id)

        # Assert
        assert result is False

    def test_AIツールを有効化できる(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツールを有効化できることをテスト。"""
        # Arrange
        sample_ai_tool.disabled_at = '2024-01-01T00:00:00+09:00'  # type: ignore[assignment]
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.return_value = None

        # Act
        result = service.enable_ai_tool(sample_ai_tool.id)

        # Assert
        assert result is True
        mock_repository.save.assert_called_once()
        enabled_tool = mock_repository.save.call_args[0][0]
        assert enabled_tool.disabled_at is None

    def test_存在しないAIツールの有効化は失敗する(
        self, service: AIToolService, mock_repository: Mock
    ) -> None:
        """存在しないAIツールの有効化は失敗することをテスト。"""
        # Arrange
        tool_id = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('AIツール', str(tool_id))

        # Act
        result = service.enable_ai_tool(tool_id)

        # Assert
        assert result is False

    def test_AIツール有効化でエラーが発生した場合はFalseを返す(
        self, service: AIToolService, mock_repository: Mock, sample_ai_tool: AITool
    ) -> None:
        """AIツール有効化でエラーが発生した場合はFalseを返すことをテスト。"""
        # Arrange
        mock_repository.find_by_id.return_value = sample_ai_tool
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = service.enable_ai_tool(sample_ai_tool.id)

        # Assert
        assert result is False
