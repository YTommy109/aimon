"""AIツールのエンティティを定義するモジュール。"""

from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from . import AIToolID

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class AITool(BaseModel):
    """AIツールのエンティティ。

    Args:
        id: ツールID。
        name_ja: 日本語名。
        description: ツールの説明。
        endpoint_url: エンドポイントURL。
        created_at: 作成日時。
        updated_at: 更新日時。
        disabled_at: 無効化日時。
    """

    id: AIToolID = Field(default_factory=lambda: AIToolID(uuid4()))
    name_ja: str
    description: str | None = None
    endpoint_url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    disabled_at: datetime | None = None
