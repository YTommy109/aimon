"""BM25キーワードインデックスの構築ユーティリティ。"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.utils.base_index_builder import BaseIndexBuilder
from app.utils.tokenizer import JapaneseTokenizer

logger = logging.getLogger('aiman')


class KeywordIndexBuilder(BaseIndexBuilder):
    """BM25キーワードインデックスの構築を管理するクラス。"""

    def __init__(self) -> None:
        """ビルダーを初期化する。"""
        super().__init__()
        self.tokenizer = JapaneseTokenizer()
        # 後方互換性のための属性
        self.keyword_db_name = 'keyword_db'

    def _get_index_db_name(self) -> str:
        """インデックスディレクトリ名を返す。

        Returns:
            インデックスディレクトリ名。
        """
        return self.keyword_db_name

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

        # BM25に最適化された設定でチャンク分割
        chunks = self._split_documents(docs, chunk_size=400, chunk_overlap=50)
        self._save_bm25_index(chunks, index_dir)

    def _tokenize_text(self, text: str) -> list[str]:
        """テキストをトークン化する。

        Args:
            text: トークン化するテキスト。

        Returns:
            トークンのリスト。
        """
        return self.tokenizer.tokenize_text(text)

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
