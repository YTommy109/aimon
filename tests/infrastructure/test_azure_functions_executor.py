import pytest
import requests
from pytest_mock import MockerFixture

from app.errors import APIConfigurationError
from app.infrastructure.ai_executors.azure_functions_executor import GenericAIToolExecutor


class TestAzureFunctionsExecutor:
    def test_execute_uses_endpoint_url(self, mocker: MockerFixture) -> None:
        # Arrange
        executor = GenericAIToolExecutor('test_tool', 'http://localhost:9999/api/ai')
        mock_post = mocker.patch(
            'app.infrastructure.ai_executors.azure_functions_executor.requests.post'
        )
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {'result': 'ok'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Act
        result = executor.execute('テスト内容', [])

        # Assert
        mock_post.assert_called_once()
        called_url = mock_post.call_args[0][0]
        assert called_url == 'http://localhost:9999/api/ai'
        assert result == 'ok'

    def test_execute_raises_on_requests_error(self, mocker: MockerFixture) -> None:
        # Arrange
        executor = GenericAIToolExecutor('test_tool', 'http://localhost:9999/api/ai')
        mock_post = mocker.patch(
            'app.infrastructure.ai_executors.azure_functions_executor.requests.post'
        )
        mock_post.side_effect = requests.RequestException('リクエスト失敗')

        # Act & Assert
        with pytest.raises(APIConfigurationError):
            executor.execute('テスト内容', [])

    def test_execute_raises_on_no_requests(self, mocker: MockerFixture) -> None:
        # Arrange
        executor = GenericAIToolExecutor('test_tool', 'http://dummy')
        mocker.patch('app.infrastructure.ai_executors.azure_functions_executor.requests', None)
        # Act & Assert
        with pytest.raises(APIConfigurationError):
            executor.execute('テスト', [])
