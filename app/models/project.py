"""プロジェクトのエンティティを定義するモジュール。"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from . import ProjectID, ToolType

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
    tool: ToolType
    result: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(JST))
    executed_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def status(self) -> ProjectStatus:
        """プロジェクトの状態を返します。"""
        # mypyの型推論を改善するために、明示的な型注釈を使用
        status: ProjectStatus
        if self.executed_at is None:
            status = ProjectStatus.PENDING
        elif self.finished_at is None:
            status = ProjectStatus.PROCESSING
        elif self.result and 'error' in self.result:
            status = ProjectStatus.FAILED
        else:
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
