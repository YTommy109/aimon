"""プロジェクト一覧のUIテスト。"""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest

from app.models.project import Project
from app.services.project_service import ProjectService
from app.ui.project_list import (
    _get_status_icon,
    _handle_project_buttons,
    _render_header_columns,
    _render_project_row,
    render_project_list,
)


class TestProjectList:
    """プロジェクト一覧のテストクラス。"""

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """モックプロジェクトサービスのフィクスチャ。"""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def mock_modal(self) -> Mock:
        """モックモーダルのフィクスチャ。"""
        return Mock()

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルプロジェクトのフィクスチャ。"""
        return Project(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name='テストプロジェクト',
            source='test_source',
            ai_tool='test_tool',
            created_at=datetime.now(ZoneInfo('Asia/Tokyo')),
        )

    def test_PENDING状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        """PENDING状態のプロジェクトのアイコンが正しく取得されることをテスト。"""
        # Act
        icon = _get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '💬'

    def test_PROCESSING状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        """PROCESSING状態のプロジェクトのアイコンが正しく取得されることをテスト。"""
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))

        # Act
        icon = _get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '⏳'

    def test_COMPLETED状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        """COMPLETED状態のプロジェクトのアイコンが正しく取得されることをテスト。"""
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.finished_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.result = {'status': 'success'}

        # Act
        icon = _get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '✅'

    def test_FAILED状態のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        """FAILED状態のプロジェクトのアイコンが正しく取得されることをテスト。"""
        # Arrange
        sample_project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.finished_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        sample_project.result = {'error': 'test error'}

        # Act
        icon = _get_status_icon(sample_project, is_running=False)

        # Assert
        assert icon == '❌'

    def test_実行中のプロジェクトのアイコンが正しく取得される(
        self, sample_project: Project
    ) -> None:
        """実行中のプロジェクトのアイコンが正しく取得されることをテスト。"""
        # Act
        icon = _get_status_icon(sample_project, is_running=True)

        # Assert
        assert icon == '🏃'

    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.divider')
    def test_ヘッダーカラムが正しく描画される(self, mock_divider: Mock, mock_columns: Mock) -> None:
        """ヘッダーカラムが正しく描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols

        # Act
        _render_header_columns()

        # Assert
        mock_columns.assert_called_once_with((1, 4, 2, 2, 1, 1))
        # 各カラムのwriteが呼ばれることを確認
        for col in mock_cols:
            col.write.assert_called_once()
        mock_divider.assert_called_once()

    @patch('app.ui.project_list.st.header')
    @patch('app.ui.project_list.st.info')
    def test_プロジェクトが空の場合にメッセージが表示される(
        self, mock_info: Mock, mock_header: Mock
    ) -> None:
        """プロジェクトが空の場合にメッセージが表示されることをテスト。"""
        # Arrange
        projects: list[Project] = []

        # Act
        render_project_list(projects, Mock(), Mock())

        # Assert
        mock_header.assert_called_once_with('プロジェクト一覧')
        mock_info.assert_called_once_with('まだプロジェクトがありません。')

    @patch('app.ui.project_list.st.header')
    @patch('app.ui.project_list._render_header_columns')
    @patch('app.ui.project_list._render_project_row')
    def test_プロジェクト一覧が正しく描画される(
        self, mock_render_row: Mock, mock_render_header: Mock, mock_header: Mock
    ) -> None:
        """プロジェクト一覧が正しく描画されることをテスト。"""
        # Arrange
        mock_project1 = Mock(spec=Project)
        mock_project2 = Mock(spec=Project)
        projects = [mock_project1, mock_project2]
        modal = Mock()
        project_service = Mock()

        # Act
        render_project_list(projects, modal, project_service)  # type: ignore[arg-type]

        # Assert
        mock_header.assert_called_once_with('プロジェクト一覧')
        mock_render_header.assert_called_once()
        assert mock_render_row.call_count == 2

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_プロジェクト行が正しく描画される(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """プロジェクト行が正しく描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        # 各カラムのbuttonメソッドの戻り値を設定
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = None  # 実行ボタンが表示される条件

        project_service = Mock()
        project_service.execute_project.return_value = (Mock(), '実行成功')

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        mock_columns.assert_called_once_with((1, 4, 1, 1, 1, 1))
        # 各カラムのbuttonが呼ばれることを確認
        mock_cols[4].button.assert_called_once_with('詳細', key=f'detail_{project.id}')
        mock_cols[5].button.assert_called_once_with('実行', key=f'run_{project.id}')
        # execute_projectは呼ばれない（ボタンが押されていないため）
        project_service.execute_project.assert_not_called()

    @patch('app.ui.project_list.st.session_state')
    def test_詳細ボタンが押された場合にモーダルが開く(
        self, mock_session_state: Mock, mock_modal: Mock
    ) -> None:
        """詳細ボタンが押された場合にモーダルが開くことをテスト。"""
        # Arrange
        button_state = {'detail_btn': True, 'exec_btn': False}
        project = Mock()
        modal = Mock()

        # Act
        _handle_project_buttons(button_state, project, modal, Mock())

        # Assert
        assert mock_session_state.modal_project == project
        modal.open.assert_called_once()

    @patch('app.ui.project_list.logging.getLogger')
    @patch('app.ui.project_list.st.info')
    @patch('app.ui.project_list.st.rerun')
    def test_実行ボタンが押された場合にプロジェクトが実行される(
        self, mock_rerun: Mock, mock_info: Mock, mock_get_logger: Mock
    ) -> None:
        """実行ボタンが押された場合にプロジェクトが実行されることをテスト。"""
        # Arrange
        button_state = {'detail_btn': False, 'exec_btn': True}
        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.ai_tool = 'test_tool'

        modal = Mock()
        project_service = Mock()
        project_service.execute_project.return_value = (Mock(), '実行成功')

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Act
        _handle_project_buttons(button_state, project, modal, project_service)

        # Assert
        project_service.execute_project.assert_called_once_with(str(project.id))
        mock_logger.info.assert_called_once()
        mock_info.assert_called_once_with('実行成功')
        mock_rerun.assert_called_once()

    @patch('app.ui.project_list.logging.getLogger')
    @patch('app.ui.project_list.st.error')
    def test_実行ボタンが押された場合にエラーが発生するとエラーメッセージが表示される(
        self, mock_error: Mock, mock_get_logger: Mock
    ) -> None:
        """実行ボタンが押された場合にエラーが発生するとエラーメッセージが表示されることをテスト。"""
        # Arrange
        button_state = {'detail_btn': False, 'exec_btn': True}
        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.ai_tool = 'test_tool'

        modal = Mock()
        project_service = Mock()
        project_service.execute_project.return_value = (None, '実行エラー')

        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Act
        _handle_project_buttons(button_state, project, modal, project_service)

        # Assert
        project_service.execute_project.assert_called_once_with(str(project.id))
        mock_logger.info.assert_called_once()
        mock_error.assert_called_once_with('実行エラー')

    def test_ボタンが押されない場合は何も起こらない(self) -> None:
        """ボタンが押されない場合は何も起こらないことをテスト。"""
        # Arrange
        button_state = {'detail_btn': False, 'exec_btn': False}
        project = Mock()
        modal = Mock()
        project_service = Mock()

        # Act
        _handle_project_buttons(button_state, project, modal, project_service)

        # Assert
        project_service.execute_project.assert_not_called()
        modal.open.assert_not_called()

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_実行済みプロジェクトの行が正しく描画される(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """実行済みプロジェクトの行が正しく描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))  # 実行済み

        project_service = Mock()

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        # 実行済みプロジェクトの場合、実行ボタンは表示されない
        mock_cols[5].button.assert_not_called()

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_実行中のプロジェクトの行が正しく描画される(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """実行中のプロジェクトの行が正しく描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {UUID('12345678-1234-5678-1234-567812345678')}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = None

        project_service = Mock()

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        # 実行中のプロジェクトでもexecuted_atがNoneなら実行ボタンは表示される
        mock_cols[5].button.assert_called_once_with(
            '実行', key='run_12345678-1234-5678-1234-567812345678'
        )

    @patch('app.ui.project_list.st.session_state')
    def test_running_workersが初期化される(self, mock_session_state: Mock) -> None:
        """running_workersが初期化されることをテスト。"""
        # Arrange
        mock_session_state.__contains__.return_value = False
        mock_session_state.running_workers = Mock()
        mock_project = Mock(spec=Project)
        mock_project.id = UUID('12345678-1234-5678-1234-567812345678')
        mock_project.name = 'テストプロジェクト'
        mock_project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        mock_project.executed_at = None
        projects = [mock_project]
        modal = Mock()
        project_service = Mock()

        # Act
        render_project_list(projects, modal, project_service)  # type: ignore[arg-type]

        # Assert
        # 実際のコードでは st.session_state.running_workers = {} を使用
        assert mock_session_state.running_workers == {}

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_プロジェクト行の各カラムが正しく描画される(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """プロジェクト行の各カラムが正しく描画されることをテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = None

        project_service = Mock()

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        # 各カラムのwriteが呼ばれることを確認
        mock_cols[0].write.assert_called_once_with('1')  # No.
        mock_cols[1].write.assert_called_once()  # プロジェクト名
        mock_cols[2].write.assert_called_once()  # 作成日時
        mock_cols[3].write.assert_called_once()  # 実行日時

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_実行日時がNoneの場合の処理(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """実行日時がNoneの場合の処理をテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = None

        project_service = Mock()

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        # 実行日時がNoneの場合、空文字が表示される
        mock_cols[3].write.assert_called_once_with('')

    @patch('app.ui.project_list.st.session_state')
    @patch('app.ui.project_list.st.columns')
    @patch('app.ui.project_list.st.button')
    def test_実行日時が設定されている場合の処理(
        self, mock_button: Mock, mock_columns: Mock, mock_session_state: Mock
    ) -> None:
        """実行日時が設定されている場合の処理をテスト。"""
        # Arrange
        mock_cols = [Mock() for _ in range(6)]
        mock_columns.return_value = mock_cols
        mock_cols[4].button.return_value = False  # detail_btn
        mock_cols[5].button.return_value = False  # exec_btn
        mock_session_state.running_workers = {}

        project = Mock()
        project.id = UUID('12345678-1234-5678-1234-567812345678')
        project.name = 'テストプロジェクト'
        project.created_at = datetime.now(ZoneInfo('Asia/Tokyo'))
        project.executed_at = datetime.now(ZoneInfo('Asia/Tokyo'))

        project_service = Mock()

        # Act
        _render_project_row(0, project, Mock(), project_service)

        # Assert
        # 実行日時が設定されている場合、フォーマットされた日時が表示される
        mock_cols[3].write.assert_called_once()
        call_args = mock_cols[3].write.call_args[0][0]
        assert isinstance(call_args, str)
        assert '/' in call_args  # 日付フォーマットが含まれている
