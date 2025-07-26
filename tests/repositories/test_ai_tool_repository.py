"""AIツールリポジトリのテスト。"""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models.ai_tool import AITool
from app.repositories.ai_tool_repository import JsonAIToolRepository


class TestJsonAIToolRepository:
    """JsonAIToolRepositoryのテストクラス。"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """一時ディレクトリのフィクスチャ。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def repository(self, temp_dir: Path) -> JsonAIToolRepository:
        """リポジトリのフィクスチャ。"""
        return JsonAIToolRepository(temp_dir)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツールのフィクスチャ。"""
        return AITool(
            id='test-tool-1',
            name_ja='テストツール1',
            description='テスト用のAIツール',
            endpoint_url='https://api.example.com/test1',
        )

    def test_初期化時にデータディレクトリとファイルが作成される(self, temp_dir: Path) -> None:
        """初期化時にデータディレクトリとAIツールファイルが作成されることをテスト。"""
        # Arrange
        JsonAIToolRepository(temp_dir)

        # Assert
        assert temp_dir.exists()
        assert (temp_dir / 'ai_tools.json').exists()

    def test_空のリポジトリから全てのツールを取得すると空リストが返される(
        self, repository: JsonAIToolRepository
    ) -> None:
        """空のリポジトリから全てのツールを取得すると空リストが返されることをテスト。"""
        # Act
        tools = repository.find_all_tools()

        # Assert
        assert tools == []

    def test_AIツールを保存して取得できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        """AIツールを保存して取得できることをテスト。"""
        # Act
        repository.save(sample_ai_tool)
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 1
        assert tools[0].id == sample_ai_tool.id
        assert tools[0].name_ja == sample_ai_tool.name_ja

    def test_存在しないIDでツールを取得するとResourceNotFoundErrorが発生する(
        self, repository: JsonAIToolRepository
    ) -> None:
        """存在しないIDでツールを取得するとResourceNotFoundErrorが発生することをテスト。"""
        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            repository.find_by_id('non-existent-id')

    def test_存在するIDでツールを取得できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        """存在するIDでツールを取得できることをテスト。"""
        # Arrange
        repository.save(sample_ai_tool)

        # Act
        found_tool = repository.find_by_id(sample_ai_tool.id)

        # Assert
        assert found_tool.id == sample_ai_tool.id
        assert found_tool.name_ja == sample_ai_tool.name_ja

    def test_既存のツールを更新できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        """既存のツールを更新できることをテスト。"""
        # Arrange
        repository.save(sample_ai_tool)
        updated_tool = AITool(
            id=sample_ai_tool.id,
            name_ja='更新されたツール名',
            description='更新された説明',
            endpoint_url='https://api.example.com/updated',
        )

        # Act
        repository.save(updated_tool)
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 1
        assert tools[0].name_ja == '更新されたツール名'
        assert tools[0].description == '更新された説明'

    def test_複数のツールを保存して取得できる(self, repository: JsonAIToolRepository) -> None:
        """複数のツールを保存して取得できることをテスト。"""
        # Arrange
        tool1 = AITool(
            id='tool-1',
            name_ja='ツール1',
            description='説明1',
            endpoint_url='https://api.example.com/1',
        )
        tool2 = AITool(
            id='tool-2',
            name_ja='ツール2',
            description='説明2',
            endpoint_url='https://api.example.com/2',
        )

        # Act
        repository.save(tool1)
        repository.save(tool2)
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 2
        tool_ids = [tool.id for tool in tools]
        assert 'tool-1' in tool_ids
        assert 'tool-2' in tool_ids

    def test_JSONファイルが存在しない場合に空リストが返される(self, temp_dir: Path) -> None:
        """JSONファイルが存在しない場合に空リストが返されることをテスト。"""
        # Arrange
        repository = JsonAIToolRepository(temp_dir)
        # ai_tools.jsonファイルを削除
        (temp_dir / 'ai_tools.json').unlink()

        # Act
        tools = repository.find_all_tools()

        # Assert
        assert tools == []

    def test_ターゲットパスがディレクトリの場合にPathIsDirectoryErrorが発生する(
        self, temp_dir: Path
    ) -> None:
        """ターゲットパスがディレクトリの場合にPathIsDirectoryErrorが発生することをテスト。"""
        # Arrange
        repository = JsonAIToolRepository(temp_dir)
        # ai_tools.jsonをディレクトリに変更
        json_path = temp_dir / 'ai_tools.json'
        json_path.unlink()
        json_path.mkdir()

        # Act & Assert
        with pytest.raises(PathIsDirectoryError):
            repository.save(
                AITool(
                    id='test-tool',
                    name_ja='テストツール',
                    description='テスト用',
                    endpoint_url='https://api.example.com/test',
                )
            )

    def test_JSONファイルの読み込みエラーが適切に処理される(self, temp_dir: Path) -> None:
        """JSONファイルの読み込みエラーが適切に処理されることをテスト。"""
        # Arrange
        repository = JsonAIToolRepository(temp_dir)
        json_path = temp_dir / 'ai_tools.json'

        # 不正なJSONを書き込み
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write('invalid json')

        # Act & Assert
        # エラーが発生しても空リストが返される
        with pytest.raises(Exception, match='.*'):
            repository.find_all_tools()

    def test_JSONファイルの書き込みエラーが適切に処理される(self, temp_dir: Path) -> None:
        """JSONファイルの書き込みエラーが適切に処理されることをテスト。"""
        # Arrange
        repository = JsonAIToolRepository(temp_dir)
        json_path = temp_dir / 'ai_tools.json'

        # 書き込み権限を削除
        json_path.chmod(0o444)

        # Act & Assert
        with pytest.raises(PermissionError):
            repository.save(
                AITool(
                    id='test-tool',
                    name_ja='テストツール',
                    description='テスト用',
                    endpoint_url='https://api.example.com/test',
                )
            )
