"""store.pyのユニットテスト。"""

import json
from pathlib import Path
from uuid import UUID

import pytest

from app.model.entities import ProjectStatus
from app.model.store import DataManager, ProjectNotFoundError


class TestDataManager:
    """DataManagerのテストクラス。"""

    def test_init_ディレクトリが存在しない場合に作成される(self, tmp_path: Path) -> None:
        # Arrange
        data_dir = tmp_path / 'test_data'

        # Act
        DataManager(data_dir)

        # Assert
        assert data_dir.is_dir()

    def test_init_projects_jsonが存在しない場合に作成される(self, tmp_path: Path) -> None:
        # Arrange
        data_dir = tmp_path
        projects_file = data_dir / 'projects.json'

        # Act
        DataManager(data_dir)

        # Assert
        assert projects_file.is_file()
        with open(projects_file) as f:
            assert json.load(f) == []

    def test_init_data_dirがファイルの場合にディレクトリに変換される(self, tmp_path: Path) -> None:
        # Arrange
        data_dir_as_file = tmp_path / 'test_data'
        data_dir_as_file.touch()

        # Act
        dm = DataManager(data_dir_as_file)

        # Assert
        assert dm.data_dir.is_dir()
        assert dm.data_dir.name == 'test_data'
        assert (dm.data_dir / 'projects.json').exists()

    def test_create_project_プロジェクトが作成され保存される(self, tmp_path: Path) -> None:
        # Arrange
        dm = DataManager(tmp_path)

        # Act
        project = dm.create_project('Test Project', '/dev/null', 'test-tool')

        # Assert
        projects = dm.get_projects()
        assert len(projects) == 1
        assert projects[0].id == project.id

    def test_get_project_指定IDのプロジェクトを取得できる(self, tmp_path: Path) -> None:
        # Arrange
        dm = DataManager(tmp_path)
        project = dm.create_project('Find Me', '/path', 'tool')

        # Act
        found_project = dm.get_project(project.id)

        # Assert
        assert found_project is not None
        assert found_project.id == project.id

    def test_get_ai_tools_利用可能なツールのみ取得する(self, tmp_path: Path) -> None:
        # Arrange
        tools_data = [
            {'id': 'tool1', 'name_ja': 'ツール1', 'description': '説明1'},
            {
                'id': 'tool2',
                'name_ja': 'ツール2',
                'description': '説明2',
                'disabled_at': '2023-01-01',
            },
        ]
        tools_file = tmp_path / 'ai_tools.json'
        with open(tools_file, 'w', encoding='utf-8') as f:
            json.dump(tools_data, f)
        dm = DataManager(tmp_path)

        # Act
        ai_tools = dm.get_ai_tools()

        # Assert
        assert len(ai_tools) == 1
        assert ai_tools[0].id == 'tool1'

    def test_update_project_status_ステータスを更新できる(self, tmp_path: Path) -> None:
        # Arrange
        dm = DataManager(tmp_path)
        project = dm.create_project('Status Update Test', '/path', 'tool')
        assert project.executed_at is None

        # Act & Assert (Processing)
        dm.update_project_status(project.id, ProjectStatus.PROCESSING)
        updated = dm.get_project(project.id)
        assert updated is not None
        assert updated.executed_at is not None

        # Act & Assert (Completed)
        dm.update_project_status(project.id, ProjectStatus.COMPLETED)
        updated = dm.get_project(project.id)
        assert updated is not None
        assert updated.finished_at is not None

    def test_update_project_result_結果を更新できる(self, tmp_path: Path) -> None:
        # Arrange
        dm = DataManager(tmp_path)
        project = dm.create_project('Result Update Test', '/path', 'tool')
        result_data = {'summary': 'This is a test summary.'}

        # Act
        dm.update_project_result(project.id, result_data)

        # Assert
        updated_project = dm.get_project(project.id)
        assert updated_project is not None
        assert updated_project.result == result_data
        assert updated_project.finished_at is not None

    def test_update_project_存在しない場合にエラーを送出する(self, tmp_path: Path) -> None:
        # Arrange
        dm = DataManager(tmp_path)
        non_existent_id = UUID('00000000-0000-0000-0000-000000000000')

        # Act & Assert
        with pytest.raises(ProjectNotFoundError):
            dm.update_project_status(non_existent_id, ProjectStatus.COMPLETED)
