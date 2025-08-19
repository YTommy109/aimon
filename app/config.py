"""アプリケーション設定を管理するモジュール。"""

import os
from collections.abc import Mapping
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_env_name(raw_value: str | None) -> str:
    """環境名を正規化して返す。

    Args:
        raw_value: 未正規化の環境名。`dev|test|prod` もしくは `development` など。

    Returns:
        正規化済みの環境名 (`dev`, `test`, `prod`)。未指定時は `dev`。
    """
    if raw_value is None or raw_value.strip() == '':
        return 'dev'
    value = raw_value.strip().lower()
    aliases: dict[str, str] = {
        'development': 'dev',
        'production': 'prod',
        'prod': 'prod',
    }
    return aliases.get(value, value)


def _determine_effective_env(environ: Mapping[str, str] | None = None) -> str:
    """ENV から有効な環境名を決定する。

    未設定なら `dev`。

    Args:
        environ: 参照する環境変数マッピング。未指定なら `os.environ`。

    Returns:
        正規化済みの環境名 (`dev`, `test`, `prod`).
    """
    env = (environ or os.environ).get('ENV')
    if env:
        return _normalize_env_name(env)
    return 'dev'


def _determine_env_file(effective_env: str) -> str:
    """有効な環境に応じた .env ファイルパスを返す。"""
    env_file = '.env.dev'
    if effective_env == 'prod':
        env_file = '.env'
    elif effective_env == 'test':
        env_file = '.env.test'
    return env_file


class Config(BaseSettings):
    """アプリケーション設定クラス。"""

    # .env に未知のキーが含まれていても無視する
    model_config = SettingsConfigDict(extra='ignore')

    # ログ設定
    DEFAULT_LOG_DIR: Path = Path('log')
    DEFAULT_LOG_FILE: str = 'app.log'
    LOG_ROTATION_DAYS: int = 7
    LOG_LEVEL: str = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    def __init__(self) -> None:
        # 動的に .env* を選択
        env_name = _determine_effective_env()
        chosen_env_file = _determine_env_file(env_name)
        super().__init__(_env_file=chosen_env_file)

    @property
    def effective_env(self) -> str:
        """正規化された有効環境名 (`dev|test|prod`)。"""
        return _determine_effective_env()

    @property
    def data_dir_path(self) -> Path:
        """現在の環境に応じたデータディレクトリのパスを返す。

        - 参照優先順位: `DATA_DIR` > 環境別デフォルト
        - デフォルト: `.data`
        """
        default_dir = '.data'
        selected = os.getenv('DATA_DIR', default_dir)
        return Path(selected)

    @property
    def log_file_path(self) -> Path:
        """ログファイルのパスを返す。"""
        return self.DEFAULT_LOG_DIR / self.DEFAULT_LOG_FILE

    # LLM設定
    @property
    def llm_provider(self) -> str:
        """使用するLLMプロバイダを返す。"""
        return os.getenv('LLM_PROVIDER', 'openai')

    @property
    def openai_api_key(self) -> str | None:
        """OpenAI APIキーを返す。"""
        return os.getenv('OPENAI_API_KEY')

    @property
    def openai_api_base(self) -> str | None:
        """OpenAI APIベースURLを返す。"""
        return os.getenv('OPENAI_API_BASE')

    @property
    def openai_model(self) -> str:
        """OpenAIモデル名を返す。"""
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    @property
    def gemini_api_key(self) -> str | None:
        """Gemini APIキーを返す。"""
        return os.getenv('GEMINI_API_KEY')

    @property
    def gemini_api_base(self) -> str | None:
        """Gemini APIベースURLを返す。"""
        return os.getenv('GEMINI_API_BASE')

    @property
    def gemini_model(self) -> str:
        """Geminiモデル名を返す。"""
        return os.getenv('GEMINI_MODEL', 'gemini-pro')

    @property
    def internal_llm_endpoint(self) -> str | None:
        """社内LLMエンドポイントを返す。"""
        return os.getenv('INTERNAL_LLM_ENDPOINT')

    @property
    def internal_llm_api_key(self) -> str | None:
        """社内LLM APIキーを返す。"""
        return os.getenv('INTERNAL_LLM_API_KEY')

    @property
    def internal_llm_model(self) -> str:
        """社内LLMモデル名を返す。"""
        return os.getenv('INTERNAL_LLM_MODEL', 'internal-model')


# vulture の誤検知回避用（Pydantic v2 は `model_config` をメタクラス経由で使用）
assert Config.model_config is not None

# グローバルなConfigインスタンスを作成
config = Config()
