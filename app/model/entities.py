"""ドメインエンティティを定義するモジュール。"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AITool(BaseModel):
    """AIツールのエンティティ。"""

    id: str
    name_ja: str
    description: str


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
    created_at: datetime = Field(default_factory=datetime.now)
    executed_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def status(self) -> ProjectStatus:
        """プロジェクトの状態を返します。"""
        match (self.executed_at, self.finished_at, self.result):
            case (None, _, _):
                return ProjectStatus.PENDING
            case (_, None, _):
                return ProjectStatus.PROCESSING
            case (_, _, {'error': _}):
                return ProjectStatus.FAILED
            case _:
                return ProjectStatus.COMPLETED

    def start_processing(self) -> None:
        """プロジェクトの処理を開始します。"""
        self.executed_at = datetime.now()

    def complete(self, result: dict[str, Any]) -> None:
        """プロジェクトを完了状態にします。"""
        self.result = result
        self.finished_at = datetime.now()

    def fail(self, error: dict[str, Any]) -> None:
        """プロジェクトを失敗状態にします。"""
        self.result = error
        self.finished_at = datetime.now()
