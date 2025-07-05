"""ApplicationContainerクラスのテスト。"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

import app.application.container as container_module
import app.infrastructure.external.ai_client as ai_client_module
from app.application.container import ApplicationContainer
from app.application.project_processor import ProjectProcessor
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.infrastructure.external.ai_client import AIServiceClient
from app.infrastructure.file_processor import FileProcessor


class TestApplicationContainer:
    """ApplicationContainerクラスのテスト。"""

    @pytest.fixture
    def container(self) -> ApplicationContainer:
        """ApplicationContainerのインスタンス。"""
        return ApplicationContainer()

    @pytest.fixture
    def container_with_custom_data_dir(self, tmp_path: Path) -> ApplicationContainer:
        """カスタムデータディレクトリを使用するApplicationContainerのインスタンス。"""
        return ApplicationContainer(data_dir=tmp_path)

    def test_ApplicationContainerが正しく初期化される(self) -> None:
        """ApplicationContainerが正しく初期化されることを確認。"""
        # Arrange & Act
        container = ApplicationContainer()

        # Assert
        assert container._project_repository is None
        assert container._ai_tool_repository is None
        assert container._file_processor is None
        assert container._ai_client is None
        assert container._project_processor is None

    def test_カスタムデータディレクトリで初期化される(self, tmp_path: Path) -> None:
        """カスタムデータディレクトリでApplicationContainerが初期化される。"""
        # Arrange & Act
        container = ApplicationContainer(data_dir=tmp_path)

        # Assert
        assert container._data_dir == tmp_path

    def test_データディレクトリがNoneの場合にconfigから取得される(
        self, mocker: MockerFixture
    ) -> None:
        """データディレクトリがNoneの場合にconfigから取得される。"""
        # Arrange
        mock_config = mocker.patch.object(container_module, 'config')
        expected_path = Path('/test/config/data')
        mock_config.data_dir_path = expected_path

        # Act
        container = ApplicationContainer(data_dir=None)

        # Assert
        assert container._data_dir == expected_path

    def test_プロジェクトリポジトリが正しく取得される(
        self, container: ApplicationContainer
    ) -> None:
        """プロジェクトリポジトリが正しく取得される。"""
        # Act
        repo = container.project_repository

        # Assert
        assert isinstance(repo, ProjectRepository)
        # 同じインスタンスが返されることを確認（シングルトン）
        assert container.project_repository is repo

    def test_AIツールリポジトリが正しく取得される(self, container: ApplicationContainer) -> None:
        """AIツールリポジトリが正しく取得される。"""
        # Act
        repo = container.ai_tool_repository

        # Assert
        assert isinstance(repo, AIToolRepository)
        # 同じインスタンスが返されることを確認（シングルトン）
        assert container.ai_tool_repository is repo

    def test_ファイルプロセッサーが正しく取得される(
        self, container: ApplicationContainer, mocker: MockerFixture
    ) -> None:
        """ファイルプロセッサーが正しく取得される。"""
        # Act
        mocker.patch.object(container_module, 'config')
        processor = container.file_processor

        # Assert
        assert isinstance(processor, FileProcessor)
        # 同じインスタンスが返されることを確認（シングルトン）
        assert container.file_processor is processor

    def test_AIサービスクライアントが正しく取得される(
        self, container: ApplicationContainer, mocker: MockerFixture
    ) -> None:
        """AIサービスクライアントが正しく取得される。"""
        # Arrange
        mock_config = mocker.patch.object(container_module, 'config')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'

        # Act
        mocker.patch.object(ai_client_module, 'genai')
        client = container.ai_client

        # Assert
        assert isinstance(client, AIServiceClient)
        # 同じインスタンスが返されることを確認（シングルトン）
        assert container.ai_client is client

    def test_プロジェクトプロセッサーが正しく取得される(
        self, container: ApplicationContainer, mocker: MockerFixture
    ) -> None:
        """プロジェクトプロセッサーが正しく取得される。"""
        # Arrange
        mock_config = mocker.patch.object(container_module, 'config')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'

        # Act
        mocker.patch.object(ai_client_module, 'genai')
        processor = container.project_processor

        # Assert
        assert isinstance(processor, ProjectProcessor)
        # 同じインスタンスが返されることを確認（シングルトン）
        assert container.project_processor is processor

    def test_全ての依存関係が正しく注入される(
        self, container: ApplicationContainer, mocker: MockerFixture
    ) -> None:
        """プロジェクトプロセッサーに全ての依存関係が正しく注入される。"""
        # Arrange
        mock_config = mocker.patch.object(container_module, 'config')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'

        # Act
        mocker.patch.object(ai_client_module, 'genai')
        processor = container.project_processor

        # Assert
        assert processor.project_repository is container.project_repository
        assert processor.file_processor is container.file_processor
        assert processor.ai_client is container.ai_client

    def test_カスタムデータディレクトリがリポジトリに渡される(self, tmp_path: Path) -> None:
        """カスタムデータディレクトリがリポジトリに正しく渡される。"""
        # Arrange
        container = ApplicationContainer(data_dir=tmp_path)

        # Act
        project_repo = container.project_repository
        ai_tool_repo = container.ai_tool_repository

        # Assert
        # リポジトリが正しく取得されることを確認
        assert isinstance(project_repo, ProjectRepository)
        assert isinstance(ai_tool_repo, AIToolRepository)
