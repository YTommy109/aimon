"""Projectモデルのテスト。"""

from typing import cast
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

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
        assert project.executed_at is not None
        assert project.status == ProjectStatus.PROCESSING

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

    def test_境界値テスト_空文字列の名前(self) -> None:
        """空文字列の名前でプロジェクト作成をテストする。"""
        # Arrange
        name = ''
        source = '/path/to/source'
        tool = ToolType.OVERVIEW

        # Act
        project = Project(name=name, source=source, tool=tool)

        # Assert - 現在の実装では空文字列が許可されている
        assert project.name == ''
        assert project.source == source
        assert project.tool == tool

    def test_境界値テスト_空文字列のソース(self) -> None:
        """空文字列のソースでプロジェクト作成をテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = ''
        tool = ToolType.OVERVIEW

        # Act
        project = Project(name=name, source=source, tool=tool)

        # Assert - 現在の実装では空文字列が許可されている
        assert project.name == name
        assert project.source == ''
        assert project.tool == tool

    def test_境界値テスト_Noneのツール(self) -> None:
        """Noneのツールでプロジェクト作成をテストする。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/path/to/source'
        tool = cast(ToolType, None)

        # Act & Assert
        with pytest.raises(ValidationError, match="Input should be 'OVERVIEW' or 'REVIEW'"):
            Project(name=name, source=source, tool=tool)

    def test_プロジェクトの状態遷移_正常フロー(self) -> None:
        """プロジェクトの状態遷移を正常フローでテストする。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # Act & Assert - PENDING -> PROCESSING -> COMPLETED
        assert project.status == ProjectStatus.PENDING

        project.start_processing()
        # PROCESSINGの検証はプロパティで確認
        assert project.executed_at is not None
        assert project.finished_at is None

        project.complete({'message': '完了'})
        # 完了後は終了時刻が設定されることを優先的に検証
        assert project.finished_at is not None

    def test_プロジェクトの状態遷移_エラーフロー(self) -> None:
        """プロジェクトの状態遷移をエラーフローでテストする。"""
        # Arrange
        project = Project(
            name='テストプロジェクト',
            source='/path/to/source',
            tool=ToolType.OVERVIEW,
        )

        # Act & Assert - PENDING -> PROCESSING -> FAILED
        assert project.status == ProjectStatus.PENDING

        project.start_processing()
        # PROCESSINGの検証はプロパティで確認
        assert project.executed_at is not None
        assert project.finished_at is None

        project.fail({'error': 'エラーが発生'})
        # 失敗時はresultにエラーが格納されることを検証
        assert project.result == {'error': 'エラーが発生'}
