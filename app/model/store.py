"""データの永続化と取得を担当するモジュール。"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from app.errors import ProjectNotFoundError
from app.model.entities import JST, AITool, Project, ProjectStatus

# 明示的にエクスポート
__all__ = ['DataManager', 'ProjectNotFoundError']

logger = logging.getLogger('aiman')


class DataManager:
    """プロジェクトやAIツールのデータを管理するクラス。"""

    def __init__(self, data_dir: str | Path) -> None:
        """インスタンスを初期化します。

        Args:
            data_dir: データファイルを保存するディレクトリのパス。
        """
        self.data_dir = Path(data_dir)

        # data_dirがファイルとして存在する場合は、一時的にリネームしてディレクトリを作成
        if self.data_dir.is_file():
            temp_file = self.data_dir.with_suffix('.tmp')
            shutil.move(self.data_dir, temp_file)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            # 元のファイルをprojects.jsonとして移動
            shutil.move(temp_file, self.data_dir / 'projects.json')
        else:
            self.data_dir.mkdir(parents=True, exist_ok=True)

        self.projects_path = self.data_dir / 'projects.json'
        self.ai_tools_path = self.data_dir / 'ai_tools.json'

        # projects.jsonがディレクトリとして存在する場合はエラー
        if self.projects_path.exists() and self.projects_path.is_dir():
            raise ValueError(
                'projects.jsonがディレクトリとして存在します。ファイルである必要があります。',
            )

        # プロジェクトファイルが存在しない場合は空のリストで初期化
        if not self.projects_path.exists():
            self._write_json(self.projects_path, [])

        # AI toolsファイルが存在しない場合は空のリストで初期化
        if not self.ai_tools_path.exists():
            self._write_json(self.ai_tools_path, [])

    def get_projects(self) -> list[Project]:
        """保存されているすべてのプロジェクトを取得します。"""
        projects_data = self._read_json(self.projects_path)
        return [Project.model_validate(p) for p in projects_data]

    def get_project(self, project_id: UUID) -> Project | None:
        """指定されたIDのプロジェクトを取得します。

        Args:
            project_id: 取得するプロジェクトのID。

        Returns:
            プロジェクトオブジェクト。見つからない場合はNone。
        """
        projects = self.get_projects()
        for project in projects:
            if project.id == project_id:
                return project
        return None

    def create_project(self, name: str, source: str, ai_tool: str) -> Project:
        """新しいプロジェクトを作成します。

        Args:
            name: プロジェクト名。
            source: 処理対象のディレクトリパス。
            ai_tool: 使用するAIツールのID。

        Returns:
            作成されたプロジェクトオブジェクト。
        """
        project = Project(name=name, source=source, ai_tool=ai_tool)
        self._save_project(project)
        return project

    def get_ai_tools(self) -> list[AITool]:
        """利用可能なAIツールの一覧を取得します。

        Returns:
            AIToolオブジェクトのリスト。
        """
        tools_data = self._read_json(self.ai_tools_path)
        return [AITool.model_validate(t) for t in tools_data if t.get('disabled_at') is None]

    def get_all_ai_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得します (無効化されたものも含む)。

        Returns:
            AIToolオブジェクトのリスト。
        """
        tools_data = self._read_json(self.ai_tools_path)
        return [AITool.model_validate(t) for t in tools_data]

    def create_ai_tool(self, tool_id: str, name_ja: str, description: str) -> AITool:
        """新しいAIツールを作成します。

        Args:
            tool_id: ツールのID。
            name_ja: ツールの日本語名。
            description: ツールの説明。

        Returns:
            作成されたAIToolオブジェクト。

        Raises:
            ValueError: 同じIDのツールが既に存在する場合。
        """
        # 既存のツールチェック
        existing_tools = self.get_all_ai_tools()
        if any(tool.id == tool_id for tool in existing_tools):
            raise ValueError(f'ID "{tool_id}" のツールは既に存在します。')

        ai_tool = AITool(id=tool_id, name_ja=name_ja, description=description)
        self._save_ai_tool(ai_tool)
        return ai_tool

    def update_ai_tool(
        self, tool_id: str, name_ja: str | None = None, description: str | None = None
    ) -> AITool:
        """既存のAIツールを更新します。

        Args:
            tool_id: 更新するツールのID。
            name_ja: 新しいツール名 (Noneの場合は更新しない)。
            description: 新しい説明 (Noneの場合は更新しない)。

        Returns:
            更新されたAIToolオブジェクト。

        Raises:
            ValueError: 指定されたIDのツールが存在しない場合。
        """
        target_tool = self._find_ai_tool(tool_id)

        # 更新処理
        if name_ja is not None:
            target_tool.name_ja = name_ja
        if description is not None:
            target_tool.description = description
        target_tool.updated_at = datetime.now(JST)

        self._save_ai_tool(target_tool)
        return target_tool

    def disable_ai_tool(self, tool_id: str) -> AITool:
        """AIツールを無効化します (論理削除)。

        Args:
            tool_id: 無効化するツールのID。

        Returns:
            無効化されたAIToolオブジェクト。

        Raises:
            ValueError: 指定されたIDのツールが存在しない場合。
        """
        target_tool = self._find_ai_tool(tool_id)
        target_tool.disabled_at = datetime.now(JST)
        target_tool.updated_at = datetime.now(JST)
        self._save_ai_tool(target_tool)
        return target_tool

    def enable_ai_tool(self, tool_id: str) -> AITool:
        """AIツールを有効化します。

        Args:
            tool_id: 有効化するツールのID。

        Returns:
            有効化されたAIToolオブジェクト。

        Raises:
            ValueError: 指定されたIDのツールが存在しない場合。
        """
        target_tool = self._find_ai_tool(tool_id)
        target_tool.disabled_at = None
        target_tool.updated_at = datetime.now(JST)
        self._save_ai_tool(target_tool)
        return target_tool

    def _find_ai_tool(self, tool_id: str) -> AITool:
        """指定されたIDのAIツールを見つけます。

        Args:
            tool_id: 検索するツールのID。

        Returns:
            見つかったAIToolオブジェクト。

        Raises:
            ValueError: 指定されたIDのツールが存在しない場合。
        """
        tools = self.get_all_ai_tools()
        for tool in tools:
            if tool.id == tool_id:
                return tool
        raise ValueError(f'ID "{tool_id}" のツールが見つかりません。')

    def update_project_status(self, project_id: UUID, status: ProjectStatus) -> None:
        """指定されたプロジェクトのステータスを更新します。"""
        project = self.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        if status == ProjectStatus.PROCESSING:
            project.start_processing()
        elif status == ProjectStatus.COMPLETED:
            project.complete({})  # 空の結果で完了
        elif status == ProjectStatus.FAILED:
            project.fail({'error': 'Unknown error'})  # デフォルトのエラー情報

        self._save_project(project)

    def update_project_result(self, project_id: UUID, result: dict[str, Any]) -> None:
        """指定されたプロジェクトの実行結果を更新します。"""
        project = self.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        project.complete(result)  # 結果を設定して完了状態に
        self._save_project(project)

    def _save_projects(self, projects: list[Project]) -> None:
        """プロジェクトのリストを保存します。"""
        projects_data = [p.model_dump(mode='json') for p in projects]
        self._write_json(self.projects_path, projects_data)

    def _save_project(self, project: Project) -> None:
        """単一のプロジェクトを保存します。"""
        projects = self.get_projects()
        for i, p in enumerate(projects):
            if p.id == project.id:
                projects[i] = project
                break
        else:
            projects.append(project)
        self._save_projects(projects)

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """JSONファイルを読み込みます。"""
        if not path.exists():
            return []
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            return cast(list[dict[str, Any]], data)

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """JSONファイルに書き込みます。"""
        # ターゲットがディレクトリの場合はエラー
        if path.exists() and path.is_dir():
            raise ValueError(
                f'{path}がディレクトリとして存在します。ファイルである必要があります。',
            )

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def _save_ai_tool(self, ai_tool: AITool) -> None:
        """単一のAIツールを保存します。"""
        tools = self.get_all_ai_tools()
        for i, tool in enumerate(tools):
            if tool.id == ai_tool.id:
                tools[i] = ai_tool
                break
        else:
            tools.append(ai_tool)
        self._write_json(self.ai_tools_path, [t.model_dump(mode='json') for t in tools])
