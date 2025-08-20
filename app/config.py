"""アプリケーション設定を管理するモジュール。"""

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

    def __init__(self) -> None:
        # 動的に .env* を選択
        _, chosen_env_file = _get_environment_config()
        super().__init__(_env_file=chosen_env_file)

    def _get_env_var(self, key: str, default: str | None = None) -> str | None:
        """環境変数を取得する。

        Args:
            key: 環境変数名。
            default: デフォルト値。

        Returns:
            環境変数の値。
        """
        return os.getenv(key, default)

    def _get_env_var_or_default(self, key: str, default: str) -> str:
        """環境変数を取得する。値がNoneの場合はデフォルト値を返す。

        Args:
            key: 環境変数名。
            default: デフォルト値。

        Returns:
            環境変数の値またはデフォルト値。
        """
        return self._get_env_var(key, default) or default

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
        return self._get_env_var_or_default('LLM_PROVIDER', 'openai')

    @property
    def openai_api_key(self) -> str | None:
        """OpenAI APIキーを返す。"""
        return self._get_env_var('OPENAI_API_KEY')

    @property
    def openai_api_base(self) -> str | None:
        """OpenAI APIベースURLを返す。"""
        return self._get_env_var('OPENAI_API_BASE')

    @property
    def openai_model(self) -> str:
        """OpenAIモデル名を返す。"""
        return self._get_env_var_or_default('OPENAI_MODEL', 'gpt-3.5-turbo')

    @property
    def gemini_api_key(self) -> str | None:
        """Gemini APIキーを返す。"""
        return self._get_env_var('GEMINI_API_KEY')

    @property
    def gemini_api_base(self) -> str | None:
        """Gemini APIベースURLを返す。"""
        return self._get_env_var('GEMINI_API_BASE')

    @property
    def gemini_model(self) -> str:
        """Geminiモデル名を返す。"""
        return self._get_env_var_or_default('GEMINI_MODEL', 'gemini-pro')

    @property
    def internal_llm_endpoint(self) -> str | None:
        """社内LLMエンドポイントを返す。"""
        return self._get_env_var('INTERNAL_LLM_ENDPOINT')

    @property
    def internal_llm_api_key(self) -> str | None:
        """社内LLM APIキーを返す。"""
        return self._get_env_var('INTERNAL_LLM_API_KEY')

    @property
    def internal_llm_model(self) -> str:
        """社内LLMモデル名を返す。"""
        return self._get_env_var_or_default('INTERNAL_LLM_MODEL', 'internal-model')


# vulture の誤検知回避用（Pydantic v2 は `model_config` をメタクラス経由で使用）
assert Config.model_config is not None

# グローバルなConfigインスタンスを作成
config = Config()
