"""AIToolモデルのテスト。"""

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from app.models.ai_tool import AITool

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class TestAITool:
    """AIToolモデルのテストクラス。"""

    def test_AIツールが正常に作成される(self) -> None:
        """AIツールが正常に作成されることをテストする。"""
        # Arrange
        name = 'テストツール'
        description = 'テスト用のAIツール'
        endpoint_url = 'https://api.example.com/test'

        # Act
        ai_tool = AITool(name_ja=name, description=description, endpoint_url=endpoint_url)

        # Assert
        assert isinstance(ai_tool.id, UUID)  # NewTypeは内部的にはUUID
        assert ai_tool.id == ai_tool.id  # 値の比較
        assert ai_tool.name_ja == name
        assert ai_tool.description == description
        assert ai_tool.endpoint_url == endpoint_url
        assert ai_tool.disabled_at is None
        assert ai_tool.created_at is not None
        assert ai_tool.updated_at is not None

    def test_AIツールの無効化(self) -> None:
        """AIツールの無効化をテストする。"""
        # Arrange
        ai_tool = AITool(name_ja='テストツール', endpoint_url='https://api.example.com/test')

        # Act
        ai_tool.disabled_at = datetime.now(JST)

        # Assert
        assert ai_tool.disabled_at is not None

    def test_AIツールの有効化(self) -> None:
        """AIツールの有効化をテストする。"""
        # Arrange
        ai_tool = AITool(name_ja='テストツール', endpoint_url='https://api.example.com/test')
        ai_tool.disabled_at = datetime.now(JST)

        # Act
        ai_tool.disabled_at = None

        # Assert
        assert ai_tool.disabled_at is None
