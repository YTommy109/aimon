"""プロジェクトサービスのテストモジュール。"""

from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from app.errors import ResourceNotFoundError
from app.models import ProjectID, ToolType
from app.models.project import Project
from app.services.project_service import ProjectService
from app.utils.llm_client import LLMError


class TestProjectService:
    """プロジェクトサービスのテストクラス。"""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """プロジェクトリポジトリのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def project_service(self, mock_repository: Mock) -> ProjectService:
        """プロジェクトサービスを作成する。"""
        return ProjectService(mock_repository)

    def test_プロジェクトを作成できる(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.OVERVIEW
        created_project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )
        mock_repository.save.return_value = created_project

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is not None
        assert result.name == 'テストプロジェクト'
        assert result.source == '/path/to/source'
        mock_repository.save.assert_called_once()

    def test_無効な入力でプロジェクト作成が失敗する(self, project_service: ProjectService) -> None:
        # Arrange
        name = ''  # 空の名前
        source = '/path/to/source'
        tool = ToolType.OVERVIEW

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is None

    def test_内蔵ツールでプロジェクト作成が成功する(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.REVIEW

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is not None
        assert result.name == name
        assert result.source == source
        assert result.tool == tool
        mock_repository.save.assert_called_once_with(result)

    def test_プロジェクト作成でエラーが発生した場合はNoneを返す(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.OVERVIEW
        mock_repository.save.side_effect = Exception('データベースエラー')

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is None

    def test_プロジェクトを実行できる(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
        tmp_path: Path,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='テストプロジェクト',
            source=str(tmp_path),
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # LLMClientのモック
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 非同期メソッドのモック
        async def mock_generate_text(prompt: str, model: str | None = None) -> str:
            return 'テスト用のLLM応答'

        mock_llm_instance.generate_text = mock_generate_text

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'
        mock_repository.save.assert_called()

    def test_存在しないプロジェクトの実行は失敗する(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ResourceNotFoundError('プロジェクト', project_id)

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is None
        assert 'が見つかりません' in message

    def test_内蔵ツールでプロジェクトを作成できる(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.OVERVIEW

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is not None
        assert result.name == name
        assert result.source == source
        assert result.tool == ToolType.OVERVIEW
        mock_repository.save.assert_called_once()

    def test_内蔵ツールでプロジェクトを実行できる(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
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

        # 新しい実装で必要なメソッドをモック
        mock_source_path.exists.return_value = True
        mock_source_path.is_dir.return_value = True
        mock_source_path.rglob.return_value = []  # 空のファイルリストを返す

        mock_open = mocker.patch('builtins.open', mocker.mock_open())

        # LLMClientのモック
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 非同期メソッドのモック
        async def mock_generate_text(prompt: str, model: str | None = None) -> str:
            return 'テスト用のLLM応答'

        mock_llm_instance.generate_text = mock_generate_text

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'
        mock_repository.save.assert_called()
        # ファイル書き込みが行われることを確認（特定の引数での呼び出しのみをチェック）
        mock_open.assert_any_call(mock_output_path, 'w', encoding='utf-8')

    def test_内蔵ツールOVERVIEWで正しいファイルが生成される(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
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
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 非同期メソッドのモック
        async def mock_generate_text(prompt: str, model: str | None = None) -> str:
            return 'テスト用のLLM応答'

        mock_llm_instance.generate_text = mock_generate_text

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'

        # overview.txt が作成されることを確認
        mock_path_class.assert_called_with('/test/source')
        mock_source_path.__truediv__.assert_called_once_with('overview.txt')
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # ファイル内容の確認 - 特定の引数での呼び出しのみをチェック
        mock_open.assert_any_call(mock_output_path, 'w', encoding='utf-8')
        handle = mock_open.return_value.__enter__.return_value

        # 実際の出力内容を確認（モックされたPathオブジェクトの文字列表現を含む）
        actual_call_args = handle.write.call_args[0][0]

        assert '# OVERVIEW result' in actual_call_args
        # モックされたLLM応答が含まれていることを確認
        assert 'テスト用のLLM応答' in actual_call_args

    def test_LLM呼び出しエラーが発生した場合の処理(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        """LLM呼び出しエラーが発生した場合の処理をテストする。"""
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='LLMエラーテストプロジェクト',
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

        # LLMClientのモック
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # LLMErrorを発生させる
        llm_error = LLMError(
            message='OpenAI API呼び出しエラー: API制限に達しました',
            provider='openai',
            model='gpt-3.5-turbo',
        )
        mock_llm_instance.generate_text.side_effect = llm_error

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is None
        assert 'OpenAI API呼び出しエラー: API制限に達しました' in message

        # プロジェクトが失敗状態で保存されることを確認
        mock_repository.save.assert_called()
        saved_project = mock_repository.save.call_args[0][0]
        assert saved_project.status.value == 'Failed'
        assert 'error' in saved_project.result
        assert saved_project.result['error'] == 'OpenAI API呼び出しエラー: API制限に達しました'

    def test_LLM呼び出しで予期しないエラーが発生した場合の処理(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        """LLM呼び出しで予期しないエラーが発生した場合の処理をテストする。"""
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='予期しないエラーテストプロジェクト',
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

        # LLMClientのモック
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 予期しないエラーを発生させる
        mock_llm_instance.generate_text.side_effect = Exception('予期しないエラー')

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is None
        assert 'LLM呼び出しエラー: 予期しないエラー' in message

        # プロジェクトが失敗状態で保存されることを確認
        mock_repository.save.assert_called()
        saved_project = mock_repository.save.call_args[0][0]
        assert saved_project.status.value == 'Failed'
        assert 'error' in saved_project.result
        assert 'LLM呼び出しエラー: 予期しないエラー' in saved_project.result['error']

    def test_内蔵ツールREVIEWで正しいファイルが生成される(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
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
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 非同期メソッドのモック
        async def mock_generate_text(prompt: str, model: str | None = None) -> str:
            return 'テスト用のLLM応答'

        mock_llm_instance.generate_text = mock_generate_text

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'

        # review.txt が作成されることを確認
        mock_path_class.assert_called_with('/test/source')
        mock_source_path.__truediv__.assert_any_call('review.txt')
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_内蔵ツール実行時にファイル書き込みエラーが発生した場合(
        self,
        mocker: MockerFixture,
        project_service: ProjectService,
        mock_repository: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='エラーテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Path をモックして正常動作させる
        mocker.patch('app.services.project_service.Path')

        # open でエラーを発生させる（.env.dev の読み込みは除く）
        def mock_open_side_effect(*args: object, **kwargs: object) -> object:
            # .env.dev ファイルの読み込みの場合は正常に動作
            if len(args) > 0 and str(args[0]).endswith('.env.dev'):
                return mocker.mock_open()()
            # その他の場合はエラーを発生
            raise OSError('Permission denied')

        mocker.patch('builtins.open', side_effect=mock_open_side_effect)

        # LLMClientのモック
        mock_llm_client = mocker.patch('app.services.project_service.LLMClient')
        mock_llm_instance = Mock()
        mock_llm_client.return_value = mock_llm_instance

        # 非同期メソッドのモック
        async def mock_generate_text(prompt: str, model: str | None = None) -> str:
            return 'テスト用のLLM応答'

        mock_llm_instance.generate_text = mock_generate_text

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is None
        assert message == '予期しないエラーが発生しました'
        # エラー時はプロジェクトが失敗状態で保存される
        mock_repository.save.assert_called()
        saved_project = mock_repository.save.call_args[0][0]
        assert saved_project.result == {'error': 'Permission denied'}
