"""統合AIツールサービス。"""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models import AIToolID
from app.models.ai_tool import AITool
from app.repositories.ai_tool_repository import JsonAIToolRepository

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class AIToolService:
    """統合AIツールサービス。"""

    def __init__(self, repository: JsonAIToolRepository):
        """サービスを初期化します。

        Args:
            repository: AIツールリポジトリ。
        """
        self.repository = repository
        self.logger = logging.getLogger('aiman')

    def get_all_ai_tools(self) -> list[AITool]:
        """全AIツールを取得する。

        Returns:
            AIツールのリスト。
        """
        return self.repository.find_all_tools()

    def get_ai_tool_by_id(self, tool_id: AIToolID) -> AITool:
        """IDでAIツールを取得する。

        Args:
            tool_id: AIツールID。

        Returns:
            AIツール。

        Raises:
            ValueError: 指定されたIDのAIツールが見つからない場合。
        """
        return self.repository.find_by_id(tool_id)

    def create_ai_tool(self, name: str, description: str, command: str) -> bool:
        """AIツールを作成する。

        Args:
            name: ツール名。
            description: 説明。
            command: 実行コマンド。

        Returns:
            作成成功時はTrue。
        """
        try:
            self.logger.info(
                f'AIツール作成開始: name={name}, description={description}, command={command}'
            )
            ai_tool = AITool(name_ja=name, description=description, command=command)
            self.logger.info(f'AIツールオブジェクト作成完了: id={ai_tool.id}')
            self.repository.save(ai_tool)
            self.logger.info(f'AIツール保存完了: id={ai_tool.id}')
            return True
        except Exception as e:
            self.logger.error(f'AIツール作成エラー: {e}')
            return False

    def update_ai_tool(self, tool_id: AIToolID, name: str, description: str, command: str) -> bool:
        """AIツールを更新する。

        Args:
            tool_id: ツールID。
            name: ツール名。
            description: 説明。
            command: 実行コマンド。

        Returns:
            更新成功時はTrue。
        """
        success = False
        try:
            ai_tool = self.repository.find_by_id(tool_id)
            ai_tool.name_ja = name
            ai_tool.description = description
            ai_tool.command = command
            ai_tool.updated_at = datetime.now(JST)
            self.repository.save(ai_tool)
            success = True
        except ValueError:
            pass
        except Exception as e:
            self.logger.error(f'AIツール更新エラー: {e}')
        return success

    def disable_ai_tool(self, tool_id: AIToolID) -> bool:
        """AIツールを無効化する。

        Args:
            tool_id: ツールID。

        Returns:
            無効化成功時はTrue。
        """
        success = False
        try:
            ai_tool = self.repository.find_by_id(tool_id)
            ai_tool.disabled_at = datetime.now(JST)
            ai_tool.updated_at = datetime.now(JST)
            self.repository.save(ai_tool)
            success = True
        except ValueError:
            pass
        except Exception as e:
            self.logger.error(f'AIツール無効化エラー: {e}')
        return success

    def enable_ai_tool(self, tool_id: AIToolID) -> bool:
        """AIツールを有効化する。

        Args:
            tool_id: ツールID。

        Returns:
            有効化成功時はTrue。
        """
        success = False
        try:
            ai_tool = self.repository.find_by_id(tool_id)
            ai_tool.disabled_at = None
            ai_tool.updated_at = datetime.now(JST)
            self.repository.save(ai_tool)
            success = True
        except ValueError:
            pass
        except Exception as e:
            self.logger.error(f'AIツール有効化エラー: {e}')
        return success
