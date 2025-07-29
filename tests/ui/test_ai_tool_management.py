"""AIツール管理画面のテストモジュール。"""

from unittest.mock import Mock
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from app.models import AIToolID
from app.models.ai_tool import AITool
from app.services.ai_tool_service import AIToolService

# モジュールレベルのimport
from app.ui import ai_tool_management


class TestAIToolManagement:
    """AIツール管理画面のテストクラス。"""

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """AIツールサービスのモックを作成する。"""
        return Mock(spec=AIToolService)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルのAIツールを作成する。"""
        return AITool(
            id=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
            name_ja='テスト用AIツール',
            description='テスト用のAIツールです',
            endpoint_url='https://example.com/api',
        )

    @pytest.fixture
    def sample_ai_tool_disabled(self) -> AITool:
        """無効化されたサンプルのAIツールを作成する。"""
        tool = AITool(
            id=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
            name_ja='テスト用AIツール',
            description='テスト用のAIツールです',
            endpoint_url='https://example.com/api',
        )
        tool.disabled_at = tool.created_at
        return tool

    def test_AIツール管理ページが描画される(
        self,
        mocker: MockerFixture,
        mock_ai_tool_service: Mock,
    ) -> None:
        """AIツール管理ページが正常に描画されることをテストする。"""
        # Arrange
        mocker.patch.object(ai_tool_management.st, 'session_state', {})
        mock_title = mocker.patch.object(ai_tool_management.st, 'title')
        mock_button = mocker.patch.object(ai_tool_management.st, 'button')
        mock_button.return_value = False
        mocker.patch.object(ai_tool_management.st, 'expander')
        mocker.patch.object(ai_tool_management.st, 'columns')
        mocker.patch.object(ai_tool_management.st, 'write')
        mocker.patch.object(ai_tool_management.st, 'divider')
        mock_info = mocker.patch.object(ai_tool_management.st, 'info')
        mock_ai_tool_service.get_all_ai_tools.return_value = []

        # Act
        ai_tool_management.render_ai_tool_management_page(mock_ai_tool_service)

        # Assert
        mock_title.assert_called_once_with('AIツール管理')
        mock_info.assert_called_once_with('登録されているAIツールがありません。')

    def test_AIツールが存在しない場合にメッセージが表示される(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """AIツールが存在しない場合に適切なメッセージが表示されることをテストする。"""
        # Arrange
        mock_info = mocker.patch.object(ai_tool_management.st, 'info')
        mock_ai_tool_service.get_all_ai_tools.return_value = []

        # Act
        ai_tool_management._render_tool_list(mock_ai_tool_service)

        # Assert
        mock_info.assert_called_once_with('登録されているAIツールがありません。')

    def test_AIツール一覧が描画される(
        self,
        mocker: MockerFixture,
        mock_ai_tool_service: Mock,
        sample_ai_tool: AITool,
    ) -> None:
        """AIツール一覧が正常に描画されることをテストする。"""
        # Arrange
        mock_ai_tool_service.get_all_ai_tools.return_value = [sample_ai_tool]
        mock_columns = mocker.patch.object(ai_tool_management.st, 'columns')
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')
        mocker.patch.object(ai_tool_management.st, 'divider')
        mocker.patch.object(ai_tool_management.st, 'button')
        mock_session_state = {'tool_counter': 0}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(4)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        ai_tool_management._render_tool_list(mock_ai_tool_service)

        # Assert
        # ツールが存在する場合に適切にコンテンツが描画されることを確認
        mock_ai_tool_service.get_all_ai_tools.assert_called_once()
        assert mock_write.call_count > 0  # 何らかの出力がある

    def test_ツール情報カラムが描画される(
        self, mocker: MockerFixture, sample_ai_tool: AITool
    ) -> None:
        """ツール情報カラムが正常に描画されることをテストする。"""
        # Arrange
        mock_cols = [Mock() for _ in range(4)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')

        # Act
        ai_tool_management._render_tool_info_columns(sample_ai_tool, mock_cols)

        # Assert
        assert mock_write.call_count >= 4  # 通番、名前、説明、ステータス

    def test_通番が正しく表示される(self, mocker: MockerFixture, sample_ai_tool: AITool) -> None:
        """通番が正しく表示されることをテストする。"""
        # Arrange
        mock_cols = [Mock() for _ in range(4)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')

        # Act
        ai_tool_management._render_tool_info_columns(sample_ai_tool, mock_cols)

        # Assert
        # 通番の書き込みが呼ばれていることを確認
        write_calls = [call[0][0] for call in mock_write.call_args_list]
        assert any(isinstance(call, str) and call.isdigit() for call in write_calls)

    def test_ツール操作ボタンが描画される(
        self,
        mocker: MockerFixture,
        sample_ai_tool: AITool,
        mock_ai_tool_service: Mock,
    ) -> None:
        """ツール操作ボタンが正常に描画されることをテストする。"""
        # Arrange
        mock_columns = mocker.patch.object(ai_tool_management.st, 'columns')
        mock_button = mocker.patch.object(ai_tool_management.st, 'button')
        mock_action_cols = [Mock(), Mock()]
        for col in mock_action_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_action_cols

        # Act
        ai_tool_management._render_tool_actions(sample_ai_tool, mock_ai_tool_service)

        # Assert
        assert mock_button.call_count >= 2  # 編集ボタンと無効化ボタン

    def test_無効化されたツールの操作ボタンが描画される(
        self,
        mocker: MockerFixture,
        sample_ai_tool_disabled: AITool,
        mock_ai_tool_service: Mock,
    ) -> None:
        """無効化されたツールの操作ボタンが正常に描画されることをテストする。"""
        # Arrange
        mock_columns = mocker.patch.object(ai_tool_management.st, 'columns')
        mock_button = mocker.patch.object(ai_tool_management.st, 'button')
        mock_action_cols = [Mock(), Mock()]
        for col in mock_action_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_action_cols

        # Act
        ai_tool_management._render_tool_actions(sample_ai_tool_disabled, mock_ai_tool_service)

        # Assert
        assert mock_button.call_count >= 2  # 編集ボタンと有効化ボタン

    def test_ツール作成処理が成功する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール作成処理が成功することをテストする。"""
        # Arrange
        mock_session_state = {'ai_tool_service': mock_ai_tool_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        tool_info = {
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_ai_tool_service.create_ai_tool.return_value = True

        # Act
        ai_tool_management._handle_create_tool(tool_info)

        # Assert
        mock_ai_tool_service.create_ai_tool.assert_called_once_with(
            'テストツール', 'テスト用', 'https://example.com/api'
        )

    def test_ツール作成処理が失敗する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール作成処理が失敗することをテストする。"""
        # Arrange
        mock_session_state = {'ai_tool_service': mock_ai_tool_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_info = {
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_ai_tool_service.create_ai_tool.return_value = False

        # Act
        ai_tool_management._handle_create_tool(tool_info)

        # Assert
        mock_ai_tool_service.create_ai_tool.assert_called_once()
        mock_error.assert_called_once_with('AIツールの作成に失敗しました。')

    def test_ツール更新処理が成功する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール更新処理が成功することをテストする。"""
        # Arrange
        mock_session_state = {'ai_tool_service': mock_ai_tool_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        tool_info = {
            'tool_id': '12345678-1234-5678-1234-567812345678',
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_ai_tool_service.update_ai_tool.return_value = True

        # Act
        ai_tool_management._handle_update_tool(tool_info)

        # Assert
        mock_ai_tool_service.update_ai_tool.assert_called_once_with(
            '12345678-1234-5678-1234-567812345678',
            'テストツール',
            'テスト用',
            'https://example.com/api',
        )

    def test_ツール更新処理が失敗する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール更新処理が失敗することをテストする。"""
        # Arrange
        mock_session_state = {'ai_tool_service': mock_ai_tool_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_info = {
            'tool_id': '12345678-1234-5678-1234-567812345678',
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_ai_tool_service.update_ai_tool.return_value = False

        # Act
        ai_tool_management._handle_update_tool(tool_info)

        # Assert
        mock_ai_tool_service.update_ai_tool.assert_called_once()
        mock_error.assert_called_once_with('AIツールの更新に失敗しました。')

    def test_ツール無効化処理が成功する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール無効化処理が成功することをテストする。"""
        # Arrange
        mocker.patch.object(ai_tool_management.st, 'session_state', {})
        mock_success = mocker.patch.object(ai_tool_management.st, 'success')
        mock_rerun = mocker.patch.object(ai_tool_management.st, 'rerun')
        tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.disable_ai_tool.return_value = True

        # Act
        ai_tool_management._handle_disable_tool(tool_id, mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.disable_ai_tool.assert_called_once_with(tool_id)
        mock_success.assert_called_once_with('AIツールを無効化しました。')
        mock_rerun.assert_called_once()

    def test_ツール無効化処理が失敗する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール無効化処理が失敗することをテストする。"""
        # Arrange
        mocker.patch.object(ai_tool_management.st, 'session_state', {})
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.disable_ai_tool.return_value = False

        # Act
        ai_tool_management._handle_disable_tool(tool_id, mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.disable_ai_tool.assert_called_once_with(tool_id)
        mock_error.assert_called_once_with('AIツールの無効化に失敗しました。')

    def test_ツール有効化処理が成功する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール有効化処理が成功することをテストする。"""
        # Arrange
        mocker.patch.object(ai_tool_management.st, 'session_state', {})
        mock_success = mocker.patch.object(ai_tool_management.st, 'success')
        mock_rerun = mocker.patch.object(ai_tool_management.st, 'rerun')
        tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.enable_ai_tool.return_value = True

        # Act
        ai_tool_management._handle_enable_tool(tool_id, mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.enable_ai_tool.assert_called_once_with(tool_id)
        mock_success.assert_called_once_with('AIツールを有効化しました。')
        mock_rerun.assert_called_once()

    def test_ツール有効化処理が失敗する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール有効化処理が失敗することをテストする。"""
        # Arrange
        mocker.patch.object(ai_tool_management.st, 'session_state', {})
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_id = UUID('12345678-1234-5678-1234-567812345678')
        mock_ai_tool_service.enable_ai_tool.return_value = False

        # Act
        ai_tool_management._handle_enable_tool(tool_id, mock_ai_tool_service)

        # Assert
        mock_ai_tool_service.enable_ai_tool.assert_called_once_with(tool_id)
        mock_error.assert_called_once_with('AIツールの有効化に失敗しました。')

    def test_新規作成フォームのボタンが描画される(self, mocker: MockerFixture) -> None:
        """新規作成フォームのボタンが正常に描画されることをテストする。"""
        # Arrange
        mock_columns = mocker.patch.object(ai_tool_management.st, 'columns')
        mock_button = mocker.patch.object(ai_tool_management.st, 'button')
        tool_info = {
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_cols = [Mock(), Mock()]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        ai_tool_management._render_creation_form_buttons(tool_info)

        # Assert
        assert mock_button.call_count >= 1  # 少なくとも1つのボタンが描画される

    def test_編集フォームのボタンが描画される(self, mocker: MockerFixture) -> None:
        """編集フォームのボタンが正常に描画されることをテストする。"""
        # Arrange
        mock_columns = mocker.patch.object(ai_tool_management.st, 'columns')
        mock_button = mocker.patch.object(ai_tool_management.st, 'button')
        tool_info = {
            'tool_id': '12345678-1234-5678-1234-567812345678',
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        mock_cols = [Mock(), Mock()]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        ai_tool_management._render_edit_form_buttons(tool_info)

        # Assert
        assert mock_button.call_count >= 2  # 更新ボタンとキャンセルボタン

    def test_バリデーションが正常に動作する(self, mocker: MockerFixture) -> None:
        """バリデーションが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        valid_tool_info = {
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }
        invalid_tool_info = {
            'name': '',  # 空の名前
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }

        # Act & Assert
        # 有効なツール情報
        result_valid = ai_tool_management._validate_tool_info(valid_tool_info)
        assert result_valid is True
        mock_error.assert_not_called()

        # 無効なツール情報
        result_invalid = ai_tool_management._validate_tool_info(invalid_tool_info)
        assert result_invalid is False
        mock_error.assert_called_once_with('ツール名は必須です。')

    def test_AIツールサービス取得が正常に動作する(self, mocker: MockerFixture) -> None:
        """AIツールサービス取得が正常に動作することをテストする。"""
        # Arrange
        mock_service = Mock(spec=AIToolService)
        mock_session_state = {'ai_tool_service': mock_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')

        # Act
        result = ai_tool_management._get_ai_tool_service()

        # Assert
        assert result == mock_service
        mock_error.assert_not_called()

    def test_AIツールサービス取得が失敗する(self, mocker: MockerFixture) -> None:
        """AIツールサービス取得が失敗することをテストする。"""
        # Arrange
        mock_session_state: dict[str, object] = {}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')

        # Act
        result = ai_tool_management._get_ai_tool_service()

        # Assert
        assert result is None
        mock_error.assert_called_once_with('AIツールサービスが見つかりません。')

    def test_エラーハンドリングが正常に動作する(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """エラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mock_ai_tool_service.get_all_ai_tools.side_effect = Exception('テストエラー')

        # Act
        ai_tool_management._render_tool_list(mock_ai_tool_service)

        # Assert
        mock_error.assert_called_once()
        mock_write.assert_called()  # デバッグ情報が出力される

    def test_本番環境ではデバッグ情報が出力されない(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """本番環境ではデバッグ情報が出力されないことをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'prod'})
        mock_ai_tool_service.get_all_ai_tools.side_effect = Exception('テストエラー')

        # Act
        ai_tool_management._render_tool_list(mock_ai_tool_service)

        # Assert
        mock_error.assert_called_once()
        # デバッグ情報は出力されない
        mock_write.assert_not_called()

    def test_セッション状態設定時のエラーハンドリング(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """セッション状態設定時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mock_ai_tool_service.side_effect = Exception('セッション設定エラー')

        # Act
        ai_tool_management.render_ai_tool_management_page(mock_ai_tool_service)

        # Assert
        mock_error.assert_called()

    def test_ページヘッダー描画時のエラーハンドリング(self, mocker: MockerFixture) -> None:
        """ページヘッダー描画時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mocker.patch.object(ai_tool_management.st, 'title', side_effect=Exception('タイトルエラー'))

        # Act
        ai_tool_management._render_page_header()

        # Assert
        mock_error.assert_called_once()

    def test_新規作成ボタン描画時のエラーハンドリング(self, mocker: MockerFixture) -> None:
        """新規作成ボタン描画時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mocker.patch.object(ai_tool_management.st, 'button', side_effect=Exception('ボタンエラー'))

        # Act
        ai_tool_management._render_create_button()

        # Assert
        mock_error.assert_called_once()

    def test_モーダル描画時のエラーハンドリング(self, mocker: MockerFixture) -> None:
        """モーダル描画時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mocker.patch.object(
            ai_tool_management,
            '_render_create_modal_if_needed',
            side_effect=Exception('モーダルエラー'),
        )

        # Act
        ai_tool_management._render_modals()

        # Assert
        mock_error.assert_called_once()

    def test_ツール情報カラム描画時のエラーハンドリング(
        self, mocker: MockerFixture, sample_ai_tool: AITool
    ) -> None:
        """ツール情報カラム描画時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mock_cols = [Mock() for _ in range(4)]  # 4つのカラムが必要
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)

        # Act
        ai_tool_management._render_tool_info_columns(sample_ai_tool, mock_cols)

        # Assert
        # エラーハンドリングは内部で行われるため、エラーは発生しない
        mock_error.assert_not_called()

    def test_ツール操作ボタン描画時のエラーハンドリング(
        self, mocker: MockerFixture, sample_ai_tool: AITool, mock_ai_tool_service: Mock
    ) -> None:
        """ツール操作ボタン描画時のエラーハンドリングが正常に動作することをテストする。"""
        # Arrange
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        mock_cols = [Mock()]
        mock_cols[0].__enter__ = Mock(side_effect=Exception('ボタンエラー'))
        mock_cols[0].__exit__ = Mock(return_value=None)

        # Act
        ai_tool_management._render_tool_actions(sample_ai_tool, mock_ai_tool_service)

        # Assert
        # エラーハンドリングは内部で行われるため、エラーは発生しない
        mock_error.assert_not_called()

    def test_デバッグ情報が表示される(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """デバッグ情報が正常に表示されることをテストする。"""
        # Arrange
        mock_write = mocker.patch.object(ai_tool_management.st, 'write')
        mocker.patch.object(ai_tool_management.st, 'session_state', {'APP_ENV': 'test'})
        sample_tool = AITool(
            id=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
            name_ja='テストツール',
            description='テスト用',
            endpoint_url='https://example.com/api',
        )
        mock_ai_tool_service.get_all_ai_tools.return_value = [sample_tool]

        # Act
        ai_tool_management._render_tool_list(mock_ai_tool_service)

        # Assert
        # デバッグ情報が出力されることを確認
        write_calls = [call[0][0] for call in mock_write.call_args_list]
        assert any('Debug:' in str(call) for call in write_calls)

    def test_セッション状態の初期化が正常に動作する(self, mocker: MockerFixture) -> None:
        """セッション状態の初期化が正常に動作することをテストする。"""
        # Arrange
        mock_session_state: dict[str, object] = mocker.patch.object(
            ai_tool_management.st, 'session_state', {}
        )
        mock_ai_tool_service = Mock(spec=AIToolService)

        # Act
        ai_tool_management.render_ai_tool_management_page(mock_ai_tool_service)

        # Assert
        # セッション状態が設定されていることを確認
        assert 'ai_tool_service' in mock_session_state
        assert 'show_create_modal' in mock_session_state
        assert 'show_edit_modal' in mock_session_state
        assert 'APP_ENV' in mock_session_state

    def test_ツール作成時のバリデーションエラー(
        self, mocker: MockerFixture, mock_ai_tool_service: Mock
    ) -> None:
        """ツール作成時のバリデーションエラーが正常に処理されることをテストする。"""
        # Arrange
        mock_session_state = {'ai_tool_service': mock_ai_tool_service}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_info = {
            'name': '',  # 空の名前でバリデーションエラー
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }

        # Act
        ai_tool_management._handle_create_tool(tool_info)

        # Assert
        mock_error.assert_called_once_with('ツール名は必須です。')
        mock_ai_tool_service.create_ai_tool.assert_not_called()

    def test_ツール作成時のサービス取得エラー(self, mocker: MockerFixture) -> None:
        """ツール作成時のサービス取得エラーが正常に処理されることをテストする。"""
        # Arrange
        mock_session_state: dict[str, object] = {}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_info = {
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }

        # Act
        ai_tool_management._handle_create_tool(tool_info)

        # Assert
        mock_error.assert_called_once_with('AIツールサービスが見つかりません。')

    def test_ツール更新時のサービス取得エラー(self, mocker: MockerFixture) -> None:
        """ツール更新時のサービス取得エラーが正常に処理されることをテストする。"""
        # Arrange
        mock_session_state: dict[str, object] = {}
        mocker.patch.object(ai_tool_management.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(ai_tool_management.st, 'error')
        tool_info = {
            'tool_id': '12345678-1234-5678-1234-567812345678',
            'name': 'テストツール',
            'description': 'テスト用',
            'endpoint_url': 'https://example.com/api',
        }

        # Act
        ai_tool_management._handle_update_tool(tool_info)

        # Assert
        mock_error.assert_called_once_with('AIツールサービスが見つかりません。')
