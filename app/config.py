"""アプリケーション設定を管理するモジュール。"""

import os
from pathlib import Path


class Config:
    """アプリケーション設定クラス。"""

    # アプリケーション環境
    APP_ENV: str = 'development'

    # データディレクトリ名
    DATA_DIR_DEVELOPMENT = '.data'
    DATA_DIR_TEST = '.data_test'

    # データファイル関連
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
    def get_data_dir_path(cls) -> Path:
        """アプリケーションの環境に応じたデータディレクトリのパスを取得します。

        環境変数を優先し、設定されていなければデフォルト値を使用します。
        - test環境: DATA_DIR_TEST (デフォルト: .data_test)
        - development環境: DATA_DIR (デフォルト: .data)

        Returns:
            データディレクトリのPath。
        """
        if cls.APP_ENV == 'test':
            dir_path = os.environ.get('DATA_DIR_TEST', cls.DATA_DIR_TEST)
        else:  # development
            dir_path = os.environ.get('DATA_DIR', cls.DATA_DIR_DEVELOPMENT)

        return Path(str(dir_path))

    @classmethod
    def get_data_file_path(cls) -> Path:
        """データファイルのパスを取得します。

        環境変数AIMAN_DATA_FILEが設定されている場合はそれを使用し、
        そうでなければアプリケーションの環境に応じたデフォルトパスを返します。

        Returns:
            データファイルのPath。
        """
        env_path = os.environ.get('AIMAN_DATA_FILE')
        if env_path:
            return Path(env_path)
        # アプリケーションの環境に応じたディレクトリパスを取得
        data_dir = cls.get_data_dir_path()
        return data_dir / cls.DEFAULT_PROJECTS_FILE

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
