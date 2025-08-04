"""アプリケーション設定を管理するモジュール。"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """アプリケーション設定クラス。"""

    # アプリケーション環境
    APP_ENV: str = 'development'

    # デフォルトファイル名
    DEFAULT_PROJECTS_FILE: str = 'projects.json'
    DEFAULT_AI_TOOLS_FILE: str = 'ai_tools.json'

    # ログ設定
    DEFAULT_LOG_DIR: Path = Path('log')
    DEFAULT_LOG_FILE: str = 'app.log'
    LOG_ROTATION_DAYS: int = 7
    LOG_LEVEL: str = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # UI設定
    AUTO_REFRESH_INTERVAL: int = 1000  # milliseconds

    # Unixコマンド実行設定
    COMMAND_TIMEOUT: int = 300  # seconds (5 minutes)
    MAX_COMMAND_LENGTH: int = 1000  # characters
    ALLOWED_COMMAND_PREFIXES: list[str] = [
        'python',
        'node',
        'npm',
        'pip',
        'poetry',
        'git',
        'curl',
        'wget',
    ]
    BLOCKED_COMMANDS: list[str] = [
        'rm -rf',
        'sudo',
        'su',
        'chmod 777',
        'passwd',
        'useradd',
        'userdel',
    ]

    @property
    def data_dir_path(self) -> Path:
        """現在の環境に応じたデータディレクトリのパスを返します。"""
        if self.APP_ENV == 'test':
            return Path(os.getenv('DATA_DIR_TEST', '.data_test'))
        return Path(os.getenv('DATA_DIR', '.data'))

    @property
    def data_file_path(self) -> Path:
        """現在の環境に応じたデータファイルのパスを返します。"""
        return self.data_dir_path / self.DEFAULT_PROJECTS_FILE

    @property
    def log_file_path(self) -> Path:
        """ログファイルのパスを返します。"""
        return self.DEFAULT_LOG_DIR / self.DEFAULT_LOG_FILE


# グローバルなConfigインスタンスを作成
config = Config()
