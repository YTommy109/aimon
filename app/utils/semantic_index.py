"""FAISSベクタインデックスの構築ユーティリティ。"""

from __future__ import annotations

import logging
import shutil
from contextlib import suppress
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import SecretStr

from app.config import config
from app.types import LLMProviderName
from app.utils.file_processor import read_text

logger = logging.getLogger('aiman')


class SemanticIndexBuilder:
    """FAISSベクタインデックスの構築を管理するクラス。"""

    def __init__(self, provider: LLMProviderName) -> None:
        """ビルダーを初期化する。

        Args:
            provider: 埋め込みプロバイダ。
        """
        self.provider = provider
        self.target_exts = {'.md', '.txt', '.py', '.pdf', '.docx', '.xlsx'}
        self.vector_db_name = 'vector_db'

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
        """プロバイダに応じた埋め込みモデルを返す。"""
        if self.provider == LLMProviderName.OPENAI:
            return OpenAIEmbeddings(
                model=config.openai_embedding_model,
                api_key=SecretStr(config.openai_api_key) if config.openai_api_key else None,
                base_url=config.openai_api_base,
            )
        if self.provider == LLMProviderName.GEMINI:
            return GoogleGenerativeAIEmbeddings(
                model=config.gemini_embedding_model,
                google_api_key=SecretStr(config.gemini_api_key) if config.gemini_api_key else None,
            )
        # 将来的に他を追加する場合はここで分岐
        raise ValueError(f'Unsupported embedding provider: {self.provider}')

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
                and (self.vector_db_name not in p.parts)
            )

        for path in filter(_should_include, source_dir.rglob('*')):
            text = self._read_text(path)
            if not text:
                continue
            rel = str(path.relative_to(source_dir))
            collected.append(Document(page_content=text, metadata={'path': rel}))
        return collected

    def _split_documents(self, docs: list[Document]) -> list[Document]:
        """ドキュメントをチャンクに分割する。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=['\n\n', '\n', ' ', ''],
        )
        return splitter.split_documents(docs)

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
