"""JSONファイルベースのリポジトリ実装。"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from app.domain.entities import JST, AITool, Project, ProjectStatus
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.errors import PathIsDirectoryError, ResourceNotFoundError

logger = logging.getLogger('aiman')


class JsonProjectRepository(ProjectRepository):
    """JSONファイルベースのプロジェクトリポジトリ。"""

    def __init__(self, data_dir: Path) -> None:
        """リポジトリを初期化します。

        Args:
            data_dir: データファイルを保存するディレクトリのパス。
        """
        self.data_dir = data_dir
        self.projects_path = data_dir / 'projects.json'
        self._ensure_data_dir_exists()
        self._ensure_projects_file_exists()

    def find_by_id(self, project_id: UUID) -> Project:
        """指定されたIDのプロジェクトを取得します。"""
        projects = self.find_all()
        for project in projects:
            if project.id == project_id:
                return project
        raise ResourceNotFoundError('Project', project_id)

    def find_all(self) -> list[Project]:
        """すべてのプロジェクトを取得します。"""
        projects_data = self._read_json(self.projects_path)
        return [Project.model_validate(p) for p in projects_data]

    def save(self, project: Project) -> None:
        """プロジェクトを保存します。"""
        projects = self.find_all()
        for i, p in enumerate(projects):
            if p.id == project.id:
                projects[i] = project
                break
        else:
            projects.append(project)
        self._save_projects(projects)

    def update_status(self, project_id: UUID, status: ProjectStatus) -> None:
        """プロジェクトのステータスを更新します。"""
        project = self.find_by_id(project_id)

        match status:
            case ProjectStatus.PROCESSING:
                project.start_processing()
            case ProjectStatus.COMPLETED:
                project.complete({})  # 空の結果で完了
            case ProjectStatus.FAILED:
                project.fail({'error': 'Unknown error'})  # デフォルトのエラー情報

        self.save(project)

    def update_result(self, project_id: UUID, result: dict[str, Any]) -> None:
        """プロジェクトの実行結果を更新します。"""
        project = self.find_by_id(project_id)
        project.complete(result)  # 結果を設定して完了状態に
        self.save(project)

    def _ensure_data_dir_exists(self) -> None:
        """データディレクトリの存在を確認し、必要に応じて作成します。"""
        # data_dirがファイルとして存在する場合は、一時的にリネームしてディレクトリを作成
        if self.data_dir.is_file():
            temp_file = self.data_dir.with_suffix('.tmp')
            shutil.move(self.data_dir, temp_file)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            # 元のファイルをprojects.jsonとして移動
            shutil.move(temp_file, self.data_dir / 'projects.json')
        else:
            self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_projects_file_exists(self) -> None:
        """プロジェクトファイルの存在を確認し、必要に応じて作成します。"""
        # projects.jsonがディレクトリとして存在する場合はエラー
        if self.projects_path.exists() and self.projects_path.is_dir():
            raise PathIsDirectoryError(str(self.projects_path))

        # プロジェクトファイルが存在しない場合は空のリストで初期化
        if not self.projects_path.exists():
            self._write_json(self.projects_path, [])

    def _save_projects(self, projects: list[Project]) -> None:
        """プロジェクトのリストを保存します。"""
        projects_data = [p.model_dump(mode='json') for p in projects]
        self._write_json(self.projects_path, projects_data)

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
            raise PathIsDirectoryError(str(path))

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)


class JsonAIToolRepository(AIToolRepository):
    """JSONファイルベースのAIツールリポジトリ。"""

    def __init__(self, data_dir: Path) -> None:
        """リポジトリを初期化します。

        Args:
            data_dir: データファイルを保存するディレクトリのパス。
        """
        self.data_dir = data_dir
        self.ai_tools_path = data_dir / 'ai_tools.json'
        self._ensure_data_dir_exists()
        self._ensure_ai_tools_file_exists()

    def find_active_tools(self) -> list[AITool]:
        """有効なAIツールの一覧を取得します。"""
        tools_data = self._read_json(self.ai_tools_path)
        return [AITool.model_validate(t) for t in tools_data if t.get('disabled_at') is None]

    def find_all_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得します。"""
        tools_data = self._read_json(self.ai_tools_path)
        return [AITool.model_validate(t) for t in tools_data]

    def find_by_id(self, tool_id: str) -> AITool:
        """指定されたIDのAIツールを取得します。"""
        tools = self.find_all_tools()
        for tool in tools:
            if tool.id == tool_id:
                return tool
        raise ResourceNotFoundError('AI Tool', tool_id)

    def save(self, ai_tool: AITool) -> None:
        """AIツールを保存します。"""
        tools = self.find_all_tools()
        for i, tool in enumerate(tools):
            if tool.id == ai_tool.id:
                tools[i] = ai_tool
                break
        else:
            tools.append(ai_tool)
        self._write_json(self.ai_tools_path, [t.model_dump(mode='json') for t in tools])

    def disable(self, tool_id: str) -> None:
        """AIツールを無効化します。"""
        tool = self.find_by_id(tool_id)
        tool.disabled_at = datetime.now(JST)
        tool.updated_at = datetime.now(JST)
        self.save(tool)

    def enable(self, tool_id: str) -> None:
        """AIツールを有効化します。"""
        tool = self.find_by_id(tool_id)
        tool.disabled_at = None
        tool.updated_at = datetime.now(JST)
        self.save(tool)

    def _ensure_data_dir_exists(self) -> None:
        """データディレクトリの存在を確認し、必要に応じて作成します。"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_ai_tools_file_exists(self) -> None:
        """AIツールファイルの存在を確認し、必要に応じて作成します。"""
        if not self.ai_tools_path.exists():
            self._write_json(self.ai_tools_path, [])

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
            raise PathIsDirectoryError(str(path))

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
