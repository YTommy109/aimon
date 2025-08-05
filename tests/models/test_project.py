"""Projectモデルのテスト。"""

from uuid import UUID
from zoneinfo import ZoneInfo

from app.models import AIToolID
from app.models.project import Project, ProjectStatus

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class TestProject:
    """Projectモデルのテストクラス。"""

    def test_command_execution_compatibility(self) -> None:
        """Ensure Project can instantiate and execute command-based operations."""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('87654321-4321-8765-4321-876543210987'))

        # Act
        project = Project(name=name, source=source, ai_tool=ai_tool)

        # Assert
        assert isinstance(project, Project)
        assert project.name == name
        assert project.source == source
        assert isinstance(project.ai_tool, UUID)  # AIToolID is NewType based on UUID
        assert project.status == ProjectStatus.PENDING
        assert project.result is None
        assert project.created_at is not None
        assert project.executed_at is None
        assert project.finished_at is None

    def test_プロジェクトが正常に作成される(self) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = AIToolID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        project = Project(name=name, source=source, ai_tool=ai_tool)

        # Assert
        assert isinstance(project.id, UUID)  # NewTypeは内部的にはUUID
        assert project.id == project.id  # 値の比較
        assert project.name == name
        assert project.source == source
        assert project.ai_tool == ai_tool
        assert project.result is None
        assert project.created_at is not None
        assert project.executed_at is None
        assert project.finished_at is None

    def test_プロジェクトの初期ステータス(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act & Assert
        assert project.status == ProjectStatus.PENDING

    def test_プロジェクトの実行開始ステータス(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act
        project.start_processing()

        # Assert
        assert project.status == ProjectStatus.PROCESSING

    def test_プロジェクトの完了ステータス(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act
        project.complete({'message': '完了'})

        # Assert
        assert project.status == ProjectStatus.COMPLETED

    def test_プロジェクトの失敗処理(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act
        project.fail({'error': 'エラーが発生しました'})

        # Assert
        assert project.status == ProjectStatus.FAILED
        assert project.result == {'error': 'エラーが発生しました'}

    def test_プロジェクトの完了処理(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )
        result = {'message': '処理が完了しました'}

        # Act
        project.complete(result)

        # Assert
        assert project.status == ProjectStatus.COMPLETED
        assert project.result == result
        assert project.finished_at is not None

    def test_プロジェクトの実行開始処理(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act
        project.start_processing()

        # Assert
        assert project.status == ProjectStatus.PROCESSING
        assert project.executed_at is not None

    def test_プロジェクトの完了時に実行開始時刻が設定される(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            ai_tool=AIToolID(UUID('12345678-1234-5678-1234-567812345678')),
        )

        # Act
        project.start_processing()
        project.complete({'message': '完了'})

        # Assert
        assert project.executed_at is not None
        assert project.finished_at is not None
        assert project.finished_at > project.executed_at
