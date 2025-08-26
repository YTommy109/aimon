"""プロジェクト詳細モーダルのテスト。"""

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from pytest_mock import MockerFixture

from app.models.project import Project
from app.types import ProjectID, ToolType
from app.ui import project_detail_modal


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


class TestProjectDetailModal:
    """プロジェクト詳細モーダルのテストクラス。"""

    @pytest.fixture
    def mock_modal(self) -> Mock:
        """モーダルのモックを作成する。"""
        mock = Mock()
        mock.container.return_value.__enter__ = Mock(return_value=mock.container.return_value)
        mock.container.return_value.__exit__ = Mock(return_value=None)
        return mock

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルのプロジェクトを作成する。"""
        return Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
            executed_at=datetime(2024, 1, 1, 12, 30, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
            finished_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')),
        )

    def test_モーダルが閉じている場合は何も描画されない(
        self, mocker: MockerFixture, mock_modal: Mock
    ) -> None:
        """モーダルが閉じている場合は何も描画されないことをテスト。"""
        # Arrange
        mocker.patch.object(project_detail_modal.st, 'session_state')
        mock_modal.is_open.return_value = False

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_not_called()

    def test_プロジェクトが存在しない場合は何も描画されない(
        self, mocker: MockerFixture, mock_modal: Mock
    ) -> None:
        """プロジェクトが存在しない場合は何も描画されないことをテスト。"""
        # Arrange
        mock_session_state = Mock()
        mock_session_state.modal_project = None
        mocker.patch.object(project_detail_modal.st, 'session_state', mock_session_state)
        mock_markdown = mocker.patch.object(project_detail_modal.st, 'markdown')
        mock_modal.is_open.return_value = True

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_called_once()
        mock_markdown.assert_not_called()

    def test_プロジェクト詳細が正しく描画される(
        self,
        mocker: MockerFixture,
        mock_modal: Mock,
        sample_project: Project,
    ) -> None:
        """プロジェクト詳細が正しく描画されることをテスト。"""
        # Arrange
        mock_session_state = Mock()
        mock_session_state.modal_project = sample_project
        mock_session_state.running_workers = {}
        mocker.patch.object(project_detail_modal.st, 'session_state', mock_session_state)
        mock_markdown = mocker.patch.object(project_detail_modal.st, 'markdown')
        mock_modal.is_open.return_value = True

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

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
        assert '内蔵ツール' in detail_text
        assert 'ステータス' in detail_text
        assert '作成日時' in detail_text
        assert '実行日時' in detail_text
        assert '終了日時' in detail_text

    def test_実行中のプロジェクトのステータスが正しく表示される(
        self,
        mocker: MockerFixture,
        mock_modal: Mock,
        sample_project: Project,
    ) -> None:
        """実行中のプロジェクトのステータスが正しく表示されることをテスト。"""
        # Arrange
        mock_session_state = Mock()
        mock_session_state.modal_project = sample_project
        mock_session_state.running_workers = {sample_project.id: 'running'}
        mocker.patch.object(project_detail_modal.st, 'session_state', mock_session_state)
        mock_markdown = mocker.patch.object(project_detail_modal.st, 'markdown')
        mock_modal.is_open.return_value = True

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert 'ステータス**: `Running`' in detail_text

    def test_実行されていないプロジェクトのステータスが正しく表示される(
        self, mocker: MockerFixture, mock_modal: Mock
    ) -> None:
        """実行されていないプロジェクトのステータスが正しく表示されることをテスト。"""
        # Arrange
        mock_session_state = MockSessionState({'running_workers': {}})
        mocker.patch.object(project_detail_modal.st, 'session_state', mock_session_state)
        mock_markdown = mocker.patch.object(project_detail_modal.st, 'markdown')
        mock_modal.is_open.return_value = True

        sample_project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        mock_session_state['modal_project'] = sample_project

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        # プロジェクトのデフォルトステータスは Pending
        assert 'ステータス**:`Pending`' in detail_text.replace(' ', '').replace('\n', '')

    def test_日時がNoneの場合にN_Aが表示される(
        self, mocker: MockerFixture, mock_modal: Mock
    ) -> None:
        """日時がNoneの場合にN/Aが表示されることをテスト。"""
        # Arrange
        mock_session_state = Mock()
        mock_session_state.running_workers = {}
        mocker.patch.object(project_detail_modal.st, 'session_state', mock_session_state)
        mock_markdown = mocker.patch.object(project_detail_modal.st, 'markdown')
        mock_modal.is_open.return_value = True

        sample_project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        sample_project.executed_at = None
        sample_project.finished_at = None

        mock_session_state.modal_project = sample_project

        # Act
        project_detail_modal.render_project_detail_modal(mock_modal)

        # Assert
        detail_call = mock_markdown.call_args_list[1]
        detail_text = detail_call[0][0]
        assert '実行日時**: `N/A`' in detail_text
        assert '終了日時**: `N/A`' in detail_text
