"""ProjectProcessorクラスのテスト。"""

import builtins
import io
import logging
from pathlib import Path
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from app.application.project_processor import ProjectProcessor
from app.domain.entities import Project, ProjectStatus
from app.domain.repositories import ProjectRepository
from app.errors import (
    APIConfigurationError,
    FileReadingError,
    FileWritingError,
    ProjectProcessingError,
)
from app.infrastructure.external.ai_client import AIServiceClient
from app.infrastructure.file_processor import FileProcessor


class TestProjectProcessor:
    """ProjectProcessorクラスのテスト。"""

    @pytest.fixture
    def mock_project_repository(self, mocker: MockerFixture) -> MagicMock:
        return mocker.MagicMock(spec=ProjectRepository)

    @pytest.fixture
    def mock_file_processor(self, mocker: MockerFixture) -> MagicMock:
        return mocker.MagicMock(spec=FileProcessor)

    @pytest.fixture
    def mock_ai_client(self, mocker: MockerFixture) -> MagicMock:
        return mocker.MagicMock(spec=AIServiceClient)

    @pytest.fixture
    def project_processor(
        self,
        mock_project_repository: MagicMock,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
    ) -> ProjectProcessor:
        return ProjectProcessor(
            mock_project_repository,
            mock_file_processor,
            mock_ai_client,
        )

    @pytest.fixture
    def sample_project(self) -> Project:
        return Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')

    @pytest.fixture
    def sample_project_id(self) -> UUID:
        return uuid4()

    def test_ProjectProcessorが正しく初期化される(
        self,
        mock_project_repository: MagicMock,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
    ) -> None:
        """初期化のテスト。"""
        # Act
        processor = ProjectProcessor(
            mock_project_repository,
            mock_file_processor,
            mock_ai_client,
        )

        # Assert
        assert processor.project_repository == mock_project_repository
        assert processor.file_processor == mock_file_processor
        assert processor.ai_client == mock_ai_client
        assert isinstance(processor.logger, logging.Logger)

    def test_プロジェクトが正常に処理され結果が保存される(
        self,
        project_processor: ProjectProcessor,
        mock_project_repository: MagicMock,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
        sample_project: Project,
        sample_project_id: UUID,
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト処理成功のテスト。"""
        # Arrange
        mock_project_repository.find_by_id.return_value = sample_project
        mock_file_processor.prepare_output_file.return_value = Path('/test/output.md')
        mock_file_processor.collect_files_to_process.return_value = [Path('/test/file1.txt')]
        mock_file_processor.read_file_content.return_value = ('テストコンテンツ', [])
        mock_ai_client.generate_summary.return_value = '要約結果'

        mocker.patch.object(builtins, 'open', mocker.mock_open())
        # Act
        project_processor.process_project(sample_project_id)

        # Assert
        mock_project_repository.find_by_id.assert_called_once_with(sample_project_id)
        assert sample_project.status == ProjectStatus.PROCESSING
        mock_project_repository.save.assert_called()
        mock_project_repository.update_result.assert_called_once()

    def test_プロジェクトが見つからない場合にProjectProcessingErrorが発生する(
        self,
        project_processor: ProjectProcessor,
        mock_project_repository: MagicMock,
        sample_project_id: UUID,
    ) -> None:
        """プロジェクトが見つからない場合のテスト。"""
        # Arrange
        mock_project_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ProjectProcessingError):
            project_processor.process_project(sample_project_id)

    def test_複数ファイルのGemini要約処理が正常に実行される(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
        mock_project_repository: MagicMock,
        sample_project: Project,
        mocker: MockerFixture,
    ) -> None:
        """Gemini要約処理成功のテスト。"""
        # Arrange
        output_file = Path('/test/output.md')
        mock_file_processor.prepare_output_file.return_value = output_file
        mock_file_processor.collect_files_to_process.return_value = [
            Path('/test/file1.txt'),
            Path('/test/file2.txt'),
        ]
        mock_file_processor.read_file_content.side_effect = [
            ('テストコンテンツ1', []),
            ('テストコンテンツ2', []),
        ]
        mock_ai_client.generate_summary.side_effect = ['要約結果1', '要約結果2']

        mocker.patch.object(builtins, 'open', mocker.mock_open())
        # Act
        project_processor._execute_gemini_summarize(sample_project)

        # Assert
        mock_file_processor.prepare_output_file.assert_called_once_with(
            Path(sample_project.source),
            sample_project.name,
        )
        mock_file_processor.collect_files_to_process.assert_called_once_with(
            Path(sample_project.source),
        )
        assert mock_file_processor.read_file_content.call_count == 2
        assert mock_ai_client.generate_summary.call_count == 2
        mock_project_repository.update_result.assert_called_once()

    def test_出力ファイル書き込みエラー時にFileWritingErrorが発生する(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        sample_project: Project,
        mocker: MockerFixture,
    ) -> None:
        """ファイル書き込みエラーのテスト。"""
        # Arrange
        output_file = Path('/test/output.md')
        mock_file_processor.prepare_output_file.return_value = output_file

        mocker.patch.object(builtins, 'open', side_effect=OSError('書き込み失敗'))
        with pytest.raises(FileWritingError):
            project_processor._execute_gemini_summarize(sample_project)

    def test_単一ファイルが正常に処理され要約が生成される(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """単一ファイル処理成功のテスト。"""
        # Arrange
        file_path = Path('/test/file.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        mock_file_processor.read_file_content.return_value = ('テストコンテンツ', [])
        mock_ai_client.generate_summary.return_value = '要約結果'

        # Act
        result = project_processor._process_single_file(file_path, mock_output)

        # Assert
        assert result is True
        mock_file_processor.read_file_content.assert_called_once_with(file_path)
        mock_file_processor.create_prompt_json.assert_called_once()
        mock_ai_client.generate_summary.assert_called_once_with('テストコンテンツ', [])

    def test_空のファイルの場合に処理がスキップされる(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """空のファイル処理のテスト。"""
        # Arrange
        file_path = Path('/test/empty.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        mock_file_processor.read_file_content.return_value = ('   ', [])

        # Act
        result = project_processor._process_single_file(file_path, mock_output)

        # Assert
        assert result is False

    def test_ファイル読み取りエラー時にエラー情報が出力される(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """ファイル処理エラーのテスト。"""
        # Arrange
        file_path = Path('/test/error.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        mock_file_processor.read_file_content.side_effect = FileReadingError('/test/error.txt')

        # Act
        result = project_processor._process_single_file(file_path, mock_output)

        # Assert
        assert result is False
        mock_output.write.assert_called()

    def test_API設定エラー時にエラー情報が出力される(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """API設定エラーのテスト。"""
        # Arrange
        file_path = Path('/test/file.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        mock_file_processor.read_file_content.return_value = ('テストコンテンツ', [])
        mock_ai_client.generate_summary.side_effect = APIConfigurationError('API設定エラー')

        # Act
        result = project_processor._process_single_file(file_path, mock_output)

        # Assert
        assert result is False
        mock_output.write.assert_called()

    def test_画像を含むファイルコンテンツが正常に処理される(
        self,
        project_processor: ProjectProcessor,
        mock_file_processor: MagicMock,
        mock_ai_client: MagicMock,
        mocker: MockerFixture,
    ) -> None:
        """画像ありファイルコンテンツ処理のテスト。"""
        # Arrange
        file_path = Path('/test/file.txt')
        content = 'テストコンテンツ'
        images = [mocker.MagicMock(spec=Image.Image)]
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        mock_ai_client.generate_summary.return_value = '要約結果'

        # Act
        result = project_processor._process_file_content(file_path, content, images, mock_output)

        # Assert
        assert result is True
        mock_file_processor.create_prompt_json.assert_called_once()
        # プロンプトに画像が含まれていることを確認
        call_args = mock_file_processor.create_prompt_json.call_args[0]
        prompt = call_args[0]
        assert len(prompt) == 2  # テキスト + 画像
        assert images[0] in prompt

    def test_プロジェクトがNoneの場合に保存処理がスキップされる(
        self,
        project_processor: ProjectProcessor,
        mock_project_repository: MagicMock,
    ) -> None:
        """プロジェクトがNoneの場合のエラーハンドリングのテスト。"""
        # Arrange
        error = ValueError('一般的なエラー')

        # Act
        project_processor._handle_project_error(None, error)

        # Assert
        # プロジェクトがNoneの場合は保存処理が呼ばれない
        mock_project_repository.save.assert_not_called()

    def test_ファイル処理エラーハンドリングが正しく動作する(
        self,
        project_processor: ProjectProcessor,
        mocker: MockerFixture,
    ) -> None:
        """ファイル処理エラーハンドリングのテスト。"""
        # Arrange
        file_path = Path('/test/error.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        error = FileReadingError('/test/error.txt')

        # Act
        result = project_processor._handle_file_processing_error(file_path, mock_output, error)

        # Assert
        assert result is False
        mock_output.write.assert_called()
        # エラーメッセージが出力に書き込まれることを確認
        write_calls = mock_output.write.call_args_list
        assert any('エラー' in str(call) for call in write_calls)

    def test_APIエラーハンドリングが正しく動作する(
        self,
        project_processor: ProjectProcessor,
        mocker: MockerFixture,
    ) -> None:
        """API設定エラーハンドリングのテスト。"""
        # Arrange
        file_path = Path('/test/api_error.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        error = APIConfigurationError('API設定失敗')

        # Act
        result = project_processor._handle_api_error(file_path, mock_output, error)

        # Assert
        assert result is False
        mock_output.write.assert_called()
        # エラーメッセージが出力に書き込まれることを確認
        write_calls = mock_output.write.call_args_list
        assert any('エラー' in str(call) for call in write_calls)

    def test_ファイル処理エラーの統合ハンドリングが正しく動作する(
        self,
        project_processor: ProjectProcessor,
        mocker: MockerFixture,
    ) -> None:
        """処理エラー統合ハンドリング(ファイル処理エラー)のテスト。"""
        # Arrange
        file_path = Path('/test/error.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        error = FileReadingError('/test/error.txt')

        # Act
        result = project_processor._handle_processing_error(file_path, mock_output, error)

        # Assert
        assert result is False

    def test_API設定エラーの統合ハンドリングが正しく動作する(
        self,
        project_processor: ProjectProcessor,
        mocker: MockerFixture,
    ) -> None:
        """処理エラー統合ハンドリング(API設定エラー)のテスト。"""
        # Arrange
        file_path = Path('/test/error.txt')
        mock_output = mocker.MagicMock(spec=io.TextIOWrapper)
        error = APIConfigurationError('API設定失敗')

        # Act
        result = project_processor._handle_processing_error(file_path, mock_output, error)

        # Assert
        assert result is False


class TestProjectProcessorIntegration:
    """ProjectProcessorの統合テスト。"""

    @pytest.fixture
    def mock_dependencies(self, mocker: MockerFixture) -> tuple[MagicMock, MagicMock, MagicMock]:
        return mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()

    def test_プロジェクト処理の完全なワークフローが正常に実行される(
        self,
        mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト処理の完全なワークフローのテスト。"""
        # Arrange
        mock_project_repo, mock_file_processor, mock_ai_client = mock_dependencies
        processor = ProjectProcessor(mock_project_repo, mock_file_processor, mock_ai_client)

        project_id = uuid4()
        project = Project(name='統合テスト', source='/test/source', ai_tool='test-tool')

        mock_project_repo.find_by_id.return_value = project
        mock_file_processor.prepare_output_file.return_value = Path('/test/output.md')
        mock_file_processor.collect_files_to_process.return_value = [
            Path('/test/file1.txt'),
            Path('/test/file2.xlsx'),
        ]
        mock_file_processor.read_file_content.side_effect = [
            ('テキストファイルの内容', []),
            ('Excelファイルの内容', [mocker.MagicMock(spec=Image.Image)]),
        ]
        mock_ai_client.generate_summary.side_effect = [
            'テキストファイルの要約',
            'Excelファイルの要約',
        ]

        mocker.patch.object(builtins, 'open', mocker.mock_open())
        # Act
        processor.process_project(project_id)

        # Assert
        # プロジェクトが処理状態になっていることを確認
        assert project.status == ProjectStatus.PROCESSING
        # 結果が更新されていることを確認
        mock_project_repo.update_result.assert_called_once()
        # 処理されたファイル数が正しいことを確認
        result_call = mock_project_repo.update_result.call_args[0][1]
        assert len(result_call['processed_files']) == 2

    def test_プロジェクト処理のE2Eテスト(
        self,
        mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
        mocker: MockerFixture,
    ) -> None:
        """プロジェクト処理のE2Eテスト。"""
        # Arrange
        mock_project_repository, mock_file_processor, mock_ai_client = mock_dependencies
        project_id = uuid4()
        project = Project(
            id=project_id,
            name='E2Eテストプロジェクト',
            source='/e2e/test/path',
            ai_tool='e2e-tool',
        )
        mock_project_repository.find_by_id.return_value = project
        mock_file_processor.prepare_output_file.return_value = Path('/e2e/output.md')
        mock_file_processor.collect_files_to_process.return_value = [Path('/e2e/file.txt')]
        mock_file_processor.read_file_content.return_value = ('E2Eテストコンテンツ', [])
        mock_ai_client.generate_summary.return_value = 'E2E要約結果'

        mocker.patch.object(builtins, 'open', mocker.mock_open())

        processor = ProjectProcessor(mock_project_repository, mock_file_processor, mock_ai_client)
        # Act
        processor.process_project(project_id)

        # Assert
        # プロジェクトが処理状態になっていることを確認
        assert project.status == ProjectStatus.PROCESSING
        # 結果が更新されていることを確認
        mock_project_repository.update_result.assert_called_once()
        # 処理されたファイル数が正しいことを確認
        result_call = mock_project_repository.update_result.call_args[0][1]
        assert len(result_call['processed_files']) == 1
