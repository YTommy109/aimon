"""AIServiceClientクラスのテスト。"""

import pytest
from PIL import Image
from pytest_mock import MockerFixture

import app.infrastructure.external.ai_client as ai_client_module
from app.errors import APICallFailedError, APIKeyNotSetError
from app.infrastructure.external.ai_client import AIServiceClient


class TestAIServiceClient:
    """AIServiceClientクラスのテスト。"""

    def test_AIServiceClientが正しく初期化される(self, mocker: MockerFixture) -> None:
        """AIServiceClientが正しく初期化される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_model = mocker.MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # Act
        client = AIServiceClient()

        # Assert
        mock_genai.configure.assert_called_once_with(api_key='test-api-key')
        mock_genai.GenerativeModel.assert_called_once_with('test-model')
        assert client.model is mock_model

    def test_APIキーが設定されていない場合にAPIKeyNotSetErrorが発生する(
        self, mocker: MockerFixture
    ) -> None:
        """APIキーが設定されていない場合にAPIKeyNotSetErrorが発生する。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_config.GEMINI_API_KEY = None

        # Act & Assert
        with pytest.raises(APIKeyNotSetError):
            AIServiceClient()

    def test_空のAPIキーの場合にAPIKeyNotSetErrorが発生する(self, mocker: MockerFixture) -> None:
        """空のAPIキーの場合にAPIKeyNotSetErrorが発生する。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_config.GEMINI_API_KEY = ''

        # Act & Assert
        with pytest.raises(APIKeyNotSetError):
            AIServiceClient()

    def test_テキストのみの要約が正常に生成される(self, mocker: MockerFixture) -> None:
        """テキストのみの要約が正常に生成される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_time = mocker.patch.object(ai_client_module, 'time')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 1.0

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        mock_response.text = '生成された要約テキスト'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()
        content = 'テスト用のコンテンツ'
        images: list[Image.Image] = []

        # Act
        result = client.generate_summary(content, images)

        # Assert
        assert result == '生成された要約テキスト'
        mock_model.generate_content.assert_called_once()
        mock_time.sleep.assert_called_once_with(1.0)

        # プロンプトの内容を確認
        call_args = mock_model.generate_content.call_args[0][0]
        assert len(call_args) == 1
        assert content in call_args[0]

    def test_画像を含む要約が正常に生成される(self, mocker: MockerFixture) -> None:
        """画像を含む要約が正常に生成される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_time = mocker.patch.object(ai_client_module, 'time')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 1.0

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        mock_response.text = '画像付き要約テキスト'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()
        content = 'テスト用のコンテンツ'
        mock_image1 = mocker.MagicMock(spec=Image.Image)
        mock_image2 = mocker.MagicMock(spec=Image.Image)
        images: list[Image.Image] = [mock_image1, mock_image2]

        # Act
        result = client.generate_summary(content, images)

        # Assert
        assert result == '画像付き要約テキスト'
        mock_model.generate_content.assert_called_once()
        mock_time.sleep.assert_called_once_with(1.0)

        # プロンプトの内容を確認（テキスト + 画像）
        call_args = mock_model.generate_content.call_args[0][0]
        assert len(call_args) == 3  # テキスト + 2つの画像
        assert content in call_args[0]
        assert mock_image1 in call_args
        assert mock_image2 in call_args

    def test_API呼び出し失敗時にAPICallFailedErrorが発生する(self, mocker: MockerFixture) -> None:
        """API呼び出し失敗時にAPICallFailedErrorが発生する。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'

        mock_model = mocker.MagicMock()
        mock_model.generate_content.side_effect = Exception('API呼び出し失敗')
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()
        content = 'テスト用のコンテンツ'
        images: list[Image.Image] = []

        # Act & Assert
        with pytest.raises(APICallFailedError):
            client.generate_summary(content, images)

    def test_レート制限遅延が正しく適用される(self, mocker: MockerFixture) -> None:
        """レート制限遅延が正しく適用される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_time = mocker.patch.object(ai_client_module, 'time')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 2.5  # カスタム遅延時間

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        mock_response.text = 'テスト応答'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()

        # Act
        client.generate_summary('テストコンテンツ', [])

        # Assert
        mock_time.sleep.assert_called_once_with(2.5)

    def test_空のコンテンツでも要約が生成される(self, mocker: MockerFixture) -> None:
        """空のコンテンツでも要約が生成される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mocker.patch.object(ai_client_module, 'time')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 1.0

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        mock_response.text = '空のコンテンツの要約'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()
        content = ''
        images: list[Image.Image] = []

        # Act
        result = client.generate_summary(content, images)

        # Assert
        assert result == '空のコンテンツの要約'
        mock_model.generate_content.assert_called_once()

    def test_応答テキストがstr型で返される(self, mocker: MockerFixture) -> None:
        """応答テキストがstr型で返される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mocker.patch.object(ai_client_module, 'time')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 1.0

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        # レスポンスオブジェクトを模倣
        mock_response.text = 123  # 数値を設定
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        client = AIServiceClient()

        # Act
        result = client.generate_summary('テストコンテンツ', [])

        # Assert
        assert result == '123'  # str()で変換される
        assert isinstance(result, str)

    def test_プロンプトフォーマットが正しく構築される(self, mocker: MockerFixture) -> None:
        """プロンプトフォーマットが正しく構築される。"""
        # Arrange
        mock_config = mocker.patch.object(ai_client_module, 'config')
        mock_genai = mocker.patch.object(ai_client_module, 'genai')
        mock_config.GEMINI_API_KEY = 'test-api-key'
        mock_config.GEMINI_MODEL_NAME = 'test-model'
        mock_config.API_RATE_LIMIT_DELAY = 0

        mock_model = mocker.MagicMock()
        mock_response = mocker.MagicMock()
        mock_response.text = 'テスト応答'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        client = AIServiceClient()
        content = 'テストコンテンツ'
        images: list[Image.Image] = []

        # Act
        client.generate_summary(content, images)

        # Assert
        call_args = mock_model.generate_content.call_args[0][0]
        # プロンプトが特定のフォーマットで構築されることを確認
        assert isinstance(call_args, list)
        assert content in call_args[0]
