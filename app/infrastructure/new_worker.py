"""リファクタリング後の新しいWorkerクラス。"""

import logging
import traceback
from multiprocessing import Process
from uuid import UUID

from app.application import ProjectProcessor
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.infrastructure.file_processor import FileProcessor


class NewWorker(Process):
    """リファクタリング後のワーカープロセス。"""

    def __init__(
        self,
        project_id: UUID,
        project_repository: ProjectRepository,
        ai_tool_repository: AIToolRepository | None = None,
    ) -> None:
        """ワーカーを初期化します。

        Args:
            project_id: 処理対象のプロジェクトID。
            project_repository: プロジェクトリポジトリ。
        """
        super().__init__()
        self.project_id = project_id
        self.project_repository = project_repository
        self.ai_tool_repository = ai_tool_repository
        self.logger = logging.getLogger('aiman')

    def run(self) -> None:
        """
        ワーカープロセスのメイン処理。
        """
        self._log_start()
        try:
            file_processor, ai_tool_repository = self._setup_dependencies()
            project_processor = self._create_project_processor(file_processor, ai_tool_repository)
            self._process_project(project_processor)
        except Exception as e:
            self._handle_exception(e)
        self._log_end()

    def _log_start(self) -> None:
        self.logger.info(f'[NewWorker] run開始: project_id={self.project_id}')

    def _log_end(self) -> None:
        self.logger.info(f'[NewWorker] run終了: project_id={self.project_id}')

    def _setup_dependencies(self) -> tuple[FileProcessor, AIToolRepository]:
        self.logger.info(f'[NewWorker] FileProcessor初期化: project_id={self.project_id}')
        file_processor = FileProcessor()
        ai_tool_repository = self.ai_tool_repository
        if ai_tool_repository is None:
            self.logger.error(f'[NewWorker] ai_tool_repositoryがNone: project_id={self.project_id}')
            raise RuntimeError('AIツールリポジトリの初期化に失敗しました')
        return file_processor, ai_tool_repository

    def _create_project_processor(
        self, file_processor: FileProcessor, ai_tool_repository: AIToolRepository
    ) -> ProjectProcessor:
        self.logger.info(f'[NewWorker] ProjectProcessor初期化: project_id={self.project_id}')
        return ProjectProcessor(
            project_repository=self.project_repository,
            file_processor=file_processor,
            ai_tool_repository=ai_tool_repository,
        )

    def _process_project(self, project_processor: ProjectProcessor) -> None:
        self.logger.info(f'[NewWorker] process_project呼び出し前: project_id={self.project_id}')
        project_processor.process_project(self.project_id)
        self.logger.info(f'[NewWorker] process_project呼び出し後: project_id={self.project_id}')

    def _handle_exception(self, e: Exception) -> None:
        tb = traceback.format_exc()
        self.logger.error(f'例外発生: {e}\n{tb}')
