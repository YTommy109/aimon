"""データ管理を統合するクラス。"""

from app.application.handlers.ai_tool_handler import AIToolHandler
from app.application.handlers.project_handler import ProjectHandler
from app.domain.entities import AITool, Project


class DataManager:
    """データ管理を統合するクラス。"""

    def __init__(
        self,
        ai_tool_handler: AIToolHandler,
        project_handler: ProjectHandler,
    ) -> None:
        """データマネージャーを初期化します。

        Args:
            ai_tool_handler: AIツールハンドラー。
            project_handler: プロジェクトハンドラー。
        """
        self.ai_tool_handler = ai_tool_handler
        self.project_handler = project_handler

    # AIツール関連

    def get_ai_tools(self) -> list[AITool]:
        """有効なAIツールの一覧を取得。

        Returns:
            有効なAIツールのリスト。
        """
        return self.ai_tool_handler.get_active_ai_tools()

    def get_all_ai_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得(無効化されたものも含む)。

        Returns:
            全てのAIツールのリスト。
        """
        return self.ai_tool_handler.get_all_ai_tools()

    def create_ai_tool(self, tool_id: str, name: str, description: str | None = None) -> bool:
        """AIツール作成処理。

        Args:
            tool_id: ツールID。
            name: ツール名。
            description: 説明(オプション)。

        Returns:
            作成が成功した場合True、失敗した場合False。
        """
        return self.ai_tool_handler.create_ai_tool(tool_id, name, description)

    def update_ai_tool(self, tool_id: str, name: str, description: str | None = None) -> bool:
        """AIツール更新処理。

        Args:
            tool_id: ツールID。
            name: ツール名。
            description: 説明(オプション)。

        Returns:
            更新が成功した場合True、失敗した場合False。
        """
        return self.ai_tool_handler.update_ai_tool(tool_id, name, description)

    def disable_ai_tool(self, tool_id: str) -> bool:
        """AIツール無効化処理。

        Args:
            tool_id: ツールID。

        Returns:
            無効化が成功した場合True、失敗した場合False。
        """
        return self.ai_tool_handler.disable_ai_tool(tool_id)

    def enable_ai_tool(self, tool_id: str) -> bool:
        """AIツール有効化処理。

        Args:
            tool_id: ツールID。

        Returns:
            有効化が成功した場合True、失敗した場合False。
        """
        return self.ai_tool_handler.enable_ai_tool(tool_id)

    # プロジェクト関連

    def get_projects(self) -> list[Project]:
        """全てのプロジェクトを取得。

        Returns:
            プロジェクトのリスト。
        """
        return self.project_handler.get_all_projects()

    def create_project(self, name: str, source: str, ai_tool: str) -> Project | None:
        """プロジェクト作成処理。

        Args:
            name: プロジェクト名。
            source: ソースディレクトリパス。
            ai_tool: AIツールID。

        Returns:
            作成したプロジェクト、失敗した場合はNone。
        """
        return self.project_handler.create_project(name, source, ai_tool)

    def get_project_by_id(self, project_id: str) -> Project | None:
        """IDでプロジェクトを取得。

        Args:
            project_id: プロジェクトID。

        Returns:
            プロジェクト、見つからない場合はNone。
        """
        return self.project_handler.get_project_by_id(project_id)

    def update_project(self, project: Project) -> bool:
        """プロジェクトを更新。

        Args:
            project: 更新するプロジェクト。

        Returns:
            更新が成功した場合True、失敗した場合False。
        """
        return self.project_handler.update_project(project)
