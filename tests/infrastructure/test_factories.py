"""Infrastructure Factoriesのテスト。"""

from pathlib import Path
from tempfile import TemporaryDirectory

from app.application.data_manager import DataManager
from app.application.handlers.ai_tool_handler import AIToolHandler
from app.application.handlers.project_handler import ProjectHandler
from app.errors import ResourceNotFoundError
from app.infrastructure.factories import create_data_manager
from app.infrastructure.persistence import JsonAIToolRepository, JsonProjectRepository


class TestFactories:
    """Factoriesのテスト。"""

    def test_create_data_manager_文字列パス(self) -> None:
        """文字列パスでDataManagerを作成するテスト。"""
        with TemporaryDirectory() as temp_dir:
            # Act
            data_manager = create_data_manager(temp_dir)

            # Assert
            assert isinstance(data_manager, DataManager)
            assert isinstance(data_manager.ai_tool_handler, AIToolHandler)
            assert isinstance(data_manager.project_handler, ProjectHandler)
            assert isinstance(data_manager.ai_tool_handler.ai_tool_repository, JsonAIToolRepository)
            assert isinstance(
                data_manager.project_handler.project_repository, JsonProjectRepository
            )

    def test_create_data_manager_Pathオブジェクト(self) -> None:
        """PathオブジェクトでDataManagerを作成するテスト。"""
        with TemporaryDirectory() as temp_dir:
            # Act
            data_manager = create_data_manager(Path(temp_dir))

            # Assert
            assert isinstance(data_manager, DataManager)
            assert isinstance(data_manager.ai_tool_handler, AIToolHandler)
            assert isinstance(data_manager.project_handler, ProjectHandler)

    def test_create_data_manager_動作確認(self) -> None:
        """作成されたDataManagerが正常に動作するかのテスト。"""
        with TemporaryDirectory() as temp_dir:
            # Act
            data_manager = create_data_manager(temp_dir)

            # AIツールの作成テスト
            try:
                data_manager.create_ai_tool('test-tool', 'テストツール', 'テスト用')
                success = True
            except ResourceNotFoundError:
                success = False  # 予期せぬエラー
            assert success, 'AIツールの作成に失敗しました'

            # プロジェクトの作成テスト
            project = data_manager.create_project(
                'テストプロジェクト', '/path/to/test-input.txt', 'test-tool'
            )
            assert project is not None
            assert project.name == 'テストプロジェクト'
            assert len(data_manager.get_projects()) == 1

            # 既存のAIツールを取得できるか
            tools = data_manager.get_all_ai_tools()
            assert any(tool.id == 'test-tool' and tool.name_ja == 'テストツール' for tool in tools)
