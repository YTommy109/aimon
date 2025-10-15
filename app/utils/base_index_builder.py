"""インデックスビルダーの基底クラス。"""

from __future__ import annotations

import logging
import shutil
from abc import ABC, abstractmethod
from contextlib import suppress
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.file_processor import read_text

logger = logging.getLogger('aiman')


class BaseIndexBuilder(ABC):
    """インデックスビルダーの基底クラス。"""

    def __init__(self) -> None:
        """ビルダーを初期化する。"""
        self.target_exts = {'.md', '.txt', '.py', '.pdf', '.docx', '.xlsx'}

    @abstractmethod
    def build_index(self, source_dir: Path, index_dir: Path) -> None:
        """インデックスを構築する。

        Args:
            source_dir: ドキュメントのルートディレクトリ。
            index_dir: 出力するインデックスディレクトリ。
        """

    @abstractmethod
    def _get_index_db_name(self) -> str:
        """インデックスディレクトリ名を返す。

        Returns:
            インデックスディレクトリ名。
        """

    def _read_text(self, path: Path) -> str:
        """ファイルからテキストを抽出する。

        Args:
            path: ファイルパス。

        Returns:
            抽出されたテキスト。
        """
        return read_text(path)

    def _ensure_clean_dir(self, path: Path) -> None:
        """出力ディレクトリを空で作り直す。

        Args:
            path: ディレクトリパス。
        """
        with suppress(Exception):
            shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True, exist_ok=True)

    def _collect_documents(self, source_dir: Path) -> list[Document]:
        """対象ディレクトリからドキュメントを収集する。

        Args:
            source_dir: ソースディレクトリ。

        Returns:
            収集されたドキュメントのリスト。
        """
        collected: list[Document] = []

        def _should_include(p: Path) -> bool:
            return (
                p.is_file()
                and (p.suffix in self.target_exts)
                and (self._get_index_db_name() not in p.parts)
            )

        for path in filter(_should_include, source_dir.rglob('*')):
            text = self._read_text(path)
            if not text:
                continue
            rel = str(path.relative_to(source_dir))
            collected.append(Document(page_content=text, metadata={'path': rel}))
        return collected

    def _split_documents(
        self, docs: list[Document], chunk_size: int = 800, chunk_overlap: int = 100
    ) -> list[Document]:
        """ドキュメントをチャンクに分割する。

        Args:
            docs: ドキュメントのリスト。
            chunk_size: チャンクサイズ。
            chunk_overlap: チャンクのオーバーラップサイズ。

        Returns:
            分割されたドキュメントのリスト。
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=['\n\n', '\n', ' ', ''],
        )
        return splitter.split_documents(docs)
