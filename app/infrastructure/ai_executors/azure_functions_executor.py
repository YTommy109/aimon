"""Azure Functions用のAIツール実行クラス。"""

import json
import logging
from typing import Any

import requests
from PIL import Image

from app.domain.ai_tool_executor import AIToolExecutor
from app.errors import APIConfigurationError


class GenericAIToolExecutor(AIToolExecutor):
    """エンドポイントURLを呼び出す汎用AIツール実行クラス。"""

    def __init__(self, ai_tool_id: str, endpoint_url: str) -> None:
        """AIツールエグゼキューターを初期化します。

        Args:
            ai_tool_id: AIツールのID。
            endpoint_url: エンドポイントURL(必須)。
        """
        self.ai_tool_id = ai_tool_id
        self.endpoint_url = endpoint_url

    def execute(self, content: str, images: list[Image.Image]) -> str:
        """エンドポイントURLのAIツールを実行して結果を取得します。
        Args:
            content: 処理対象のテキスト内容。
            images: 処理対象の画像リスト。
        Returns:
            AIツールの実行結果。
        Raises:
            APIConfigurationError: API設定エラーが発生した場合。
            APICallFailedError: API呼び出しに失敗した場合。
        """
        logger = logging.getLogger('aiman')
        payload = {
            'content': content,
            'images': self._convert_images_to_base64(images) if images else [],
        }
        logger.info(f'[GenericAIToolExecutor] POST to {self.endpoint_url} with payload: {payload}')
        response = self._post_request(payload, logger)
        return self._parse_response(response, logger)

    def _post_request(self, payload: dict[str, Any], logger: logging.Logger) -> requests.Response:
        if requests is None:
            raise APIConfigurationError('requests library is required for endpoint integration')
        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60,
            )
            logger.info(
                f'[GenericAIToolExecutor] Response status: {response.status_code}, '
                f'body: {response.text}'
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f'[GenericAIToolExecutor] RequestException: {e}')
            raise APIConfigurationError(str(e)) from e

    def _parse_response(self, response: requests.Response, logger: logging.Logger) -> str:
        try:
            result = response.json()
            logger.info(f'[GenericAIToolExecutor] Parsed result: {result}')
            return str(result.get('result', ''))
        except json.JSONDecodeError as e:
            logger.error(
                f'[GenericAIToolExecutor] JSONDecodeError: {e}, '
                f'response: {getattr(response, "text", None)}'
            )
            raise APIConfigurationError(str(e)) from e

    def _convert_images_to_base64(self, images: list[Image.Image]) -> list[str]:  # noqa: ARG002
        """画像をBase64エンコードされた文字列に変換します。

        Args:
            images: 変換対象の画像リスト。

        Returns:
            Base64エンコードされた画像文字列のリスト。
        """
        # TODO: 画像のBase64エンコード処理を実装
        # 現在は開発段階のため、空リストを返す
        return []
