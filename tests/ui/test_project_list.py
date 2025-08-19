"""プロジェクトリストのテストモジュール。"""

from datetime import datetime
from unittest.mock import Mock
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from pytest_mock import MockerFixture

from app.models import ToolType
from app.models.project import Project
from app.ui import project_list


class MockSessionState(dict[str, object]):
    """辞書と属性アクセスの両方をサポートするSessionStateモック。"""

    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from e

    def __setattr__(self, name: str, value: object) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from e


class TestProjectList:
    """プロジェクトリストのテストクラス。"""

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """プロジェクトサービスのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def mock_modal(self) -> Mock:
        """モーダルのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルのプロジェクトを作成する。"""
        return Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

    def test_PENDING状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        # Arrange
        sample_project.executed_at = None
        sample_project.finished_at = None

        # Act
        icon = project_list._get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '💬'

    def test_PROCESSING状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.finished_at = None

        # Act
        icon = project_list._get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '⏳'

    def test_COMPLETED状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.finished_at = datetime.now(ZoneInfo('Asia/Tokyo'))

        # Act
        icon = project_list._get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '✅'

    def test_FAILED状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.finished_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        # resultにerrorを含めることでFAILED状態にする
        sample_project.result = {'error': 'テストエラー'}

        # Act
        icon = project_list._get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '❌'

    def test_実行中のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        # Act
        icon = project_list._get_status_icon(sample_project, is_running=True)

        # Assert
        assert icon == '🏃'

    def test_ヘッダーカラムが正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_divider = mocker.patch.object(project_list.st, 'divider')

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_header_columns()

        # Assert
        mock_columns.assert_called_once_with((1, 4, 2, 2, 1, 1))
        # 各カラムのwriteが呼ばれることを確認
        for col in mock_cols:
            col.write.assert_called_once()
        mock_divider.assert_called_once()

    def test_プロジェクトが空の場合にメッセージが表示される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_header = mocker.patch.object(project_list.st, 'header')
        mock_info = mocker.patch.object(project_list.st, 'info')
        mock_session_state = MockSessionState()
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)

        # Act
        project_list.render_project_list([], Mock(), Mock())

        # Assert
        mock_header.assert_called_once_with('プロジェクト一覧')
        mock_info.assert_called_once_with('まだプロジェクトがありません。')

    def test_プロジェクト一覧が正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_header = mocker.patch.object(project_list.st, 'header')
        mock_session_state = MockSessionState()
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_render_header_columns')
        mocker.patch.object(project_list, '_render_project_row')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # Act
        project_list.render_project_list([sample_project], Mock(), Mock())

        # Assert
        mock_header.assert_called_once_with('プロジェクト一覧')

    def test_プロジェクト行が正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            col.button.return_value = False  # ボタンが押されていない状態
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        mock_columns.assert_called_once_with((1, 4, 1, 1, 1, 1))
        # 各カラムで適切なメソッドが呼ばれることを確認
        mock_cols[0].write.assert_called_once()  # No.
        mock_cols[1].write.assert_called_once()  # プロジェクト名
        mock_cols[2].write.assert_called_once()  # 作成日時
        mock_cols[3].write.assert_called_once()  # 実行日時
        mock_cols[4].button.assert_called_once()  # 詳細ボタン
        mock_cols[5].button.assert_called_once()  # 実行ボタン

    def test_詳細ボタンが押された場合にモーダルが開く(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_session_state = Mock()
        mock_session_state.running_workers = {}
        mock_session_state.modal_project = None
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mock_modal = Mock()
        mock_modal.open = Mock()

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        button_state = {'detail_btn': True, 'exec_btn': False}

        # Act
        project_list._handle_project_buttons(button_state, sample_project, mock_modal, Mock())

        # Assert
        assert mock_session_state.modal_project == sample_project
        mock_modal.open.assert_called_once()

    def test_実行ボタンが押された場合にプロジェクトが実行される(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_session_state = Mock()
        mock_session_state.running_workers = {}
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mock_info = mocker.patch.object(project_list.st, 'info')
        mock_rerun = mocker.patch.object(project_list.st, 'rerun')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service = Mock()
        mock_project_service.execute_project.return_value = (sample_project, '実行成功')

        button_state = {'detail_btn': False, 'exec_btn': True}

        # Act
        project_list._handle_project_buttons(
            button_state, sample_project, Mock(), mock_project_service
        )

        # Assert
        mock_project_service.execute_project.assert_called_once_with(sample_project.id)
        mock_info.assert_called_once_with('実行成功')
        mock_rerun.assert_called_once()

    def test_実行ボタンが押された場合にエラーが発生するとエラーメッセージが表示される(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_session_state = Mock()
        mock_session_state.running_workers = {}
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mock_error = mocker.patch.object(project_list.st, 'error')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service = Mock()
        mock_project_service.execute_project.return_value = (None, '実行失敗')

        button_state = {'detail_btn': False, 'exec_btn': True}

        # Act
        project_list._handle_project_buttons(
            button_state, sample_project, Mock(), mock_project_service
        )

        # Assert
        mock_project_service.execute_project.assert_called_once_with(sample_project.id)
        mock_error.assert_called_once_with('実行失敗')

    def test_ボタンが押されない場合は何も起こらない(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_session_state = Mock()
        mock_session_state.running_workers = {}
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mock_modal = Mock()
        mock_project_service = Mock()

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        button_state = {'detail_btn': False, 'exec_btn': False}

        # Act
        project_list._handle_project_buttons(
            button_state, sample_project, mock_modal, mock_project_service
        )

        # Assert
        mock_modal.open.assert_not_called()
        mock_project_service.execute_project.assert_not_called()

    def test_実行済みプロジェクトの行が正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        mock_columns.assert_called_once_with((1, 4, 1, 1, 1, 1))
        # 各カラムのwriteが呼ばれることを確認
        mock_cols[0].write.assert_called_once()
        mock_cols[1].write.assert_called_once()
        mock_cols[2].write.assert_called_once()
        mock_cols[3].write.assert_called_once()
        mock_cols[4].button.assert_called_once()
        mock_cols[5].button.assert_not_called()

    def test_実行中のプロジェクトの行が正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState(
            {'running_workers': {UUID('12345678-1234-5678-1234-567812345678')}}
        )
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        mock_columns.assert_called_once_with((1, 4, 1, 1, 1, 1))
        # 各カラムのwriteが呼ばれることを確認
        for i, col in enumerate(mock_cols):
            if i < 4:
                col.write.assert_called()

    def test_running_workersが初期化される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_session_state = MockSessionState()
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list.st, 'header')
        mocker.patch.object(project_list, '_render_header_columns')
        mocker.patch.object(project_list, '_render_project_row')

        # Act
        project_list.render_project_list([], Mock(), Mock())

        # Assert
        assert 'running_workers' in mock_session_state
        assert mock_session_state['running_workers'] == {}

    def test_プロジェクト行の各カラムが正しく描画される(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        # 各カラムに適切な内容が書き込まれていることを確認
        mock_cols[0].write.assert_called()
        mock_cols[1].write.assert_called()
        mock_cols[2].write.assert_called()
        mock_cols[3].write.assert_called()
        mock_cols[4].button.assert_called()
        mock_cols[5].button.assert_called()

    def test_実行日時がNoneの場合の処理(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        sample_project.executed_at = None

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        # 各カラムのwriteが呼ばれることを確認
        mock_cols[0].write.assert_called()
        mock_cols[1].write.assert_called()
        mock_cols[2].write.assert_called()
        mock_cols[3].write.assert_called()
        mock_cols[4].button.assert_called()
        mock_cols[5].button.assert_called()

    def test_実行日時が設定されている場合の処理(self, mocker: MockerFixture) -> None:
        # Arrange
        mock_columns = mocker.patch.object(project_list.st, 'columns')
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_list.st, 'session_state', mock_session_state)
        mocker.patch.object(project_list, '_handle_project_buttons')

        sample_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        sample_project.executed_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo'))

        # カラムのモックを正しく設定
        mock_cols = [Mock() for _ in range(6)]
        for col in mock_cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        mock_columns.return_value = mock_cols

        # Act
        project_list._render_project_row(0, sample_project, Mock(), Mock())

        # Assert
        # 各カラムのwriteが呼ばれることを確認
        mock_cols[0].write.assert_called()
        mock_cols[1].write.assert_called()
        mock_cols[2].write.assert_called()
        mock_cols[3].write.assert_called()
        mock_cols[4].button.assert_called()
        mock_cols[5].button.assert_not_called()
