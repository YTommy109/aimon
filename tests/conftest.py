"""テスト用の共通設定とフィクスチャ。"""

import tempfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from uuid import UUID

import pytest

from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.project_service import ProjectService
from app.types import ProjectID, ToolType


@pytest.fixture
def project_repository() -> Generator[JsonProjectRepository, None, None]:
    """テスト用のJsonProjectRepositoryフィクスチャ。

    一時ディレクトリを作成し、テスト終了後に削除する。
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield JsonProjectRepository(Path(tmp_dir))


@pytest.fixture
def sample_project() -> Project:
    """サンプルのプロジェクトを作成する。"""
    return Project(
        name='テストプロジェクト',
        source='/path/to/source',
        tool=ToolType.OVERVIEW,
    )


@pytest.fixture
def sample_project_id() -> ProjectID:
    """サンプルのプロジェクトIDを作成する。"""
    return ProjectID(UUID('12345678-1234-5678-1234-567812345678'))


@pytest.fixture
def mock_project_repository() -> Mock:
    """プロジェクトリポジトリのモックを作成する。"""
    return Mock()


@pytest.fixture
def project_service(mock_project_repository: Mock) -> ProjectService:
    """プロジェクトサービスを作成する。"""
    return ProjectService(mock_project_repository)


@pytest.fixture
def mock_project_service() -> Mock:
    """プロジェクトサービスのモックを作成する。"""
    return Mock()


@pytest.fixture
def mock_modal() -> Mock:
    """モーダルのモックを作成する。"""
    return Mock()


class MockSessionState(dict[str, object]):
    """辞書と属性アクセスの両方をサポートするSessionStateモック。"""

    def __getattr__(self, name: str) -> object:
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from e

    def __setattr__(self, name: str, value: object) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as e:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from e


@pytest.fixture
def mock_session_state() -> MockSessionState:
    """Streamlitのセッション状態のモックを作成する。"""
    return MockSessionState()


def create_test_project(
    name: str = 'テストプロジェクト',
    source: str = '/path/to/source',
    tool: ToolType = ToolType.OVERVIEW,
    project_id: ProjectID | None = None,
    result: dict[str, object] | None = None,
    created_at: datetime | None = None,
    executed_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> Project:
    """テスト用のプロジェクトを作成するヘルパー関数。"""
    project = Project(name=name, source=source, tool=tool)
    # 任意フィールドはループで簡潔に設定
    for key, value in (
        ('id', project_id),
        ('result', result),
        ('created_at', created_at),
        ('executed_at', executed_at),
        ('finished_at', finished_at),
    ):
        if value is not None:
            setattr(project, key, value)
    return project


def assert_project_created_correctly(
    project: Project, expected_name: str, expected_source: str, expected_tool: ToolType
) -> None:
    """プロジェクトが正しく作成されたかを検証するヘルパー関数。"""
    assert project is not None
    assert project.name == expected_name
    assert project.source == expected_source
    assert project.tool == expected_tool
    assert project.status.value == 'pending'
    assert project.result is None
    assert project.created_at is not None
    assert project.executed_at is None
    assert project.finished_at is None
