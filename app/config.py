"""アプリケーション設定を管理するモジュール。"""

import os
from pathlib import Path


class Config:
    """アプリケーション設定クラス。"""

    # データファイル関連
    DEFAULT_DATA_DIR = '.data'
    DEFAULT_PROJECTS_FILE = 'projects.json'
    DEFAULT_AI_TOOLS_FILE = 'ai_tools.json'

    # ログ関連
    DEFAULT_LOG_DIR = 'log'
    DEFAULT_LOG_FILE = 'app.log'
    LOG_ROTATION_DAYS = 7

    # API関連
    GEMINI_MODEL_NAME = 'gemini-1.5-flash'
    API_RATE_LIMIT_DELAY = 1.0  # seconds

    # UI関連
    AUTO_REFRESH_INTERVAL = 1000  # milliseconds

    @classmethod
    def get_data_file_path(cls) -> Path:
        """データファイルのパスを取得します。

        環境変数AIMAN_DATA_FILEが設定されている場合はそれを使用し、
        そうでなければデフォルトパスを返します。

        Returns:
            データファイルのPath。
        """
        env_path = os.environ.get('AIMAN_DATA_FILE')
        if env_path:
            return Path(env_path)
        return Path(cls.DEFAULT_DATA_DIR) / cls.DEFAULT_PROJECTS_FILE

    @classmethod
    def get_log_file_path(cls) -> Path:
        """ログファイルのパスを取得します。

        Returns:
            ログファイルのPath。
        """
        return Path(cls.DEFAULT_LOG_DIR) / cls.DEFAULT_LOG_FILE

    @classmethod
    def get_gemini_api_key(cls) -> str | None:
        """Gemini APIキーを環境変数から取得します。

        Returns:
            APIキー文字列。設定されていない場合はNone。
        """
        return os.environ.get('GEMINI_API_KEY')
