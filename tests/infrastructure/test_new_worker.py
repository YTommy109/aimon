"""NewWorkerクラスのユニットテスト。"""

import logging
from multiprocessing import Process
from uuid import uuid4

from pytest_mock import MockerFixture

import app.infrastructure.new_worker as new_worker_module
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.infrastructure.new_worker import NewWorker


class TestNewWorker:
    """NewWorkerクラスのテスト。"""

    def test_NewWorkerが正しく初期化される(self, mocker: MockerFixture) -> None:
        # Arrange
        project_id = uuid4()
        mock_repository = mocker.MagicMock(spec=ProjectRepository)

        # Act
        worker = NewWorker(project_id, mock_repository)

        # Assert
        assert isinstance(worker, Process)
        assert worker.project_id == project_id
        assert worker.project_repository == mock_repository
        assert isinstance(worker.logger, logging.Logger)
        assert worker.logger.name == 'aiman'

    def test_runメソッドが正常に依存関係を構築してプロジェクトを処理する(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch.object(new_worker_module, 'FileProcessor')
        mock_project_processor_class = mocker.patch.object(new_worker_module, 'ProjectProcessor')

        project_id = uuid4()
        mock_repository = mocker.MagicMock(spec=ProjectRepository)

        mock_file_processor = mocker.MagicMock()
        mock_project_processor = mocker.MagicMock()

        mock_file_processor_class.return_value = mock_file_processor
        mock_project_processor_class.return_value = mock_project_processor

        # arrange部でai_tool_repositoryのモックを用意
        mock_ai_tool_repository = mocker.MagicMock(spec=AIToolRepository)

        worker = NewWorker(project_id, mock_repository, ai_tool_repository=mock_ai_tool_repository)

        # Act
        mock_logger = mocker.patch.object(worker, 'logger')
        worker.run()

        # Assert
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(f'[NewWorker] run開始: project_id={project_id}' in msg for msg in info_calls)
        mock_file_processor_class.assert_called_once()
        mock_project_processor_class.assert_called_once_with(
            project_repository=mock_repository,
            file_processor=mock_file_processor,
            ai_tool_repository=mock_ai_tool_repository,
        )
        mock_project_processor.process_project.assert_called_once_with(project_id)

    def test_runメソッド実行中に例外が発生した場合にエラーログが出力される(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_file_processor_class = mocker.patch.object(new_worker_module, 'FileProcessor')
        mocker.patch.object(new_worker_module, 'ProjectProcessor')

        project_id = uuid4()
        mock_repository = mocker.MagicMock(spec=ProjectRepository)

        error_message = 'Test error'
        mock_file_processor_class.side_effect = Exception(error_message)

        worker = NewWorker(project_id, mock_repository)

        # Act
        mock_logger = mocker.patch.object(worker, 'logger')
        worker.run()

        # Assert
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(f'[NewWorker] run開始: project_id={project_id}' in msg for msg in info_calls)
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert '例外発生:' in error_call_args
        assert error_message in error_call_args

    def test_ProjectProcessor初期化時に例外が発生した場合にエラーログが出力される(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mocker.patch.object(new_worker_module, 'FileProcessor')
        mock_project_processor_class = mocker.patch.object(new_worker_module, 'ProjectProcessor')

        project_id = uuid4()
        mock_repository = mocker.MagicMock(spec=ProjectRepository)

        error_message = 'ProjectProcessor initialization failed'
        mock_project_processor_class.side_effect = Exception(error_message)

        worker = NewWorker(
            project_id, mock_repository, ai_tool_repository=mocker.MagicMock(spec=AIToolRepository)
        )

        # Act
        mock_logger = mocker.patch.object(worker, 'logger')
        worker.run()

        # Assert
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(f'[NewWorker] run開始: project_id={project_id}' in msg for msg in info_calls)
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert '例外発生:' in error_call_args
        assert error_message in error_call_args

    def test_process_project実行時に例外が発生した場合にエラーログが出力される(
        self, mocker: MockerFixture
    ) -> None:
        # Arrange
        mocker.patch.object(new_worker_module, 'FileProcessor')
        mock_project_processor_class = mocker.patch.object(new_worker_module, 'ProjectProcessor')

        project_id = uuid4()
        mock_repository = mocker.MagicMock(spec=ProjectRepository)

        mock_project_processor = mocker.MagicMock()
        error_message = 'Process project failed'
        mock_project_processor.process_project.side_effect = Exception(error_message)
        mock_project_processor_class.return_value = mock_project_processor

        worker = NewWorker(
            project_id, mock_repository, ai_tool_repository=mocker.MagicMock(spec=AIToolRepository)
        )

        # Act
        mock_logger = mocker.patch.object(worker, 'logger')
        worker.run()

        # Assert
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(f'[NewWorker] run開始: project_id={project_id}' in msg for msg in info_calls)
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert '例外発生:' in error_call_args
        assert error_message in error_call_args
