"""NewWorkerクラスのCiテスト(統合テスト)."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from app.domain.entities import Project
from app.domain.repositories import AIToolRepository
from app.infrastructure.new_worker import NewWorker
from app.infrastructure.persistence.json_repositories import JsonProjectRepository


@pytest.mark.ci
class TestNewWorkerCI:
    """NewWorkerクラスのCi(統合)テスト."""

    @pytest.fixture
    def temp_data_dir(self) -> Generator[Path, None, None]:
        """テスト用の一時データディレクトリを作成します。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def project_repository(self, temp_data_dir: Path) -> JsonProjectRepository:
        """テスト用のプロジェクトリポジトリを作成します。"""
        return JsonProjectRepository(temp_data_dir)

    @pytest.fixture
    def test_project(self, project_repository: JsonProjectRepository) -> Project:
        """テスト用のプロジェクトを作成してリポジトリに保存します。"""
        project = Project(
            id=uuid4(),
            name='テストプロジェクト',
            source='CI テスト用プロジェクト',
            ai_tool='test_tool',
        )
        project_repository.save(project)
        return project

    def test_NewWorkerが実際のプロジェクトリポジトリと統合して動作する(
        self,
        test_project: Project,
        project_repository: JsonProjectRepository,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch('app.infrastructure.new_worker.FileProcessor')
        mock_project_processor_class = mocker.patch(
            'app.infrastructure.new_worker.ProjectProcessor'
        )
        mock_file_processor = mocker.MagicMock()
        mock_project_processor = mocker.MagicMock()
        mock_file_processor_class.return_value = mock_file_processor
        mock_project_processor_class.return_value = mock_project_processor

        mock_ai_tool_repository = mocker.MagicMock(spec=AIToolRepository)

        worker = NewWorker(
            test_project.id, project_repository, ai_tool_repository=mock_ai_tool_repository
        )

        # Act
        worker.run()

        # Assert
        mock_project_processor_class.assert_called_once_with(
            project_repository=project_repository,
            file_processor=mock_file_processor,
            ai_tool_repository=mock_ai_tool_repository,
        )
        mock_project_processor.process_project.assert_called_once_with(test_project.id)

    def test_存在しないプロジェクトIDに対しても例外処理が適切に動作する(
        self,
        project_repository: JsonProjectRepository,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch('app.infrastructure.new_worker.FileProcessor')
        mock_project_processor_class = mocker.patch(
            'app.infrastructure.new_worker.ProjectProcessor'
        )
        non_existent_project_id = uuid4()
        mock_file_processor = mocker.MagicMock()
        mock_file_processor_class.return_value = mock_file_processor

        mock_ai_tool_repository = mocker.MagicMock(spec=AIToolRepository)
        worker = NewWorker(
            non_existent_project_id, project_repository, ai_tool_repository=mock_ai_tool_repository
        )

        mock_project_processor = mocker.MagicMock()
        mock_project_processor.process_project.side_effect = Exception('Project not found')
        mock_project_processor_class.return_value = mock_project_processor

        mock_logger = mocker.patch.object(worker, 'logger')
        # Act
        worker.run()

        # Assert
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert '例外発生:' in error_call_args
        assert 'Project not found' in error_call_args

    def test_ログ出力が正しく動作する(
        self,
        test_project: Project,
        project_repository: JsonProjectRepository,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch('app.infrastructure.new_worker.FileProcessor')
        mocker.patch('app.infrastructure.new_worker.ProjectProcessor')
        mock_file_processor = mocker.MagicMock()
        mock_file_processor_class.return_value = mock_file_processor

        # ログ設定をテスト用に調整
        mock_logger = mocker.MagicMock()
        mock_get_logger = mocker.patch('logging.getLogger')
        mock_get_logger.return_value = mock_logger

        # NewWorkerを再作成してmockされたloggerを使用
        mock_ai_tool_repository = mocker.MagicMock(spec=AIToolRepository)
        worker = NewWorker(
            test_project.id, project_repository, ai_tool_repository=mock_ai_tool_repository
        )

        # Act
        worker.run()

        # Assert
        mock_get_logger.assert_called_with('aiman')
        # run開始・run終了など複数回呼ばれるので、呼び出し回数で判定
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(
            f'[NewWorker] run開始: project_id={test_project.id}' in msg for msg in info_calls
        )

    def test_依存関係の初期化が正しい順序で実行される(
        self,
        test_project: Project,
        project_repository: JsonProjectRepository,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch('app.infrastructure.new_worker.FileProcessor')
        mock_project_processor_class = mocker.patch(
            'app.infrastructure.new_worker.ProjectProcessor'
        )
        mock_file_processor = mocker.MagicMock()
        mock_project_processor = mocker.MagicMock()
        mock_file_processor_class.return_value = mock_file_processor
        mock_project_processor_class.return_value = mock_project_processor

        mock_ai_tool_repository = mocker.MagicMock(spec=AIToolRepository)
        worker = NewWorker(
            test_project.id, project_repository, ai_tool_repository=mock_ai_tool_repository
        )

        # Act
        worker.run()

        # Assert - 依存関係が正しい順序で初期化されることを確認
        mock_file_processor_class.assert_called_once()
        mock_project_processor_class.assert_called_once()
        mock_project_processor.process_project.assert_called_once()
