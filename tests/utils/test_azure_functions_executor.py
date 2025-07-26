"""Azure Functions実行クラスのテスト。"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

from app.utils.executors.azure_functions_executor import AsyncGenericAIToolExecutor


class TestAsyncGenericAIToolExecutor:
    """AsyncGenericAIToolExecutorのテストクラス。"""

    def test_AsyncGenericAIToolExecutorが正しく初期化される(self) -> None:
        """AsyncGenericAIToolExecutorが正しく初期化されることをテスト。"""
        # Arrange
        ai_tool_id = 'test-tool-1'
        endpoint_url = 'https://api.example.com/test'

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_異なるパラメータでAsyncGenericAIToolExecutorが初期化される(self) -> None:
        """異なるパラメータでAsyncGenericAIToolExecutorが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = 'another-tool'
        endpoint_url = 'https://api.example.com/another'

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_空文字列のパラメータでAsyncGenericAIToolExecutorが初期化される(self) -> None:
        """空文字列のパラメータでAsyncGenericAIToolExecutorが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = ''
        endpoint_url = ''

        # Act
        executor = AsyncGenericAIToolExecutor(ai_tool_id, endpoint_url)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.endpoint_url == endpoint_url

    def test_ファイルの内容が正しく読み取られる(self) -> None:
        """ファイルの内容が正しく読み取られることをテスト。"""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('テストファイルの内容')
            temp_file_path = f.name

        executor = AsyncGenericAIToolExecutor('test-tool', 'https://api.example.com/test')

        try:
            # Act
            payload = executor._build_payload(temp_file_path)

            # Assert
            assert payload['text'] == 'テストファイルの内容'
        finally:
            Path(temp_file_path).unlink()

    def test_ディレクトリの内容が正しく読み取られる(self) -> None:
        """ディレクトリの内容が正しく読み取られることをテスト。"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # テストファイルを作成
            (temp_path / 'file1.txt').write_text('ファイル1の内容')
            (temp_path / 'file2.txt').write_text('ファイル2の内容')
            (temp_path / '.hidden').write_text('隠しファイル')  # スキップされるべき

            executor = AsyncGenericAIToolExecutor('test-tool', 'https://api.example.com/test')

            # Act
            payload = executor._build_payload(str(temp_path))

            # Assert
            assert '=== file1.txt ===' in payload['text']
            assert 'ファイル1の内容' in payload['text']
            assert '=== file2.txt ===' in payload['text']
            assert 'ファイル2の内容' in payload['text']
            assert '.hidden' not in payload['text']

    def test_存在しないパスの場合の処理(self) -> None:
        """存在しないパスの場合の処理をテスト。"""
        # Arrange
        executor = AsyncGenericAIToolExecutor('test-tool', 'https://api.example.com/test')

        # Act
        payload = executor._build_payload('/nonexistent/path')

        # Assert
        assert 'パスが見つかりません' in payload['text']

    @patch('httpx.Client')
    def test_正常なHTTPリクエストが送信される(self, mock_client_class: Mock) -> None:
        """正常なHTTPリクエストが送信されることをテスト。"""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'data': {'summary': 'テスト結果'}}
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        executor = AsyncGenericAIToolExecutor('test-tool', 'https://api.example.com/test')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('テストファイルの内容')
            temp_file_path = f.name

        try:
            # Act
            result = executor.execute('test-project', temp_file_path)

            # Assert
            assert result['success'] is True
            assert result['data']['summary'] == 'テスト結果'
            assert result['project_id'] == 'test-project'
            assert result['source_path'] == temp_file_path
            assert result['ai_tool_id'] == 'test-tool'
            assert result['endpoint_url'] == 'https://api.example.com/test'

            # HTTPリクエストが正しく送信されたことを確認
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == 'https://api.example.com/test'
            assert call_args[1]['json'] == {'text': 'テストファイルの内容'}
            assert call_args[1]['headers'] == {'Content-Type': 'application/json'}
        finally:
            Path(temp_file_path).unlink()

    @patch('httpx.Client')
    def test_HTTPエラーが適切に処理される(self, mock_client_class: Mock) -> None:
        """HTTPエラーが適切に処理されることをテスト。"""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            '400 Bad Request', request=Mock(), response=mock_response
        )
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        executor = AsyncGenericAIToolExecutor('test-tool', 'https://api.example.com/test')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('テストファイルの内容')
            temp_file_path = f.name

        try:
            # Act & Assert
            with pytest.raises(Exception, match='HTTPステータスエラー: 400'):
                executor.execute('test-project', temp_file_path)
        finally:
            Path(temp_file_path).unlink()
