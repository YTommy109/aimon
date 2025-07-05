"""AI API呼び出し専門クラス。"""

import time

import google.generativeai as genai
from PIL import Image

from app.config import config
from app.errors import APICallFailedError, APIKeyNotSetError


class AIServiceClient:
    """AI API呼び出し専門クラス。"""

    def __init__(self) -> None:
        """AIサービスクライアントを初期化します。

        Raises:
            APIKeyNotSetError: APIキーが設定されていない場合。
        """
        if not config.GEMINI_API_KEY:
            raise APIKeyNotSetError()

        genai.configure(api_key=config.GEMINI_API_KEY)  # type: ignore[attr-defined]
        self.model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)  # type: ignore[attr-defined]

    def generate_summary(self, content: str, images: list[Image.Image]) -> str:
        """テキストと画像から要約を生成します。

        Args:
            content: 要約対象のテキスト。
            images: 要約対象の画像リスト。

        Returns:
            生成された要約テキスト。

        Raises:
            APICallFailedError: API呼び出しに失敗した場合。
        """
        prompt: list[str | Image.Image] = [
            f'以下の文章と図の内容を日本語で3行で要約し、各図の内容も簡単に解説してください。\\n\\n---\\n{content}',
        ]

        # 画像があればプロンプトに追加
        if images:
            prompt.extend(images)

        try:
            response = self.model.generate_content(prompt)
            # APIのレート制限を考慮
            time.sleep(config.API_RATE_LIMIT_DELAY)
            return str(response.text)
        except Exception as e:
            raise APICallFailedError(e) from e
