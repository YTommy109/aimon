"""プロジェクト一覧ビューのテスト。"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.model import Project
from app.view.project_list import _get_status_icon


class TestGetStatusIcon:
    """_get_status_icon関数のテストクラス。"""

    def test_実行中の場合は走るアイコンを返す(self) -> None:
        # Arrange
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        is_running = True

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '🏃'

    def test_処理中ステータスの場合は砂時計アイコンを返す(self) -> None:
        # Arrange
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        project.start_processing()  # executed_atを設定してPROCESSING状態にする
        is_running = False

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '⏳'

    def test_完了ステータスの場合はチェックマークアイコンを返す(self) -> None:
        # Arrange
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        project.start_processing()  # executed_atを設定
        project.complete({'success': True})  # 完了状態にする
        is_running = False

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '✅'

    def test_失敗ステータスの場合はバツアイコンを返す(self) -> None:
        # Arrange
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        project.start_processing()  # executed_atを設定
        project.fail({'error': 'Test error'})  # 失敗状態にする
        is_running = False

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '❌'

    def test_その他のステータスの場合は吹き出しアイコンを返す(self) -> None:
        # Arrange
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        # デフォルトはPENDING状態
        is_running = False

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '💬'

    def test_実行中フラグが優先される(self) -> None:
        # Arrange: 完了ステータスだが実行中フラグがTrue
        project = Project(
            name='Test Project',
            source='/test/path',
            ai_tool='test_tool',
        )
        project.start_processing()  # executed_atを設定
        project.complete({'success': True})  # 完了状態にする
        is_running = True

        # Act
        result = _get_status_icon(project, is_running)

        # Assert
        assert result == '🏃'  # 実行中フラグが優先される


class TestRenderProjectListIntegration:
    """render_project_list関数の統合テストクラス。

    注意: これらのテストはstreamlit関数をモックして実行します。
    """

    @pytest.fixture
    def mock_streamlit(self, mocker: MockerFixture) -> tuple[MagicMock, list[MagicMock]]:
        """Streamlit関数をモックするフィクスチャ。"""
        mock_st = mocker.patch('app.view.project_list.st')
        mock_st.session_state.running_workers = {}
        mock_st.session_state.modal_project = None

        # columnsメソッドのモック
        mock_columns = [MagicMock() for _ in range(6)]
        mock_st.columns.return_value = mock_columns

        return mock_st, mock_columns

    @pytest.fixture
    def sample_projects(self) -> list[Project]:
        """テスト用のサンプルプロジェクトリスト。"""
        project1 = Project(
            name='プロジェクト1',
            source='/test/path1',
            ai_tool='tool1',
        )
        project1.created_at = datetime(2023, 1, 1, 10, 0, 0)

        project2 = Project(
            name='プロジェクト2',
            source='/test/path2',
            ai_tool='tool2',
        )
        project2.created_at = datetime(2023, 1, 2, 11, 0, 0)
        project2.executed_at = datetime(2023, 1, 2, 12, 0, 0)

        return [project1, project2]

    def test_プロジェクトが空の場合にメッセージを表示(
        self, mock_streamlit: tuple[MagicMock, list[MagicMock]], mocker: MockerFixture
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, _ = mock_streamlit
        projects: list[Project] = []
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # Act
        render_project_list(projects, mock_modal, mock_data_manager)

        # Assert
        mock_st.header.assert_called_once_with('プロジェクト一覧')
        mock_st.info.assert_called_once_with('まだプロジェクトがありません。')

    def test_プロジェクトがある場合にヘッダーとデータを表示(
        self,
        mock_streamlit: tuple[MagicMock, list[MagicMock]],
        sample_projects: list[Project],
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, mock_columns = mock_streamlit
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # ボタンのモックを設定
        for col in mock_columns:
            col.button.return_value = False

        # Act
        render_project_list(sample_projects, mock_modal, mock_data_manager)

        # Assert
        mock_st.header.assert_called_once_with('プロジェクト一覧')
        mock_st.divider.assert_called_once()

        # ヘッダーの確認
        header_calls = mock_st.columns.call_args_list[0][0][0]
        assert header_calls == (1, 4, 2, 2, 1)

        # プロジェクト行の確認
        assert mock_st.columns.call_count >= 2  # ヘッダー + プロジェクト行数

    def test_詳細ボタンクリック時にモーダルが開く(
        self,
        mock_streamlit: tuple[MagicMock, list[MagicMock]],
        sample_projects: list[Project],
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, mock_columns = mock_streamlit
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # プロジェクト行用のモックカラムを追加設定
        project_columns = [MagicMock() for _ in range(6)]  # プロジェクト行は6列
        mock_st.columns.side_effect = [
            mock_columns,
            project_columns,
            project_columns,
        ]  # ヘッダー + 各プロジェクト行

        # 最初のプロジェクトの詳細ボタンがクリックされたことをシミュレート
        project_columns[4].button.return_value = True  # 詳細ボタン
        project_columns[5].button.return_value = False  # 実行ボタン

        # Act
        render_project_list(sample_projects, mock_modal, mock_data_manager)

        # Assert
        # モーダルは各プロジェクトごとに呼ばれる可能性があるので、呼ばれたことを確認
        assert mock_modal.open.called
        # 何らかのプロジェクトがセットされていることを確認
        assert mock_st.session_state.modal_project in sample_projects

    def test_実行ボタンクリック時にハンドラーが呼ばれる(
        self,
        mock_streamlit: tuple[MagicMock, list[MagicMock]],
        sample_projects: list[Project],
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, mock_columns = mock_streamlit
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # handle_project_executionのモック
        mock_handler = mocker.patch('app.view.project_list.handle_project_execution')
        mock_handler.return_value = (MagicMock(), 'プロジェクトを実行しました')

        # プロジェクト行用のモックカラムを追加設定
        project_columns = [MagicMock() for _ in range(6)]  # プロジェクト行は6列
        mock_st.columns.side_effect = [
            mock_columns,
            project_columns,
            project_columns,
        ]  # ヘッダー + 各プロジェクト行

        # 実行ボタンがクリックされたことをシミュレート（未実行のプロジェクトのみ）
        project_columns[4].button.return_value = False  # 詳細ボタン
        project_columns[5].button.return_value = True  # 実行ボタン

        # Act
        render_project_list(sample_projects, mock_modal, mock_data_manager)

        # Assert
        mock_handler.assert_called_once()
        mock_st.info.assert_called_once_with('プロジェクトを実行しました')
        mock_st.rerun.assert_called_once()

    def test_実行済みプロジェクトには実行ボタンが表示されない(
        self,
        mock_streamlit: tuple[MagicMock, list[MagicMock]],
        sample_projects: list[Project],
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, mock_columns = mock_streamlit
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # すべてのプロジェクトを実行済みにする
        for project in sample_projects:
            project.executed_at = datetime.now()

        # Act
        render_project_list(sample_projects, mock_modal, mock_data_manager)

        # Assert
        # 実行ボタンが呼ばれていないことを確認
        for col in mock_columns:
            button_calls = [call for call in col.button.call_args_list if '実行' in str(call)]
            assert len(button_calls) == 0

    def test_ステータスアイコンが正しく表示される(
        self, mock_streamlit: tuple[MagicMock, list[MagicMock]], mocker: MockerFixture
    ) -> None:
        # Arrange
        from app.view.project_list import render_project_list

        mock_st, mock_columns = mock_streamlit
        mock_modal = MagicMock()
        mock_data_manager = MagicMock()

        # 異なるステータスのプロジェクトを作成
        completed_project = Project(
            name='完了プロジェクト',
            source='/test/path',
            ai_tool='tool1',
        )
        completed_project.start_processing()
        completed_project.complete({'success': True})

        failed_project = Project(
            name='失敗プロジェクト',
            source='/test/path',
            ai_tool='tool2',
        )
        failed_project.start_processing()
        failed_project.fail({'error': 'Test error'})

        projects = [completed_project, failed_project]

        # Act
        render_project_list(projects, mock_modal, mock_data_manager)

        # Assert
        # writeメソッドの呼び出しを確認
        write_calls = []
        for col in mock_columns:
            write_calls.extend([call[0][0] for call in col.write.call_args_list])

        # ステータスアイコンが含まれていることを確認
        status_texts = [call for call in write_calls if '✅' in call or '❌' in call]
        assert len(status_texts) >= 2  # 2つのプロジェクトのステータスアイコン
