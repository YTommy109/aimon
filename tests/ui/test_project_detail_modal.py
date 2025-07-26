"""プロジェクト詳細モーダルのUIテスト。"""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest

from app.models.project import Project, ProjectStatus
from app.ui.project_detail_modal import render_project_detail_modal


class TestProjectDetailModal:
    """プロジェクト詳細モーダルのテストクラス。"""

    @pytest.fixture
    def mock_modal(self) -> Mock:
        """モックモーダルのフィクスチャ。"""
        mock = Mock()
        mock.is_open.return_value = True
        # コンテキストマネージャーとして動作するように設定
        mock.container.return_value.__enter__ = Mock()
        mock.container.return_value.__exit__ = Mock()
        return mock

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルプロジェクトのフィクスチャ。"""
        return Project(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name='テストプロジェクト',
            source='test_source',
            ai_tool='test_tool',
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
            executed_at=datetime(2024, 1, 1, 12, 30, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
            finished_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
        )

    @patch('app.ui.project_detail_modal.st.session_state')
    def test_モーダルが閉じている場合は何も描画されない(
        self, mock_session_state: Mock, mock_modal: Mock
    ) -> None:
        """モーダルが閉じている場合は何も描画されないことをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = False

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_not_called()

    @patch('app.ui.project_detail_modal.st.session_state')
    @patch('app.ui.project_detail_modal.st.markdown')
    def test_プロジェクトが存在しない場合は何も描画されない(
        self, mock_markdown: Mock, mock_session_state: Mock, mock_modal: Mock
    ) -> None:
        """プロジェクトが存在しない場合は何も描画されないことをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_session_state.modal_project = None

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_called_once()
        mock_markdown.assert_not_called()

    @patch('app.ui.project_detail_modal.st.session_state')
    @patch('app.ui.project_detail_modal.st.markdown')
    def test_プロジェクト詳細が正しく描画される(
        self,
        mock_markdown: Mock,
        mock_session_state: Mock,
        mock_modal: Mock,
        sample_project: Project,
    ) -> None:
        """プロジェクト詳細が正しく描画されることをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_session_state.modal_project = sample_project
        mock_session_state.running_workers = {}

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_called_once()
        assert mock_markdown.call_count == 2  # タイトルと詳細情報

        # タイトルの確認
        title_call = mock_markdown.call_args_list[0]
        assert '### テストプロジェクト' in title_call[0][0]

        # 詳細情報の確認
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert 'UUID' in detail_text
        assert '対象パス' in detail_text
        assert 'AIツール' in detail_text
        assert 'ステータス' in detail_text
        assert '作成日時' in detail_text
        assert '実行日時' in detail_text
        assert '終了日時' in detail_text

    @patch('app.ui.project_detail_modal.st.session_state')
    @patch('app.ui.project_detail_modal.st.markdown')
    def test_実行中のプロジェクトのステータスが正しく表示される(
        self,
        mock_markdown: Mock,
        mock_session_state: Mock,
        mock_modal: Mock,
        sample_project: Project,
    ) -> None:
        """実行中のプロジェクトのステータスが正しく表示されることをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_session_state.modal_project = sample_project
        mock_session_state.running_workers = {sample_project.id: 'running'}

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert 'Running' in detail_text

    @patch('app.ui.project_detail_modal.st.session_state')
    @patch('app.ui.project_detail_modal.st.markdown')
    def test_実行されていないプロジェクトのステータスが正しく表示される(
        self, mock_markdown: Mock, mock_session_state: Mock, mock_modal: Mock
    ) -> None:
        """実行されていないプロジェクトのステータスが正しく表示されることをテスト。"""
        # Arrange
        project = Project(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name='テストプロジェクト',
            source='test_source',
            ai_tool='test_tool',
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
        )
        mock_modal.is_open.return_value = True
        mock_session_state.modal_project = project
        mock_session_state.running_workers = {}

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert ProjectStatus.PENDING.value in detail_text

    @patch('app.ui.project_detail_modal.st.session_state')
    @patch('app.ui.project_detail_modal.st.markdown')
    def test_日時がNoneの場合にN_Aが表示される(
        self, mock_markdown: Mock, mock_session_state: Mock, mock_modal: Mock
    ) -> None:
        """日時がNoneの場合にN/Aが表示されることをテスト。"""
        # Arrange
        project = Project(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name='テストプロジェクト',
            source='test_source',
            ai_tool='test_tool',
            executed_at=None,
            finished_at=None,
        )
        mock_modal.is_open.return_value = True
        mock_session_state.modal_project = project
        mock_session_state.running_workers = {}

        # Act
        render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert 'N/A' in detail_text
        assert '作成日時' in detail_text
        assert '実行日時' in detail_text
        assert '終了日時' in detail_text
