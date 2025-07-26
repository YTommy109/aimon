"""AIツール管理画面のテストモジュール。"""

from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time

from app.models.ai_tool import AITool
from app.services.ai_tool_service import AIToolService

# モジュールレベルのimport
from app.ui.ai_tool_management import (
    _handle_create_tool,
    _handle_disable_tool,
    _handle_enable_tool,
    _handle_update_tool,
    _render_creation_form_buttons,
    _render_edit_form_buttons,
    _render_tool_actions,
    _render_tool_info_columns,
    _render_tool_list,
    render_ai_tool_management_page,
)


class TestAIToolManagement:
    """AIツール管理画面のテストクラス。"""

    def _setup_mock_columns(self) -> tuple[list[Mock], list[Mock]]:
        """モックカラムの設定を行う。

        Returns:
            テーブル用カラムとアクション用カラムのタプル。
        """
        # メインのテーブル用の7つのカラム
        mock_table_cols = [Mock() for _ in range(7)]
        for col in mock_table_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)

        # アクションボタン用の2つのカラム
        mock_action_cols = [Mock(), Mock()]
        for col in mock_action_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)

        return mock_table_cols, mock_action_cols

    def _create_mock_columns_side_effect(
        self, mock_table_cols: list[Mock], mock_action_cols: list[Mock]
    ) -> Callable[[int | list[int]], list[Mock]]:
        """モックカラムのサイドエフェクトを作成する。

        Args:
            mock_table_cols: テーブル用カラム。
            mock_action_cols: アクション用カラム。

        Returns:
            サイドエフェクト関数。
        """

        def mock_columns_side_effect(num_cols: int | list[int]) -> list[Mock]:
            # 配列が渡された場合（[2, 2, 3, 2, 2, 1, 2]など）
            if isinstance(num_cols, list):
                return mock_table_cols
            # 数値が渡された場合（2など）
            return mock_action_cols if num_cols == 2 else [Mock() for _ in range(num_cols)]

        return mock_columns_side_effect

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """AIツールサービスのモック。"""
        return Mock(spec=AIToolService)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツール。"""
        with freeze_time('2025-01-15 10:30:00'):
            return AITool(
                id='test-tool-1',
                name_ja='テストツール1',
                description='テスト用のAIツール',
                endpoint_url='https://api.example.com/test1',
            )

    @pytest.fixture
    def sample_ai_tool_disabled(self) -> AITool:
        """無効化されたサンプルAIツール。"""
        with freeze_time('2025-01-15 10:30:00'):
            tool = AITool(
                id='test-tool-2',
                name_ja='テストツール2',
                description='無効化されたテストツール',
                endpoint_url='https://api.example.com/test2',
            )
            tool.disabled_at = tool.created_at
            return tool

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.title')
    @patch('app.ui.ai_tool_management._render_tool_list')
    @patch('app.ui.ai_tool_management.st.button')
    def test_AIツール管理ページが描画される(
        self,
        mock_button: Mock,
        mock_render_tool_list: Mock,
        mock_title: Mock,
        mock_ai_tool_service: Mock,
    ) -> None:
        """AIツール管理ページが描画されることをテスト。"""
        # Arrange
        mock_button.return_value = False

        # Act
        render_ai_tool_management_page(mock_ai_tool_service)

        # Assert
        mock_title.assert_called_once_with('AIツール管理')
        mock_render_tool_list.assert_called_once_with(mock_ai_tool_service)
        mock_button.assert_called_once_with('新規AIツール登録')

    @patch('app.ui.ai_tool_management.st.info')
    def test_AIツールが存在しない場合にメッセージが表示される(
        self, mock_info: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """AIツールが存在しない場合にメッセージが表示されることをテスト。"""
        # Arrange
        mock_ai_tool_service.get_all_ai_tools.return_value = []

        # Act
        _render_tool_list(mock_ai_tool_service)

        # Assert
        mock_info.assert_called_once_with('💡 AIツールがまだ登録されていません。')

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.write')
    @patch('app.ui.ai_tool_management.st.divider')
    def test_AIツール一覧が描画される(
        self,
        mock_divider: Mock,
        mock_write: Mock,
        mock_columns: Mock,
        mock_ai_tool_service: Mock,
        sample_ai_tool: AITool,
    ) -> None:
        """AIツール一覧が描画されることをテスト。"""
        # Arrange
        mock_ai_tool_service.get_all_ai_tools.return_value = [sample_ai_tool]
        mock_table_cols, mock_action_cols = self._setup_mock_columns()
        mock_columns.side_effect = self._create_mock_columns_side_effect(
            mock_table_cols, mock_action_cols
        )

        # Act
        _render_tool_list(mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.get_all_ai_tools.assert_called_once()
        mock_columns.assert_called()

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.write')
    def test_ツール情報カラムが描画される(
        self, mock_write: Mock, mock_columns: Mock, sample_ai_tool: AITool
    ) -> None:
        """ツール情報カラムが描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(7)]
        # Mockオブジェクトにコンテキストマネージャー機能を追加
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        _render_tool_info_columns(sample_ai_tool, mock_cols)

        # Assert
        assert mock_write.call_count >= 6  # 各カラムでwriteが呼ばれる

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール操作ボタンが描画される(
        self,
        mock_button: Mock,
        mock_columns: Mock,
        sample_ai_tool: AITool,
        mock_ai_tool_service: Mock,
    ) -> None:
        """ツール操作ボタンが描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock(), Mock()]
        # Mockオブジェクトにコンテキストマネージャー機能を追加
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols
        mock_button.return_value = False

        # Act
        _render_tool_actions(sample_ai_tool, mock_ai_tool_service)

        # Assert
        mock_columns.assert_called_once_with(2)

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.button')
    def test_無効化されたツールの操作ボタンが描画される(
        self,
        mock_button: Mock,
        mock_columns: Mock,
        sample_ai_tool_disabled: AITool,
        mock_ai_tool_service: Mock,
    ) -> None:
        """無効化されたツールの操作ボタンが描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock(), Mock()]
        # Mockオブジェクトにコンテキストマネージャー機能を追加
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols
        mock_button.return_value = False

        # Act
        _render_tool_actions(sample_ai_tool_disabled, mock_ai_tool_service)

        # Assert
        mock_columns.assert_called_once_with(2)

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール作成処理が成功する(self, mock_button: Mock, mock_ai_tool_service: Mock) -> None:
        """ツール作成処理が成功することをテスト。"""
        # Arrange
        mock_ai_tool_service.create_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'test-tool',
            'name': 'テストツール',
            'description': 'テスト用ツール',
            'endpoint_url': 'https://api.example.com/test',
        }

        # st.session_stateのモックを設定
        mock_session_state = Mock()
        mock_session_state.get = Mock(return_value=mock_ai_tool_service)
        mock_session_state.__setitem__ = Mock()
        with patch('app.ui.ai_tool_management.st.session_state', mock_session_state):
            # Act
            _handle_create_tool(tool_info)

        # Assert
        mock_ai_tool_service.create_ai_tool.assert_called_once_with(
            'test-tool', 'テストツール', 'テスト用ツール', 'https://api.example.com/test'
        )
        mock_session_state.__setitem__.assert_called_once_with('show_create_modal', False)  # noqa: FBT003

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール作成処理が失敗する(self, mock_button: Mock, mock_ai_tool_service: Mock) -> None:
        """ツール作成処理が失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.create_ai_tool.return_value = False
        tool_info = {
            'tool_id': 'test-tool',
            'name': 'テストツール',
            'description': 'テスト用ツール',
            'endpoint_url': 'https://api.example.com/test',
        }

        # st.session_stateのモックを設定
        mock_session_state = Mock()
        mock_session_state.get = Mock(return_value=mock_ai_tool_service)
        mock_session_state.__setitem__ = Mock()
        with patch('app.ui.ai_tool_management.st.session_state', mock_session_state):
            # Act
            _handle_create_tool(tool_info)

        # Assert
        mock_ai_tool_service.create_ai_tool.assert_called_once()

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール更新処理が成功する(self, mock_button: Mock, mock_ai_tool_service: Mock) -> None:
        """ツール更新処理が成功することをテスト。"""
        # Arrange
        mock_ai_tool_service.update_ai_tool.return_value = True
        tool_info = {
            'tool_id': 'test-tool',
            'name': '更新されたツール',
            'description': '更新された説明',
            'endpoint_url': 'https://api.example.com/updated',
        }

        # st.session_stateのモックを設定
        mock_session_state = Mock()
        mock_session_state.get = Mock(return_value=mock_ai_tool_service)
        mock_session_state.__setitem__ = Mock()
        with patch('app.ui.ai_tool_management.st.session_state', mock_session_state):
            # Act
            _handle_update_tool(tool_info)

        # Assert
        mock_ai_tool_service.update_ai_tool.assert_called_once_with(
            'test-tool', '更新されたツール', '更新された説明', 'https://api.example.com/updated'
        )
        mock_session_state.__setitem__.assert_called_once_with('show_edit_modal', False)  # noqa: FBT003

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール更新処理が失敗する(self, mock_button: Mock, mock_ai_tool_service: Mock) -> None:
        """ツール更新処理が失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.update_ai_tool.return_value = False
        tool_info = {
            'tool_id': 'test-tool',
            'name': '更新されたツール',
            'description': '更新された説明',
            'endpoint_url': 'https://api.example.com/updated',
        }

        # st.session_stateのモックを設定
        mock_session_state = Mock()
        mock_session_state.get = Mock(return_value=mock_ai_tool_service)
        mock_session_state.__setitem__ = Mock()
        with patch('app.ui.ai_tool_management.st.session_state', mock_session_state):
            # Act
            _handle_update_tool(tool_info)

        # Assert
        mock_ai_tool_service.update_ai_tool.assert_called_once()

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール無効化処理が成功する(
        self, mock_button: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """ツール無効化処理が成功することをテスト。"""
        # Arrange
        mock_ai_tool_service.disable_ai_tool.return_value = True

        # Act
        _handle_disable_tool('test-tool', mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.disable_ai_tool.assert_called_once_with('test-tool')

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール無効化処理が失敗する(
        self, mock_button: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """ツール無効化処理が失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.disable_ai_tool.return_value = False

        # Act
        _handle_disable_tool('test-tool', mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.disable_ai_tool.assert_called_once_with('test-tool')

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール有効化処理が成功する(
        self, mock_button: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """ツール有効化処理が成功することをテスト。"""
        # Arrange
        mock_ai_tool_service.enable_ai_tool.return_value = True

        # Act
        _handle_enable_tool('test-tool', mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.enable_ai_tool.assert_called_once_with('test-tool')

    @patch('app.ui.ai_tool_management.st.session_state', {})
    @patch('app.ui.ai_tool_management.st.button')
    def test_ツール有効化処理が失敗する(
        self, mock_button: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """ツール有効化処理が失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.enable_ai_tool.return_value = False

        # Act
        _handle_enable_tool('test-tool', mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.enable_ai_tool.assert_called_once_with('test-tool')

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.button')
    def test_新規作成フォームのボタンが描画される(
        self, mock_button: Mock, mock_columns: Mock
    ) -> None:
        """新規作成フォームのボタンが描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock(), Mock()]
        # Mockオブジェクトにコンテキストマネージャー機能を追加
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols
        mock_button.return_value = False
        tool_info = {
            'tool_id': 'test-tool',
            'name': 'テストツール',
            'description': 'テスト用ツール',
            'endpoint_url': 'https://api.example.com/test',
        }

        # Act
        _render_creation_form_buttons(tool_info)

        # Assert
        assert mock_button.call_count >= 2  # 登録ボタンとキャンセルボタン

    @patch('app.ui.ai_tool_management.st.columns')
    @patch('app.ui.ai_tool_management.st.button')
    def test_編集フォームのボタンが描画される(self, mock_button: Mock, mock_columns: Mock) -> None:
        """編集フォームのボタンが描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock(), Mock()]
        # Mockオブジェクトにコンテキストマネージャー機能を追加
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols
        mock_button.return_value = False
        tool_info = {
            'tool_id': 'test-tool',
            'name': '更新されたツール',
            'description': '更新された説明',
            'endpoint_url': 'https://api.example.com/updated',
        }

        # Act
        _render_edit_form_buttons(tool_info)

        # Assert
        assert mock_button.call_count >= 2  # 更新ボタンとキャンセルボタン
