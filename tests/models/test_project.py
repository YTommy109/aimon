"""Projectモデルのテスト。"""

from zoneinfo import ZoneInfo

from app.models.project import Project, ProjectStatus

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class TestProject:
    """Projectモデルのテストクラス。"""

    def test_プロジェクトが正常に作成される(self) -> None:
        """プロジェクトが正常に作成されることをテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        ai_tool = 'test_tool'

        # Act
        project = Project(name=name, source=source, ai_tool=ai_tool)

        # Assert
        assert project.name == name
        assert project.source == source
        assert project.ai_tool == ai_tool
        assert project.result is None

    def test_プロジェクトの処理開始(self) -> None:
        """プロジェクトの処理開始をテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')

        # Act
        project.start_processing()

        # Assert
        assert project.executed_at is not None
        assert project.result is None

    def test_プロジェクトの完了(self) -> None:
        """プロジェクトの完了をテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        result = {'message': '処理完了'}

        # Act
        project.complete(result)

        # Assert
        assert project.result == result
        assert project.finished_at is not None

    def test_プロジェクトの失敗(self) -> None:
        """プロジェクトの失敗をテストする。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool')
        error = {'error': '処理エラー'}

        # Act
        project.fail(error)

        # Assert
        assert project.result == error
        assert project.finished_at is not None

    def test_プロジェクトのステータス遷移(self) -> None:
        """プロジェクトのステータス遷移をテストする。"""
        # Arrange
        project: Project = Project(
            name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool'
        )

        # Act & Assert - 初期状態
        assert project.status == ProjectStatus.PENDING

        # Act & Assert - 処理開始後
        project.start_processing()
        assert project.status == ProjectStatus.PROCESSING  # type: ignore[comparison-overlap]

    def test_プロジェクトのステータス遷移_完了(self) -> None:
        """プロジェクトのステータス遷移(完了)をテストする。"""
        # Arrange
        project: Project = Project(
            name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool'
        )
        project.start_processing()

        # Act & Assert
        project.complete({'message': '完了'})
        assert project.status == ProjectStatus.COMPLETED

    def test_プロジェクトの失敗ステータス(self) -> None:
        """プロジェクトの失敗ステータスをテストする。"""
        # Arrange
        project: Project = Project(
            name='テストプロジェクト', source='/path/to/source', ai_tool='test_tool'
        )
        project.start_processing()

        # Act & Assert
        project.fail({'error': 'エラー'})
        assert project.status == ProjectStatus.FAILED
