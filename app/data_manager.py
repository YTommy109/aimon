import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger('aiman')


# --- Custom Exceptions ---


class DataManagerError(Exception):
    """DataManager関連のベース例外クラス。"""

    pass


class ProjectNotFoundError(DataManagerError):
    """指定されたプロジェクトが見つからない場合の例外。"""

    pass


class DataFileError(DataManagerError):
    """データファイルの読み書きに関する例外。"""

    pass


# --- Pydantic Models ---


class AITool(BaseModel):
    id: str
    name_ja: str
    description: str


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid.uuid4)
    name: str
    source: str
    ai_tool: str
    status: str = 'Pending'
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    executed_at: datetime | None = None
    finished_at: datetime | None = None


# --- DataManager Class ---


class DataManager:
    """プロジェクトやAIツールのデータを管理するクラス。"""

    def __init__(self, data_file: Path) -> None:
        """DataManagerを初期化します。

        Args:
            data_file: プロジェクトデータが保存されているJSONファイルのパス。
        """
        self.data_dir = data_file.parent
        self.projects_path = data_file
        self.ai_tools_path = self.data_dir / 'ai_tools.json'
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        """データディレクトリと必要なJSONファイルが存在することを確認し、なければ作成します。"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.projects_path.exists():
            self._write_json(self.projects_path, [])
        if not self.ai_tools_path.exists():
            self._write_json(self.ai_tools_path, [])

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """JSONファイルを読み込み、辞書のリストを返します。

        ファイルが存在しない、空、または不正な形式の場合は空のリストを返します。

        Args:
            path: 読み込むJSONファイルのパス。

        Returns:
            ファイルから読み込んだデータのリスト。

        Raises:
            DataFileError: ファイル読み込み時に予期しないエラーが発生した場合。
        """
        if not path.exists() or path.stat().st_size == 0:
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                logger.warning(f'JSONファイル {path} の形式が不正です（リスト以外）')
                return []  # Not a list, return empty list
        except json.JSONDecodeError as e:
            logger.warning(f'JSONファイル {path} の形式が不正です: {e}')
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            raise DataFileError(
                f'ファイル {path} の読み込み中にエラーが発生しました: {e}'
            ) from e

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """リストをJSONファイルに書き込みます。

        Args:
            path: 書き込むJSONファイルのパス。
            data: 書き込むデータのリスト。
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    # --- AI Tool Methods ---

    def get_ai_tools(self) -> list[AITool]:
        """登録されているすべてのAIツールを取得します。

        Returns:
            AIツールオブジェクトのリスト。
        """
        data = self._read_json(self.ai_tools_path)
        return [AITool(**item) for item in data]

    # --- Project Methods ---

    def get_projects(self) -> list[Project]:
        """すべてのプロジェクトを取得します。

        プロジェクトファイルからデータを読み込み、日付文字列をdatetimeオブジェクトに変換します。

        Returns:
            プロジェクトオブジェクトのリスト。
        """
        data = self._read_json(self.projects_path)
        # 日付文字列をdatetimeオブジェクトに変換
        for item in data:
            for key in ['created_at', 'executed_at', 'finished_at']:
                if item.get(key) and isinstance(item[key], str):
                    # Pydantic v2では'Z'を+00:00に置換する必要がある
                    item[key] = datetime.fromisoformat(item[key].replace('Z', '+00:00'))
        return [Project(**item) for item in data]

    def get_project(self, project_id: UUID) -> Project | None:
        """指定されたIDを持つ単一のプロジェクトを取得します。

        Args:
            project_id: 取得するプロジェクトのID。

        Returns:
            見つかったプロジェクトオブジェクト。見つからない場合はNone。
        """
        projects = self.get_projects()
        for project in projects:
            if project.id == project_id:
                return project
        return None

    def create_project(self, name: str, source: str, ai_tool: str) -> Project:
        """新しいプロジェクトを作成し、永続化します。

        Args:
            name: プロジェクト名。
            source: 処理対象のディレクトリパス。
            ai_tool: 使用するAIツールのID。

        Returns:
            作成されたプロジェクトオブジェクト。
        """
        project = Project(name=name, source=source, ai_tool=ai_tool)

        projects = self.get_projects()
        projects.append(project)
        project_dicts = [p.model_dump(mode='json') for p in projects]
        self._write_json(self.projects_path, project_dicts)
        logger.info(f'Created new project: {project.name}')
        return project

    def update_project_status(self, project_id: UUID, status: str) -> None:
        """指定されたプロジェクトのステータスと日時を更新します。

        ステータスが'Processing'の場合は実行日時を、'Completed'または'Failed'の
        場合は終了日時を現在時刻で記録します。

        Args:
            project_id: 更新するプロジェクトのID。
            status: 設定する新しいステータス。

        Raises:
            ProjectNotFoundError: 指定されたIDのプロジェクトが見つからない場合。
        """
        projects = self.get_projects()
        for i, p in enumerate(projects):
            if p.id == project_id:
                projects[i].status = status
                now = datetime.now()
                if status == 'Processing':
                    projects[i].executed_at = now
                elif status in ['Completed', 'Failed']:
                    projects[i].finished_at = now
                projects_data = [proj.model_dump(mode='json') for proj in projects]
                self._write_json(self.projects_path, projects_data)
                return
        raise ProjectNotFoundError(f'Project with id {project_id} not found')

    def update_project_result(self, project_id: UUID, result: dict[str, Any]) -> None:
        """指定されたプロジェクトの実行結果を更新します。

        Args:
            project_id: 更新するプロジェクトのID。
            result: 保存する実行結果。

        Raises:
            ProjectNotFoundError: 指定されたIDのプロジェクトが見つからない場合。
        """
        projects = self.get_projects()
        for i, p in enumerate(projects):
            if p.id == project_id:
                projects[i].result = result
                projects_data = [proj.model_dump(mode='json') for proj in projects]
                self._write_json(self.projects_path, projects_data)
                return
        raise ProjectNotFoundError(f'Project with id {project_id} not found')
