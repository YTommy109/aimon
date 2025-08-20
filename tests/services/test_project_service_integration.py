"""ProjectServiceとLLMClientの統合テスト。"""

from unittest.mock import Mock, patch
from uuid import uuid4

from app.errors import ResourceNotFoundError
from app.models import ProjectID, ToolType
from app.models.project import Project
from app.services.project_service import ProjectService


class TestProjectServiceLLMIntegration:
    """ProjectServiceとLLMClientの統合テスト。"""

    def test_overview_tool_execution_workflow(self, mocker: Mock) -> None:
        """OVERVIEWツールの実行ワークフローをテストする。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        project = Project(
            name='OVERVIEWテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path と open をモック
        mock_path_class = mocker.patch('app.services.project_service.Path')
        mock_source_path = Mock()
        mock_output_path = Mock()
        mock_parent = Mock()

        # Path(project.source) を返すモック
        mock_path_class.return_value = mock_source_path
        # Path(project.source) / output_filename を返すモック
        mock_source_path.__truediv__ = Mock(return_value=mock_output_path)
        mock_output_path.parent = mock_parent

        # ディレクトリスキャンのモック
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True
        mock_source_path.rglob.return_value = []  # 空のファイルリストを返す

        mock_open = mocker.patch('builtins.open', mocker.mock_open())

        # LLMClientのモック
        with patch('app.services.project_service.LLMClient') as mock_llm_client_class:
            mock_llm_client = Mock()
            mock_llm_client_class.return_value = mock_llm_client

            # 非同期メソッドのモック
            async def mock_generate_text(prompt: str, model: str) -> str:
                return 'OpenAI default-model response: テスト応答'

            mock_llm_client.generate_text = mock_generate_text

            # Act
            result_project, message = project_service.execute_project(project.id)

            # Assert
            assert result_project is not None
            assert message == 'プロジェクトの実行が完了しました'

            # overview.txt が作成されることを確認
            mock_path_class.assert_called_with('/test/source')
            mock_source_path.__truediv__.assert_called_once_with('overview.txt')
            mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # ファイル内容の確認
            mock_open.assert_called_once_with(mock_output_path, 'w', encoding='utf-8')
            handle = mock_open.return_value.__enter__.return_value

            # 実際の出力内容を確認
            actual_call_args = handle.write.call_args[0][0]
            assert '# OVERVIEW result' in actual_call_args
            assert 'OpenAI default-model response:' in actual_call_args
            # LLMの応答内容を確認（プロンプト内容ではなく）
            assert 'テスト応答' in actual_call_args

    def test_review_tool_execution_workflow(self, mocker: Mock) -> None:
        """REVIEWツールの実行ワークフローをテストする。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        project = Project(
            name='REVIEWテストプロジェクト',
            source='/test/source',
            tool=ToolType.REVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path と open をモック
        mock_path_class = mocker.patch('app.services.project_service.Path')
        mock_source_path = Mock()
        mock_output_path = Mock()
        mock_parent = Mock()

        # Path(project.source) を返すモック
        mock_path_class.return_value = mock_source_path
        # Path(project.source) / output_filename を返すモック
        mock_source_path.__truediv__ = Mock(return_value=mock_output_path)
        mock_output_path.parent = mock_parent

        # ディレクトリスキャンのモック
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True

        # Pythonファイルのモック
        mock_python_file = Mock()
        mock_python_file.suffix = '.py'
        mock_python_file.relative_to.return_value = 'test.py'
        mock_source_path.rglob.return_value = [mock_python_file]

        # ファイル読み込みのモック
        mocker.patch('builtins.open', mocker.mock_open(read_data='def test_function():\n    pass'))

        # LLMClientのモック
        with patch('app.services.project_service.LLMClient') as mock_llm_client_class:
            mock_llm_client = Mock()
            mock_llm_client_class.return_value = mock_llm_client

            # 非同期メソッドのモック
            async def mock_generate_text(prompt: str, model: str) -> str:
                return 'Gemini default-model response: レビュー結果'

            mock_llm_client.generate_text = mock_generate_text

            # Act
            result_project, message = project_service.execute_project(project.id)

            # Assert
            assert result_project is not None
            assert message == 'プロジェクトの実行が完了しました'

            # review.txt が作成されることを確認
            mock_path_class.assert_called_with('/test/source')
            mock_source_path.__truediv__.assert_any_call('review.txt')
            mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_llm_provider_environment_variable(self, mocker: Mock) -> None:
        """環境変数によるLLMプロバイダの切り替えをテストする。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        project = Project(
            name='プロバイダテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path と open をモック
        mock_path_class = mocker.patch('app.services.project_service.Path')
        mock_source_path = Mock()
        mock_output_path = Mock()
        mock_parent = Mock()

        mock_path_class.return_value = mock_source_path
        mock_source_path.__truediv__ = Mock(return_value=mock_output_path)
        mock_output_path.parent = mock_parent
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True
        mock_source_path.rglob.return_value = []

        mocker.patch('builtins.open', mocker.mock_open())

        # 環境変数のモック
        with (
            patch.dict('os.environ', {'LLM_PROVIDER': 'gemini'}),
            patch('app.services.project_service.LLMClient') as mock_llm_client_class,
        ):
            mock_llm_client = Mock()
            mock_llm_client_class.return_value = mock_llm_client

            # 非同期メソッドのモック
            async def mock_generate_text(prompt: str, model: str) -> str:
                return 'Gemini default-model response: 環境変数テスト'

            mock_llm_client.generate_text = mock_generate_text

            # Act
            result_project, message = project_service.execute_project(project.id)

            # Assert
            assert result_project is not None
            assert message == 'プロジェクトの実行が完了しました'

            # LLMClientが正しいプロバイダで初期化されたことを確認
            mock_llm_client_class.assert_called_with('gemini')

    def test_error_handling_integration(self, mocker: Mock) -> None:
        """エラーハンドリングの統合テスト。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        project = Project(
            name='エラーテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path と open をモック
        mock_path_class = mocker.patch('app.services.project_service.Path')
        mock_source_path = Mock()
        mock_output_path = Mock()
        mock_parent = Mock()

        mock_path_class.return_value = mock_source_path
        mock_source_path.__truediv__ = Mock(return_value=mock_output_path)
        mock_output_path.parent = mock_parent
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True
        mock_source_path.rglob.return_value = []

        mocker.patch('builtins.open', mocker.mock_open())

        # LLMClientでエラーが発生する場合のモック
        with patch('app.services.project_service.LLMClient') as mock_llm_client_class:
            mock_llm_client = Mock()
            mock_llm_client_class.return_value = mock_llm_client

            # エラーを発生させる
            async def mock_generate_text(prompt: str, model: str) -> None:
                raise RuntimeError('LLM API エラー')

            mock_llm_client.generate_text = mock_generate_text

            # Act & Assert
            result_project, message = project_service.execute_project(project.id)

            # プロジェクトが失敗状態になったことを確認
            assert result_project is None
            assert 'LLM呼び出しエラー' in message

            # プロジェクトの状態も確認
            assert project.status == 'Failed'
            assert project.result is not None
            assert 'error' in project.result
            assert 'LLM API エラー' in project.result['error']

    def test_file_reading_error_integration(self, mocker: Mock) -> None:
        """ファイル読み込みエラーの統合テスト。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        project = Project(
            name='ファイル読み込みエラーテスト',
            source='/test/source',
            tool=ToolType.REVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path と open をモック
        mock_path_class = mocker.patch('app.services.project_service.Path')
        mock_source_path = Mock()
        mock_output_path = Mock()
        mock_parent = Mock()

        mock_path_class.return_value = mock_source_path
        mock_source_path.__truediv__ = Mock(return_value=mock_output_path)
        mock_output_path.parent = mock_parent
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True

        # Pythonファイルのモック
        mock_python_file = Mock()
        mock_python_file.suffix = '.py'
        mock_python_file.relative_to.return_value = 'test.py'
        mock_source_path.rglob.return_value = [mock_python_file]

        # ファイル読み込みでエラーを発生させる
        mocker.patch('builtins.open', side_effect=PermissionError('Permission denied'))

        # Act & Assert
        result_project, message = project_service.execute_project(project.id)

        # プロジェクトが失敗状態になったことを確認
        assert result_project is None
        assert '予期しないエラーが発生しました' in message

        # プロジェクトの状態も確認
        assert project.status == 'Failed'
        assert project.result is not None
        assert 'error' in project.result
        assert 'Permission denied' in project.result['error']

    def test_invalid_project_id_error(self, mocker: Mock) -> None:
        """不正なプロジェクトIDのエラーテスト。"""
        # Arrange
        mock_repository = Mock()
        project_service = ProjectService(mock_repository)

        invalid_project_id = ProjectID(uuid4())
        mock_repository.find_by_id.side_effect = ResourceNotFoundError(
            'Project', invalid_project_id
        )

        # Act
        result_project, message = project_service.execute_project(invalid_project_id)

        # Assert
        assert result_project is None
        assert str(invalid_project_id) in message
