"""LangChain ベースの LLM クライアント。OpenAI / Gemini に対応。"""

from abc import ABC, abstractmethod
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import config
from app.errors import LLMAPICallError, MissingConfigError, ProviderInitializationError
from app.types import LLMProviderName

__all__ = ['GeminiProvider', 'LLMClient', 'LLMProvider', 'LLMProviderName', 'OpenAIProvider']


class LLMProvider(ABC):
    """LLMプロバイダの抽象クラス。"""

    PROVIDER_NAME: LLMProviderName
    _client: Any
    _model: str

    @abstractmethod
    def __init__(self) -> None:
        """サブクラスでクライアントとモデルを初期化する。"""
        raise NotImplementedError

    async def generate_text(self, prompt: str) -> str:
        """プロンプトからテキストを生成する。"""
        try:
            message = await self._client.ainvoke(prompt)
            return str(message.content)
        except Exception as err:
            raise LLMAPICallError(self.PROVIDER_NAME, self._model, err) from err


class OpenAIProvider(LLMProvider):
    """OpenAI 用プロバイダ。"""

    PROVIDER_NAME = LLMProviderName.OPENAI

    def __init__(self, api_key: str, base_url: str | None) -> None:
        self._model = config.openai_model
        self._client = ChatOpenAI(
            model=self._model,
            api_key=SecretStr(api_key),
            base_url=base_url,
        )


class GeminiProvider(LLMProvider):
    """Gemini 用プロバイダ。"""

    PROVIDER_NAME = LLMProviderName.GEMINI

    def __init__(self, api_key: str) -> None:
        self._model = config.gemini_model
        self._client = ChatGoogleGenerativeAI(model=self._model, api_key=SecretStr(api_key))


class LLMClient:
    """LLM呼び出しを管理するクライアント。"""

    def __init__(self, provider: LLMProviderName):
        self._provider_name = provider
        self._provider: LLMProvider | None = None

    def _initialize_provider(self) -> None:
        try:
            factory_map = {
                LLMProviderName.OPENAI: self._create_openai_provider,
                LLMProviderName.GEMINI: self._create_gemini_provider,
            }
            create = factory_map.get(self._provider_name)
            if create is None:
                raise ProviderInitializationError()
            self._provider = create()
        except Exception as err:
            raise ProviderInitializationError() from err

    def _create_openai_provider(self) -> LLMProvider:
        api_key = config.openai_api_key
        if not api_key:
            raise MissingConfigError('OPENAI_API_KEY')
        return OpenAIProvider(api_key, config.openai_api_base)

    def _create_gemini_provider(self) -> LLMProvider:
        api_key = config.gemini_api_key
        if not api_key:
            raise MissingConfigError('GEMINI_API_KEY')
        return GeminiProvider(api_key)

    async def generate_text(self, prompt: str) -> str:
        if self._provider is None:
            self._initialize_provider()
        if self._provider is None:
            raise ProviderInitializationError()
        return await self._provider.generate_text(prompt)
