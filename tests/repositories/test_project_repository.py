"""プロジェクトリポジトリのテスト。"""

import json
import os
import stat
import tempfile
from pathlib import Path
from uuid import UUID

import pytest

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.types import ProjectID, ToolType


class TestJsonProjectRepository:
    """JsonProjectRepositoryのテストクラス。"""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """一時ディレクトリを作成する。"""
        return Path(tempfile.mkdtemp())

    @pytest.fixture
    def repository(self, temp_dir: Path) -> JsonProjectRepository:
        """リポジトリを作成する。"""
        return JsonProjectRepository(temp_dir)

    @pytest.fixture
    def sample_project(self) -> Project:
        """サンプルプロジェクトを作成する。"""
        return Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

    def test_プロジェクト一覧を取得できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        # Arrange
        repository.save(sample_project)

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 1
        assert projects[0].id == sample_project.id
        assert projects[0].name == sample_project.name
        assert projects[0].source == sample_project.source
        assert projects[0].tool == sample_project.tool

    def test_IDでプロジェクトを取得できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        # Arrange
        repository.save(sample_project)

        # Act
        found_project = repository.find_by_id(sample_project.id)

        # Assert
        assert found_project.id == sample_project.id
        assert found_project.name == sample_project.name
        assert found_project.source == sample_project.source
        assert found_project.tool == sample_project.tool

    def test_存在しないIDでプロジェクトを取得するとResourceNotFoundErrorが発生する(
        self, repository: JsonProjectRepository
    ) -> None:
        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            repository.find_by_id(ProjectID(UUID('12345678-1234-5678-1234-567812345678')))

    def test_プロジェクトを保存できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        # Act
        repository.save(sample_project)

        # Assert
        projects = repository.find_all()
        assert len(projects) == 1
        assert projects[0].id == sample_project.id

    def test_複数のプロジェクトを保存できる(self, repository: JsonProjectRepository) -> None:
        # Arrange
        project1 = Project(
            name='プロジェクト1',
            source='/path1',
            tool=ToolType.OVERVIEW,
        )
        project2 = Project(
            name='プロジェクト2',
            source='/path2',
            tool=ToolType.REVIEW,
        )

        # Act
        repository.save(project1)
        repository.save(project2)

        # Assert
        projects = repository.find_all()
        assert len(projects) == 2
        project_ids = [p.id for p in projects]
        assert project1.id in project_ids
        assert project2.id in project_ids

    def test_プロジェクトを更新できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        # Arrange
        repository.save(sample_project)
        sample_project.name = '更新されたプロジェクト'

        # Act
        repository.save(sample_project)

        # Assert
        updated_project = repository.find_by_id(sample_project.id)
        assert updated_project.name == '更新されたプロジェクト'

    def test_空のファイルから開始できる(self, repository: JsonProjectRepository) -> None:
        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 0

    def test_JSONファイルが正しく作成される(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        # Act
        repository.save(sample_project)

        # Assert
        projects_file = repository.data_dir / 'projects.json'
        assert projects_file.exists()
        with open(projects_file, encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['name'] == sample_project.name

    def test_JSONファイル読み込みエラー時に空リストを返す(
        self, repository: JsonProjectRepository, temp_dir: Path
    ) -> None:
        # Arrange
        projects_file = temp_dir / 'projects.json'
        with open(projects_file, 'w', encoding='utf-8') as f:
            f.write('invalid json')

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 0

    def test_保存時にエラーが発生しても例外を再送出する(
        self, repository: JsonProjectRepository, sample_project: Project, temp_dir: Path
    ) -> None:
        # Arrange
        projects_file = temp_dir / 'projects.json'
        # ファイルを読み取り専用にして書き込みエラーを発生させる
        os.chmod(projects_file, stat.S_IREAD)

        # Act & Assert
        with pytest.raises(OSError, match='Permission denied'):
            repository.save(sample_project)

    def test_データディレクトリがファイルとして存在する場合にファイル移動処理が実行される(
        self, temp_dir: Path
    ) -> None:
        # Arrange
        data_dir = temp_dir / 'data'
        data_dir.write_text('some content')

        # Act
        JsonProjectRepository(temp_dir)

        # Assert
        assert data_dir.exists()
        assert data_dir.is_file()

    def test_プロジェクトファイルがディレクトリとして存在する場合にPathIsDirectoryErrorが発生する(
        self, temp_dir: Path
    ) -> None:
        # Arrange
        projects_file = temp_dir / 'projects.json'
        projects_file.mkdir()

        # Act & Assert
        with pytest.raises(PathIsDirectoryError):
            JsonProjectRepository(temp_dir)

    def test_内蔵ツール付きプロジェクトを保存できる(
        self, repository: JsonProjectRepository, temp_dir: Path
    ) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # Act
        repository.save(project)

        # Assert
        projects = repository.find_all()
        assert len(projects) == 1
        assert projects[0].tool == ToolType.OVERVIEW

    def test_内蔵ツール付きプロジェクトのシリアライゼーション(
        self, repository: JsonProjectRepository, temp_dir: Path
    ) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.REVIEW,
        )

        # Act
        repository.save(project)

        # Assert - JSONファイルの内容を直接確認
        projects_file = temp_dir / 'projects.json'
        with open(projects_file, encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]['tool'] == 'REVIEW'
        assert 'status' not in data[0]  # statusは除外されることを確認
