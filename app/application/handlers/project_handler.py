"""プロジェクト管理のハンドラー。"""

from uuid import UUID

from app.domain.entities import Project
from app.domain.repositories import ProjectRepository


class ProjectHandler:
    """プロジェクト管理のハンドラー。"""

    def __init__(self, project_repository: ProjectRepository) -> None:
        """ハンドラーを初期化します.

        Args:
            project_repository: プロジェクトリポジトリ。
        """
        self.project_repository = project_repository

    def create_project(self, name: str, source: str, ai_tool: str) -> Project | None:
        """プロジェクト作成処理。

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
            self.project_repository.save(project)
        except Exception:
            project = None

        return project

    def get_all_projects(self) -> list[Project]:
        """全てのプロジェクトを取得。

        Returns:
            プロジェクトのリスト。
        """
        return self.project_repository.find_all()

    def get_project_by_id(self, project_id: str) -> Project | None:
        """IDでプロジェクトを取得。

        Args:
            project_id: プロジェクトID。

        Returns:
            プロジェクト、見つからない場合はNone。
        """
        try:
            uuid_id = UUID(project_id)
        except (ValueError, Exception):
            return None

        return self.project_repository.find_by_id(uuid_id)

    def update_project(self, project: Project) -> bool:
        """プロジェクトを更新。

        Args:
            project: 更新するプロジェクト。

        Returns:
            更新が成功した場合True、失敗した場合False。
        """
        try:
            self.project_repository.save(project)
            return True
        except Exception:
            return False

    def _is_valid_input(self, name: str, source: str, ai_tool: str) -> bool:
        """入力値の妥当性チェック。"""
        return (
            bool(name and name.strip())
            and bool(source and source.strip())
            and bool(ai_tool and ai_tool.strip())
        )
