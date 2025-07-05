"""新しいドメイン層のエンティティテスト。"""

from datetime import datetime

from app.domain.entities import JST, AITool, Project, ProjectStatus


class TestProject:
    """Projectエンティティのテスト。"""

    def test_新しいプロジェクトのデフォルト値(self) -> None:
        """新しいプロジェクトのデフォルト値をテストします。"""
        # Arrange & Act
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')

        # Assert
        assert project.name == 'テストプロジェクト'
        assert project.source == '/test/path'
        assert project.ai_tool == 'test-tool'
        assert project.result is None
        assert project.executed_at is None
        assert project.finished_at is None
        assert isinstance(project.created_at, datetime)
        assert project.created_at.tzinfo == JST

    def test_プロジェクトのステータス_待機中(self) -> None:
        """待機中ステータスのテスト。"""
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')

        # Act & Assert
        assert project.status == ProjectStatus.PENDING

    def test_プロジェクトのステータス_処理中(self) -> None:
        """処理中ステータスのテスト。"""
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')

        # Act
        project.start_processing()

        # Assert
        assert project.status == ProjectStatus.PROCESSING
        assert project.executed_at is not None

    def test_プロジェクトのステータス_完了(self) -> None:
        """完了ステータスのテスト。"""
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        project.start_processing()

        # Act
        project.complete({'result': 'success'})

        # Assert
        assert project.status == ProjectStatus.COMPLETED
        assert project.finished_at is not None
        assert project.result == {'result': 'success'}

    def test_プロジェクトのステータス_失敗(self) -> None:
        """失敗ステータスのテスト。"""
        # Arrange
        project = Project(name='テスト', source='/path', ai_tool='tool')
        project.start_processing()

        # Act
        project.fail({'error': 'テストエラー'})

        # Assert
        assert project.status == ProjectStatus.FAILED
        assert project.finished_at is not None
        assert project.result == {'error': 'テストエラー'}


class TestAITool:
    """AIToolエンティティのテスト。"""

    def test_新しいAIツールの作成(self) -> None:
        """新しいAIツールの作成をテストします。"""
        # Arrange & Act
        ai_tool = AITool(id='test-tool', name_ja='テストツール', description='テスト用のAIツール')

        # Assert
        assert ai_tool.id == 'test-tool'
        assert ai_tool.name_ja == 'テストツール'
        assert ai_tool.description == 'テスト用のAIツール'
        assert ai_tool.disabled_at is None
        assert isinstance(ai_tool.created_at, datetime)
        assert isinstance(ai_tool.updated_at, datetime)
        assert ai_tool.created_at.tzinfo == JST
        assert ai_tool.updated_at.tzinfo == JST

    def test_AIツールの説明なし(self) -> None:
        """説明なしのAIツール作成をテストします。"""
        # Arrange & Act
        ai_tool = AITool(id='test-tool', name_ja='テストツール')

        # Assert
        assert ai_tool.description is None
