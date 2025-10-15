"""プロジェクトサービスのテスト。"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from pytest_mock import MockerFixture

from app.errors import LLMError, ProjectNotFoundError
from app.models.project import Project
from app.services.project_service import ProjectService
from app.types import LLMProviderName, ProjectID, ToolType
from app.utils.llm_client import LLMClient


class TestProjectService:
    """プロジェクトサービスのテストクラス。"""

    @pytest.fixture
    def mock_repository(self) -> Mock:
        """プロジェクトリポジトリのモックを作成する。"""
        return Mock()

    @pytest.fixture
    def mock_file_system(self) -> Mock:
        """ファイルシステムのモックを作成する。"""
        mock_fs = Mock()
        # デフォルトの振る舞いを設定
        mock_fs.exists.return_value = True
        mock_fs.is_dir.return_value = True
        mock_fs.is_file.return_value = True
        mock_fs.list_files.return_value = []
        mock_fs.read_file.return_value = 'test content'
        return mock_fs

    @pytest.fixture
    def mock_llm_client(self) -> Mock:
        """LLMClientのモックを作成する。"""
        mock_client = Mock(spec=LLMClient)
        mock_client.generate_text = AsyncMock(return_value='テスト用のLLM応答')
        return mock_client

    @pytest.fixture
    def mock_llm_client_factory(self, mock_llm_client: Mock) -> Mock:
        """LLMClientファクトリのモックを作成する。"""
        return Mock(return_value=mock_llm_client)

    @pytest.fixture
    def project_service(
        self, mock_repository: Mock, mock_file_system: Mock, mock_llm_client_factory: Mock
    ) -> ProjectService:
        """プロジェクトサービスを作成する。"""
        return ProjectService(mock_repository, mock_file_system, mock_llm_client_factory)

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
        # インデックス作成の開始・終了で2回saveが呼ばれる
        assert mock_repository.save.call_count == 2

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
        # インデックス作成の開始・終了で2回saveが呼ばれる
        assert mock_repository.save.call_count == 2

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
        project_service: ProjectService,
        mock_repository: Mock,
        mock_file_system: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='テストプロジェクト',
            source='/test/path',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'
        mock_repository.save.assert_called()
        mock_file_system.write_file.assert_called_once()

    def test_存在しないプロジェクトの実行は失敗する(
        self, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        mock_repository.find_by_id.side_effect = ProjectNotFoundError(project_id)

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
        # インデックス作成の開始・終了で2回saveが呼ばれる
        assert mock_repository.save.call_count == 2

    def test_プロジェクト作成時にベクタDBが構築される(
        self, mocker: MockerFixture, project_service: ProjectService, mock_repository: Mock
    ) -> None:
        # Arrange
        name = 'RAGテスト'
        source = '/path/to/source'
        tool = ToolType.OVERVIEW

        # build_faiss_index をモックして外部依存を避ける
        mock_build = mocker.patch('app.services.project_service.build_faiss_index')
        mock_path = mocker.patch('app.services.project_service.Path')
        mock_path_instance = mock_path.return_value
        mock_path_instance.__truediv__ = mocker.Mock(return_value=mock_path_instance)

        # Act
        result = project_service.create_project(name, source, tool)

        # Assert
        assert result is not None
        # build_faiss_index が呼ばれたことを確認
        mock_build.assert_called_once()
        args, _ = mock_build.call_args
        # 引数: source_dir, index_dir, provider
        assert args[0] == mock_path_instance  # Path(project.source)
        assert args[1] == mock_path_instance  # Path(project.source) / 'vector_db'
        assert isinstance(args[2], LLMProviderName)

    def test_内蔵ツールでプロジェクトを実行できる(
        self,
        project_service: ProjectService,
        mock_repository: Mock,
        mock_file_system: Mock,
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

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'
        mock_repository.save.assert_called()
        mock_file_system.write_file.assert_called_once()

    def test_内蔵ツールOVERVIEWで正しいファイルが生成される(
        self,
        project_service: ProjectService,
        mock_repository: Mock,
        mock_file_system: Mock,
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

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'

        # overview.txt が作成されることを確認
        mock_file_system.write_file.assert_called_once()
        call_args = mock_file_system.write_file.call_args
        output_path = call_args[0][0]
        content = call_args[0][1]

        assert str(output_path).endswith('overview.txt')
        assert '# OVERVIEW result' in content
        assert 'テスト用のLLM応答' in content

    def test_LLM呼び出しエラーが発生した場合の処理(
        self,
        project_service: ProjectService,
        mock_repository: Mock,
        mock_llm_client: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='LLMエラーテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # LLMErrorを発生させる
        llm_error = LLMError(
            message='OpenAI API呼び出しエラー: API制限に達しました',
            provider=LLMProviderName.OPENAI,
            model='gpt-3.5-turbo',
        )
        mock_llm_client.generate_text.side_effect = llm_error

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
        project_service: ProjectService,
        mock_repository: Mock,
        mock_llm_client: Mock,
    ) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))
        project = Project(
            name='予期しないエラーテストプロジェクト',
            source='/test/source',
            tool=ToolType.OVERVIEW,
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # 予期しないエラーを発生させる
        mock_llm_client.generate_text.side_effect = Exception('予期しないエラー')

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
        project_service: ProjectService,
        mock_repository: Mock,
        mock_file_system: Mock,
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

        # Pythonファイルのモック
        mock_python_file = Mock()
        mock_python_file.suffix = '.py'
        mock_python_file.is_file.return_value = True
        mock_python_file.relative_to.return_value = Path('test.py')
        mock_file_system.list_files.return_value = [mock_python_file]
        mock_file_system.read_file.return_value = 'def test_function():\n    pass'

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is not None
        assert message == 'プロジェクトの実行が完了しました'

        # review.txt が作成されることを確認
        mock_file_system.write_file.assert_called_once()
        call_args = mock_file_system.write_file.call_args
        output_path = call_args[0][0]
        content = call_args[0][1]

        assert str(output_path).endswith('review.txt')
        assert '# REVIEW result' in content

    def test_内蔵ツール実行時にファイル書き込みエラーが発生した場合(
        self,
        project_service: ProjectService,
        mock_repository: Mock,
        mock_file_system: Mock,
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

        # ファイル書き込みでエラーを発生させる
        mock_file_system.write_file.side_effect = OSError('Permission denied')

        # Act
        result_project, message = project_service.execute_project(project_id)

        # Assert
        assert result_project is None
        assert message == '予期しないエラーが発生しました'
        # エラー時はプロジェクトが失敗状態で保存される
        mock_repository.save.assert_called()
        saved_project = mock_repository.save.call_args[0][0]
        assert saved_project.result == {'error': 'Permission denied'}

    def test_インデックス再構築が正常に実行される(
        self, project_service: ProjectService, mock_repository: Mock, mock_file_system: Mock
    ) -> None:
        """インデックス再構築が正常に実行されることをテストする。"""
        # Arrange
        project_id = ProjectID(uuid4())
        project = Project(
            id=project_id, name='テストプロジェクト', source='/test/source', tool=ToolType.OVERVIEW
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # Act
        result_project, message = project_service.rebuild_project_indexes(project_id)

        # Assert
        assert result_project is not None
        assert str(result_project.id) == str(project_id)
        assert message == 'インデックスの再構築が完了しました'
        mock_repository.find_by_id.assert_called_once_with(project_id)
        # インデックス構築開始と完了で2回保存される
        assert mock_repository.save.call_count == 2

    def test_インデックス再構築でエラーが発生した場合(
        self, project_service: ProjectService, mock_repository: Mock, mock_file_system: Mock
    ) -> None:
        """インデックス再構築でエラーが発生した場合の処理をテストする。"""
        # Arrange
        project_id = ProjectID(uuid4())
        project = Project(
            id=project_id, name='テストプロジェクト', source='/test/source', tool=ToolType.OVERVIEW
        )

        mock_repository.find_by_id.return_value = project
        mock_repository.save.return_value = None

        # インデックス構築でエラーを発生させる
        mock_file_system.exists.return_value = False

        # Act
        result_project, message = project_service.rebuild_project_indexes(project_id)

        # Assert
        assert result_project is not None
        assert 'インデックスの再構築が完了しました' in message
        mock_repository.find_by_id.assert_called_once_with(project_id)
        # エラー時でもプロジェクトは保存される
        assert mock_repository.save.call_count == 2
