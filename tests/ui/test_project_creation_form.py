"""プロジェクト作成フォームのテストモジュール。"""

from unittest.mock import Mock, patch

import pytest

from app.errors import ResourceNotFoundError
from app.models.ai_tool import AITool
from app.models.project import Project
from app.services.ai_tool_service import AIToolService
from app.services.project_service import ProjectService
from app.ui.project_creation_form import (
    ProjectFormInputs,
    _create_ai_tool_options,
    _create_project_with_validation,
    _display_result_message,
    _format_ai_tool,
    _handle_form_submission,
    _handle_form_submission_logic,
    _handle_project_creation_button,
    _render_form_inputs,
    _validate_ai_tool_exists,
    _validate_project_inputs,
    render_project_creation_form,
)


class TestProjectCreationForm:
    """プロジェクト作成フォームのテストクラス。"""

    @pytest.fixture
    def mock_project_service(self) -> Mock:
        """プロジェクトサービスのモック。"""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def mock_ai_tool_service(self) -> Mock:
        """AIツールサービスのモック。"""
        return Mock(spec=AIToolService)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツール。"""
        return AITool(
            id='test-tool-1',
            name_ja='テストツール1',
            description='テスト用のAIツール',
            endpoint_url='https://api.example.com/test1',
        )

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルプロジェクト。"""
        return Project(
            name='テストプロジェクト',
            source='/test/path',
            ai_tool='test-tool-1',
        )

    def test_AIツールオプションが正しく作成される(self, sample_ai_tool: AITool) -> None:
        """AIツールオプションが正しく作成されることをテスト。"""
        # Arrange
        ai_tools = [sample_ai_tool]

        # Act
        all_options, ai_tool_options = _create_ai_tool_options(ai_tools)

        # Assert
        assert len(all_options) == 2  # ツール + セパレータ
        assert all_options[0] == 'test-tool-1'
        assert all_options[1] == '---'
        assert ai_tool_options['test-tool-1'] == 'テストツール1 (テスト用のAIツール)'

    def test_空のAIツールリストの場合にセパレータが追加されない(self) -> None:
        """空のAIツールリストの場合にセパレータが追加されないことをテスト。"""
        # Arrange
        ai_tools: list[AITool] = []

        # Act
        all_options, ai_tool_options = _create_ai_tool_options(ai_tools)

        # Assert
        assert len(all_options) == 0
        assert len(ai_tool_options) == 0

    def test_AIツールフォーマットが正しく実行される(self, sample_ai_tool: AITool) -> None:
        """AIツールフォーマットが正しく実行されることをテスト。"""
        # Arrange
        ai_tool_options = {'test-tool-1': 'テストツール1'}

        # Act
        result = _format_ai_tool('test-tool-1', ai_tool_options)

        # Assert
        assert result == 'テストツール1'

    def test_有効なプロジェクト入力が検証される(self) -> None:
        """有効なプロジェクト入力が検証されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is True
        assert error_message == ''

    def test_プロジェクト名が空の場合にエラーが返される(self) -> None:
        """プロジェクト名が空の場合にエラーが返されることをテスト。"""
        # Arrange
        project_name = ''
        source_dir = '/test/path'
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名' in error_message

    def test_ソースディレクトリが空の場合にエラーが返される(self) -> None:
        """ソースディレクトリが空の場合にエラーが返されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = ''
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください。' in error_message

    def test_AIツールが選択されていない場合にエラーが返される(self) -> None:
        """AIツールが選択されていない場合にエラーが返されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = None

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'AIツール' in error_message

    def test_AIツールがセパレータの場合にエラーが返される(self) -> None:
        """AIツールがセパレータの場合にエラーが返されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '/test/path'
        selected_ai_tool_id = '---'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'AIツール' in error_message

    def test_存在するAIツールが検証される(
        self, mock_ai_tool_service: Mock, sample_ai_tool: AITool
    ) -> None:
        """存在するAIツールが検証されることをテスト。"""
        # Arrange
        mock_ai_tool_service.get_ai_tool_by_id.return_value = sample_ai_tool

        # Act
        result = _validate_ai_tool_exists('test-tool-1', mock_ai_tool_service)

        # Assert
        assert result is True
        mock_ai_tool_service.get_ai_tool_by_id.assert_called_once_with('test-tool-1')

    def test_存在しないAIツールが検証される(self, mock_ai_tool_service: Mock) -> None:
        """存在しないAIツールが検証されることをテスト。"""
        # Arrange
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = ResourceNotFoundError(
            'AI Tool', 'non-existent-tool'
        )

        # Act
        result = _validate_ai_tool_exists('non-existent-tool', mock_ai_tool_service)

        # Assert
        assert result is False

    def test_プロジェクト作成が成功する(
        self,
        mock_project_service: Mock,
        mock_ai_tool_service: Mock,
        sample_project: Project,
        sample_ai_tool: AITool,
    ) -> None:
        """プロジェクト作成が成功することをテスト。"""
        # Arrange
        mock_ai_tool_service.get_ai_tool_by_id.return_value = sample_ai_tool
        mock_project_service.create_project.return_value = sample_project

        # Act
        success, message = _create_project_with_validation(
            sample_project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is True
        assert 'プロジェクトを作成しました。' in message
        mock_project_service.create_project.assert_called_once()

    def test_存在しないAIツールでプロジェクト作成が失敗する(
        self, mock_project_service: Mock, mock_ai_tool_service: Mock, sample_project: Project
    ) -> None:
        """存在しないAIツールでプロジェクト作成が失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.get_ai_tool_by_id.side_effect = ResourceNotFoundError(
            'AI Tool', 'test-tool-1'
        )

        # Act
        success, message = _create_project_with_validation(
            sample_project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is False
        assert '選択されたAIツールが見つかりません。' in message
        mock_project_service.create_project.assert_not_called()

    def test_プロジェクト作成サービスが失敗する(
        self,
        mock_project_service: Mock,
        mock_ai_tool_service: Mock,
        sample_project: Project,
        sample_ai_tool: AITool,
    ) -> None:
        """プロジェクト作成サービスが失敗することをテスト。"""
        # Arrange
        mock_ai_tool_service.get_ai_tool_by_id.return_value = sample_ai_tool
        mock_project_service.create_project.return_value = None

        # Act
        success, message = _create_project_with_validation(
            sample_project, mock_project_service, mock_ai_tool_service
        )

        # Assert
        assert success is False
        assert '失敗' in message

    @patch('app.ui.project_creation_form.st.success')
    def test_成功メッセージが表示される(self, mock_success: Mock) -> None:
        """成功メッセージが表示されることをテスト。"""
        # Act
        _display_result_message(success=True, message='成功メッセージ')

        # Assert
        mock_success.assert_called_once_with('成功メッセージ')

    @patch('app.ui.project_creation_form.st.warning')
    def test_警告メッセージが表示される(self, mock_warning: Mock) -> None:
        """警告メッセージが表示されることをテスト。"""
        # Act
        _display_result_message(success=False, message='警告メッセージ')

        # Assert
        mock_warning.assert_called_once_with('警告メッセージ')

    @patch('app.ui.project_creation_form.st.warning')
    def test_プロジェクトがNoneの場合に警告が表示される(self, mock_warning: Mock) -> None:
        """プロジェクトがNoneの場合に警告が表示されることをテスト。"""
        # Act
        _handle_project_creation_button(None, Mock(), Mock())

        # Assert
        mock_warning.assert_called_once_with('プロジェクトデータが不正です。')

    @patch('app.ui.project_creation_form._create_project_with_validation')
    @patch('app.ui.project_creation_form._display_result_message')
    def test_プロジェクト作成ボタンが処理される(
        self, mock_display_result: Mock, mock_create_project: Mock, sample_project: Project
    ) -> None:
        """プロジェクト作成ボタンが処理されることをテスト。"""
        # Arrange
        mock_create_project.return_value = (True, '成功メッセージ')
        project_service = Mock()
        ai_tool_service = Mock()

        # Act
        _handle_project_creation_button(sample_project, project_service, ai_tool_service)

        # Assert
        mock_create_project.assert_called_once_with(
            sample_project, project_service, ai_tool_service
        )
        mock_display_result.assert_called_once_with(success=True, message='成功メッセージ')

    @patch('app.ui.project_creation_form.st.warning')
    def test_無効な入力でフォーム送信ロジックが警告を表示する(self, mock_warning: Mock) -> None:
        """無効な入力でフォーム送信ロジックが警告を表示することをテスト。"""
        # Arrange
        inputs = ProjectFormInputs(
            project_name=None, source_dir='/test/path', selected_ai_tool_id='test-tool-1'
        )

        # Act
        _handle_form_submission_logic(inputs, Mock(), Mock())

        # Assert
        mock_warning.assert_called_once()

    @patch('app.ui.project_creation_form._handle_form_submission')
    def test_有効な入力でフォーム送信ロジックが処理される(
        self, mock_handle_submission: Mock
    ) -> None:
        """有効な入力でフォーム送信ロジックが処理されることをテスト。"""
        # Arrange
        inputs = ProjectFormInputs(
            project_name='テストプロジェクト',
            source_dir='/test/path',
            selected_ai_tool_id='test-tool-1',
        )
        project_service = Mock()
        ai_tool_service = Mock()

        # Act
        _handle_form_submission_logic(inputs, project_service, ai_tool_service)

        # Assert
        mock_handle_submission.assert_called_once()
        # Projectオブジェクトが作成されていることを確認
        call_args = mock_handle_submission.call_args[0]
        project = call_args[0]
        assert project.name == 'テストプロジェクト'
        assert project.source == '/test/path'
        assert project.ai_tool == 'test-tool-1'

    @patch('app.ui.project_creation_form.st.sidebar')
    @patch('app.ui.project_creation_form.st.header')
    @patch('app.ui.project_creation_form._render_form_inputs')
    @patch('app.ui.project_creation_form.st.button')
    def test_プロジェクト作成フォームが描画される(
        self, mock_button: Mock, mock_render_inputs: Mock, mock_header: Mock, mock_sidebar: Mock
    ) -> None:
        """プロジェクト作成フォームが描画されることをテスト。"""
        # Arrange
        mock_sidebar.__enter__ = Mock()
        mock_sidebar.__exit__ = Mock()
        mock_render_inputs.return_value = ('テストプロジェクト', '/test/path', 'test-tool-1')
        mock_button.return_value = False

        # Act
        render_project_creation_form(Mock(), Mock())

        # Assert
        mock_header.assert_called_once_with('プロジェクト作成')
        mock_render_inputs.assert_called_once()
        mock_button.assert_called_once_with('プロジェクト作成')

    @patch('app.ui.project_creation_form.st.text_input')
    @patch('app.ui.project_creation_form.st.selectbox')
    def test_フォーム入力フィールドが描画される(
        self, mock_selectbox: Mock, mock_text_input: Mock, mock_ai_tool_service: Mock
    ) -> None:
        """フォーム入力フィールドが描画されることをテスト。"""
        # Arrange
        mock_text_input.side_effect = ['テストプロジェクト', '/test/path']
        mock_selectbox.return_value = 'test-tool-1'
        mock_ai_tool_service.get_all_ai_tools.return_value = []

        # Act
        result = _render_form_inputs(mock_ai_tool_service)

        # Assert
        assert result == ('テストプロジェクト', '/test/path', 'test-tool-1')
        assert mock_text_input.call_count == 2
        mock_selectbox.assert_called_once()

    @patch('app.ui.project_creation_form._handle_project_creation_button')
    def test_フォーム送信が処理される(
        self, mock_handle_button: Mock, sample_project: Project
    ) -> None:
        """フォーム送信が処理されることをテスト。"""
        # Arrange
        project_service = Mock()
        ai_tool_service = Mock()

        # Act
        _handle_form_submission(sample_project, project_service, ai_tool_service)

        # Assert
        mock_handle_button.assert_called_once_with(sample_project, project_service, ai_tool_service)

    def test_空白文字のみのプロジェクト名でエラーが返される(self) -> None:
        """空白文字のみのプロジェクト名でエラーが返されることをテスト。"""
        # Arrange
        project_name = '   '
        source_dir = '/test/path'
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください。' in error_message

    def test_空白文字のみのソースディレクトリでエラーが返される(self) -> None:
        """空白文字のみのソースディレクトリでエラーが返されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = '   '
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください。' in error_message

    def test_Noneのプロジェクト名でエラーが返される(self) -> None:
        """Noneのプロジェクト名でエラーが返されることをテスト。"""
        # Arrange
        project_name = None
        source_dir = '/test/path'
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名' in error_message

    def test_Noneのソースディレクトリでエラーが返される(self) -> None:
        """Noneのソースディレクトリでエラーが返されることをテスト。"""
        # Arrange
        project_name = 'テストプロジェクト'
        source_dir = None
        selected_ai_tool_id = 'test-tool-1'

        # Act
        is_valid, error_message = _validate_project_inputs(
            project_name, source_dir, selected_ai_tool_id
        )

        # Assert
        assert is_valid is False
        assert 'プロジェクト名と対象ディレクトリのパスを入力してください。' in error_message
