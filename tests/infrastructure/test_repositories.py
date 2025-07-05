"""インフラストラクチャ層のリポジトリテスト。"""

import tempfile
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest

from app.domain.entities import AITool, Project
from app.errors import ResourceNotFoundError
from app.infrastructure.persistence import JsonAIToolRepository, JsonProjectRepository


class TestJsonProjectRepository:
    """JsonProjectRepositoryのテスト。"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """テスト用の一時ディレクトリを作成します。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def repository(self, temp_dir: Path) -> JsonProjectRepository:
        """テスト用のJsonProjectRepositoryを作成します。"""
        return JsonProjectRepository(temp_dir)

    def test_新しいプロジェクトの保存と取得(self, repository: JsonProjectRepository) -> None:
        """新しいプロジェクトの保存と取得をテストします。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')

        # Act
        repository.save(project)
        retrieved_project = repository.find_by_id(project.id)

        # Assert
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.name == project.name
        assert retrieved_project.source == project.source
        assert retrieved_project.ai_tool == project.ai_tool

    def test_存在しないプロジェクトの取得(self, repository: JsonProjectRepository) -> None:
        """存在しないプロジェクトの取得をテストします。"""
        # Arrange
        non_existent_id = uuid4()

        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            repository.find_by_id(non_existent_id)

    def test_全プロジェクトの取得(self, repository: JsonProjectRepository) -> None:
        """全プロジェクトの取得をテストします。"""
        # Arrange
        project1 = Project(name='プロジェクト1', source='/path1', ai_tool='tool1')
        project2 = Project(name='プロジェクト2', source='/path2', ai_tool='tool2')

        # Act
        repository.save(project1)
        repository.save(project2)
        all_projects = repository.find_all()

        # Assert
        assert len(all_projects) == 2
        project_ids = [p.id for p in all_projects]
        assert project1.id in project_ids
        assert project2.id in project_ids

    def test_プロジェクトの更新(self, repository: JsonProjectRepository) -> None:
        """プロジェクトの更新をテストします。"""
        # Arrange
        project = Project(name='元の名前', source='/path', ai_tool='tool')
        repository.save(project)

        # Act
        project.name = '更新された名前'
        project.start_processing()
        repository.save(project)
        updated_project = repository.find_by_id(project.id)

        # Assert
        assert updated_project is not None
        assert updated_project.name == '更新された名前'
        assert updated_project.executed_at is not None


class TestJsonAIToolRepository:
    """JsonAIToolRepositoryのテスト。"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """テスト用の一時ディレクトリを作成します。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def repository(self, temp_dir: Path) -> JsonAIToolRepository:
        """テスト用のJsonAIToolRepositoryを作成します。"""
        return JsonAIToolRepository(temp_dir)

    def test_新しいAIツールの保存と取得(self, repository: JsonAIToolRepository) -> None:
        """新しいAIツールの保存と取得をテストします。"""
        # Arrange
        ai_tool = AITool(id='test-tool', name_ja='テストツール', description='テスト用')

        # Act
        repository.save(ai_tool)
        retrieved_tool = repository.find_by_id('test-tool')

        # Assert
        assert retrieved_tool is not None
        assert retrieved_tool.id == 'test-tool'
        assert retrieved_tool.name_ja == 'テストツール'
        assert retrieved_tool.description == 'テスト用'

    def test_有効なAIツールの取得(self, repository: JsonAIToolRepository) -> None:
        """有効なAIツールの取得をテストします。"""
        # Arrange
        active_tool = AITool(id='active-tool', name_ja='有効ツール')
        disabled_tool = AITool(id='disabled-tool', name_ja='無効ツール')

        repository.save(active_tool)
        repository.save(disabled_tool)
        repository.disable('disabled-tool')

        # Act
        active_tools = repository.find_active_tools()

        # Assert
        assert len(active_tools) == 1
        assert active_tools[0].id == 'active-tool'

    def test_全AIツールの取得(self, repository: JsonAIToolRepository) -> None:
        """全AIツールの取得をテストします。"""
        # Arrange
        active_tool = AITool(id='active-tool', name_ja='有効ツール')
        disabled_tool = AITool(id='disabled-tool', name_ja='無効ツール')

        repository.save(active_tool)
        repository.save(disabled_tool)
        repository.disable('disabled-tool')

        # Act
        all_tools = repository.find_all_tools()

        # Assert
        assert len(all_tools) == 2
        tool_ids = [t.id for t in all_tools]
        assert 'active-tool' in tool_ids
        assert 'disabled-tool' in tool_ids

    def test_AIツールの無効化と有効化(self, repository: JsonAIToolRepository) -> None:
        """AIツールの無効化と有効化をテストします。"""
        # Arrange
        ai_tool = AITool(id='test-tool', name_ja='テストツール')
        repository.save(ai_tool)

        # Act & Assert - 無効化
        repository.disable('test-tool')
        disabled_tool = repository.find_by_id('test-tool')
        assert disabled_tool is not None
        assert disabled_tool.disabled_at is not None

        # Act & Assert - 有効化
        repository.enable('test-tool')
        enabled_tool = repository.find_by_id('test-tool')
        assert enabled_tool is not None
        assert enabled_tool.disabled_at is None
