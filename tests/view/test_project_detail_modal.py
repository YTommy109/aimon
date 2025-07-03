"""プロジェクト詳細モーダルビューのテスト。"""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from app.model import Project
from app.view import project_detail_modal as pdm


class TestRenderProjectDetailModal:
    """render_project_detail_modal関数のテストクラス。

    注意: これらのテストはstreamlit関数をモックして実行します。
    """

    @pytest.fixture
    def mock_streamlit(self, mocker: MockerFixture) -> MagicMock:
        """Streamlit関数をモックするフィクスチャ。"""
        mock_st = mocker.patch.object(pdm, 'st')
        mock_st.session_state.running_workers = {}
        mock_st.session_state.modal_project = None
        return mock_st

    @pytest.fixture
    def mock_modal(self) -> MagicMock:
        """Modalオブジェクトのモックを提供するフィクスチャ。"""
        mock_modal = MagicMock()
        mock_modal.is_open.return_value = False

        # コンテキストマネージャーとしての動作をモック
        mock_container = MagicMock()
        mock_modal.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_modal.container.return_value.__exit__ = MagicMock(return_value=None)

        return mock_modal

    @pytest.fixture
    def sample_project(self) -> Project:
        """テスト用のサンプルプロジェクト。"""
        project = Project(
            id=uuid4(),
            name='テストプロジェクト',
            source='/test/source/path',
            ai_tool='test_ai_tool',
        )
        project.created_at = datetime(2023, 1, 1, 10, 0, 0)
        return project

    def test_モーダルが閉じている場合は何も表示されない(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """モーダルが閉じている場合は何も表示されないことをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = False

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_not_called()
        mock_streamlit.markdown.assert_not_called()

    def test_モーダルが開いているがプロジェクトがNoneの場合は何も表示されない(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """モーダルが開いているがプロジェクトがNoneの場合は何も表示されないことをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = None

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_called_once()
        mock_streamlit.markdown.assert_not_called()

    def test_基本的なプロジェクト情報が表示される(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """基本的なプロジェクト情報が正しく表示されることをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        mock_modal.is_open.assert_called_once()
        mock_modal.container.assert_called_once()

        # markdown呼び出しを確認
        markdown_calls = mock_streamlit.markdown.call_args_list
        assert len(markdown_calls) == 2

        # タイトルの確認
        title_call = markdown_calls[0][0][0]
        assert 'テストプロジェクト' in title_call
        assert '###' in title_call

        # 詳細情報の確認
        detail_call = markdown_calls[1][0][0]
        assert str(sample_project.id) in detail_call
        assert '/test/source/path' in detail_call
        assert 'test_ai_tool' in detail_call
        assert 'Pending' in detail_call  # デフォルトのステータス
        assert '2023/01/01' in detail_call or '2023-01-01' in detail_call

    def test_実行中プロジェクトのステータス表示(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """実行中プロジェクトのステータスが正しく表示されることをテスト。"""
        # Arrange
        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        mock_streamlit.session_state.running_workers = {sample_project.id: MagicMock()}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        assert 'Running' in detail_call

    def test_処理中ステータスのプロジェクト表示(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """処理中ステータスのプロジェクトが正しく表示されることをテスト。"""
        # Arrange
        sample_project.start_processing()
        sample_project.executed_at = datetime(2023, 1, 1, 11, 0, 0)

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        assert 'Processing' in detail_call
        assert '2023/01/01' in detail_call or '2023-01-01' in detail_call  # 実行日時が表示される

    def test_完了ステータスのプロジェクト表示(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """完了ステータスのプロジェクトが正しく表示されることをテスト。"""
        # Arrange
        sample_project.start_processing()
        sample_project.executed_at = datetime(2023, 1, 1, 11, 0, 0)
        sample_project.complete({'result': 'success'})
        sample_project.finished_at = datetime(2023, 1, 1, 12, 0, 0)

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        assert 'Completed' in detail_call
        # 実行日時と終了日時が表示される
        assert '2023/01/01' in detail_call or '2023-01-01' in detail_call

    def test_失敗ステータスのプロジェクト表示(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """失敗ステータスのプロジェクトが正しく表示されることをテスト。"""
        # Arrange
        sample_project.start_processing()
        sample_project.executed_at = datetime(2023, 1, 1, 11, 0, 0)
        sample_project.fail({'error': 'Something went wrong'})
        sample_project.finished_at = datetime(2023, 1, 1, 12, 0, 0)

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        assert 'Failed' in detail_call

    def test_日時がNoneの場合はNA表示(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """日時がNoneの場合はN/Aが表示されることをテスト。"""
        # Arrange
        project = Project(
            name='No Dates Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        # setattr を使って一時的にNoneを設定してmypyの警告を回避
        project.created_at = None  # type: ignore[assignment]
        project.executed_at = None
        project.finished_at = None

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        # N/Aが3回表示される（作成日時、実行日時、終了日時）
        assert detail_call.count('N/A') == 3

    def test_実行中フラグが優先される(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
        sample_project: Project,
    ) -> None:
        """実行中フラグがプロジェクトのステータスより優先されることをテスト。"""
        # Arrange
        sample_project.start_processing()
        sample_project.complete({'result': 'success'})  # 完了状態にする

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = sample_project
        # 実行中ワーカーにプロジェクトIDを追加
        mock_streamlit.session_state.running_workers = {sample_project.id: MagicMock()}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        detail_call = markdown_calls[1][0][0]
        # 完了状態だが実行中フラグが優先されて'Running'が表示される
        assert 'Running' in detail_call
        assert 'Completed' not in detail_call

    def test_複数のプロジェクトが連続表示される(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """複数のプロジェクトが連続して表示されることをテスト。"""
        # Arrange
        project1 = Project(
            name='プロジェクト1',
            source='/path1',
            ai_tool='tool1',
        )
        project2 = Project(
            name='プロジェクト2',
            source='/path2',
            ai_tool='tool2',
        )

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.running_workers = {}

        # 1回目: プロジェクト1
        mock_streamlit.session_state.modal_project = project1
        pdm.render_project_detail_modal(mock_modal)

        # 1回目の確認
        markdown_calls = mock_streamlit.markdown.call_args_list
        assert len(markdown_calls) == 2
        title_call = markdown_calls[0][0][0]
        assert 'プロジェクト1' in title_call

        # 2回目: プロジェクト2
        mock_streamlit.markdown.reset_mock()  # モックをリセット
        mock_streamlit.session_state.modal_project = project2
        pdm.render_project_detail_modal(mock_modal)

        # 2回目の確認
        markdown_calls = mock_streamlit.markdown.call_args_list
        assert len(markdown_calls) == 2
        title_call = markdown_calls[0][0][0]
        assert 'プロジェクト2' in title_call

    def test_長いプロジェクト名とパスが表示される(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """長いプロジェクト名とパスが正しく表示されることをテスト。"""
        # Arrange
        long_name = 'とても長いプロジェクト名' * 10
        long_path = '/very/long/path/to/project/directory/with/many/subdirectories'

        project = Project(
            name=long_name,
            source=long_path,
            ai_tool='test_tool',
        )

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = project
        mock_streamlit.session_state.running_workers = {}

        # Act
        pdm.render_project_detail_modal(mock_modal)

        # Assert
        markdown_calls = mock_streamlit.markdown.call_args_list
        title_call = markdown_calls[0][0][0]
        detail_call = markdown_calls[1][0][0]

        assert long_name in title_call
        assert long_path in detail_call

    def test_特殊文字を含むプロジェクト情報が表示される(
        self,
        mock_streamlit: MagicMock,
        mock_modal: MagicMock,
    ) -> None:
        """特殊文字を含むプロジェクト情報が正しく表示されることをテスト。"""
        # Arrange
        project = Project(
            name='プロジェクト<>&"\'',
            source='/path/with spaces/and-dashes_and.dots',
            ai_tool='ai-tool_v2.0',
        )

        mock_modal.is_open.return_value = True
        mock_streamlit.session_state.modal_project = project
        mock_streamlit.session_state.running_workers = {}

        # Act & Assert (例外が発生しないことを確認)
        pdm.render_project_detail_modal(mock_modal)

        # 特殊文字が含まれていても正常に表示される
        markdown_calls = mock_streamlit.markdown.call_args_list
        assert len(markdown_calls) == 2
