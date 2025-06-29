"""プロジェクト作成フォームビューのテスト。"""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.model import AITool, DataManager, Project
from app.view.project_creation_form import render_project_creation_form


class TestRenderProjectCreationForm:
    """render_project_creation_form関数のテストクラス。

    注意: これらのテストはstreamlit関数をモックして実行します。
    """

    @pytest.fixture
    def mock_streamlit(self, mocker: MockerFixture) -> MagicMock:
        """Streamlit関数をモックするフィクスチャ。"""
        mock_st = mocker.patch('app.view.project_creation_form.st')
        mock_st.session_state = {}

        # サイドバーのコンテキストマネージャをモック
        mock_sidebar = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_st.sidebar.__exit__ = MagicMock(return_value=None)

        # 入力フィールドのデフォルト値を設定
        mock_st.text_input.return_value = ''
        mock_st.selectbox.return_value = None
        mock_st.button.return_value = False

        return mock_st

    @pytest.fixture
    def mock_data_manager(self) -> MagicMock:
        """DataManagerのモックを提供するフィクスチャ。"""
        mock_dm = MagicMock(spec=DataManager)

        # サンプルAIツールを設定
        sample_ai_tools = [
            AITool(id='tool1', name_ja='ツール1', description='説明1'),
            AITool(id='tool2', name_ja='ツール2', description='説明2'),
            AITool(id='tool3', name_ja='ツール3', description='説明3'),
        ]
        mock_dm.get_ai_tools.return_value = sample_ai_tools

        return mock_dm

    @pytest.fixture
    def get_data_manager_func(self, mock_data_manager: MagicMock) -> MagicMock:
        """get_data_manager関数のモックを提供するフィクスチャ。"""
        return MagicMock(return_value=mock_data_manager)

    def test_フォームの基本構成が表示される(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """フォームの基本的なUI要素が正しく表示されることをテスト。"""
        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_streamlit.sidebar.__enter__.assert_called_once()
        mock_streamlit.header.assert_called_once_with('プロジェクト作成')

        # 入力フィールドの確認
        text_input_calls = mock_streamlit.text_input.call_args_list
        assert len(text_input_calls) == 2
        assert text_input_calls[0][0][0] == 'プロジェクト名'
        assert text_input_calls[1][0][0] == '対象ディレクトリのパス'

        # セレクトボックスの確認
        mock_streamlit.selectbox.assert_called_once()
        selectbox_args = mock_streamlit.selectbox.call_args
        assert selectbox_args[0][0] == 'AIツールを選択'
        assert 'options' in selectbox_args[1]
        assert 'format_func' in selectbox_args[1]
        assert selectbox_args[1]['index'] is None
        assert selectbox_args[1]['placeholder'] == '選択...'

        # ボタンの確認
        mock_streamlit.button.assert_called_once_with('プロジェクト作成')

    def test_AIツール選択肢が正しく設定される(
        self,
        mock_streamlit: MagicMock,
        mock_data_manager: MagicMock,
        get_data_manager_func: MagicMock,
    ) -> None:
        """AIツールの選択肢が正しく設定されることをテスト。"""
        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_data_manager.get_ai_tools.assert_called_once()

        # セレクトボックスの options を確認
        selectbox_call = mock_streamlit.selectbox.call_args
        options = selectbox_call[1]['options']
        expected_options = ['tool1', 'tool2', 'tool3']
        assert options == expected_options

        # format_func をテスト
        format_func = selectbox_call[1]['format_func']
        assert format_func('tool1') == 'ツール1 (説明1)'
        assert format_func('tool2') == 'ツール2 (説明2)'
        assert format_func('unknown') == '不明なツール'

    def test_対象ディレクトリパスの前後空白が除去される(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """対象ディレクトリのパスの前後空白が除去されることをテスト。"""
        # Arrange
        mock_streamlit.text_input.side_effect = ['Test Project', '  /path/with/spaces  ']
        mock_streamlit.selectbox.return_value = 'tool1'
        mock_streamlit.button.return_value = True

        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')
        mock_project = Project(name='Test Project', source='/path/with/spaces', ai_tool='tool1')
        mock_handle.return_value = (mock_project, 'プロジェクトを作成しました。')

        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_handle.assert_called_once()
        args = mock_handle.call_args[0]
        assert args[1] == '/path/with/spaces'  # 前後の空白が除去されている

    def test_プロジェクト作成ボタンクリック_成功ケース(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mock_data_manager: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト作成ボタンのクリック時、成功ケースをテスト。"""
        # Arrange
        mock_streamlit.text_input.side_effect = ['Test Project', '/test/path']
        mock_streamlit.selectbox.return_value = 'tool1'
        mock_streamlit.button.return_value = True

        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')
        mock_project = Project(name='Test Project', source='/test/path', ai_tool='tool1')
        mock_handle.return_value = (mock_project, 'プロジェクト「Test Project」を作成しました。')

        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_handle.assert_called_once_with(
            'Test Project', '/test/path', 'tool1', mock_data_manager
        )
        mock_streamlit.success.assert_called_once_with(
            'プロジェクト「Test Project」を作成しました。'
        )
        mock_streamlit.warning.assert_not_called()

    def test_プロジェクト作成ボタンクリック_失敗ケース(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mock_data_manager: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト作成ボタンのクリック時、失敗ケースをテスト。"""
        # Arrange
        mock_streamlit.text_input.side_effect = ['Test Project', '/test/path']
        mock_streamlit.selectbox.return_value = 'tool1'
        mock_streamlit.button.return_value = True

        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')
        mock_handle.return_value = (None, 'プロジェクトの作成に失敗しました: エラーが発生しました')

        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_handle.assert_called_once_with(
            'Test Project', '/test/path', 'tool1', mock_data_manager
        )
        mock_streamlit.warning.assert_called_once_with(
            'プロジェクトの作成に失敗しました: エラーが発生しました'
        )
        mock_streamlit.success.assert_not_called()

    def test_AIツール未選択時にワーニングメッセージが表示される(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """AIツールが未選択の場合にワーニングメッセージが表示されることをテスト。"""
        # Arrange
        mock_streamlit.text_input.side_effect = ['Test Project', '/test/path']
        mock_streamlit.selectbox.return_value = None  # 未選択
        mock_streamlit.button.return_value = True

        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')

        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_streamlit.warning.assert_called_once_with('AIツールを選択してください。')
        mock_handle.assert_not_called()
        mock_streamlit.success.assert_not_called()

    def test_ボタンがクリックされていない場合は何も実行されない(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト作成ボタンがクリックされていない場合は何も実行されないことをテスト。"""
        # Arrange
        mock_streamlit.text_input.side_effect = ['Test Project', '/test/path']
        mock_streamlit.selectbox.return_value = 'tool1'
        mock_streamlit.button.return_value = False  # ボタンがクリックされていない

        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')

        # Act
        render_project_creation_form(get_data_manager_func)

        # Assert
        mock_handle.assert_not_called()
        mock_streamlit.success.assert_not_called()
        mock_streamlit.warning.assert_not_called()

    def test_空のAIツールリストでもエラーにならない(
        self,
        mock_streamlit: MagicMock,
        mock_data_manager: MagicMock,
        get_data_manager_func: MagicMock,
    ) -> None:
        """AIツールリストが空でもエラーにならないことをテスト。"""
        # Arrange
        mock_data_manager.get_ai_tools.return_value = []  # 空のリスト

        # Act & Assert (例外が発生しないことを確認)
        render_project_creation_form(get_data_manager_func)

        # セレクトボックスのオプションが空リストになっていることを確認
        selectbox_call = mock_streamlit.selectbox.call_args
        options = selectbox_call[1]['options']
        assert options == []

    def test_複数のプロジェクト作成が連続して行える(
        self,
        mock_streamlit: MagicMock,
        get_data_manager_func: MagicMock,
        mock_data_manager: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """複数のプロジェクト作成が連続して行えることをテスト。"""
        # Arrange
        mock_handle = mocker.patch('app.view.project_creation_form.handle_project_creation')

        # 1回目の呼び出し
        mock_streamlit.text_input.side_effect = ['Project 1', '/path1']
        mock_streamlit.selectbox.return_value = 'tool1'
        mock_streamlit.button.return_value = True

        mock_project1 = Project(name='Project 1', source='/path1', ai_tool='tool1')
        mock_handle.return_value = (mock_project1, 'プロジェクト「Project 1」を作成しました。')

        # Act - 1回目
        render_project_creation_form(get_data_manager_func)

        # Assert - 1回目
        assert mock_handle.call_count == 1
        mock_streamlit.success.assert_called_with('プロジェクト「Project 1」を作成しました。')

        # Arrange - 2回目の呼び出し
        mock_streamlit.text_input.side_effect = ['Project 2', '/path2']
        mock_streamlit.selectbox.return_value = 'tool2'
        mock_streamlit.button.return_value = True

        mock_project2 = Project(name='Project 2', source='/path2', ai_tool='tool2')
        mock_handle.return_value = (mock_project2, 'プロジェクト「Project 2」を作成しました。')

        # Act - 2回目
        render_project_creation_form(get_data_manager_func)

        # Assert - 2回目
        assert mock_handle.call_count == 2

        # 各呼び出しの引数を確認
        call_args_list = mock_handle.call_args_list
        first_call_args = call_args_list[0][0]
        second_call_args = call_args_list[1][0]

        assert first_call_args == ('Project 1', '/path1', 'tool1', mock_data_manager)
        assert second_call_args == ('Project 2', '/path2', 'tool2', mock_data_manager)
