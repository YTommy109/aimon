"""アプリケーション設定を管理するモジュール。"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """アプリケーション設定クラス。"""

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True, extra='ignore')

    # アプリケーション環境
    APP_ENV: str = 'development'

    # データディレクトリ
    DATA_DIR: Path = Path('.data')
    DATA_DIR_TEST: Path = Path('.data_test')

    # デフォルトファイル名
    DEFAULT_PROJECTS_FILE: str = 'projects.json'
    DEFAULT_AI_TOOLS_FILE: str = 'ai_tools.json'

    # ログ設定
    DEFAULT_LOG_DIR: Path = Path('log')
    DEFAULT_LOG_FILE: str = 'app.log'
    LOG_ROTATION_DAYS: int = 7

    # Gemini API設定
    GEMINI_MODEL_NAME: str = 'gemini-1.5-flash'
    API_RATE_LIMIT_DELAY: float = 1.0
    GEMINI_API_KEY: str | None = Field(default=None, validate_default=False)

    # UI設定
    AUTO_REFRESH_INTERVAL: int = 1000  # milliseconds

    @property
    def data_dir_path(self) -> Path:
        """現在の環境に応じたデータディレクトリのパスを返します。"""
        if self.APP_ENV == 'test':
            return self.DATA_DIR_TEST
        return self.DATA_DIR

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
