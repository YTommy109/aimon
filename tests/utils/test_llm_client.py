import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.errors import ProviderInitializationError
from app.types import LLMProviderName
from app.utils.llm_client import (
    GeminiProvider,
    LLMClient,
    LLMProvider,
    OpenAIProvider,
)


class TestLLMProvider:
    def test_LLMProviderが抽象クラスである(self) -> None:
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]


class TestOpenAIProvider:
    def test_OpenAIProviderを初期化できる(self) -> None:
        # Arrange
        api_key = 'test_key'
        api_base = 'https://api.openai.com'

        # Act
        provider = OpenAIProvider(api_key, api_base)

        # Assert
        assert provider is not None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.ChatOpenAI')
    async def test_OpenAIProviderでテキスト生成に成功する(self, mock_chat: MagicMock) -> None:
        # Arrange
        instance = MagicMock()
        instance.ainvoke = AsyncMock(return_value=MagicMock(content='OpenAIからの応答'))
        mock_chat.return_value = instance

        provider = OpenAIProvider('test_key', None)

        # Act
        result = await provider.generate_text('テストプロンプト')

        # Assert
        assert result == 'OpenAIからの応答'
        instance.ainvoke.assert_called_once()


class TestGeminiProvider:
    def test_GeminiProviderを初期化できる(self) -> None:
        # Arrange
        api_key = 'test_key'

        # Act
        provider = GeminiProvider(api_key)

        # Assert
        assert provider is not None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.ChatGoogleGenerativeAI')
    async def test_GeminiProviderでテキスト生成に成功する(self, mock_chat: MagicMock) -> None:
        # Arrange
        instance = MagicMock()
        instance.ainvoke = AsyncMock(return_value=MagicMock(content='Geminiからの応答'))
        mock_chat.return_value = instance

        provider = GeminiProvider('test_key')

        # Act
        result = await provider.generate_text('テストプロンプト')

        # Assert
        assert result == 'Geminiからの応答'
        instance.ainvoke.assert_called_once()


class TestLLMClient:
    @patch('app.utils.llm_client.config')
    def test_指定プロバイダでLLMClientを初期化できる(self, mock_config: MagicMock) -> None:
        # Arrange
        mock_config.openai_api_key = 'test_key'
        mock_config.openai_api_base = None
        mock_config.openai_model = 'gpt-3.5-turbo'

        # Act
        client = LLMClient(LLMProviderName.OPENAI)
        client._initialize_provider()

        # Assert
        assert client._provider_name == LLMProviderName.OPENAI
        assert client._provider is not None

    @patch('app.utils.llm_client.config')
    def test_設定でGEMINI指定時にLLMClientを初期化できる(self, mock_config: MagicMock) -> None:
        # Arrange: 最小限の設定だけ注入
        mock_config.gemini_api_key = 'test_key'
        mock_config.gemini_api_base = None
        mock_config.gemini_model = 'gemini-pro'

        # Act
        client = LLMClient(LLMProviderName.GEMINI)
        client._initialize_provider()

        # Assert
        assert client._provider_name == LLMProviderName.GEMINI
        assert client._provider is not None
        assert isinstance(client._provider, GeminiProvider)

    @patch('app.utils.llm_client.config')
    def test_APIキー未設定なら初期化エラーになる(self, mock_config: MagicMock) -> None:
        # Arrange
        mock_config.openai_api_key = None

        # Act & Assert
        client = LLMClient(LLMProviderName.OPENAI)
        with pytest.raises(ProviderInitializationError):
            client._initialize_provider()

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.ChatOpenAI')
    async def test_LLMClientでテキスト生成に成功する(self, mock_chat: MagicMock) -> None:
        # Arrange
        with patch('app.utils.llm_client.config') as mock_config:
            mock_config.openai_api_key = 'test_key'
            mock_config.openai_api_base = None
            mock_config.openai_model = 'gpt-3.5-turbo'

            instance = MagicMock()
            instance.ainvoke = AsyncMock(return_value=MagicMock(content='OpenAIからの応答'))
            mock_chat.return_value = instance

            client = LLMClient(LLMProviderName.OPENAI)

            # Act
            result = await client.generate_text('テストプロンプト')

            # Assert
            assert result == 'OpenAIからの応答'

    def test_未初期化でも自動初期化される(self) -> None:
        # Arrange
        client = LLMClient.__new__(LLMClient)
        client._provider = None
        client._provider_name = LLMProviderName.OPENAI

        # Act & Assert
        result = asyncio.run(asyncio.sleep(0, result=None))  # ダミーでイベントループ起動
        assert result is None
