"""モデルパッケージの初期化ファイル。"""

from enum import StrEnum
from typing import NewType
from uuid import UUID

# 型安全性のためのカスタムID型
ProjectID = NewType('ProjectID', UUID)


class ToolType(StrEnum):
    OVERVIEW = 'OVERVIEW'
    REVIEW = 'REVIEW'


__all__ = ['ProjectID', 'ToolType']
