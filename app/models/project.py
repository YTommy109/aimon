"""プロジェクトのエンティティを定義するモジュール。"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from . import AIToolID, ProjectID

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


class ProjectStatus(StrEnum):
    """プロジェクトの状態を表す列挙型。"""

    PENDING = 'Pending'  # 作成済みで実行待ち
    PROCESSING = 'Processing'  # 実行中
    FAILED = 'Failed'  # エラーで終了
    COMPLETED = 'Completed'  # 正常終了


class Project(BaseModel):
    """プロジェクトのエンティティ。"""

    id: ProjectID = Field(default_factory=lambda: ProjectID(uuid4()))
    name: str
    source: str
    ai_tool: AIToolID
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    executed_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def status(self) -> ProjectStatus:
        """プロジェクトの状態を返します。"""
        match (self.executed_at, self.finished_at, self.result):
            case (None, _, _):
                status = ProjectStatus.PENDING
            case (_, None, _):
                status = ProjectStatus.PROCESSING
            case (_, _, result) if result and 'error' in result:
                status = ProjectStatus.FAILED
            case _:
                status = ProjectStatus.COMPLETED
        return status

    def start_processing(self) -> None:
        """プロジェクトの処理を開始します。"""
        self.executed_at = datetime.now(JST)

    def complete(self, result: dict[str, Any]) -> None:
        """プロジェクトを完了状態にします。"""
        if self.executed_at is None:
            self.executed_at = datetime.now(JST)
        self.result = result
        self.finished_at = datetime.now(JST)

    def fail(self, error: dict[str, Any]) -> None:
        """プロジェクトを失敗状態にします。"""
        if self.executed_at is None:
            self.executed_at = datetime.now(JST)
        self.result = error
        self.finished_at = datetime.now(JST)
