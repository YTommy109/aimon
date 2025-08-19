"""Projectモデルのテスト。"""

from uuid import UUID
from zoneinfo import ZoneInfo

from app.models import ToolType
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
        tool = ToolType.OVERVIEW

        # Act
        project = Project(name=name, source=source, tool=tool)

        # Assert
        assert isinstance(project, Project)
        assert project.name == name
        assert project.source == source
        assert project.tool == tool
        assert project.status == ProjectStatus.PENDING
        assert project.result is None
        assert project.created_at is not None
        assert project.executed_at is None
        assert project.finished_at is None

    def test_プロジェクトが正常に作成される(self) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.OVERVIEW

        # Act
        project = Project(name=name, source=source, tool=tool)

        # Assert
        assert isinstance(project.id, UUID)  # NewTypeは内部的にはUUID
        assert project.id == project.id  # 値の比較
        assert project.name == name
        assert project.source == source
        assert project.tool == tool
        assert project.result is None
        assert project.created_at is not None
        assert project.executed_at is None
        assert project.finished_at is None

    def test_プロジェクトの初期ステータス(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # Act & Assert
        assert project.status == ProjectStatus.PENDING

    def test_プロジェクトの実行開始ステータス(self) -> None:
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
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
            tool=ToolType.OVERVIEW,
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
            tool=ToolType.OVERVIEW,
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
            tool=ToolType.OVERVIEW,
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
            tool=ToolType.OVERVIEW,
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
            tool=ToolType.OVERVIEW,
        )

        # Act
        project.start_processing()
        project.complete({'message': '完了'})

        # Assert
        assert project.executed_at is not None
        assert project.finished_at is not None
        assert project.finished_at > project.executed_at

    def test_内蔵ツールREVIEWが指定できる(self) -> None:
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = ToolType.REVIEW

        # Act
        project = Project(name=name, source=source, tool=tool)

        # Assert
        assert project.tool == ToolType.REVIEW
