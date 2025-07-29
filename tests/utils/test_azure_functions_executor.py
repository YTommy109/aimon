"""Azure Functions エグゼキューターのテストモジュール。"""

from unittest.mock import Mock
from uuid import UUID

import httpx
import pytest
from pytest_mock import MockerFixture

from app.utils.executors.azure_functions_executor import AsyncGenericAIToolExecutor


class TestAsyncGenericAIToolExecutor:
    """AsyncGenericAIToolExecutorのテストクラス。"""

    def test_エグゼキューターが正常に初期化される(self) -> None:
        """エグゼキューターが正常に初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_異なるAIツールIDでエグゼキューターが初期化される(self) -> None:
        """異なるAIツールIDでエグゼキューターが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('87654321-4321-8765-4321-876543210987')
        endpoint_url = 'https://api.example.com/different'

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_空のAIツールIDでエグゼキューターが初期化される(self) -> None:
        """空のAIツールIDでエグゼキューターが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('00000000-0000-0000-0000-000000000000')
        endpoint_url = 'https://api.example.com/test'

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_正常なリクエストが送信される(self, mocker: MockerFixture) -> None:
        """正常なリクエストが送信されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'

        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': 'test result'}

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['success'] is True
        assert result['data'] == 'test result'
        assert result['project_id'] == project_id
        assert result['source_path'] == source_path
        assert result['ai_tool_id'] == str(ai_tool_id)
        assert result['endpoint_url'] == endpoint_url

        # リクエストが正しく送信されたことを確認
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == endpoint_url
        assert call_args[1]['headers']['Content-Type'] == 'application/json'

    def test_HTTPステータスエラーが適切に処理される(self, mocker: MockerFixture) -> None:
        """HTTPステータスエラーが適切に処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'

        # エラーレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.side_effect = httpx.HTTPStatusError(
            '500', request=Mock(), response=mock_response
        )
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act & Assert
        with pytest.raises(Exception, match='HTTPステータスエラー: 500'):
            executor.execute(project_id, source_path)

    def test_リクエストエラーが適切に処理される(self, mocker: MockerFixture) -> None:
        """リクエストエラーが適切に処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.side_effect = httpx.RequestError('Connection error')
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act & Assert
        with pytest.raises(Exception, match='リクエストエラー: Connection error'):
            executor.execute(project_id, source_path)

    def test_JSONデコードエラーが適切に処理される(self, mocker: MockerFixture) -> None:
        """JSONデコードエラーが適切に処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'

        # 無効なJSONレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError('Invalid JSON')

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act & Assert
        with pytest.raises(Exception, match='AIツール実行エラー: Invalid JSON'):
            executor.execute(project_id, source_path)

    def test_ファイルパスが正しく処理される(self, mocker: MockerFixture) -> None:
        """ファイルパスが正しく処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/file.txt'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'file content'

        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': 'test result'}

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['source_path'] == source_path
        # ファイルが正しく読み込まれたことを確認
        mock_open.assert_called_once()

    def test_ディレクトリパスが正しく処理される(self, mocker: MockerFixture) -> None:
        """ディレクトリパスが正しく処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_dir = mocker.patch('pathlib.Path.is_dir')
        mock_rglob = mocker.patch('pathlib.Path.rglob')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/directory'

        # ディレクトリの存在と内容をモック
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_file_paths = [Mock(), Mock()]
        mock_rglob.return_value = mock_file_paths

        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': 'test result'}

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['source_path'] == source_path
        # ディレクトリが正しく処理されたことを確認
        mock_rglob.assert_called_once_with('*')

    def test_単一ファイルが正しく読み込まれる(self, mocker: MockerFixture) -> None:
        """単一ファイルが正しく読み込まれることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_file = mocker.patch('pathlib.Path.is_file')
        mock_open = mocker.patch('builtins.open')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/single_file.txt'

        # ファイルの存在と内容をモック
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = 'single file content'

        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': 'test result'}

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['source_path'] == source_path
        # ファイルが正しく読み込まれたことを確認
        mock_open.assert_called_once()

    def test_ディレクトリが正しく処理される(self, mocker: MockerFixture) -> None:
        """ディレクトリが正しく処理されることをテスト。"""
        # Arrange
        mock_client_class = mocker.patch('httpx.Client')
        mock_exists = mocker.patch('pathlib.Path.exists')
        mock_is_dir = mocker.patch('pathlib.Path.is_dir')
        mock_rglob = mocker.patch('pathlib.Path.rglob')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        endpoint_url = 'https://api.example.com/test'
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)
        project_id = 'test-project'
        source_path = '/path/to/project_directory'

        # ディレクトリの存在と内容をモック
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_file_paths = [Mock(), Mock(), Mock()]
        mock_rglob.return_value = mock_file_paths

        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': 'test result'}

        # モッククライアントの設定
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['source_path'] == source_path
        # ディレクトリが正しく処理されたことを確認
        mock_rglob.assert_called_once_with('*')
