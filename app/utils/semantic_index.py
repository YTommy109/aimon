"""FAISSベクタインデックスの構築ユーティリティ。"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.types import LLMProviderName
from app.utils.base_index_builder import BaseIndexBuilder
from app.utils.embeddings_factory import get_embeddings_model

logger = logging.getLogger('aiman')


class SemanticIndexBuilder(BaseIndexBuilder):
    """FAISSベクタインデックスの構築を管理するクラス。"""

    def __init__(self, provider: LLMProviderName) -> None:
        """ビルダーを初期化する。

        Args:
            provider: 埋め込みプロバイダ。
        """
        super().__init__()
        self.provider = provider
        # 後方互換性のための属性
        self.vector_db_name = 'vector_db'

    def _get_index_db_name(self) -> str:
        """インデックスディレクトリ名を返す。

        Returns:
            インデックスディレクトリ名。
        """
        return self.vector_db_name

    def build_index(self, source_dir: Path, index_dir: Path) -> None:
        """指定ディレクトリのテキストを分割・埋め込みし、FAISSを保存する。

        Args:
            source_dir: ドキュメントのルートディレクトリ。
            index_dir: 出力するFAISSディレクトリ(常に上書き)。
        """
        if not source_dir.exists() or not source_dir.is_dir():
            logger.warning(f'インデックス生成をスキップ: 無効なディレクトリ {source_dir}')
            return

        docs = self._collect_documents(source_dir)
        if not docs:
            logger.info(f'インデックス対象なし: {source_dir}')
            self._ensure_clean_dir(index_dir)
            return

        chunks = self._split_documents(docs)
        embeddings = self._get_embeddings()
        self._save_faiss(chunks, embeddings, index_dir)

    def _get_embeddings(self) -> Embeddings:
        """プロバイダに応じた埋め込みモデルを返す。

        Returns:
            埋め込みモデル。
        """
        return get_embeddings_model(self.provider)

    def _save_faiss(self, chunks: list[Document], embeddings: Embeddings, index_dir: Path) -> None:
        """FAISSインデックスを保存する。"""
        self._ensure_clean_dir(index_dir)
        vs = FAISS.from_documents(chunks, embeddings)
        vs.save_local(str(index_dir))


def build_faiss_index(
    source_dir: Path,
    index_dir: Path,
    provider: LLMProviderName,
) -> None:
    """指定ディレクトリのテキストを分割・埋め込みし、FAISSを保存する。

    Args:
        source_dir: ドキュメントのルートディレクトリ。
        index_dir: 出力するFAISSディレクトリ(常に上書き)。
        provider: 埋め込みのプロバイダ(OpenAI/Gemini)。
    """
    builder = SemanticIndexBuilder(provider)
    builder.build_index(source_dir, index_dir)
