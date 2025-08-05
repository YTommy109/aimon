"""プロジェクトサービスモジュール。"""

import logging

from app.errors import CommandExecutionError, CommandSecurityError, ResourceNotFoundError
from app.models import AIToolID, ProjectID
from app.models.ai_tool import AITool
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.ai_tool_service import AIToolService
from app.utils.executors import CommandExecutor

logger = logging.getLogger('aiman')


class ProjectService:
    """プロジェクトのビジネスロジックを管理するサービス。"""

    def __init__(self, repository: JsonProjectRepository, ai_tool_service: AIToolService):
        """サービスを初期化します。

        Args:
            repository: プロジェクトリポジトリ。
            ai_tool_service: AIツールサービス。
        """
        self.repository = repository
        self.ai_tool_service = ai_tool_service

    def create_project(self, name: str, source: str, ai_tool: AIToolID) -> Project | None:
        """プロジェクトを作成する。

        Args:
            name: プロジェクト名。
            source: ソースディレクトリパス。
            ai_tool: AIツールID。

        Returns:
            作成したプロジェクト、失敗した場合はNone。
        """
        if not self._is_valid_input(name, source, ai_tool):
            return None

        try:
            project = Project(name=name, source=source, ai_tool=ai_tool)
            self.repository.save(project)
            result = project
        except Exception as e:
            logger.error(f'[ERROR] プロジェクト作成エラー: {e}')
            result = None

        return result

    def get_all_projects(self) -> list[Project]:
        """全プロジェクトを取得する。

        Returns:
            プロジェクトのリスト。
        """
        return self.repository.find_all()

    def execute_project(self, project_id: ProjectID) -> tuple[Project | None, str]:
        """プロジェクトを実行する。

        Args:
            project_id: プロジェクトID。

        Returns:
            (更新されたプロジェクト, メッセージ)
        """
        logger.debug(f'[DEBUG] execute_project開始: project_id={project_id}')
        project: Project | None = None

        try:
            project, ai_tool = self._prepare_execution(project_id)
            self._execute_ai_tool(project, ai_tool)
            self._complete_project(project)
            return project, 'プロジェクトの実行が完了しました'
        except Exception as e:
            return self._handle_execution_error(project, e)

    def _prepare_execution(self, project_id: ProjectID) -> tuple[Project, AITool]:
        """プロジェクト実行の準備を行う。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, AIツール)

        Raises:
            ValueError: 無効なプロジェクトID。
            ResourceNotFoundError: プロジェクトまたはAIツールが見つからない。
        """
        project = self.repository.find_by_id(project_id)
        ai_tool = self.ai_tool_service.get_ai_tool_by_id(project.ai_tool)
        return project, ai_tool

    def _execute_ai_tool(self, project: Project, ai_tool: AITool) -> None:
        """AIツールを実行します。

        Args:
            project: プロジェクト。
            ai_tool: AIツール。
        """
        project.start_processing()
        executor = CommandExecutor(ai_tool.id, ai_tool.command)
        executor.execute(str(project.id), project.source)

    def _complete_project(self, project: Project) -> None:
        """プロジェクトを完了状態にします。

        Args:
            project: プロジェクト。
        """
        project.complete({'message': 'プロジェクトの実行が完了しました。'})
        self.repository.save(project)

    def _handle_execution_error(
        self, project: Project | None, error: Exception
    ) -> tuple[None, str]:
        """実行エラーを処理する。

        Args:
            project: プロジェクト(存在する場合)。
            error: 発生したエラー。

        Returns:
            (None, エラーメッセージ)
        """
        if isinstance(error, ValueError):
            message = '無効なプロジェクトIDです'
        elif isinstance(
            error, ResourceNotFoundError | CommandExecutionError | CommandSecurityError
        ):
            message = str(error)
        else:
            message = '予期しないエラーが発生しました'

        logger.error(f'[ERROR] {message}')

        if project and not isinstance(error, ValueError | ResourceNotFoundError):
            project.fail({'error': str(error)})
            self.repository.save(project)

        return None, message

    def _is_valid_input(self, name: str, source: str, ai_tool: AIToolID) -> bool:
        """入力値の妥当性チェック。"""
        return (
            bool(name and name.strip()) and bool(source and source.strip()) and ai_tool is not None
        )
