"""ドメインエンティティを定義するモジュール。"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class AITool(BaseModel):
    """AIツールのエンティティ。"""

    id: str
    name_ja: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    disabled_at: datetime | None = None


class ProjectStatus(StrEnum):
    """プロジェクトの状態を表す列挙型。"""

    PENDING = 'Pending'  # 作成済みで実行待ち
    PROCESSING = 'Processing'  # 実行中
    FAILED = 'Failed'  # エラーで終了
    COMPLETED = 'Completed'  # 正常終了


class Project(BaseModel):
    """プロジェクトのエンティティ。"""

    id: UUID = Field(default_factory=uuid4)
    name: str
    source: str
    ai_tool: str
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    executed_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def status(self) -> ProjectStatus:
        """プロジェクトの状態を返します。"""
        match (self.executed_at, self.finished_at, self.result):
            case (None, _, _):
                project_status = ProjectStatus.PENDING
            case (_, None, _):
                project_status = ProjectStatus.PROCESSING
            case (_, _, {'error': _}):
                project_status = ProjectStatus.FAILED
            case _:
                project_status = ProjectStatus.COMPLETED

        return project_status

    def start_processing(self) -> None:
        """プロジェクトの処理を開始します。"""
        self.executed_at = datetime.now(JST)

    def complete(self, result: dict[str, Any]) -> None:
        """プロジェクトを完了状態にします。"""
        self.result = result
        self.finished_at = datetime.now(JST)

    def fail(self, error: dict[str, Any]) -> None:
        """プロジェクトを失敗状態にします。"""
        self.result = error
        self.finished_at = datetime.now(JST)
