"""BM25キーワードインデックスの構築ユーティリティ。"""

from __future__ import annotations

import logging
import pickle
import re
import shutil
from contextlib import suppress
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

from app.utils.file_processor import read_text

logger = logging.getLogger('aiman')


class KeywordIndexBuilder:
    """BM25キーワードインデックスの構築を管理するクラス。"""

    # 日本語トークンの最大長（これ以上は分割）
    MAX_JAPANESE_TOKEN_LENGTH = 10
    # 日本語トークンの分割ステップ
    JAPANESE_TOKEN_SPLIT_STEP = 2

    def __init__(self) -> None:
        """ビルダーを初期化する。"""
        self.target_exts = {'.md', '.txt', '.py', '.pdf', '.docx', '.xlsx'}
        self.keyword_db_name = 'keyword_db'

    def build_index(self, source_dir: Path, index_dir: Path) -> None:
        """指定ディレクトリのテキストを分割・トークン化し、BM25インデックスを保存する。

        Args:
            source_dir: ドキュメントのルートディレクトリ。
            index_dir: 出力するBM25インデックスディレクトリ(常に上書き)。
        """
        if not source_dir.exists() or not source_dir.is_dir():
            logger.warning(f'キーワードインデックス生成をスキップ: 無効なディレクトリ {source_dir}')
            return

        docs = self._collect_documents(source_dir)
        if not docs:
            logger.info(f'キーワードインデックス対象なし: {source_dir}')
            self._ensure_clean_dir(index_dir)
            return

        chunks = self._split_documents(docs)
        self._save_bm25_index(chunks, index_dir)

    def _read_text(self, path: Path) -> str:
        """ファイルからテキストを抽出する(拡張子に応じて委譲)。"""
        return read_text(path)

    def _ensure_clean_dir(self, path: Path) -> None:
        """出力ディレクトリを空で作り直す。"""
        with suppress(Exception):
            shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)

    def _collect_documents(self, source_dir: Path) -> list[Document]:
        """対象ディレクトリからドキュメントを収集する。"""
        collected: list[Document] = []

        def _should_include(p: Path) -> bool:
            return (
                p.is_file()
                and (p.suffix in self.target_exts)
                and (self.keyword_db_name not in p.parts)
            )

        for path in filter(_should_include, source_dir.rglob('*')):
            text = self._read_text(path)
            if not text:
                continue
            rel = str(path.relative_to(source_dir))
            collected.append(Document(page_content=text, metadata={'path': rel}))
        return collected

    def _split_documents(self, docs: list[Document]) -> list[Document]:
        """ドキュメントをチャンクに分割する。BM25に最適化された設定を使用。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # BM25には小さめのチャンクが効果的
            chunk_overlap=50,  # オーバーラップも小さめに設定
            separators=['\n\n', '\n', ' ', ''],
        )
        return splitter.split_documents(docs)

    def _tokenize_text(self, text: str) -> list[str]:
        """テキストをトークン化する。日本語対応の改善実装。"""
        tokens = []

        # 英数字のトークンを抽出
        tokens.extend(self._extract_alphanumeric_tokens(text))

        # 日本語のトークンを抽出
        tokens.extend(self._extract_japanese_tokens(text))

        # 短すぎるトークンや空白のみのトークンを除去
        return [token for token in tokens if len(token) > 1 and token.strip()]

    def _extract_alphanumeric_tokens(self, text: str) -> list[str]:
        """英数字のトークンを抽出する。"""
        tokens = []
        for match in re.finditer(r'[a-zA-Z0-9]+', text):
            tokens.append(match.group().lower())
        return tokens

    def _extract_japanese_tokens(self, text: str) -> list[str]:
        """日本語のトークンを抽出する。"""
        tokens = []
        for match in re.finditer(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', text):
            token = match.group()
            if len(token) > self.MAX_JAPANESE_TOKEN_LENGTH:
                tokens.extend(self._split_long_japanese_token(token))
            else:
                tokens.append(token)
        return tokens

    def _split_long_japanese_token(self, token: str) -> list[str]:
        """長い日本語トークンを分割する。"""
        split_tokens = []
        for i in range(0, len(token), self.JAPANESE_TOKEN_SPLIT_STEP):
            if i + self.JAPANESE_TOKEN_SPLIT_STEP <= len(token):
                split_tokens.append(token[i : i + self.JAPANESE_TOKEN_SPLIT_STEP])
            else:
                split_tokens.append(token[i:])
        return split_tokens

    def _save_bm25_index(self, chunks: list[Document], index_dir: Path) -> None:
        """BM25インデックスを保存する。"""
        self._ensure_clean_dir(index_dir)

        # ドキュメントをトークン化
        tokenized_docs = [self._tokenize_text(chunk.page_content) for chunk in chunks]

        # BM25インデックスを構築
        bm25 = BM25Okapi(tokenized_docs)

        # インデックスとメタデータを保存
        index_path = index_dir / 'bm25_index.pkl'
        metadata_path = index_dir / 'metadata.pkl'

        with open(index_path, 'wb') as f:
            pickle.dump(bm25, f)

        # チャンクのメタデータを保存
        metadata = [
            {'path': chunk.metadata.get('path', ''), 'content': chunk.page_content}
            for chunk in chunks
        ]
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

        logger.info(f'BM25インデックスを保存: {index_dir} ({len(chunks)}個のチャンク)')


def build_keyword_index(source_dir: Path, index_dir: Path) -> None:
    """指定ディレクトリのテキストを分割・トークン化し、BM25インデックスを保存する。

    Args:
        source_dir: ドキュメントのルートディレクトリ。
        index_dir: 出力するBM25インデックスディレクトリ(常に上書き)。
    """
    builder = KeywordIndexBuilder()
    builder.build_index(source_dir, index_dir)
