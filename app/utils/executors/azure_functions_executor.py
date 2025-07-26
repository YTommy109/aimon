"""Azure Functions用のAIツール実行クラス。"""

import json
import logging
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger('aiman')


class AsyncGenericAIToolExecutor:
    """非同期エンドポイントURLを呼び出す汎用AIツール実行クラス。"""

    def __init__(self, ai_tool_id: str, endpoint_url: str) -> None:
        """AIツールエグゼキューターを初期化します。

        Args:
            ai_tool_id: AIツールのID。
            endpoint_url: エンドポイントURL(必須)。
        """
        self.ai_tool_id = ai_tool_id
        self.endpoint_url = endpoint_url

    def execute(self, project_id: str, source_path: str) -> dict[str, Any]:
        """AIツールを実行します。

        Args:
            project_id: プロジェクトID。
            source_path: ソースディレクトリのパス。

        Returns:
            実行結果の辞書。

        Raises:
            Exception: HTTPリクエストエラーまたはレスポンスエラーの場合。
        """
        logger.debug(
            f'[DEBUG] AsyncGenericAIToolExecutor.execute開始: '
            f'ai_tool_id={self.ai_tool_id}, endpoint_url={self.endpoint_url}, '
            f'project_id={project_id}, source_path={source_path}'
        )

        return self._execute_with_error_handling(project_id, source_path)

    def _execute_with_error_handling(self, project_id: str, source_path: str) -> dict[str, Any]:
        """エラーハンドリング付きでAIツールを実行します。

        Args:
            project_id: プロジェクトID。
            source_path: ソースディレクトリのパス。

        Returns:
            実行結果の辞書。

        Raises:
            Exception: HTTPリクエストエラーまたはレスポンスエラーの場合。
        """
        try:
            return self._execute_successful_request(project_id, source_path)
        except Exception as e:
            self._handle_execution_error(e)
            raise RuntimeError('Unexpected error in execute method') from e

    def _execute_successful_request(self, project_id: str, source_path: str) -> dict[str, Any]:
        """成功時のリクエスト実行を行います。

        Args:
            project_id: プロジェクトID。
            source_path: ソースディレクトリのパス。

        Returns:
            実行結果の辞書。
        """
        payload = self._build_payload(source_path)
        result = self._send_request(payload)
        result = self._add_metadata(result, project_id, source_path)

        logger.debug(f'[DEBUG] AIツール実行完了: result={result}')
        return result

    def _build_payload(self, source_path: str) -> dict[str, Any]:
        """リクエストペイロードを構築します。

        Args:
            source_path: ソースディレクトリのパス。

        Returns:
            リクエストペイロード。
        """
        # source_pathからファイルの内容を読み取る
        text_content = self._read_source_content(source_path)

        return {
            'text': text_content,
        }

    def _read_source_content(self, source_path: str) -> str:
        """ソースパスからファイルの内容を読み取ります。

        Args:
            source_path: ソースディレクトリのパス。

        Returns:
            ファイルの内容。
        """
        try:
            path = Path(source_path)
            return self._get_content_by_path_type(path, source_path)
        except Exception as e:
            logger.error(f'[ERROR] ファイル読み取りエラー: {e}')
            return f'ファイル読み取りエラー: {e}'

    def _get_content_by_path_type(self, path: Path, source_path: str) -> str:
        """パスの種類に応じてコンテンツを取得します。

        Args:
            path: パスオブジェクト。
            source_path: ソースパス文字列。

        Returns:
            ファイルの内容。
        """
        return self._determine_content_type(path, source_path)

    def _determine_content_type(self, path: Path, source_path: str) -> str:
        """パスの種類を判定してコンテンツを取得します。

        Args:
            path: パスオブジェクト。
            source_path: ソースパス文字列。

        Returns:
            ファイルの内容。
        """
        content_handlers = {
            'file': lambda: self._read_single_file(path),
            'dir': lambda: self._read_directory_files(path),
            'not_found': lambda: f'パスが見つかりません: {source_path}',
        }

        path_type = self._get_path_type(path)
        return content_handlers[path_type]()

    def _get_path_type(self, path: Path) -> str:
        """パスの種類を判定します。

        Args:
            path: パスオブジェクト。

        Returns:
            パスの種類('file', 'dir', 'not_found')。
        """
        path_types = {
            'file': path.is_file,
            'dir': path.is_dir,
        }

        for path_type, check_func in path_types.items():
            if check_func():
                return path_type
        return 'not_found'

    def _read_single_file(self, file_path: Path) -> str:
        """単一ファイルの内容を読み取ります。

        Args:
            file_path: ファイルパス。

        Returns:
            ファイルの内容。
        """
        with open(file_path, encoding='utf-8') as f:
            return f.read()

    def _read_directory_files(self, dir_path: Path) -> str:
        """ディレクトリ内の全ファイルの内容を読み取ります。

        Args:
            dir_path: ディレクトリパス。

        Returns:
            全ファイルの内容を結合した文字列。
        """
        content_parts = []
        for file_path in dir_path.rglob('*'):
            if self._should_read_file(file_path):
                file_content = self._read_file_safely(file_path)
                if file_content:
                    content_parts.append(f'=== {file_path.name} ===\n{file_content}\n')
        return '\n'.join(content_parts)

    def _should_read_file(self, file_path: Path) -> bool:
        """ファイルを読み取るべきかどうかを判定します。

        Args:
            file_path: ファイルパス。

        Returns:
            読み取るべき場合はTrue。
        """
        return file_path.is_file() and not file_path.name.startswith('.')

    def _read_file_safely(self, file_path: Path) -> str:
        """ファイルを安全に読み取ります。

        Args:
            file_path: ファイルパス。

        Returns:
            ファイルの内容。読み取れない場合は空文字列。
        """
        try:
            with open(file_path, encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # バイナリファイルはスキップ
            return ''

    def _send_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """HTTPリクエストを送信します。

        Args:
            payload: リクエストペイロード。

        Returns:
            レスポンスのJSONデータ。

        Raises:
            httpx.HTTPStatusError: HTTPステータスエラーの場合。
            httpx.RequestError: リクエストエラーの場合。
            json.JSONDecodeError: JSONデコードエラーの場合。
        """
        logger.debug(f'[DEBUG] HTTPリクエスト送信: url={self.endpoint_url}, payload={payload}')

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.endpoint_url, json=payload, headers={'Content-Type': 'application/json'}
            )

        response.raise_for_status()
        result: dict[str, Any] = response.json()

        logger.debug(
            f'[DEBUG] HTTPレスポンス受信: status_code={response.status_code}, result={result}'
        )
        return result

    def _add_metadata(
        self, result: dict[str, Any], project_id: str, source_path: str
    ) -> dict[str, Any]:
        """結果にメタデータを追加します。

        Args:
            result: 元の結果。
            project_id: プロジェクトID。
            source_path: ソースディレクトリのパス。

        Returns:
            メタデータが追加された結果。
        """
        result.update(
            {
                'project_id': project_id,
                'source_path': source_path,
                'ai_tool_id': self.ai_tool_id,
                'endpoint_url': self.endpoint_url,
            }
        )
        return result

    def _handle_http_status_error(self, e: httpx.HTTPStatusError) -> None:
        """HTTPステータスエラーを処理します。

        Args:
            e: HTTPステータスエラー。

        Raises:
            Exception: エラーメッセージを含む例外。
        """
        logger.error(
            f'[ERROR] HTTPステータスエラー: status_code={e.response.status_code}, '
            f'response={e.response.text}'
        )
        raise Exception(f'HTTPステータスエラー: {e.response.status_code}') from e

    def _handle_request_error(self, e: httpx.RequestError) -> None:
        """リクエストエラーを処理します。

        Args:
            e: リクエストエラー。

        Raises:
            Exception: エラーメッセージを含む例外。
        """
        logger.error(f'[ERROR] HTTPリクエストエラー: {e}')
        raise Exception(f'HTTPリクエストエラー: {e}') from e

    def _handle_json_decode_error(self, e: json.JSONDecodeError) -> None:
        """JSONデコードエラーを処理します。

        Args:
            e: JSONデコードエラー。

        Raises:
            Exception: エラーメッセージを含む例外。
        """
        logger.error(f'[ERROR] JSONデコードエラー: {e}')
        raise Exception(f'JSONデコードエラー: {e}') from e

    def _handle_general_error(self, e: Exception) -> None:
        """一般的なエラーを処理します。

        Args:
            e: 一般的なエラー。

        Raises:
            Exception: エラーメッセージを含む例外。
        """
        logger.error(f'[ERROR] AIツール実行エラー: {e}')
        raise Exception(f'AIツール実行エラー: {e}') from e

    def _handle_execution_error(self, error: Exception) -> None:
        """実行エラーを処理します。

        Args:
            error: 発生したエラー。
        """
        if isinstance(error, httpx.HTTPStatusError):
            self._handle_http_status_error(error)
        elif isinstance(error, httpx.RequestError):
            self._handle_request_error(error)
        elif isinstance(error, json.JSONDecodeError):
            self._handle_json_decode_error(error)
        else:
            self._handle_general_error(error)
