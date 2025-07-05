"""ProjectHandlerクラスのテスト。"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from app.application.handlers.project_handler import ProjectHandler
from app.domain.entities import Project
from app.domain.repositories import ProjectRepository


class TestProjectHandler:
    """ProjectHandlerクラスのテスト。"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> MagicMock:
        """ProjectRepositoryのモックを提供するフィクスチャ。"""
        return mocker.MagicMock(spec=ProjectRepository)

    @pytest.fixture
    def project_handler(self, mock_repository: MagicMock) -> ProjectHandler:
        """ProjectHandlerインスタンスを提供するフィクスチャ。"""
        return ProjectHandler(mock_repository)

    # create_projectのテスト

    def test_create_project_成功(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """プロジェクト作成が成功する場合のテスト。"""
        # Arrange
        name = 'テストプロジェクト'
        source = '/test/path'
        ai_tool = 'test-tool'

        # Act
        result = project_handler.create_project(name, source, ai_tool)

        # Assert
        assert result is not None
        assert result.name == name
        assert result.source == source
        assert result.ai_tool == ai_tool
        mock_repository.save.assert_called_once_with(result)

    def test_create_project_無効な入力_空の名前(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """名前が空の場合にプロジェクト作成が失敗するテスト。"""
        # Act
        result = project_handler.create_project('', '/test/path', 'test-tool')

        # Assert
        assert result is None
        mock_repository.save.assert_not_called()

    def test_create_project_無効な入力_空のソース(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """ソースが空の場合にプロジェクト作成が失敗するテスト。"""
        # Act
        result = project_handler.create_project('テストプロジェクト', '', 'test-tool')

        # Assert
        assert result is None
        mock_repository.save.assert_not_called()

    def test_create_project_無効な入力_空のAIツール(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """AIツールが空の場合にプロジェクト作成が失敗するテスト。"""
        # Act
        result = project_handler.create_project('テストプロジェクト', '/test/path', '')

        # Assert
        assert result is None
        mock_repository.save.assert_not_called()

    def test_create_project_無効な入力_空白のみの名前(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """名前が空白のみの場合にプロジェクト作成が失敗するテスト。"""
        # Act
        result = project_handler.create_project('   ', '/test/path', 'test-tool')

        # Assert
        assert result is None
        mock_repository.save.assert_not_called()

    def test_create_project_保存で例外が発生(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """保存時に例外が発生した場合にNoneを返すテスト。"""
        # Arrange
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = project_handler.create_project('テストプロジェクト', '/test/path', 'test-tool')

        # Assert
        assert result is None

    # get_all_projectsのテスト

    def test_get_all_projects(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """全プロジェクト取得のテスト。"""
        # Arrange
        expected_projects = [
            Project(name='プロジェクト1', source='/path1', ai_tool='tool1'),
            Project(name='プロジェクト2', source='/path2', ai_tool='tool2'),
        ]
        mock_repository.find_all.return_value = expected_projects

        # Act
        result = project_handler.get_all_projects()

        # Assert
        assert result == expected_projects
        mock_repository.find_all.assert_called_once()

    # get_project_by_idのテスト

    def test_get_project_by_id_正常なUUID(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """正常なUUIDでプロジェクトを取得するテスト。"""
        # Arrange
        project_id = str(uuid4())
        expected_project = Project(
            name='テストプロジェクト', source='/test/path', ai_tool='test-tool'
        )
        mock_repository.find_by_id.return_value = expected_project

        # Act
        result = project_handler.get_project_by_id(project_id)

        # Assert
        assert result == expected_project
        mock_repository.find_by_id.assert_called_once()

    def test_get_project_by_id_無効なUUID(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """無効なUUIDでプロジェクト取得を試行するテスト。"""
        # Act
        result = project_handler.get_project_by_id('invalid-uuid')

        # Assert
        assert result is None
        mock_repository.find_by_id.assert_not_called()

    def test_get_project_by_id_空の文字列(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """空の文字列でプロジェクト取得を試行するテスト。"""
        # Act
        result = project_handler.get_project_by_id('')

        # Assert
        assert result is None
        mock_repository.find_by_id.assert_not_called()

    # update_projectのテスト

    def test_update_project_成功(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """プロジェクト更新が成功する場合のテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')

        # Act
        result = project_handler.update_project(project)

        # Assert
        assert result is True
        mock_repository.save.assert_called_once_with(project)

    def test_update_project_保存で例外が発生(
        self,
        project_handler: ProjectHandler,
        mock_repository: MagicMock,
    ) -> None:
        """更新時に例外が発生した場合にFalseを返すテスト。"""
        # Arrange
        project = Project(name='テストプロジェクト', source='/test/path', ai_tool='test-tool')
        mock_repository.save.side_effect = Exception('保存エラー')

        # Act
        result = project_handler.update_project(project)

        # Assert
        assert result is False

    # _is_valid_inputのテスト

    def test_is_valid_input_すべて有効(
        self,
        project_handler: ProjectHandler,
    ) -> None:
        """すべての入力が有効な場合のテスト。"""
        # Act & Assert
        assert project_handler._is_valid_input('名前', '/パス', 'ツール') is True

    def test_is_valid_input_名前がNone(
        self,
        project_handler: ProjectHandler,
    ) -> None:
        """名前がNoneの場合のテスト。"""
        # Act & Assert
        assert project_handler._is_valid_input(None, '/パス', 'ツール') is False  # type: ignore[arg-type]

    def test_is_valid_input_名前が空文字列(
        self,
        project_handler: ProjectHandler,
    ) -> None:
        """名前が空文字列の場合のテスト。"""
        # Act & Assert
        assert project_handler._is_valid_input('', '/パス', 'ツール') is False

    def test_is_valid_input_名前が空白のみ(
        self,
        project_handler: ProjectHandler,
    ) -> None:
        """名前が空白のみの場合のテスト。"""
        # Act & Assert
        assert project_handler._is_valid_input('   ', '/パス', 'ツール') is False
