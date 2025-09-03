"""アプリケーション設定を管理するモジュール。"""

import logging
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_environment_config() -> tuple[str, str]:
    """環境設定を取得する。

    Returns:
        (環境名, .envファイル名)のタプル。
    """
    # 環境変数から環境名を取得
    env = os.getenv('ENV', 'dev').strip().lower()

    # 空文字の場合は 'dev' に変換
    if not env:
        env = 'dev'

    # 環境名の正規化
    env_aliases = {
        'development': 'dev',
        'production': 'prod',
        'prod': 'prod',
    }
    normalized_env = env_aliases.get(env, env)

    # .envファイル名の決定
    env_file_map = {
        'prod': '.env',
        'test': '.env.test',
        'dev': '.env.dev',
    }
    env_file = env_file_map.get(normalized_env, '.env.dev')

    # ログ出力
    logger = logging.getLogger('aiman')
    logger.info(
        f'Environment configuration: ENV={env} -> normalized={normalized_env} -> '
        f'env_file={env_file}'
    )

    return normalized_env, env_file


class Config(BaseSettings):
    """アプリケーション設定クラス。"""

    # .env に未知のキーが含まれていても無視する
    model_config = SettingsConfigDict(extra='ignore')

    # ログ設定
    DEFAULT_LOG_DIR: Path = Path('log')
    DEFAULT_LOG_FILE: str = 'app.log'
    LOG_ROTATION_DAYS: int = 7
    LOG_LEVEL: str = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # データディレクトリ設定（環境変数/環境ファイルから読み込む）
    # pydantic-settings により、`DATA_DIR` 環境変数（.env.* 含む）が
    # フィールド `data_dir` に自動的にマッピングされる
    data_dir: str = '.data'

    # LLM設定
    LLM_PROVIDER: str = 'openai'
    OPENAI_API_KEY: str | None = None
    OPENAI_API_BASE: str | None = None
    OPENAI_MODEL: str = 'gpt-3.5-turbo'
    GEMINI_API_KEY: str | None = None
    GEMINI_API_BASE: str | None = None
    GEMINI_MODEL: str = 'gemini-pro'

    def __init__(self) -> None:
        # 動的に .env* を選択
        normalized_env, chosen_env_file = _get_environment_config()

        # ログ出力
        logger = logging.getLogger('aiman')
        logger.info(
            f'Loading configuration from {chosen_env_file} for environment {normalized_env}'
        )

        super().__init__(_env_file=chosen_env_file)

        # 設定読み込み後のログ出力
        llm_provider = getattr(self, 'LLM_PROVIDER', 'not set')
        logger.info(f'Configuration loaded: data_dir={self.data_dir}, LLM_PROVIDER={llm_provider}')

    @property
    def data_dir_path(self) -> Path:
        """現在の環境に応じたデータディレクトリのパスを返す。

        - 参照優先順位: `DATA_DIR` > 環境別デフォルト
        - デフォルト: `.data`
        """
        return Path(self.data_dir)

    @property
    def log_file_path(self) -> Path:
        """ログファイルのパスを返す。"""
        return self.DEFAULT_LOG_DIR / self.DEFAULT_LOG_FILE

    # LLM設定
    @property
    def llm_provider(self) -> str:
        """使用するLLMプロバイダを返す。"""
        return self.LLM_PROVIDER

    @property
    def openai_api_key(self) -> str | None:
        """OpenAI APIキーを返す。"""
        return self.OPENAI_API_KEY

    @property
    def openai_api_base(self) -> str | None:
        """OpenAI APIベースURLを返す。"""
        return self.OPENAI_API_BASE

    @property
    def openai_model(self) -> str:
        """OpenAIモデル名を返す。"""
        return self.OPENAI_MODEL

    @property
    def gemini_api_key(self) -> str | None:
        """Gemini APIキーを返す。"""
        return self.GEMINI_API_KEY

    @property
    def gemini_api_base(self) -> str | None:
        """Gemini APIベースURLを返す。"""
        return self.GEMINI_API_BASE

    @property
    def gemini_model(self) -> str:
        """Geminiモデル名を返す。"""
        return self.GEMINI_MODEL


# vulture の誤検知回避用（Pydantic v2 は `model_config` をメタクラス経由で使用）
assert Config.model_config is not None


config = Config()


__all__ = ['config']
