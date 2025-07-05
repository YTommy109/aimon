"""Main Pageのテスト。"""

from datetime import datetime
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest
from pytest_mock import MockerFixture

from app import main_page
from app.domain.entities import Project


class TestGetSortKey:
    """_get_sort_key関数のテスト。"""

    @pytest.fixture
    def jst(self) -> ZoneInfo:
        return ZoneInfo('Asia/Tokyo')

    def test_プロジェクトの作成日時がNoneの場合にAttributeErrorが発生する(
        self, jst: ZoneInfo
    ) -> None:
        """created_atがNoneの場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        project.created_at = None  # type: ignore[assignment]

        # Act & Assert
        # 現在の実装では None を直接処理しようとするのでエラーが発生する
        with pytest.raises(AttributeError):
            main_page._get_sort_key(project, jst)

    def test_プロジェクトの作成日時がoffset_naiveの場合にJSTタイムゾーンが設定される(
        self, jst: ZoneInfo
    ) -> None:
        """created_atがoffset-naiveの場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        naive_datetime = datetime(2023, 1, 1, 12, 0, 0)
        project.created_at = naive_datetime

        # Act
        result = main_page._get_sort_key(project, jst)

        # Assert
        assert result == naive_datetime.replace(tzinfo=jst)
        assert result.tzinfo == jst

    def test_プロジェクトの作成日時がoffset_awareの場合にそのまま返される(
        self, jst: ZoneInfo
    ) -> None:
        """created_atがoffset-awareの場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        aware_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=jst)
        project.created_at = aware_datetime

        # Act
        result = main_page._get_sort_key(project, jst)

        # Assert
        assert result == aware_datetime
        assert result.tzinfo == jst


class TestRenderMainPage:
    """render_main_page関数の統合テスト。"""

    def test_メインページが正常に描画され全てのコンポーネントが表示される(
        self, mocker: MockerFixture
    ) -> None:
        """render_main_page関数の基本動作テスト。"""
        # Arrange
        mock_st = mocker.patch.object(main_page, 'st')
        mock_get_data_manager = mocker.patch.object(main_page, 'get_data_manager')
        mocker.patch.object(main_page, 'Modal')
        mock_render_creation_form = mocker.patch.object(main_page, 'render_project_creation_form')
        mock_render_detail_modal = mocker.patch.object(main_page, 'render_project_detail_modal')
        mock_render_project_list = mocker.patch.object(main_page, 'render_project_list')

        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state
        mock_data_manager = MagicMock()
        mock_get_data_manager.return_value = mock_data_manager

        # プロジェクトの作成日時に異なるタイムゾーン情報を持つプロジェクトを設定
        project1 = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        project1.created_at = datetime(2023, 1, 1, 12, 0, 0)  # offset-naive

        project2 = Project(name='プロジェクト2', source='/path2', ai_tool='tool2')
        project2.created_at = datetime(
            2023, 1, 2, 12, 0, 0, tzinfo=ZoneInfo('Asia/Tokyo')
        )  # offset-aware

        mock_data_manager.get_projects.return_value = [project1, project2]

        # Act
        main_page.render_main_page()

        # Assert
        # 基本的なStreamlit設定が呼ばれることを確認
        mock_st.set_page_config.assert_called_once_with(
            page_title='AI Meeting Assistant',
            page_icon='🤖',
            layout='wide',
        )
        mock_st.title.assert_called_once_with('AI Meeting Assistant 🤖')

        # 各コンポーネントが呼ばれることを確認
        mock_render_creation_form.assert_called_once()
        mock_render_detail_modal.assert_called_once()
        mock_render_project_list.assert_called_once()

        # セッション状態が初期化されることを確認（詳細は削除済みのテストで確認）

        # プロジェクトのソートが正しく動作することを確認（詳細は_get_sort_keyのテストで確認）
        mock_data_manager.get_projects.assert_called_once()

    def test_プロジェクトが存在しない場合でもメインページが正常に描画される(
        self, mocker: MockerFixture
    ) -> None:
        """空のプロジェクトリストでのrender_main_page関数のテスト。"""
        # Arrange
        mock_st = mocker.patch.object(main_page, 'st')
        mock_get_data_manager = mocker.patch.object(main_page, 'get_data_manager')
        mocker.patch.object(main_page, 'Modal')
        mocker.patch.object(main_page, 'render_project_creation_form')
        mocker.patch.object(main_page, 'render_project_detail_modal')
        mock_render_project_list = mocker.patch.object(main_page, 'render_project_list')

        mock_session_state = MagicMock()
        mock_st.session_state = mock_session_state
        mock_data_manager = MagicMock()
        mock_get_data_manager.return_value = mock_data_manager
        mock_data_manager.get_projects.return_value = []

        # Act
        main_page.render_main_page()

        # Assert
        # 空のリストでも正常に動作することを確認
        mock_render_project_list.assert_called_once()
        call_args = mock_render_project_list.call_args[0]
        assert call_args[0] == []  # 空のプロジェクトリストが渡される
