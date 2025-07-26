"""メインページのUIテスト。"""

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
import streamlit as st

from app.models.project import Project
from app.services.ai_tool_service import AIToolService
from app.services.project_service import ProjectService
from app.ui.main_page import (
    _get_sort_key,
    _initialize_session_state,
    get_services,
    render_main_page,
)


class TestMainPage:
    """メインページのテストクラス。"""

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """モックプロジェクトサービスのフィクスチャ。"""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """モックAIツールサービスのフィクスチャ。"""
        return Mock(spec=AIToolService)

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルプロジェクトのフィクスチャ。"""
        return Project(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            name='テストプロジェクト1',
            source='test_source',
            ai_tool='test_tool',
            created_at=datetime.now(ZoneInfo('Asia/Tokyo')),
        )

    def test_セッション状態が初期化される(self) -> None:
        """セッション状態が初期化されることをテスト。"""
        # Arrange
        if 'running_workers' in st.session_state:
            del st.session_state['running_workers']
        if 'modal_project' in st.session_state:
            del st.session_state['modal_project']

        # Act
        _initialize_session_state()

        # Assert
        assert 'running_workers' in st.session_state
        assert 'modal_project' in st.session_state
        assert st.session_state['running_workers'] == {}
        assert st.session_state['modal_project'] is None

    def test_既にセッション状態が存在する場合は変更されない(self) -> None:
        """既にセッション状態が存在する場合は変更されないことをテスト。"""
        # Arrange
        st.session_state['running_workers'] = {'worker1': 'running'}
        st.session_state['modal_project'] = {'id': 'test'}

        # Act
        _initialize_session_state()

        # Assert
        assert st.session_state['running_workers'] == {'worker1': 'running'}
        assert st.session_state['modal_project'] == {'id': 'test'}

    def test_プロジェクトのソートキーが正しく取得される(self, sample_project: Project) -> None:
        """プロジェクトのソートキーが正しく取得されることをテスト。"""
        # Arrange
        jst = ZoneInfo('Asia/Tokyo')

        # Act
        sort_key = _get_sort_key(sample_project, jst)

        # Assert
        assert isinstance(sort_key, datetime)
        assert sort_key.tzinfo == jst

    def test_タイムゾーン情報がないプロジェクトのソートキーが正しく取得される(self) -> None:
        """タイムゾーン情報がないプロジェクトのソートキーが正しく取得されることをテスト。"""
        # Arrange
        naive_datetime = datetime.now()
        project = Project(
            id=UUID('87654321-4321-8765-4321-876543210987'),
            name='テストプロジェクト',
            source='test_source',
            ai_tool='test_tool',
            created_at=naive_datetime,
        )
        jst = ZoneInfo('Asia/Tokyo')

        # Act
        sort_key = _get_sort_key(project, jst)

        # Assert
        assert isinstance(sort_key, datetime)
        assert sort_key.tzinfo == jst
        assert sort_key.replace(tzinfo=None) == naive_datetime

    @patch('app.ui.main_page.JsonProjectRepository')
    @patch('app.ui.main_page.JsonAIToolRepository')
    @patch('app.ui.main_page.ProjectService')
    @patch('app.ui.main_page.AIToolService')
    @patch('app.ui.main_page.config')
    def test_サービスが正しく取得される(
        self,
        mock_config: Mock,
        mock_ai_tool_service_class: Mock,
        mock_project_service_class: Mock,
        mock_ai_tool_repo_class: Mock,
        mock_project_repo_class: Mock,
    ) -> None:
        """サービスが正しく取得されることをテスト。"""
        # Arrange
        mock_config.data_dir_path = '/test/path'
        mock_project_repo = Mock()
        mock_ai_tool_repo = Mock()
        mock_project_service = Mock()
        mock_ai_tool_service = Mock()

        mock_project_repo_class.return_value = mock_project_repo
        mock_ai_tool_repo_class.return_value = mock_ai_tool_repo
        mock_project_service_class.return_value = mock_project_service
        mock_ai_tool_service_class.return_value = mock_ai_tool_service

        # Act
        project_service, ai_tool_service = get_services()

        # Assert
        mock_project_repo_class.assert_called_once_with('/test/path')
        mock_ai_tool_repo_class.assert_called_once_with('/test/path')
        mock_ai_tool_service_class.assert_called_once_with(mock_ai_tool_repo)
        mock_project_service_class.assert_called_once_with(mock_project_repo, mock_ai_tool_service)
        assert project_service == mock_project_service
        assert ai_tool_service == mock_ai_tool_service

    @patch('app.ui.main_page.st.set_page_config')
    @patch('app.ui.main_page.st.title')
    @patch('app.ui.main_page.get_services')
    @patch('app.ui.main_page.render_project_creation_form')
    @patch('app.ui.main_page.Modal')
    @patch('app.ui.main_page.render_project_detail_modal')
    @patch('app.ui.main_page.render_project_list')
    def test_メインページが正しく描画される(
        self,
        mock_render_project_list: Mock,
        mock_render_project_detail_modal: Mock,
        mock_modal_class: Mock,
        mock_render_project_creation_form: Mock,
        mock_get_services: Mock,
        mock_title: Mock,
        mock_set_page_config: Mock,
    ) -> None:
        """メインページが正しく描画されることをテスト。"""
        # Arrange
        mock_project_service = Mock()
        mock_ai_tool_service = Mock()
        mock_get_services.return_value = (mock_project_service, mock_ai_tool_service)

        mock_modal = Mock()
        mock_modal_class.return_value = mock_modal

        mock_project_service.get_all_projects.return_value = []

        # Act
        render_main_page()

        # Assert
        mock_set_page_config.assert_called_once_with(
            page_title='AI Meeting Assistant', page_icon='🤖', layout='wide'
        )
        mock_title.assert_called_once_with('AI Meeting Assistant 🤖')
        mock_get_services.assert_called_once()
        mock_render_project_creation_form.assert_called_once_with(
            mock_project_service, mock_ai_tool_service
        )
        mock_modal_class.assert_called_once_with(
            title='プロジェクト詳細', key='project_detail_modal'
        )
        mock_render_project_detail_modal.assert_called_once_with(mock_modal)
        mock_render_project_list.assert_called_once()

    @patch('app.ui.main_page.st.set_page_config')
    @patch('app.ui.main_page.st.title')
    @patch('app.ui.main_page.get_services')
    @patch('app.ui.main_page.render_project_creation_form')
    @patch('app.ui.main_page.Modal')
    @patch('app.ui.main_page.render_project_detail_modal')
    @patch('app.ui.main_page.render_project_list')
    def test_プロジェクト一覧が正しくソートされて描画される(
        self,
        mock_render_project_list: Mock,
        mock_render_project_detail_modal: Mock,
        mock_modal_class: Mock,
        mock_render_project_creation_form: Mock,
        mock_get_services: Mock,
        mock_title: Mock,
        mock_set_page_config: Mock,
    ) -> None:
        """プロジェクト一覧が正しくソートされて描画されることをテスト。"""
        # Arrange
        mock_project_service = Mock()
        mock_ai_tool_service = Mock()
        mock_get_services.return_value = (mock_project_service, mock_ai_tool_service)

        mock_modal = Mock()
        mock_modal_class.return_value = mock_modal

        # 古いプロジェクトと新しいプロジェクトを作成
        old_project = Project(
            id=UUID('11111111-1111-1111-1111-111111111111'),
            name='古いプロジェクト',
            source='old_source',
            ai_tool='old_tool',
            created_at=datetime(2023, 1, 1, tzinfo=ZoneInfo('Asia/Tokyo')),
        )
        new_project = Project(
            id=UUID('22222222-2222-2222-2222-222222222222'),
            name='新しいプロジェクト',
            source='new_source',
            ai_tool='new_tool',
            created_at=datetime(2024, 1, 1, tzinfo=ZoneInfo('Asia/Tokyo')),
        )

        mock_project_service.get_all_projects.return_value = [old_project, new_project]

        # Act
        render_main_page()

        # Assert
        # render_project_listが呼ばれた時の引数を確認
        call_args = mock_render_project_list.call_args
        projects_arg = call_args[0][0]  # 最初の引数（プロジェクトリスト）
        assert len(projects_arg) == 2
        # 新しいプロジェクトが最初に来る（降順ソート）
        assert projects_arg[0].id == UUID('22222222-2222-2222-2222-222222222222')
        assert projects_arg[1].id == UUID('11111111-1111-1111-1111-111111111111')
