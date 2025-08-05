"""AIツールリポジトリのテスト。"""

import json
import os
import stat
import tempfile
from pathlib import Path
from uuid import UUID

import pytest

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models import AIToolID
from app.models.ai_tool import AITool
from app.repositories.ai_tool_repository import JsonAIToolRepository


class TestJsonAIToolRepository:
    """JsonAIToolRepositoryのテストクラス。"""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """一時ディレクトリを作成する。"""
        return Path(tempfile.mkdtemp())

    @pytest.fixture
    def repository(self, temp_dir: Path) -> JsonAIToolRepository:
        """リポジトリを作成する。"""
        return JsonAIToolRepository(temp_dir)

    @pytest.fixture
    def sample_ai_tool(self) -> AITool:
        """サンプルAIツールを作成する。"""
        return AITool(
            name_ja='テストツール',
            description='テスト用のAIツール',
            command='curl -X GET https://api.example.com/test',
        )

    def test_AIツール一覧を取得できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        # Arrange
        repository.save(sample_ai_tool)

        # Act
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 1
        assert tools[0].id == sample_ai_tool.id
        assert tools[0].name_ja == sample_ai_tool.name_ja
        assert tools[0].description == sample_ai_tool.description
        assert tools[0].command == sample_ai_tool.command

    def test_IDでAIツールを取得できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        # Arrange
        repository.save(sample_ai_tool)

        # Act
        found_tool = repository.find_by_id(sample_ai_tool.id)

        # Assert
        assert found_tool.id == sample_ai_tool.id
        assert found_tool.name_ja == sample_ai_tool.name_ja
        assert found_tool.description == sample_ai_tool.description
        assert found_tool.command == sample_ai_tool.command

    def test_存在しないIDでAIツールを取得するとResourceNotFoundErrorが発生する(
        self, repository: JsonAIToolRepository
    ) -> None:
        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            repository.find_by_id(AIToolID(UUID('12345678-1234-5678-1234-567812345678')))

    def test_AIツールを保存できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        # Act
        repository.save(sample_ai_tool)

        # Assert
        tools = repository.find_all_tools()
        assert len(tools) == 1
        assert tools[0].id == sample_ai_tool.id

    def test_複数のAIツールを保存できる(self, repository: JsonAIToolRepository) -> None:
        # Arrange
        tool1 = AITool(
            name_ja='ツール1',
            description='ツール1の説明',
            command='curl -X GET https://api.example.com/tool1',
        )
        tool2 = AITool(
            name_ja='ツール2',
            description='ツール2の説明',
            command='curl -X GET https://api.example.com/tool2',
        )

        # Act
        repository.save(tool1)
        repository.save(tool2)

        # Assert
        tools = repository.find_all_tools()
        assert len(tools) == 2
        tool_ids = [t.id for t in tools]
        assert tool1.id in tool_ids
        assert tool2.id in tool_ids

    def test_AIツールを更新できる(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        # Arrange
        repository.save(sample_ai_tool)
        sample_ai_tool.name_ja = '更新されたツール'

        # Act
        repository.save(sample_ai_tool)

        # Assert
        updated_tool = repository.find_by_id(sample_ai_tool.id)
        assert updated_tool.name_ja == '更新されたツール'

    def test_空のファイルから開始できる(self, repository: JsonAIToolRepository) -> None:
        # Act
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 0

    def test_JSONファイルが正しく作成される(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool
    ) -> None:
        # Act
        repository.save(sample_ai_tool)

        # Assert
        tools_file = repository.data_dir / 'ai_tools.json'
        assert tools_file.exists()
        with open(tools_file, encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['name_ja'] == sample_ai_tool.name_ja

    def test_JSONファイル読み込みエラー時に空リストを返す(
        self, repository: JsonAIToolRepository, temp_dir: Path
    ) -> None:
        # Arrange
        tools_file = temp_dir / 'ai_tools.json'
        with open(tools_file, 'w', encoding='utf-8') as f:
            f.write('invalid json')

        # Act
        tools = repository.find_all_tools()

        # Assert
        assert len(tools) == 0

    def test_ディレクトリがパスとして指定された場合にPathIsDirectoryErrorが発生する(
        self, temp_dir: Path
    ) -> None:
        # Arrange
        tools_file = temp_dir / 'ai_tools.json'
        tools_file.mkdir(exist_ok=True)

        # Act & Assert
        # 実際のリポジトリは初期化時にエラーを発生させないため、
        # 保存時にエラーが発生することを確認する
        repository = JsonAIToolRepository(temp_dir)
        sample_ai_tool = AITool(
            name_ja='テストツール',
            description='テスト用のAIツール',
            command='curl -X GET https://api.example.com/test',
        )

        with pytest.raises(PathIsDirectoryError):
            repository.save(sample_ai_tool)

    def test_保存時にエラーが発生しても例外を再送出する(
        self, repository: JsonAIToolRepository, sample_ai_tool: AITool, temp_dir: Path
    ) -> None:
        # Arrange
        tools_file = temp_dir / 'ai_tools.json'
        # ファイルを読み取り専用にして書き込みエラーを発生させる
        os.chmod(tools_file, stat.S_IREAD)

        # Act & Assert
        with pytest.raises(OSError, match='Permission denied'):
            repository.save(sample_ai_tool)
