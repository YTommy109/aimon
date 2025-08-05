"""JSONファイルベースのAIツールリポジトリ実装。"""

import json
import logging
import traceback
from pathlib import Path
from typing import Any, cast

from app.errors import PathIsDirectoryError, ResourceNotFoundError
from app.models import AIToolID
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

        # デバッグ情報を出力
        logger.info(f'AIツールリポジトリ初期化: data_dir={data_dir}')
        logger.info(f'AIツールファイルパス: {self.ai_tools_path}')
        logger.info(f'データディレクトリ存在: {data_dir.exists()}')

        self._ensure_data_dir_exists()
        self._ensure_ai_tools_file_exists()

    def find_all_tools(self) -> list[AITool]:
        """全てのAIツールの一覧を取得します。"""
        try:
            tools_data = self._read_json(self.ai_tools_path)
            tools = [AITool.model_validate(t) for t in tools_data]
            logger.debug(f'AIツール一覧を取得しました: {len(tools)}件')
            return tools
        except Exception as e:
            logger.error(f'AIツール一覧取得エラー: {e}')
            return []

    def find_by_id(self, tool_id: AIToolID) -> AITool:
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
        try:
            logger.info(f'AIツール保存開始: {ai_tool.name_ja}, id={ai_tool.id}')
            logger.info(f'保存先ディレクトリ: {self.data_dir}')
            logger.info(f'保存先ファイル: {self.ai_tools_path}')

            tools = self._update_tools_list(ai_tool)
            self._save_tools_to_file(tools)
            logger.info(f'AIツールを保存しました: {ai_tool.name_ja}')
        except Exception as e:
            logger.error(f'AIツール保存エラー: {e}')
            logger.error(f'スタックトレース: {traceback.format_exc()}')
            raise

    def _update_tools_list(self, ai_tool: AITool) -> list[AITool]:
        """ツールリストを更新します。"""
        tools = self.find_all_tools()
        logger.info(f'既存ツール数: {len(tools)}')

        for i, tool in enumerate(tools):
            if tool.id == ai_tool.id:
                tools[i] = ai_tool
                logger.info(f'既存ツールを更新: {tool.name_ja}')
                break
        else:
            tools.append(ai_tool)
            logger.info(f'新規ツールを追加: {ai_tool.name_ja}')

        return tools

    def _save_tools_to_file(self, tools: list[AITool]) -> None:
        """ツールリストをファイルに保存します。"""
        tools_data = [t.model_dump(mode='json') for t in tools]
        logger.info(f'保存するツール数: {len(tools_data)}')
        logger.info(f'保存先ファイル: {self.ai_tools_path}')
        logger.info(f'保存先ディレクトリ存在: {self.ai_tools_path.parent.exists()}')
        self._write_json(self.ai_tools_path, tools_data)

    def _ensure_data_dir_exists(self) -> None:
        """データディレクトリの存在を確認し、必要に応じて作成します。"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_ai_tools_file_exists(self) -> None:
        """AIツールファイルの存在を確認し、必要に応じて作成します。"""
        if not self.ai_tools_path.exists():
            self._write_json(self.ai_tools_path, [])

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """JSONファイルを読み込みます。"""
        result = []

        if path.exists():
            try:
                self._validate_path_is_not_directory(path)
                result = self._load_json_data(path)
            except Exception as e:
                logger.error(f'JSONファイル読み込みエラー: {path}, エラー: {e}')
        else:
            logger.debug(f'JSONファイルが存在しません: {path}')

        return result

    def _validate_path_is_not_directory(self, path: Path) -> None:
        """パスがディレクトリでないことを確認します。"""
        if path.is_dir():
            raise PathIsDirectoryError(str(path))

    def _load_json_data(self, path: Path) -> list[dict[str, Any]]:
        """JSONデータを読み込みます。"""
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f'JSONファイルを読み込みました: {path}')
            return cast(list[dict[str, Any]], data)

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """JSONファイルに書き込みます。"""
        try:
            self._validate_write_path(path)
            self._ensure_parent_directory(path)
            self._log_write_data(path, data)
            self._perform_write(path, data)
            logger.info(f'JSONファイルに書き込みました: {path}')
        except Exception as e:
            logger.error(f'JSONファイル書き込みエラー: {path}, エラー: {e}')
            logger.error(f'スタックトレース: {traceback.format_exc()}')
            raise

    def _validate_write_path(self, path: Path) -> None:
        """書き込みパスを検証します。"""
        logger.info(f'JSONファイル書き込み開始: {path}')

        # ターゲットがディレクトリの場合はエラー
        if path.exists() and path.is_dir():
            raise PathIsDirectoryError(str(path))

    def _ensure_parent_directory(self, path: Path) -> None:
        """親ディレクトリの存在を確認し、必要に応じて作成します。"""
        logger.info(f'ファイルの親ディレクトリ: {path.parent}')
        logger.info(f'親ディレクトリ存在: {path.parent.exists()}')

        # 親ディレクトリが存在することを確認
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f'親ディレクトリ作成完了: {path.parent}')

    def _log_write_data(self, path: Path, data: list[dict[str, Any]]) -> None:
        """書き込みデータをログに出力します。"""
        logger.info(f'書き込み先ファイル: {path}')
        logger.info(f'データ数: {len(data)}')
        logger.info(f'保存するデータ: {data}')

    def _perform_write(self, path: Path, data: list[dict[str, Any]]) -> None:
        """実際の書き込み処理を実行します。"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
