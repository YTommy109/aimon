"""AIツールのエンティティを定義するモジュール。"""

from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator

from . import AIToolID

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class AITool(BaseModel):
    """AIツールのエンティティ。

    Args:
        id: ツールID。
        name_ja: 日本語名。
        description: ツールの説明。
        command: 実行するコマンド文字列。
        created_at: 作成日時。
        updated_at: 更新日時。
        disabled_at: 無効化日時。
    """

    id: AIToolID = Field(default_factory=lambda: AIToolID(uuid4()))
    name_ja: str
    description: str | None = None
    command: str  # 実行するコマンド文字列（例: "python script.py", "curl -X GET https://api.example.com"）
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    disabled_at: datetime | None = None

    @field_validator('command')
    @classmethod
    def validate_command_not_empty(cls, v: str) -> str:
        """コマンドが空文字列でないことを検証する。"""
        if not v.strip():
            raise ValueError('command cannot be empty')
        return v
