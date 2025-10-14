"""RAGチャットページのテスト。"""

from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from pytest_mock import MockerFixture

from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.project_service import ProjectService
from app.types import ProjectID, ToolType
from app.ui.rag_chat_page import RAGChatPage


class TestRAGChatPage:
    """RAGチャットページのテストクラス。"""

    def test_初期化が正しく行われる(self, mocker: MockerFixture) -> None:
        """RAGチャットページが正しく初期化されることをテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')
        mock_session_state = mocker.MagicMock()
        mock_st.session_state = mock_session_state
        # セッション状態のキーが存在しない場合のモック
        mock_session_state.__contains__ = mocker.MagicMock(return_value=False)

        # Act
        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Assert
        assert page.project_service == mock_project_service
        assert page.project_repo == mock_project_repo
        # セッション状態の初期化が呼び出されることを確認
        assert mock_session_state.__contains__.call_count >= 3

    def test_プロジェクト選択でIDが表示されない(self, mocker: MockerFixture) -> None:
        """プロジェクト選択時にIDが表示されないことをテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')

        # テスト用プロジェクトを作成
        project1 = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト1',
            source='/test/source1',
            tool=ToolType.OVERVIEW,
        )
        project2 = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト2',
            source='/test/source2',
            tool=ToolType.REVIEW,
        )
        projects = [project1, project2]

        mock_project_repo.find_all.return_value = projects
        mock_st.selectbox.return_value = 'テストプロジェクト1'

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        result = page._select_project_from_list(projects)

        # Assert
        assert result == project1
        # selectboxに渡される選択肢にIDが含まれていないことを確認
        call_args = mock_st.selectbox.call_args
        project_names = call_args[0][1]  # 2番目の引数が選択肢のリスト
        assert 'テストプロジェクト1' in project_names
        assert 'テストプロジェクト2' in project_names
        # IDが含まれていないことを確認（プロジェクト名のみが表示される）
        for name in project_names:
            assert name in ['テストプロジェクト1', 'テストプロジェクト2']

    def test_インデックス再構築が正常に実行される(self, mocker: MockerFixture) -> None:
        """インデックス再構築が正常に実行されることをテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')

        project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        updated_project = Project(
            id=project.id, name='テストプロジェクト', source='/test/source', tool=ToolType.OVERVIEW
        )

        mock_project_service.rebuild_project_indexes.return_value = (
            updated_project,
            'インデックスの再構築が完了しました',
        )

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        page._rebuild_indexes(project)

        # Assert
        mock_project_service.rebuild_project_indexes.assert_called_once_with(project.id)
        mock_st.success.assert_called_once_with('インデックスの再構築が完了しました')
        mock_st.rerun.assert_called_once()

    def test_インデックス再構築でエラーが発生した場合(self, mocker: MockerFixture) -> None:
        """インデックス再構築でエラーが発生した場合の処理をテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')

        project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service.rebuild_project_indexes.return_value = (None, 'エラーメッセージ')

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        page._rebuild_indexes(project)

        # Assert
        mock_project_service.rebuild_project_indexes.assert_called_once_with(project.id)
        mock_st.error.assert_called_once_with('エラーメッセージ')
        mock_st.rerun.assert_not_called()

    def test_インデックス再構築で例外が発生した場合(self, mocker: MockerFixture) -> None:
        """インデックス再構築で例外が発生した場合の処理をテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')
        mock_logger = mocker.patch('app.ui.rag_chat_page.logger')

        project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_project_service.rebuild_project_indexes.side_effect = Exception('テスト例外')

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        page._rebuild_indexes(project)

        # Assert
        mock_project_service.rebuild_project_indexes.assert_called_once_with(project.id)
        mock_logger.error.assert_called_once()
        mock_st.error.assert_called_once()
        mock_st.rerun.assert_not_called()

    def test_インデックス状態表示が正しく行われる(self, mocker: MockerFixture) -> None:
        """インデックス状態表示が正しく行われることをテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')

        # Streamlitのcolumnsメソッドをモック
        mock_col1 = mocker.MagicMock()
        mock_col2 = mocker.MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # ボタンが押されていない場合のモック
        mock_st.button.return_value = False

        # セッション状態をモック
        mock_session_state = mocker.MagicMock()
        mock_st.session_state = mock_session_state

        # project_serviceのrebuild_project_indexesをモック
        mock_project_service.rebuild_project_indexes.return_value = (None, 'テストメッセージ')

        project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )
        project.index_finished_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo'))

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        page._render_index_status(project)

        # Assert
        mock_st.columns.assert_called_once_with([3, 1])
        mock_st.button.assert_called_once_with('インデックス再構築', key='rebuild_indexes')

    def test_インデックス未作成状態の表示(self, mocker: MockerFixture) -> None:
        """インデックス未作成状態が正しく表示されることをテストする。"""
        # Arrange
        mock_project_service = mocker.MagicMock(spec=ProjectService)
        mock_project_repo = mocker.MagicMock(spec=JsonProjectRepository)
        mock_st = mocker.patch('app.ui.rag_chat_page.st')

        # Streamlitのcolumnsメソッドをモック
        mock_col1 = mocker.MagicMock()
        mock_col2 = mocker.MagicMock()
        mock_st.columns.return_value = [mock_col1, mock_col2]

        # ボタンが押されていない場合のモック
        mock_st.button.return_value = False

        # セッション状態をモック
        mock_session_state = mocker.MagicMock()
        mock_st.session_state = mock_session_state

        # project_serviceのrebuild_project_indexesをモック
        mock_project_service.rebuild_project_indexes.return_value = (None, 'テストメッセージ')

        project = Project(
            id=ProjectID(uuid4()),
            name='テストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )
        # index_finished_atはNoneのまま

        page = RAGChatPage(mock_project_service, mock_project_repo)

        # Act
        page._render_index_status(project)

        # Assert
        mock_st.columns.assert_called_once_with([3, 1])
        mock_st.button.assert_called_once_with('インデックス再構築', key='rebuild_indexes')
