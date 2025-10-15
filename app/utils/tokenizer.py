"""テキストトークン化ユーティリティ。"""

import re


class JapaneseTokenizer:
    """日本語対応のテキストトークナイザー。"""

    # 日本語トークンの最大長（これ以上は分割）
    MAX_JAPANESE_TOKEN_LENGTH = 10
    # 日本語トークンの分割ステップ
    JAPANESE_TOKEN_SPLIT_STEP = 2

    @staticmethod
    def tokenize_text(text: str) -> list[str]:
        """テキストをトークン化する。日本語対応の改善実装。

        Args:
            text: トークン化するテキスト。

        Returns:
            トークンのリスト。
        """
        tokens = []

        # 英数字のトークンを抽出
        tokens.extend(JapaneseTokenizer._extract_alphanumeric_tokens(text))

        # 日本語のトークンを抽出
        tokens.extend(JapaneseTokenizer._extract_japanese_tokens(text))

        # 短すぎるトークンや空白のみのトークンを除去
        return [token for token in tokens if len(token) > 1 and token.strip()]

    @staticmethod
    def _extract_alphanumeric_tokens(text: str) -> list[str]:
        """英数字のトークンを抽出する。

        Args:
            text: 対象テキスト。

        Returns:
            英数字トークンのリスト。
        """
        tokens = []
        for match in re.finditer(r'[a-zA-Z0-9]+', text):
            tokens.append(match.group().lower())
        return tokens

    @staticmethod
    def _extract_japanese_tokens(text: str) -> list[str]:
        """日本語のトークンを抽出する。

        Args:
            text: 対象テキスト。

        Returns:
            日本語トークンのリスト。
        """
        tokens = []
        for match in re.finditer(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', text):
            token = match.group()
            if len(token) > JapaneseTokenizer.MAX_JAPANESE_TOKEN_LENGTH:
                tokens.extend(JapaneseTokenizer._split_long_japanese_token(token))
            else:
                tokens.append(token)
        return tokens

    @staticmethod
    def _split_long_japanese_token(token: str) -> list[str]:
        """長い日本語トークンを分割する。

        Args:
            token: 長い日本語トークン。

        Returns:
            分割されたトークンのリスト。
        """
        split_tokens = []
        for i in range(0, len(token), JapaneseTokenizer.JAPANESE_TOKEN_SPLIT_STEP):
            if i + JapaneseTokenizer.JAPANESE_TOKEN_SPLIT_STEP <= len(token):
                split_tokens.append(token[i : i + JapaneseTokenizer.JAPANESE_TOKEN_SPLIT_STEP])
            else:
                split_tokens.append(token[i:])
        return split_tokens
