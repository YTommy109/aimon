"""LLM呼び出し処理を管理するクライアントクラス。"""

import asyncio
from abc import ABC, abstractmethod

import litellm
from litellm import completion
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from app.config import config
from app.errors import LLMError

__all__ = [
    'GeminiProvider',
    'InternalLLMProvider',
    'LLMClient',
    'LLMError',
    'LLMProvider',
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


class OpenAIProvider(LLMProvider):
    """OpenAI APIプロバイダ。"""

    def __init__(self, api_key: str, api_base: str | None = None):
        """OpenAIプロバイダを初期化する。

        Args:
            api_key: OpenAI APIキー。
            api_base: OpenAI APIベースURL(オプション)。
        """
        self.api_key = api_key
        self.api_base = api_base

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
            return self._extract_content(response)
        except Exception as err:
            raise LLMError(f'OpenAI API呼び出しエラー: {err!s}', 'openai', model, err) from err

    def _setup_environment(self) -> None:
        """環境変数を設定する。"""
        litellm.api_key = self.api_key
        if self.api_base:
            litellm.api_base = self.api_base

    async def _call_api(self, prompt: str, model: str) -> LLMResponse:
        """API呼び出しを実行する。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: completion(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1000,
                temperature=0.7,
            ),
        )

    def _extract_content(self, response: LLMResponse) -> str:
        """レスポンスからテキストを抽出する。"""
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                if isinstance(content, str):
                    return content
                return str(content)
        raise LLMError(f'Unexpected response format from OpenAI: {response}', 'openai', 'unknown')


class GeminiProvider(LLMProvider):
    """Gemini APIプロバイダ。"""

    def __init__(self, api_key: str, api_base: str | None = None):
        """Geminiプロバイダを初期化する。

        Args:
            api_key: Gemini APIキー。
            api_base: Gemini APIベースURL(オプション)。
        """
        self.api_key = api_key
        self.api_base = api_base

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
            response = await self._call_api(prompt, model)
            return self._extract_content(response)
        except Exception as err:
            raise LLMError(f'Gemini API呼び出しエラー: {err!s}', 'gemini', model, err) from err

    def _setup_environment(self) -> None:
        """環境変数を設定する。"""
        litellm.api_key = self.api_key
        if self.api_base:
            litellm.api_base = self.api_base

    async def _call_api(self, prompt: str, model: str) -> LLMResponse:
        """API呼び出しを実行する。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: completion(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1000,
                temperature=0.7,
            ),
        )

    def _extract_content(self, response: LLMResponse) -> str:
        """レスポンスからテキストを抽出する。"""
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                if isinstance(content, str):
                    return content
                return str(content)
        raise LLMError(f'Unexpected response format from Gemini: {response}', 'gemini', 'unknown')


class InternalLLMProvider(LLMProvider):
    """社内LLM APIプロバイダ。"""

    def __init__(self, endpoint: str, api_key: str | None = None):
        """社内LLMプロバイダを初期化する。

        Args:
            endpoint: 社内LLM APIエンドポイント。
            api_key: APIキー(オプション)。
        """
        self.endpoint = endpoint
        self.api_key = api_key

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
            return self._extract_content(response)
        except Exception as err:
            raise LLMError(f'社内LLM API呼び出しエラー: {err!s}', 'internal', model, err) from err

    async def _call_api(self, prompt: str, model: str) -> LLMResponse:
        """API呼び出しを実行する。"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: completion(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1000,
                temperature=0.7,
            ),
        )

    def _extract_content(self, response: LLMResponse) -> str:
        """レスポンスからテキストを抽出する。"""
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                if isinstance(content, str):
                    return content
                return str(content)
        raise LLMError(
            f'Unexpected response format from Internal LLM: {response}', 'internal', 'unknown'
        )


class LLMClient:
    """LLM呼び出し処理を管理するクライアント。"""

    def __init__(self, provider: str | None = None):
        """LLMクライアントを初期化する。

        Args:
            provider: 使用するプロバイダ(openai, gemini, internal)。
                     未指定の場合は環境変数から取得。
        """
        self.provider_name = provider or config.llm_provider
        self._provider: LLMProvider | None = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """プロバイダを初期化する。"""
        try:
            self._initialize_specific_provider()
        except Exception as err:
            raise RuntimeError(f'プロバイダの初期化に失敗しました: {err!s}') from err

    def _initialize_specific_provider(self) -> None:
        """特定のプロバイダを初期化する。"""
        if self.provider_name == 'openai':
            self._initialize_openai_provider()
        elif self.provider_name == 'gemini':
            self._initialize_gemini_provider()
        elif self.provider_name == 'internal':
            self._initialize_internal_provider()
        else:
            raise ValueError(f'サポートされていないプロバイダ: {self.provider_name}')

    def _initialize_openai_provider(self) -> None:
        """OpenAIプロバイダを初期化する。"""
        api_key = config.openai_api_key
        if not api_key:
            raise ValueError(
                'OpenAI APIキーが設定されていません。OPENAI_API_KEY環境変数を設定してください。'
            )

        self._provider = OpenAIProvider(api_key=api_key, api_base=config.openai_api_base)

    def _initialize_gemini_provider(self) -> None:
        """Geminiプロバイダを初期化する。"""
        api_key = config.gemini_api_key
        if not api_key:
            raise ValueError(
                'Gemini APIキーが設定されていません。GEMINI_API_KEY環境変数を設定してください。'
            )

        self._provider = GeminiProvider(api_key=api_key, api_base=config.gemini_api_base)

    def _initialize_internal_provider(self) -> None:
        """社内LLMプロバイダを初期化する。"""
        endpoint = config.internal_llm_endpoint
        if not endpoint:
            raise ValueError(
                '社内LLMエンドポイントが設定されていません。'
                'INTERNAL_LLM_ENDPOINT環境変数を設定してください。'
            )

        self._provider = InternalLLMProvider(endpoint=endpoint, api_key=config.internal_llm_api_key)

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
            raise RuntimeError('プロバイダが初期化されていません')

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
        default_models = {
            'openai': config.openai_model,
            'gemini': config.gemini_model,
            'internal': config.internal_llm_model,
        }

        return default_models.get(self.provider_name, 'default')

    def switch_provider(self, provider: str) -> None:
        """プロバイダを切り替える。

        Args:
            provider: 新しいプロバイダ名。

        Raises:
            ValueError: サポートされていないプロバイダが指定された場合。
            RuntimeError: プロバイダの初期化に失敗した場合。
        """
        self.provider_name = provider
        self._initialize_provider()
