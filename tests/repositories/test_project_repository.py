"""プロジェクトリポジトリのテスト。"""

import json
import os
import stat
import tempfile
from pathlib import Path
from uuid import UUID

import pytest

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models import AIToolID, ProjectID
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository


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
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

    def test_プロジェクト一覧を取得できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        """プロジェクト一覧を取得できることをテスト。"""
        # Arrange
        repository.save(sample_project)

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 1
        assert projects[0].id == sample_project.id
        assert projects[0].name == sample_project.name
        assert projects[0].source == sample_project.source
        assert projects[0].ai_tool == sample_project.ai_tool

    def test_IDでプロジェクトを取得できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        """IDでプロジェクトを取得できることをテスト。"""
        # Arrange
        repository.save(sample_project)

        # Act
        found_project = repository.find_by_id(sample_project.id)

        # Assert
        assert found_project.id == sample_project.id
        assert found_project.name == sample_project.name
        assert found_project.source == sample_project.source
        assert found_project.ai_tool == sample_project.ai_tool

    def test_存在しないIDでプロジェクトを取得するとResourceNotFoundErrorが発生する(
        self, repository: JsonProjectRepository
    ) -> None:
        """存在しないIDでプロジェクトを取得するとResourceNotFoundErrorが発生することをテスト。"""
        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            repository.find_by_id(ProjectID(UUID('12345678-1234-5678-1234-567812345678')))

    def test_プロジェクトを保存できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        """プロジェクトを保存できることをテスト。"""
        # Act
        repository.save(sample_project)

        # Assert
        projects = repository.find_all()
        assert len(projects) == 1
        assert projects[0].id == sample_project.id

    def test_複数のプロジェクトを保存できる(self, repository: JsonProjectRepository) -> None:
        """複数のプロジェクトを保存できることをテスト。"""
        # Arrange
        project1 = Project(
            name='プロジェクト1',
            source='/path1',
            ai_tool=AIToolID(UUID('11111111-1111-1111-1111-111111111111')),
        )
        project2 = Project(
            name='プロジェクト2',
            source='/path2',
            ai_tool=AIToolID(UUID('22222222-2222-2222-2222-222222222222')),
        )

        # Act
        repository.save(project1)
        repository.save(project2)

        # Assert
        projects = repository.find_all()
        assert len(projects) == 2
        project_ids = [project.id for project in projects]
        assert project1.id in project_ids
        assert project2.id in project_ids

    def test_プロジェクトを更新できる(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        """プロジェクトを更新できることをテスト。"""
        # Arrange
        repository.save(sample_project)

        # Act
        sample_project.name = '更新されたプロジェクト名'
        sample_project.source = '/updated/path'
        repository.save(sample_project)

        # Assert
        updated_project = repository.find_by_id(sample_project.id)
        assert updated_project.name == '更新されたプロジェクト名'
        assert updated_project.source == '/updated/path'

    def test_空のファイルから開始できる(self, repository: JsonProjectRepository) -> None:
        """空のファイルから開始できることをテスト。"""
        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 0

    def test_JSONファイルが正しく作成される(
        self, repository: JsonProjectRepository, sample_project: Project
    ) -> None:
        """JSONファイルが正しく作成されることをテスト。"""
        # Act
        repository.save(sample_project)

        # Assert
        json_file = repository.projects_path
        assert json_file.exists()

        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['name'] == sample_project.name
            assert data[0]['source'] == sample_project.source
            assert data[0]['ai_tool'] == str(sample_project.ai_tool)

    def test_JSONファイル読み込みエラー時に空リストを返す(
        self, repository: JsonProjectRepository, temp_dir: Path
    ) -> None:
        """JSONファイル読み込みエラー時に空リストを返すことをテスト。"""
        # Arrange
        invalid_json_file = temp_dir / 'projects.json'
        invalid_json_file.write_text('invalid json content')

        # Act
        projects = repository.find_all()

        # Assert
        assert len(projects) == 0

    def test_保存時にエラーが発生しても例外を再送出する(
        self, repository: JsonProjectRepository, sample_project: Project, temp_dir: Path
    ) -> None:
        """保存時にエラーが発生しても例外を再送出することをテスト。"""
        # Arrange
        # 読み取り専用ディレクトリを作成して書き込みエラーを発生させる
        read_only_dir = temp_dir / 'readonly'
        read_only_dir.mkdir()
        os.chmod(read_only_dir, stat.S_IREAD)

        repository.projects_path = read_only_dir / 'projects.json'

        # Act & Assert
        with pytest.raises(OSError, match='Permission denied'):
            repository.save(sample_project)

    def test_データディレクトリがファイルとして存在する場合にファイル移動処理が実行される(
        self, temp_dir: Path
    ) -> None:
        """データディレクトリがファイルとして存在する場合にファイル移動処理が実行されることをテスト。"""
        # Arrange
        file_path = temp_dir / 'data_dir'
        file_path.write_text('test content')

        # Act
        JsonProjectRepository(file_path)

        # Assert
        assert file_path.is_dir()
        assert (file_path / 'projects.json').exists()

    def test_プロジェクトファイルがディレクトリとして存在する場合にPathIsDirectoryErrorが発生する(
        self, temp_dir: Path
    ) -> None:
        """プロジェクトファイルがディレクトリとして存在する場合にPathIsDirectoryErrorが発生することをテスト。"""
        # Arrange
        projects_dir = temp_dir / 'projects.json'
        projects_dir.mkdir()

        # Act & Assert
        with pytest.raises(PathIsDirectoryError):
            JsonProjectRepository(temp_dir)
