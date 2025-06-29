"""DataManagerのテスト。"""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.model import DataManager, ProjectNotFoundError, ProjectStatus


@pytest.fixture
def data_manager(tmp_path: Path) -> DataManager:
    """テスト用のDataManagerインスタンスを作成する"""
    data_dir = tmp_path / '.data'
    data_dir.mkdir()
    # ai_tools.jsonも作成しておく
    (data_dir / 'ai_tools.json').touch()
    return DataManager(data_dir)


def test_データファイルが空でも正しく初期化される(data_manager: DataManager) -> None:
    # Act
    projects = data_manager.get_projects()
    # Assert
    assert projects == []


def test_プロジェクトファイルが正しいパスにあることを確認する(data_manager: DataManager) -> None:
    """プロジェクトファイルが正しいパスに保存されているか確認するテスト"""
    projects_path = data_manager.data_dir / 'projects.json'
    ai_tools_path = data_manager.data_dir / 'ai_tools.json'

    assert projects_path.is_file(), f'{projects_path} should be a file.'
    assert ai_tools_path.is_file(), f'{ai_tools_path} should be a file.'

    # Check that there's no directory with the same name
    assert not projects_path.is_dir(), f'{projects_path} should not be a directory.'
    assert not ai_tools_path.is_dir(), f'{ai_tools_path} should not be a directory.'


def test_プロジェクトを正しく作成して取得できる(data_manager: DataManager) -> None:
    # Arrange
    name = 'Test Project'
    source = '/path/to/source'
    ai_tool = 'TestTool'

    # Act
    created_project = data_manager.create_project(name, source, ai_tool)
    retrieved_project = data_manager.get_project(created_project.id)

    # Assert
    assert retrieved_project is not None
    assert retrieved_project.name == name
    assert retrieved_project.source == source
    assert retrieved_project.ai_tool == ai_tool
    assert retrieved_project.status == ProjectStatus.PENDING

    all_projects = data_manager.get_projects()
    assert len(all_projects) == 1
    assert all_projects[0].id == created_project.id


def test_プロジェクトのステータスと結果を更新できる(data_manager: DataManager) -> None:
    # Arrange
    project = data_manager.create_project('Update Test', '/src', 'ToolX')

    # Act: ステータスを更新
    data_manager.update_project_status(project.id, ProjectStatus.PROCESSING)
    updated_project_1 = data_manager.get_project(project.id)

    # Assert: ステータスが更新されたことを確認
    assert updated_project_1 is not None
    assert updated_project_1.status == ProjectStatus.PROCESSING

    # Act: 結果を更新
    result_data = {'summary': 'This is a test.'}
    data_manager.update_project_result(project.id, result_data)
    updated_project_2 = data_manager.get_project(project.id)

    # Assert: 結果が更新されたことを確認
    assert updated_project_2 is not None
    assert updated_project_2.result == result_data


def test_AIツールの一覧を正しく取得できる(data_manager: DataManager) -> None:
    # Arrange
    ai_tools_data = [
        {'id': 'tool1', 'name_ja': 'ツール1', 'description': '説明1'},
        {'id': 'tool2', 'name_ja': 'ツール2', 'description': '説明2'},
    ]
    with open(data_manager.ai_tools_path, 'w', encoding='utf-8') as f:
        json.dump(ai_tools_data, f)

    # Act
    ai_tools = data_manager.get_ai_tools()

    # Assert
    assert len(ai_tools) == 2
    assert ai_tools[0].id == 'tool1'
    assert ai_tools[1].name_ja == 'ツール2'


def test_存在しないプロジェクトの更新でProjectNotFoundErrorが発生する(
    data_manager: DataManager,
) -> None:
    # Arrange
    non_existent_id = uuid4()

    # Act & Assert
    with pytest.raises(ProjectNotFoundError):
        data_manager.update_project_status(non_existent_id, ProjectStatus.PROCESSING)

    with pytest.raises(ProjectNotFoundError):
        data_manager.update_project_result(non_existent_id, {'result': 'test'})


def test_projects_jsonがディレクトリとして存在する場合にエラーが発生する(
    tmp_path: Path,
) -> None:
    """projects.jsonがディレクトリとして存在する場合にエラーが発生することをテストする"""
    data_dir = tmp_path / '.data'
    projects_dir = data_dir / 'projects.json'
    projects_dir.mkdir(parents=True)

    with pytest.raises(ValueError, match='projects.jsonがディレクトリとして存在します'):
        DataManager(data_dir)


def test_data_dirがファイルとして存在する場合に適切に処理される(
    tmp_path: Path,
) -> None:
    """data_dirがファイルとして存在する場合にディレクトリに変換されることをテストする"""
    data_file = tmp_path / '.data'
    data_file.write_text('[]')  # 空のプロジェクトリスト

    data_manager = DataManager(data_file)

    assert data_file.is_dir()  # ファイルがディレクトリに変換された
    assert (data_file / 'projects.json').exists()  # 元のデータが移動された
    assert (data_file / 'ai_tools.json').exists()  # ai_tools.jsonが作成された

    projects = data_manager.get_projects()
    assert len(projects) == 0  # 空のリストで初期化された


def test_write_json_でディレクトリが存在する場合にエラーが発生する(
    data_manager: DataManager,
) -> None:
    """_write_jsonでターゲットがディレクトリの場合にエラーが発生することをテストする"""
    # Arrange: ターゲットパスにディレクトリを作成
    test_dir = data_manager.data_dir / 'test_file.json'
    test_dir.mkdir()

    # Act & Assert
    with pytest.raises(ValueError, match='がディレクトリとして存在します'):
        data_manager._write_json(test_dir, [])
