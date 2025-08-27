"""LLM呼び出し処理を管理するクライアントクラス。"""

import asyncio
from abc import ABC, abstractmethod

import litellm
from litellm import completion
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from app.config import get_config
from app.errors import (
    LLMAPICallError,
    LLMError,
    LLMUnexpectedResponseError,
    MissingConfigError,
    ProviderInitializationError,
)
from app.types import LLMProviderName

__all__ = [
    'GeminiProvider',
    'InternalLLMProvider',
    'LLMClient',
    'LLMError',
    'LLMProvider',
    'LLMProviderName',
    'OpenAIProvider',
]

# 型エイリアス
LLMResponse = ModelResponse | CustomStreamWrapper


class LLMProvider(ABC):
    """LLMプロバイダの抽象基底クラス。"""

    @abstractmethod
    async def generate_text(self, prompt: str, model: str) -> str:
        """テキスト生成を実行する。

        Args:
            prompt: プロンプト。
            model: 使用するモデル名。

        Returns:
            生成されたテキスト。

        Raises:
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """


class BaseLLMProvider(LLMProvider):
    """LLMプロバイダの共通基底クラス。"""

    def __init__(self, api_key: str | None = None, api_base: str | None = None):
        """共通基底クラスを初期化する。

        Args:
            api_key: APIキー。
            api_base: APIベースURL(オプション)。
        """
        self.api_key = api_key
        self.api_base = api_base

    async def _call_api(self, prompt: str, model: str) -> LLMResponse:
        """API呼び出しを実行する。"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: completion(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1000,
                temperature=0.7,
            ),
        )

    def _extract_content(self, response: LLMResponse, provider_name: str, model: str) -> str:
        """レスポンスからテキストを抽出する。

        Args:
            response: LLMレスポンス。
            provider_name: プロバイダ名。

        Returns:
            抽出されたテキスト。

        Raises:
            LLMError: レスポンス形式が予期しない場合。
        """
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                if isinstance(content, str):
                    return content
                return str(content)
        raise LLMUnexpectedResponseError(provider_name, model)

    def _setup_environment(self) -> None:
        """環境変数を設定する。"""
        if self.api_key:
            litellm.api_key = self.api_key
        if self.api_base:
            litellm.api_base = self.api_base


class OpenAIProvider(BaseLLMProvider):
    """OpenAI APIプロバイダ。"""

    async def generate_text(self, prompt: str, model: str) -> str:
        """OpenAI APIを使用してテキスト生成を実行する。

        Args:
            prompt: プロンプト。
            model: 使用するモデル名。

        Returns:
            生成されたテキスト。

        Raises:
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """
        try:
            self._setup_environment()
            response = await self._call_api(prompt, model)
            return self._extract_content(response, 'openai', model)
        except LLMError:
            raise
        except Exception as err:
            raise LLMAPICallError('openai', model, err) from err


class GeminiProvider(BaseLLMProvider):
    """Gemini APIプロバイダ。"""

    async def generate_text(self, prompt: str, model: str) -> str:
        """Gemini APIを使用してテキスト生成を実行する。

        Args:
            prompt: プロンプト。
            model: 使用するモデル名。

        Returns:
            生成されたテキスト。

        Raises:
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """
        try:
            self._setup_environment()
            # Gemini APIを直接呼び出すために、明示的にgeminiプロバイダーを指定
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: completion(
                    model=f'gemini/{model}',
                    messages=[{'role': 'user', 'content': prompt}],
                    max_tokens=1000,
                    temperature=0.7,
                ),
            )
            return self._extract_content(response, 'gemini', model)
        except LLMError:
            raise
        except Exception as err:
            raise LLMAPICallError('gemini', model, err) from err


class InternalLLMProvider(BaseLLMProvider):
    """社内LLM APIプロバイダ。"""

    def __init__(self, endpoint: str, api_key: str | None = None):
        """社内LLMプロバイダを初期化する。

        Args:
            endpoint: 社内LLM APIエンドポイント。
            api_key: APIキー(オプション)。
        """
        super().__init__(api_key)
        self.endpoint = endpoint
        # 固定ヘッダーを設定
        self._headers = {
            'accept': 'application/json',
            'x-request-type': 'sync',
            'x-pool-type': 'shared',
            'Content-Type': 'application/json',
        }

    def _get_headers(self) -> dict[str, str]:
        """ヘッダーを取得する。"""
        headers = self._headers.copy()
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def _call_api(self, prompt: str, _model: str) -> LLMResponse:
        """API呼び出しを実行する。"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: completion(
                model='custom/internal-model',  # litellmの要件を満たすためのダミーモデル名
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1000,
                temperature=0.7,
                api_base=self.endpoint,
                api_key=self.api_key,
                extra_headers=self._get_headers(),
            ),
        )

    async def generate_text(self, prompt: str, model: str) -> str:
        """社内LLM APIを使用してテキスト生成を実行する。

        Args:
            prompt: プロンプト。
            model: 使用するモデル名。

        Returns:
            生成されたテキスト。

        Raises:
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """
        try:
            response = await self._call_api(prompt, model)
            return self._extract_content(response, 'internal', model)
        except LLMError:
            raise
        except Exception as err:
            raise LLMAPICallError('internal', model, err) from err


