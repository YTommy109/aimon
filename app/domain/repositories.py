"""リポジトリインターフェースを定義するモジュール。"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from .entities import AITool, Project, ProjectStatus


class ProjectRepository(ABC):
    """プロジェクトリポジトリのインターフェース。"""

    @abstractmethod
    def find_by_id(self, project_id: UUID) -> Project | None:
        """指定されたIDのプロジェクトを取得します。

        Args:
            project_id: 取得するプロジェクトのID。

        Returns:
            プロジェクトオブジェクト。見つからない場合はNone。
        """

    @abstractmethod
    def find_all(self) -> list[Project]:
        """すべてのプロジェクトを取得します。

        Returns:
            プロジェクトのリスト。
        """

    @abstractmethod
    def save(self, project: Project) -> None:
        """プロジェクトを保存します。

        Args:
            project: 保存するプロジェクトオブジェクト。
        """

    @abstractmethod
    def update_status(self, project_id: UUID, status: ProjectStatus) -> None:
        """プロジェクトのステータスを更新します。

        Args:
            project_id: 更新するプロジェクトのID。
            status: 新しいステータス。
        """

    @abstractmethod
    def update_result(self, project_id: UUID, result: dict[str, Any]) -> None:
        """プロジェクトの実行結果を更新します。

        Args:
            project_id: 更新するプロジェクトのID。
            result: 実行結果。
        """


class AIToolRepository(ABC):
    """AIツールリポジトリのインターフェース。"""

    @abstractmethod
    def find_active_tools(self) -> list[AITool]:
        """有効なAIツールの一覧を取得します。

        Returns:
            有効なAIToolオブジェクトのリスト。
        """

    @abstractmethod
    def find_all_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得します。

        Returns:
            全てのAIToolオブジェクトのリスト(無効化されたものも含む)。
        """

    @abstractmethod
    def find_by_id(self, tool_id: str) -> AITool | None:
        """指定されたIDのAIツールを取得します。

        Args:
            tool_id: 取得するツールのID。

        Returns:
            AIToolオブジェクト。見つからない場合はNone。
        """

    @abstractmethod
    def save(self, ai_tool: AITool) -> None:
        """AIツールを保存します。

        Args:
            ai_tool: 保存するAIToolオブジェクト。
        """

    @abstractmethod
    def disable(self, tool_id: str) -> None:
        """AIツールを無効化します。

        Args:
            tool_id: 無効化するツールのID。
        """

    @abstractmethod
    def enable(self, tool_id: str) -> None:
        """AIツールを有効化します。

        Args:
            tool_id: 有効化するツールのID。
        """
