"""カスタム型の定義。"""

from typing import NewType
from uuid import UUID

# 型安全性のためのカスタムID型
ProjectID = NewType('ProjectID', UUID)
