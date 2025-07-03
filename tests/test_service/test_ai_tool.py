"""AIツール管理サービスのテスト。"""

from app.model.store import DataManager
from app.service.ai_tool import (
    handle_ai_tool_creation,
    handle_ai_tool_disable,
    handle_ai_tool_enable,
    handle_ai_tool_update,
)


class TestHandleAiToolCreation:
    """AIツール作成機能のテストクラス。"""

    def test_正常なツール作成が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is True
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 1
        assert ai_tools[0].id == tool_id
        assert ai_tools[0].name_ja == name
        assert ai_tools[0].description == description

    def test_空のツールIDで作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = ''
        name = 'テストツール'
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0

    def test_空の名前で作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = ''
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0

    def test_長すぎるツールIDで作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'a' * 51  # MAX_TOOL_ID_LENGTH + 1
        name = 'テストツール'
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0

    def test_長すぎる名前で作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'a' * 101  # MAX_TOOL_NAME_LENGTH + 1
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0

    def test_長すぎる説明で作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'a' * 501  # MAX_TOOL_DESCRIPTION_LENGTH + 1

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0

    def test_重複するツールIDで作成が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # 最初のツールを作成
        handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, '別のツール', '別の説明')

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 1  # 最初のツールのみ存在

    def test_無効化されたツールと同じIDで作成が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # 最初のツールを作成して無効化
        handle_ai_tool_creation(data_manager, tool_id, name, description)
        handle_ai_tool_disable(data_manager, tool_id)

        # Act
        new_name = '新しいツール'
        new_description = '新しい説明'
        result = handle_ai_tool_creation(data_manager, tool_id, new_name, new_description)

        # Assert
        assert result is True
        active_tools = data_manager.get_ai_tools()
        assert len(active_tools) == 1
        assert active_tools[0].id == tool_id
        assert active_tools[0].name_ja == new_name
        assert active_tools[0].description == new_description

    def test_説明がNoneでも作成が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = None

        # Act
        result = handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Assert
        assert result is True
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 1
        assert ai_tools[0].id == tool_id
        assert ai_tools[0].name_ja == name
        # Noneの場合は空文字として保存される
        assert ai_tools[0].description == ''


class TestHandleAiToolUpdate:
    """AIツール更新機能のテストクラス。"""

    def test_正常なツール更新が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # 最初にツールを作成
        handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Act
        new_name = '更新されたツール'
        new_description = '更新された説明'
        result = handle_ai_tool_update(data_manager, tool_id, new_name, new_description)

        # Assert
        assert result is True
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 1
        assert ai_tools[0].id == tool_id
        assert ai_tools[0].name_ja == new_name
        assert ai_tools[0].description == new_description

    def test_存在しないツールの更新が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'nonexistent_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # Act
        result = handle_ai_tool_update(data_manager, tool_id, name, description)

        # Assert
        assert result is False
        ai_tools = data_manager.get_ai_tools()
        assert len(ai_tools) == 0


class TestHandleAiToolDisable:
    """AIツール無効化機能のテストクラス。"""

    def test_正常なツール無効化が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # 最初にツールを作成
        handle_ai_tool_creation(data_manager, tool_id, name, description)

        # Act
        result = handle_ai_tool_disable(data_manager, tool_id)

        # Assert
        assert result is True
        ai_tools = data_manager.get_all_ai_tools()
        assert len(ai_tools) == 1
        assert ai_tools[0].id == tool_id
        assert ai_tools[0].disabled_at is not None

    def test_存在しないツールの無効化が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'nonexistent_tool'

        # Act
        result = handle_ai_tool_disable(data_manager, tool_id)

        # Assert
        assert result is False
        ai_tools = data_manager.get_all_ai_tools()
        assert len(ai_tools) == 0


class TestHandleAiToolEnable:
    """AIツール有効化機能のテストクラス。"""

    def test_正常なツール有効化が成功する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'test_tool'
        name = 'テストツール'
        description = 'テスト用のツール'

        # 最初にツールを作成して無効化
        handle_ai_tool_creation(data_manager, tool_id, name, description)
        handle_ai_tool_disable(data_manager, tool_id)

        # Act
        result = handle_ai_tool_enable(data_manager, tool_id)

        # Assert
        assert result is True
        ai_tools = data_manager.get_all_ai_tools()
        assert len(ai_tools) == 1
        assert ai_tools[0].id == tool_id
        assert ai_tools[0].disabled_at is None

    def test_存在しないツールの有効化が失敗する(self, data_manager: DataManager) -> None:
        # Arrange
        tool_id = 'nonexistent_tool'

        # Act
        result = handle_ai_tool_enable(data_manager, tool_id)

        # Assert
        assert result is False
        ai_tools = data_manager.get_all_ai_tools()
        assert len(ai_tools) == 0
