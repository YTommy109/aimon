"""列挙型の定義。"""

from enum import StrEnum


class ToolType(StrEnum):
    """AIツールの種類。"""

    OVERVIEW = 'OVERVIEW'
    REVIEW = 'REVIEW'


class ProjectStatus(StrEnum):
    """プロジェクトの状態を表す列挙型。"""

    PENDING = 'Pending'  # 作成済みで実行待ち
    PROCESSING = 'Processing'  # 実行中
    FAILED = 'Failed'  # エラーで終了
    COMPLETED = 'Completed'  # 正常終了


class LLMProviderName(StrEnum):
    """LLMプロバイダ名。"""

    OPENAI = 'openai'
    GEMINI = 'gemini'
    # INTERNAL は廃止
