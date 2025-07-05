"""リファクタリング後の新しいWorkerクラス。"""

import logging
from multiprocessing import Process
from uuid import UUID

from app.application import ProjectProcessor
from app.domain.repositories import ProjectRepository
from app.infrastructure.external import AIServiceClient
from app.infrastructure.file_processor import FileProcessor


class NewWorker(Process):
    """リファクタリング後のワーカープロセス。"""

    def __init__(self, project_id: UUID, project_repository: ProjectRepository) -> None:
        """ワーカーを初期化します。

        Args:
            project_id: 処理対象のプロジェクトID。
            project_repository: プロジェクトリポジトリ。
        """
        super().__init__()
        self.project_id = project_id
        self.project_repository = project_repository
        self.logger = logging.getLogger('aiman')

    def run(self) -> None:
        """ワーカープロセスのメイン処理。"""
        self.logger.info(f'New Worker started for project_id: {self.project_id}')

        try:
            # 依存性を組み立て
            file_processor = FileProcessor()
            ai_client = AIServiceClient()

            # プロジェクトプロセッサーを作成
            project_processor = ProjectProcessor(
                project_repository=self.project_repository,
                file_processor=file_processor,
                ai_client=ai_client,
            )

            # プロジェクトを処理
            project_processor.process_project(self.project_id)

        except Exception as e:
            self.logger.error(f'New Worker error: {e}')
            # エラーハンドリングはProjectProcessorに委譲
