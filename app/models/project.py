"""プロジェクトのエンティティを定義するモジュール。"""

from datetime import datetime
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from app.types import ProjectID, ProjectStatus, ToolType

# 日本標準時のタイムゾーン
JST = ZoneInfo('Asia/Tokyo')


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
    index_started_at: datetime | None = None
    index_finished_at: datetime | None = None

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

    def start_indexing(self) -> None:
        """インデックス作成を開始します。"""
        self.index_started_at = datetime.now(JST)

    def finish_indexing(self) -> None:
        """インデックス作成を完了します。"""
        if self.index_started_at is None:
            self.index_started_at = datetime.now(JST)
        self.index_finished_at = datetime.now(JST)
