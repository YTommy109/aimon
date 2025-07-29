"""モデルパッケージの初期化ファイル。"""

from typing import NewType
from uuid import UUID

# 型安全性のためのカスタムID型
ProjectID = NewType('ProjectID', UUID)
AIToolID = NewType('AIToolID', UUID)

__all__ = ['AIToolID', 'ProjectID']
