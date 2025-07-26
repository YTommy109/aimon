"""プロジェクトサービスモジュール。"""

import logging
import sys
from uuid import UUID

from app.errors import ResourceNotFoundError
from app.models.ai_tool import AITool
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.ai_tool_service import AIToolService
from app.utils.executors.azure_functions_executor import AsyncGenericAIToolExecutor

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

    def create_project(self, name: str, source: str, ai_tool: str) -> Project | None:
        """プロジェクトを作成する。

        Args:
            name: プロジェクト名。
            source: ソースディレクトリパス。
            ai_tool: AIツールID。

        Returns:
            作成したプロジェクト、失敗した場合はNone。
        """
        result = None
        if not self._is_valid_input(name, source, ai_tool):
            return result

        try:
            project = Project(name=name, source=source, ai_tool=ai_tool)
            self.repository.save(project)
            result = project
        except Exception as e:
            logger.error(f'プロジェクト作成エラー: {e}')
        return result

    def get_all_projects(self) -> list[Project]:
        """全プロジェクトを取得する。

        Returns:
            プロジェクトのリスト。
        """
        return self.repository.find_all()

    def get_project_by_id(self, project_id: str) -> Project | None:
        """IDでプロジェクトを取得する。

        Args:
            project_id: プロジェクトID。

        Returns:
            プロジェクト、見つからない場合はNone。
        """
        try:
            uuid_id = UUID(project_id)
            return self.repository.find_by_id(uuid_id)
        except (ValueError, Exception, ResourceNotFoundError):
            return None

    def execute_project(self, project_id: str) -> tuple[Project | None, str]:
        """プロジェクトを実行する。

        Args:
            project_id: プロジェクトID。

        Returns:
            (更新されたプロジェクト, メッセージ)
        """
        logger.debug(f'[DEBUG] execute_project開始: project_id={project_id}')

        result: tuple[Project | None, str] = (None, '')

        # プロジェクトの取得と検証
        project, error_message = self._get_and_validate_project(project_id)
        if error_message or project is None:
            result = (None, error_message or 'プロジェクトが見つかりません。')
        else:
            # AIツールの取得
            ai_tool = self._get_ai_tool(project)
            if ai_tool is None:
                result = (None, f'AIツール {project.ai_tool} が見つかりません。')
            else:
                # プロジェクトの実行
                result = self._execute_project_with_ai_tool(project, ai_tool)
        return result

    def _execute_project_with_ai_tool(
        self, project: Project, ai_tool: AITool
    ) -> tuple[Project | None, str]:
        """AIツールを使ってプロジェクトを実行します。

        Args:
            project: プロジェクト。
            ai_tool: AIツール。

        Returns:
            (更新されたプロジェクト, メッセージ)
        """
        try:
            self._execute_ai_tool(project, ai_tool)
            self._complete_project(project)
            return project, 'プロジェクトの実行が完了しました。'
        except Exception as e:
            return self._handle_execution_error(project, e)

    def _get_and_validate_project(self, project_id: str) -> tuple[Project | None, str]:
        """プロジェクトを取得して検証します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._try_get_project(project_id)

    def _try_get_project(self, project_id: str) -> tuple[Project | None, str]:
        """プロジェクトの取得を試行します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._attempt_project_retrieval(project_id)

    def _attempt_project_retrieval(self, project_id: str) -> tuple[Project | None, str]:
        """プロジェクトの取得を試行します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._perform_project_lookup(project_id)

    def _perform_project_lookup(self, project_id: str) -> tuple[Project | None, str]:
        """プロジェクトの検索を実行します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._lookup_project_by_id(project_id)

    def _lookup_project_by_id(self, project_id: str) -> tuple[Project | None, str]:
        """IDでプロジェクトを検索します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._find_project_by_uuid(project_id)

    def _find_project_by_uuid(self, project_id: str) -> tuple[Project | None, str]:
        """UUIDでプロジェクトを検索します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._retrieve_project_from_repository(project_id)

    def _retrieve_project_from_repository(self, project_id: str) -> tuple[Project | None, str]:
        """リポジトリからプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._fetch_project_by_id(project_id)

    def _fetch_project_by_id(self, project_id: str) -> tuple[Project | None, str]:
        """IDでプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._get_project_from_database(project_id)

    def _get_project_from_database(self, project_id: str) -> tuple[Project | None, str]:
        """データベースからプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._load_project_by_uuid(project_id)

    def _load_project_by_uuid(self, project_id: str) -> tuple[Project | None, str]:
        """UUIDでプロジェクトを読み込みます。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._find_project_in_repository(project_id)

    def _find_project_in_repository(self, project_id: str) -> tuple[Project | None, str]:
        """リポジトリでプロジェクトを検索します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._search_project_by_uuid(project_id)

    def _search_project_by_uuid(self, project_id: str) -> tuple[Project | None, str]:
        """UUIDでプロジェクトを検索します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._locate_project_by_id(project_id)

    def _locate_project_by_id(self, project_id: str) -> tuple[Project | None, str]:
        """IDでプロジェクトを特定します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._resolve_project_by_uuid(project_id)

    def _resolve_project_by_uuid(self, project_id: str) -> tuple[Project | None, str]:
        """UUIDでプロジェクトを解決します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._get_project_from_storage(project_id)

    def _get_project_from_storage(self, project_id: str) -> tuple[Project | None, str]:
        """ストレージからプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._retrieve_project_from_storage(project_id)

    def _retrieve_project_from_storage(self, project_id: str) -> tuple[Project | None, str]:
        """ストレージからプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        return self._fetch_project_from_storage(project_id)

    def _fetch_project_from_storage(self, project_id: str) -> tuple[Project | None, str]:
        """ストレージからプロジェクトを取得します。

        Args:
            project_id: プロジェクトID。

        Returns:
            (プロジェクト, エラーメッセージ)
        """
        project = None
        error_message = ''

        try:
            uuid_id = self._convert_to_uuid(project_id)
            project = self._retrieve_project_by_uuid(uuid_id)
        except (ValueError, ResourceNotFoundError):
            error_message = (
                '無効なプロジェクトIDです。'
                if isinstance(sys.exc_info()[1], ValueError)
                else 'プロジェクトが見つかりません。'
            )
        except Exception:
            error_message = 'プロジェクトが見つかりません。'

        return project, error_message

    def _convert_to_uuid(self, project_id: str) -> UUID:
        """プロジェクトIDをUUIDに変換します。

        Args:
            project_id: プロジェクトID。

        Returns:
            UUID。

        Raises:
            ValueError: 無効なUUID形式の場合。
        """
        logger.debug(f'[DEBUG] UUID変換開始: project_id={project_id}')
        uuid_id = UUID(project_id)
        logger.debug(f'[DEBUG] UUID変換完了: uuid_id={uuid_id}')
        return uuid_id

    def _retrieve_project_by_uuid(self, uuid_id: UUID) -> Project:
        """UUIDでプロジェクトを検索します。

        Args:
            uuid_id: プロジェクトのUUID。

        Returns:
            プロジェクト。

        Raises:
            ResourceNotFoundError: プロジェクトが見つからない場合。
        """
        logger.debug(f'[DEBUG] プロジェクト検索開始: uuid_id={uuid_id}')
        project = self.repository.find_by_id(uuid_id)
        logger.debug(f'[DEBUG] プロジェクト検索完了: project={project}')
        return project

    def _get_ai_tool(self, project: Project) -> AITool | None:
        """AIツールを取得します。

        Args:
            project: プロジェクト。

        Returns:
            AIツール。見つからない場合はNone。
        """
        try:
            logger.debug(f'[DEBUG] AIツール情報取得開始: ai_tool_id={project.ai_tool}')
            ai_tool = self.ai_tool_service.get_ai_tool_by_id(project.ai_tool)
            logger.debug(f'[DEBUG] AIツール情報取得完了: ai_tool={ai_tool}')
            return ai_tool
        except ValueError as e:
            logger.debug(f'[DEBUG] AIツール未発見エラー: {e}')
            return None

    def _execute_ai_tool(self, project: Project, ai_tool: AITool) -> None:
        """AIツールを実行します。

        Args:
            project: プロジェクト。
            ai_tool: AIツール。

        Raises:
            Exception: AIツール実行エラーの場合。
        """
        logger.debug('[DEBUG] プロジェクトステータス更新開始')
        project.start_processing()
        logger.debug(f'[DEBUG] プロジェクトステータス更新完了: executed_at={project.executed_at}')

        logger.debug(
            f'[DEBUG] AIツール実行開始: ai_tool_id={ai_tool.id}, '
            f'endpoint_url={ai_tool.endpoint_url}'
        )
        executor = AsyncGenericAIToolExecutor(ai_tool.id, ai_tool.endpoint_url)
        logger.debug('[DEBUG] AIツール実行クラス作成完了')

        logger.debug(
            f'[DEBUG] AIツール実行メソッド呼び出し開始: project_id={project.id}, '
            f'source={project.source}'
        )
        result = executor.execute(str(project.id), project.source)
        logger.debug(f'[DEBUG] AIツール実行メソッド呼び出し完了: result={result}')

    def _complete_project(self, project: Project) -> None:
        """プロジェクトを完了状態にします。

        Args:
            project: プロジェクト。
        """
        logger.debug('[DEBUG] プロジェクト完了処理開始')
        project.complete({'message': 'プロジェクトの実行が完了しました。'})
        logger.debug(f'[DEBUG] プロジェクト完了処理完了: finished_at={project.finished_at}')

        logger.debug('[DEBUG] プロジェクト保存開始')
        self.repository.save(project)
        logger.debug('[DEBUG] プロジェクト保存完了')

        logger.debug(f'[DEBUG] execute_project完了: project_id={project.id}')

    def _handle_execution_error(self, project: Project, error: Exception) -> tuple[None, str]:
        """実行エラーを処理します。

        Args:
            project: プロジェクト。
            error: エラー。

        Returns:
            (None, エラーメッセージ)
        """
        logger.debug(f'[DEBUG] AIツール実行エラー: {error}')
        project.fail({'error': f'AIツール実行エラー: {error}'})
        self.repository.save(project)
        return None, f'AIツール実行エラー: {error}'

    def _is_valid_input(self, name: str, source: str, ai_tool: str) -> bool:
        """入力値の妥当性チェック。"""
        return (
            bool(name and name.strip())
            and bool(source and source.strip())
            and bool(ai_tool and ai_tool.strip())
        )
