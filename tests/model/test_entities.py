from datetime import datetime
from typing import Any
from uuid import UUID

from app.model.entities import AITool, Project, ProjectStatus


class TestAITool:
    """AIToolエンティティのテストクラス。"""

    def test_AIToolエンティティが正しく作成される(self) -> None:
        # Arrange & Act
        ai_tool = AITool(
            id='test_tool',
            name_ja='テストツール',
            description='テスト用のAIツール',
        )

        # Assert
        assert ai_tool.id == 'test_tool'
        assert ai_tool.name_ja == 'テストツール'
        assert ai_tool.description == 'テスト用のAIツール'
        assert isinstance(ai_tool.created_at, datetime)
        assert isinstance(ai_tool.updated_at, datetime)
        assert ai_tool.disabled_at is None


class TestProjectStatus:
    """ProjectStatusエンティティのテストクラス。"""

    def test_ProjectStatusの値が正しく定義されている(self) -> None:
        # Arrange & Act & Assert
        assert ProjectStatus.PENDING.value == 'Pending'
        assert ProjectStatus.PROCESSING.value == 'Processing'
        assert ProjectStatus.FAILED.value == 'Failed'
        assert ProjectStatus.COMPLETED.value == 'Completed'


class TestProject:
    """Projectエンティティのテストクラス。"""

    def test_Projectエンティティがデフォルト値で作成される(self) -> None:
        # Arrange
        project_data: dict[str, Any] = {
            'name': 'テストプロジェクト',
            'source': '/path/to/source',
            'ai_tool': 'test_tool',
        }

        # Act
        project = Project(**project_data)

        # Assert
        assert project.name == 'テストプロジェクト'
        assert project.source == '/path/to/source'
        assert project.ai_tool == 'test_tool'
        assert isinstance(project.id, UUID)
        assert isinstance(project.created_at, datetime)
        assert project.executed_at is None
        assert project.finished_at is None
        assert project.result is None

    def test_Projectのstatusプロパティが初期状態でPENDINGを返す(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')

        # Act
        status = project.status

        # Assert
        assert status == ProjectStatus.PENDING

    def test_Projectのstatusプロパティが実行中にPROCESSINGを返す(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        project.executed_at = datetime.now()

        # Act
        status = project.status

        # Assert
        assert status == ProjectStatus.PROCESSING

    def test_Projectのstatusプロパティがエラー時にFAILEDを返す(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        project.executed_at = datetime.now()
        project.finished_at = datetime.now()
        project.result = {'error': 'テストエラー'}

        # Act
        status = project.status

        # Assert
        assert status == ProjectStatus.FAILED

    def test_Projectのstatusプロパティが完了時にCOMPLETEDを返す(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        project.executed_at = datetime.now()
        project.finished_at = datetime.now()
        project.result = {'summary': 'テスト結果'}

        # Act
        status = project.status

        # Assert
        assert status == ProjectStatus.COMPLETED

    def test_start_processingメソッドが実行時刻を設定する(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        assert project.executed_at is None

        # Act
        project.start_processing()

        # Assert
        assert project.executed_at is not None

    def test_completeメソッドが結果と完了時刻を設定する(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        result = {'summary': 'テスト結果', 'data': [1, 2, 3]}
        assert project.result is None
        assert project.finished_at is None

        # Act
        project.complete(result)

        # Assert
        assert project.result == result
        assert project.finished_at is not None

    def test_failメソッドがエラー結果と完了時刻を設定する(self) -> None:
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        error = {'error': 'テストエラー', 'details': 'エラーの詳細'}
        assert project.result is None
        assert project.finished_at is None

        # Act
        project.fail(error)

        # Assert
        assert project.result == error
        assert project.finished_at is not None
