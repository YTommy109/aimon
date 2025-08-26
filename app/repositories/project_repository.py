"""プロジェクトのデータアクセスを管理するリポジトリ。"""

import json
import logging
import shutil
from pathlib import Path
from typing import Any, cast

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models.project import Project
from app.types import ProjectID

logger = logging.getLogger('aiman')


class JsonProjectRepository:
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

    def find_by_id(self, project_id: ProjectID) -> Project:
        """指定されたIDのプロジェクトを取得します。

        Args:
            project_id: 取得するプロジェクトのID。

        Returns:
            指定されたIDのプロジェクト。

        Raises:
            ResourceNotFoundError: 指定されたIDのプロジェクトが見つからない場合。
        """
        projects = self.find_all()
        project = next((p for p in projects if p.id == project_id), None)
        if project is None:
            raise ResourceNotFoundError('Project', project_id)
        return project

    def find_all(self) -> list[Project]:
        """すべてのプロジェクトを取得します。"""
        projects_data = self._read_json(self.projects_path)
        normalized = [self._normalize_project_data(p) for p in projects_data]
        return [Project.model_validate(p) for p in normalized]

    def _normalize_project_data(self, project_data: dict[str, Any]) -> dict[str, Any]:
        """プロジェクトデータを正規化します。"""
        normalized_project = {}

        # 永続化フォーマットからモデルへ読み戻す際に、未知のキーや計算プロパティを除外する。
        # - `Project.model_fields` に存在するキーのみを採用することで、スキーマ外の値を排除する。
        # - 例: 過去の互換フィールドや計算プロパティ（`status` など）はここで弾かれる。
        for k, v in project_data.items():
            if k in Project.model_fields:
                normalized_project[k] = v

        return normalized_project

    def save(self, project: Project) -> None:
        """プロジェクトを保存します。

        Args:
            project: 保存対象の`Project`インスタンス。
                既存のIDと一致する場合は更新、存在しない場合は追加します。
        """
        projects = self.find_all()
        for i, p in enumerate(projects):
            if p.id == project.id:
                projects[i] = project
                break
        else:
            projects.append(project)
        self._save_projects(projects)

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
        # status を除外して tool のみを保存
        projects_data = [p.model_dump(mode='json', exclude={'status'}) for p in projects]
        self._write_json(self.projects_path, projects_data)

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """JSONファイルを読み込みます。"""
        result = []

        if path.exists():
            try:
                with open(path, encoding='utf-8') as f:
                    data = json.load(f)
                    result = cast(list[dict[str, Any]], data)
            except Exception as e:
                logger.error(f'JSONファイル読み込みエラー: {path}, エラー: {e}')

        return result

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """JSONファイルに書き込みます。"""
        # ターゲットがディレクトリの場合はエラー
        if path.exists() and path.is_dir():
            raise PathIsDirectoryError(str(path))

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
