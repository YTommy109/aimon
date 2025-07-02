"""データの永続化と取得を担当するモジュール。"""

import json
import logging
import shutil
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from app.errors import ProjectNotFoundError
from app.model.entities import AITool, Project, ProjectStatus

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
