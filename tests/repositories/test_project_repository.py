"""JsonProjectRepositoryのテスト。"""

from pathlib import Path
from uuid import UUID

import pytest

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository


class TestJsonProjectRepository:
    """JsonProjectRepositoryのテストクラス。"""

    def test_プロジェクトが正常に保存される(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """プロジェクトが正常に保存されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')

        # Act
        project_repository.save(project)
        saved_projects = project_repository.find_all()

        # Assert
        assert len(saved_projects) == 1
        assert saved_projects[0].name == project.name

    def test_プロジェクトが正常に取得される(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """プロジェクトが正常に取得されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        project_repository.save(project)

        # Act
        found_project = project_repository.find_by_id(project.id)

        # Assert
        assert found_project is not None
        assert found_project.name == project.name

    def test_存在しないプロジェクトは例外を投げる(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """存在しないプロジェクトは例外を投げることをテストする。"""
        # Arrange
        non_existent_id = UUID('12345678-1234-1234-1234-123456789012')

        # Act & Assert
        with pytest.raises(ResourceNotFoundError) as exc_info:
            project_repository.find_by_id(non_existent_id)
        assert str(non_existent_id) in str(exc_info.value)

    def test_プロジェクトの結果が正常に更新される(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """プロジェクトの結果が正常に更新されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        project_repository.save(project)
        result = {'processed_files': ['file1.txt'], 'message': '完了'}

        # Act
        project.result = result
        project_repository.save(project)

        # Assert
        updated_project = project_repository.find_by_id(project.id)
        assert updated_project is not None
        assert updated_project.result == result

    def test_データディレクトリが存在しない場合に作成される(self, tmp_path: Path) -> None:
        """データディレクトリが存在しない場合に作成されることをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'

        # Act
        JsonProjectRepository(data_dir)

        # Assert
        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_データディレクトリがファイルの場合にディレクトリに変換される(
        self, tmp_path: Path
    ) -> None:
        """データディレクトリがファイルの場合にディレクトリに変換されることをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'
        data_dir.write_text('old content')

        # Act
        JsonProjectRepository(data_dir)

        # Assert
        assert data_dir.exists()
        assert data_dir.is_dir()
        assert (data_dir / 'projects.json').exists()

    def test_プロジェクトファイルが存在しない場合に作成される(self, tmp_path: Path) -> None:
        """プロジェクトファイルが存在しない場合に作成されることをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'
        data_dir.mkdir()

        # Act
        JsonProjectRepository(data_dir)

        # Assert
        projects_file = data_dir / 'projects.json'
        assert projects_file.exists()
        assert projects_file.read_text() == '[]'

    def test_プロジェクトファイルがディレクトリの場合に例外が発生する(self, tmp_path: Path) -> None:
        """プロジェクトファイルがディレクトリの場合に例外が発生することをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'
        data_dir.mkdir()
        projects_file = data_dir / 'projects.json'
        projects_file.mkdir()

        # Act & Assert
        with pytest.raises(PathIsDirectoryError):
            JsonProjectRepository(data_dir)

    def test_複数のプロジェクトが正常に保存される(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """複数のプロジェクトが正常に保存されることをテストする。"""
        # Arrange
        project1 = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        project2 = Project(name='プロジェクト2', source='/path2', ai_tool='tool2')

        # Act
        project_repository.save(project1)
        project_repository.save(project2)
        saved_projects = project_repository.find_all()

        # Assert
        assert len(saved_projects) == 2
        assert any(p.name == 'プロジェクト1' for p in saved_projects)
        assert any(p.name == 'プロジェクト2' for p in saved_projects)

    def test_既存のプロジェクトが更新される(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """既存のプロジェクトが更新されることをテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        project_repository.save(project)

        # Act
        project.name = '更新されたプロジェクト'
        project_repository.save(project)

        # Assert
        updated_project = project_repository.find_by_id(project.id)
        assert updated_project is not None
        assert updated_project.name == '更新されたプロジェクト'

    def test_空のプロジェクトリストが正常に読み込まれる(
        self, project_repository: JsonProjectRepository
    ) -> None:
        """空のプロジェクトリストが正常に読み込まれることをテストする。"""
        # Act
        projects = project_repository.find_all()

        # Assert
        assert projects == []

    def test_JSONファイルが存在しない場合に空のリストが返される(self, tmp_path: Path) -> None:
        """JSONファイルが存在しない場合に空のリストが返されることをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'
        data_dir.mkdir()

        # Act
        repository = JsonProjectRepository(data_dir)
        # projects.jsonファイルを削除
        (data_dir / 'projects.json').unlink()
        projects = repository.find_all()

        # Assert
        assert projects == []

    def test_書き込み先がディレクトリの場合に例外が発生する(self, tmp_path: Path) -> None:
        """書き込み先がディレクトリの場合に例外が発生することをテストする。"""
        # Arrange
        data_dir = tmp_path / 'data'
        data_dir.mkdir()
        projects_file = data_dir / 'projects.json'
        projects_file.mkdir()  # ディレクトリとして作成

        # Act & Assert
        with pytest.raises(PathIsDirectoryError):
            JsonProjectRepository(data_dir)
