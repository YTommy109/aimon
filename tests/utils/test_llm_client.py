"""LLMClientクラスのテスト。"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.utils.llm_client import (
    GeminiProvider,
    InternalLLMProvider,
    LLMClient,
    LLMError,
    LLMProvider,
    OpenAIProvider,
)


class TestLLMProvider:
    """LLMProvider抽象クラスのテスト。"""

    def test_llm_provider_is_abstract(self) -> None:
        """LLMProviderが抽象クラスであることを確認する。"""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]


class TestOpenAIProvider:
    """OpenAIProviderクラスのテスト。"""

    def test_openai_provider_initialization(self) -> None:
        """OpenAIProviderの初期化をテストする。"""
        # Arrange
        api_key = 'test_key'
        api_base = 'https://api.openai.com'

        # Act
        provider = OpenAIProvider(api_key, api_base)

        # Assert
        assert provider.api_key == api_key
        assert provider.api_base == api_base

    def test_openai_provider_initialization_without_api_base(self) -> None:
        """APIベースなしでのOpenAIProvider初期化をテストする。"""
        # Arrange
        api_key = 'test_key'

        # Act
        provider = OpenAIProvider(api_key)

        # Assert
        assert provider.api_key == api_key
        assert provider.api_base is None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_openai_provider_generate_text_success(self, mock_completion: MagicMock) -> None:
        """OpenAIProviderのテキスト生成成功をテストする。"""
        # Arrange
        provider = OpenAIProvider('test_key')
        prompt = 'テストプロンプト'
        model = 'gpt-3.5-turbo'

        # モックレスポンスを設定
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'OpenAIからの応答'
        mock_completion.return_value = mock_response

        # Act
        result = await provider.generate_text(prompt, model)

        # Assert
        assert result == 'OpenAIからの応答'
        mock_completion.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_openai_provider_generate_text_api_error(
        self, mock_completion: MagicMock
    ) -> None:
        """OpenAIProviderのAPI呼び出しエラーをテストする。"""
        # Arrange
        provider = OpenAIProvider('test_key')
        prompt = 'テストプロンプト'
        model = 'gpt-3.5-turbo'

        # API呼び出しエラーをシミュレート
        mock_completion.side_effect = Exception('API呼び出しエラー')

        # Act & Assert
        with pytest.raises(LLMError) as exc_info:
            await provider.generate_text(prompt, model)

        assert 'OpenAI API呼び出しエラー' in str(exc_info.value)
        assert exc_info.value.provider == 'openai'
        assert exc_info.value.model == model
        assert exc_info.value.original_error is not None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_openai_provider_generate_text_invalid_response(
        self, mock_completion: MagicMock
    ) -> None:
        """OpenAIProviderの無効なレスポンス形式をテストする。"""
        # Arrange
        provider = OpenAIProvider('test_key')
        prompt = 'テストプロンプト'
        model = 'gpt-3.5-turbo'

        # 無効なレスポンス形式をシミュレート
        mock_response = MagicMock()
        mock_response.choices = []  # 空のchoices
        mock_completion.return_value = mock_response

        # Act & Assert
        with pytest.raises(LLMError) as exc_info:
            await provider.generate_text(prompt, model)

        assert 'Unexpected response format from OpenAI' in str(exc_info.value)
        assert exc_info.value.provider == 'openai'
        assert exc_info.value.model == model


class TestGeminiProvider:
    """GeminiProviderクラスのテスト。"""

    def test_gemini_provider_initialization(self) -> None:
        """GeminiProviderの初期化をテストする。"""
        # Arrange
        api_key = 'test_key'
        api_base = 'https://generativelanguage.googleapis.com'

        # Act
        provider = GeminiProvider(api_key, api_base)

        # Assert
        assert provider.api_key == api_key
        assert provider.api_base == api_base

    def test_gemini_provider_initialization_without_api_base(self) -> None:
        """APIベースなしでのGeminiProvider初期化をテストする。"""
        # Arrange
        api_key = 'test_key'

        # Act
        provider = GeminiProvider(api_key)

        # Assert
        assert provider.api_key == api_key
        assert provider.api_base is None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_gemini_provider_generate_text_success(self, mock_completion: MagicMock) -> None:
        """GeminiProviderのテキスト生成成功をテストする。"""
        # Arrange
        provider = GeminiProvider('test_key')
        prompt = 'テストプロンプト'
        model = 'gemini-pro'

        # モックレスポンスを設定
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = 'Geminiからの応答'
        mock_completion.return_value = mock_response

        # Act
        result = await provider.generate_text(prompt, model)

        # Assert
        assert result == 'Geminiからの応答'
        mock_completion.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_gemini_provider_generate_text_api_error(
        self, mock_completion: MagicMock
    ) -> None:
        """GeminiProviderのAPI呼び出しエラーをテストする。"""
        # Arrange
        provider = GeminiProvider('test_key')
        prompt = 'テストプロンプト'
        model = 'gemini-pro'

        # API呼び出しエラーをシミュレート
        mock_completion.side_effect = Exception('API呼び出しエラー')

        # Act & Assert
        with pytest.raises(LLMError) as exc_info:
            await provider.generate_text(prompt, model)

        assert 'Gemini API呼び出しエラー' in str(exc_info.value)
        assert exc_info.value.provider == 'gemini'
        assert exc_info.value.model == model
        assert exc_info.value.original_error is not None


class TestInternalLLMProvider:
    """InternalLLMProviderクラスのテスト。"""

    def test_internal_llm_provider_initialization(self) -> None:
        """InternalLLMProviderの初期化をテストする。"""
        # Arrange
        endpoint = 'https://internal-llm.example.com'
        api_key = 'test_key'

        # Act
        provider = InternalLLMProvider(endpoint, api_key)

        # Assert
        assert provider.endpoint == endpoint
        assert provider.api_key == api_key

    def test_internal_llm_provider_initialization_without_api_key(self) -> None:
        """APIキーなしでのInternalLLMProvider初期化をテストする。"""
        # Arrange
        endpoint = 'https://internal-llm.example.com'

        # Act
        provider = InternalLLMProvider(endpoint)

        # Assert
        assert provider.endpoint == endpoint
        assert provider.api_key is None

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_internal_llm_provider_generate_text_success(
        self, mock_completion: MagicMock
    ) -> None:
        """InternalLLMProviderのテキスト生成成功をテストする。"""
        # Arrange
        provider = InternalLLMProvider('https://internal-llm.example.com')
        prompt = 'テストプロンプト'
        model = 'internal-model'

        # モックレスポンスを設定
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '社内LLMからの応答'
        mock_completion.return_value = mock_response

        # Act
        result = await provider.generate_text(prompt, model)

        # Assert
        assert result == '社内LLMからの応答'
        mock_completion.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_internal_llm_provider_generate_text_api_error(
        self, mock_completion: MagicMock
    ) -> None:
        """InternalLLMProviderのAPI呼び出しエラーをテストする。"""
        # Arrange
        provider = InternalLLMProvider('https://internal-llm.example.com')
        prompt = 'テストプロンプト'
        model = 'internal-model'

        # API呼び出しエラーをシミュレート
        mock_completion.side_effect = Exception('API呼び出しエラー')

        # Act & Assert
        with pytest.raises(LLMError) as exc_info:
            await provider.generate_text(prompt, model)

        assert '社内LLM API呼び出しエラー' in str(exc_info.value)
        assert exc_info.value.provider == 'internal'
        assert exc_info.value.model == model
        assert exc_info.value.original_error is not None


class TestLLMClient:
    """LLMClientクラスのテスト。"""

    @patch('app.utils.llm_client.config')
    def test_llm_client_initialization_with_provider(self, mock_config: MagicMock) -> None:
        """プロバイダを指定したLLMClientの初期化をテストする。"""
        # Arrange
        mock_config.openai_api_key = 'test_key'
        mock_config.openai_api_base = None

        # Act
        client = LLMClient('openai')

        # Assert
        assert client.provider_name == 'openai'
        assert client._provider is not None

    @patch('app.utils.llm_client.config')
    def test_llm_client_initialization_without_provider(self, mock_config: MagicMock) -> None:
        """プロバイダ未指定でのLLMClientの初期化をテストする。"""
        # Arrange
        mock_config.llm_provider = 'gemini'
        mock_config.gemini_api_key = 'test_key'
        mock_config.gemini_api_base = None

        # Act
        client = LLMClient()

        # Assert
        assert client.provider_name == 'gemini'
        assert client._provider is not None

    @patch('app.utils.llm_client.config')
    def test_llm_client_initialization_missing_api_key(self, mock_config: MagicMock) -> None:
        """APIキーが設定されていない場合の初期化エラーをテストする。"""
        # Arrange
        mock_config.openai_api_key = None

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            LLMClient('openai')

        assert 'プロバイダの初期化に失敗しました' in str(exc_info.value)

    @patch('app.utils.llm_client.config')
    def test_llm_client_initialization_unsupported_provider(self, mock_config: MagicMock) -> None:
        """サポートされていないプロバイダでの初期化エラーをテストする。"""
        # Arrange
        mock_config.openai_api_key = 'test_key'

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            LLMClient('unsupported')

        assert 'プロバイダの初期化に失敗しました' in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_llm_client_generate_text_success(self, mock_completion: MagicMock) -> None:
        """LLMClientのテキスト生成成功をテストする。"""
        # Arrange
        with patch('app.utils.llm_client.config') as mock_config:
            mock_config.openai_api_key = 'test_key'
            mock_config.openai_api_base = None
            mock_config.openai_model = 'gpt-3.5-turbo'

            client = LLMClient('openai')

            # モックレスポンスを設定
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'OpenAIからの応答'
            mock_completion.return_value = mock_response

            # Act
            result = await client.generate_text('テストプロンプト')

            # Assert
            assert result == 'OpenAIからの応答'

    @pytest.mark.asyncio
    @patch('app.utils.llm_client.completion')
    async def test_llm_client_generate_text_with_model(self, mock_completion: MagicMock) -> None:
        """モデルを指定したLLMClientのテキスト生成をテストする。"""
        # Arrange
        with patch('app.utils.llm_client.config') as mock_config:
            mock_config.openai_api_key = 'test_key'
            mock_config.openai_api_base = None

            client = LLMClient('openai')

            # モックレスポンスを設定
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = 'OpenAIからの応答'
            mock_completion.return_value = mock_response

            # Act
            result = await client.generate_text('テストプロンプト', 'custom-model')

            # Assert
            assert result == 'OpenAIからの応答'

    def test_llm_client_generate_text_provider_not_initialized(self) -> None:
        """プロバイダが初期化されていない場合のエラーをテストする。"""
        # Arrange
        client = LLMClient.__new__(LLMClient)
        client._provider = None

        # Act & Assert
        with pytest.raises(RuntimeError, match='プロバイダが初期化されていません'):
            # 非同期メソッドを同期的にテストするため、イベントループを作成
            asyncio.run(client.generate_text('テストプロンプト'))

    @patch('app.utils.llm_client.config')
    def test_llm_client_switch_provider(self, mock_config: MagicMock) -> None:
        """LLMClientのプロバイダ切り替えをテストする。"""
        # Arrange
        mock_config.openai_api_key = 'openai_key'
        mock_config.openai_api_base = None
        mock_config.gemini_api_key = 'gemini_key'
        mock_config.gemini_api_base = None

        client = LLMClient('openai')
        initial_provider = client._provider

        # Act
        client.switch_provider('gemini')

        # Assert
        assert client.provider_name == 'gemini'
        assert client._provider != initial_provider


class TestLLMError:
    """LLMErrorクラスのテスト。"""

    def test_llm_error_initialization(self) -> None:
        """LLMErrorの初期化をテストする。"""
        # Arrange
        message = 'テストエラーメッセージ'
        provider = 'openai'
        model = 'gpt-3.5-turbo'
        original_error = Exception('元のエラー')

        # Act
        error = LLMError(message, provider, model, original_error)

        # Assert
        assert error.message == message
        assert error.provider == provider
        assert error.model == model
        assert error.original_error == original_error
        assert str(error) == message

    def test_llm_error_initialization_without_original_error(self) -> None:
        """元のエラーなしでのLLMError初期化をテストする。"""
        # Arrange
        message = 'テストエラーメッセージ'
        provider = 'gemini'
        model = 'gemini-pro'

        # Act
        error = LLMError(message, provider, model)

        # Assert
        assert error.message == message
        assert error.provider == provider
        assert error.model == model
        assert error.original_error is None
        assert str(error) == message
