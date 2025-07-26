"""JSONファイルベースのAIツールリポジトリ実装。"""

import json
import logging
from pathlib import Path
from typing import Any, cast

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models.ai_tool import AITool

logger = logging.getLogger('aiman')


class JsonAIToolRepository:
    """JSONファイルベースのAIツールリポジトリ。"""

    def __init__(self, data_dir: Path) -> None:
        """リポジトリを初期化します。

        Args:
            data_dir: データファイルを保存するディレクトリのパス。
        """
        self.data_dir = data_dir
        self.ai_tools_path = data_dir / 'ai_tools.json'
        self._ensure_data_dir_exists()
        self._ensure_ai_tools_file_exists()

    def find_all_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得します。"""
        tools_data = self._read_json(self.ai_tools_path)
        return [AITool.model_validate(t) for t in tools_data]

    def find_by_id(self, tool_id: str) -> AITool:
        """指定されたIDのAIツールを取得します。

        Args:
            tool_id: 取得するAIツールのID。

        Returns:
            指定されたIDのAIツール。

        Raises:
            ResourceNotFoundError: 指定されたIDのAIツールが見つからない場合。
        """
        tools = self.find_all_tools()
        try:
            return next(tool for tool in tools if tool.id == tool_id)
        except StopIteration:
            raise ResourceNotFoundError('AIツール', tool_id) from None

    def save(self, ai_tool: AITool) -> None:
        """AIツールを保存します。"""
        tools = self.find_all_tools()
        for i, tool in enumerate(tools):
            if tool.id == ai_tool.id:
                tools[i] = ai_tool
                break
        else:
            tools.append(ai_tool)
        # endpoint_urlも含めて保存
        self._write_json(self.ai_tools_path, [t.model_dump(mode='json') for t in tools])

    def _ensure_data_dir_exists(self) -> None:
        """データディレクトリの存在を確認し、必要に応じて作成します。"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_ai_tools_file_exists(self) -> None:
        """AIツールファイルの存在を確認し、必要に応じて作成します。"""
        if not self.ai_tools_path.exists():
            self._write_json(self.ai_tools_path, [])

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """JSONファイルを読み込みます。"""
        if not path.exists():
            return []
        # ターゲットがディレクトリの場合はエラー
        if path.is_dir():
            raise PathIsDirectoryError(str(path))
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            return cast(list[dict[str, Any]], data)

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """JSONファイルに書き込みます。"""
        # ターゲットがディレクトリの場合はエラー
        if path.exists() and path.is_dir():
            raise PathIsDirectoryError(str(path))

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
