"""依存性注入コンテナ。"""

from pathlib import Path

from app.config import config
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.infrastructure.file_processor import FileProcessor
from app.infrastructure.persistence import JsonAIToolRepository, JsonProjectRepository

from .project_processor import ProjectProcessor


class ApplicationContainer:
    """アプリケーションの依存性注入コンテナ。"""

    def __init__(self, data_dir: Path | None = None) -> None:
        """コンテナを初期化します。

        Args:
            data_dir: データディレクトリのパス。Noneの場合はconfigから取得。
        """
        self._data_dir = data_dir or config.data_dir_path
        self._project_repository: ProjectRepository | None = None
        self._ai_tool_repository: AIToolRepository | None = None
        self._file_processor: FileProcessor | None = None
        self._project_processor: ProjectProcessor | None = None

    @property
    def project_repository(self) -> ProjectRepository:
        """プロジェクトリポジトリを取得します。"""
        if self._project_repository is None:
            self._project_repository = JsonProjectRepository(self._data_dir)
        return self._project_repository

    @property
    def ai_tool_repository(self) -> AIToolRepository:
        """AIツールリポジトリを取得します。"""
        if self._ai_tool_repository is None:
            self._ai_tool_repository = JsonAIToolRepository(self._data_dir)
        return self._ai_tool_repository

    @property
    def file_processor(self) -> FileProcessor:
        """ファイルプロセッサーを取得します。"""
        if self._file_processor is None:
            self._file_processor = FileProcessor()
        return self._file_processor

    @property
    def project_processor(self) -> ProjectProcessor:
        """プロジェクトプロセッサーを取得します。"""
        if self._project_processor is None:
            self._project_processor = ProjectProcessor(
                project_repository=self.project_repository,
                file_processor=self.file_processor,
                ai_tool_repository=self.ai_tool_repository,
            )
        return self._project_processor