class LLMClient:
    """LLM呼び出し処理を管理するクライアント。"""

    def __init__(self, provider: str | None = None):
        """LLMクライアントを初期化する。

        Args:
            provider: 使用するプロバイダ(openai, gemini, internal)。
                     未指定の場合は環境変数から取得。
        """
        # 内部的には StrEnum で保持し、外部公開は文字列プロパティで互換性維持
        self._provider_name_value: str | None = provider
        self._provider_name: LLMProviderName | None = None
        self._provider: LLMProvider | None = None
        # プロバイダの初期化は遅延させる

    @property
    def provider_name(self) -> str:
        """現在のプロバイダ名を文字列で返す。"""
        result = None
        if self._provider_name is not None:
            result = self._provider_name.value
        elif self._provider_name_value is not None:
            result = self._provider_name_value
        else:
            # プロバイダが初期化されてない場合は、設定から取得
            result = get_config().llm_provider
        return result

    def _initialize_provider(self) -> None:
        """プロバイダを初期化する。"""
        try:
            # プロバイダ名が指定されてない場合は設定から取得
            if self._provider_name_value is None:
                self._provider_name_value = get_config().llm_provider

            # ここで列挙体へ変換し、例外を固定メッセージの例外で包む
            self._provider_name = LLMProviderName(self._provider_name_value.strip().lower())
            self._initialize_by_match()
        except Exception as err:
            raise ProviderInitializationError() from err

    def _initialize_by_match(self) -> None:
        """プロバイダの種別に応じて初期化する。"""
        match self._provider_name:
            case LLMProviderName.OPENAI:
                self._initialize_openai_provider()
            case LLMProviderName.GEMINI:
                self._initialize_gemini_provider()
            case LLMProviderName.INTERNAL:
                self._initialize_internal_provider()

    def _initialize_openai_provider(self) -> None:
        """OpenAIプロバイダを初期化する。"""
        api_key = get_config().openai_api_key
        if not api_key:
            raise MissingConfigError('OPENAI_API_KEY')

        self._provider = OpenAIProvider(api_key=api_key, api_base=get_config().openai_api_base)

    def _initialize_gemini_provider(self) -> None:
        """Geminiプロバイダを初期化する。"""
        api_key = get_config().gemini_api_key
        if not api_key:
            raise MissingConfigError('GEMINI_API_KEY')

        self._provider = GeminiProvider(api_key=api_key, api_base=get_config().gemini_api_base)

    def _initialize_internal_provider(self) -> None:
        """社内LLMプロバイダを初期化する。"""
        endpoint = get_config().internal_llm_endpoint
        if not endpoint:
            raise MissingConfigError('INTERNAL_LLM_ENDPOINT')

        self._provider = InternalLLMProvider(
            endpoint=endpoint, api_key=get_config().internal_llm_api_key
        )

    async def generate_text(self, prompt: str, model: str | None = None) -> str:
        """テキスト生成を実行する。

        Args:
            prompt: プロンプト。
            model: 使用するモデル名。未指定の場合は環境変数から取得。

        Returns:
            生成されたテキスト。

        Raises:
            RuntimeError: プロバイダが初期化されていない場合。
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """
        if self._provider is None:
            self._initialize_provider()

        # 初期化後もプロバイダがNoneの場合はエラー
        if self._provider is None:
            raise RuntimeError('プロバイダの初期化に失敗しました')

        # モデル名が未指定の場合は環境変数から取得
        model_name = self._get_model_name(model)
        return await self._provider.generate_text(prompt, model_name)

    def _get_model_name(self, model: str | None) -> str:
        """モデル名を取得する。

        Args:
            model: 指定されたモデル名。

        Returns:
            使用するモデル名。
        """
        if model is not None:
            return model

        return self._get_default_model_name()

    def _get_default_model_name(self) -> str:
        """デフォルトのモデル名を取得する。"""
        default_models: dict[LLMProviderName, str] = {
            LLMProviderName.OPENAI: get_config().openai_model,
            LLMProviderName.GEMINI: get_config().gemini_model,
            LLMProviderName.INTERNAL: get_config().internal_llm_model,
        }

        if self._provider_name is None:
            # 初期化前のフォールバック（通常到達しない）
            fallback_map: dict[str, str] = {
                'openai': get_config().openai_model,
                'gemini': get_config().gemini_model,
                'internal': get_config().internal_llm_model,
            }
            provider_name_value = self._provider_name_value or 'openai'
            return fallback_map.get(provider_name_value, 'default')

        return default_models.get(self._provider_name, 'default')
