"""ファイルシステム操作の抽象化。"""

import logging
from pathlib import Path
from typing import Protocol

logger = logging.getLogger('aiman')


class FileSystemProtocol(Protocol):
    """ファイルシステム操作のプロトコル。"""

    def read_file(self, path: Path, encoding: str = 'utf-8') -> str:
        """ファイルを読み込む。

        Args:
            path: ファイルパス。
            encoding: エンコーディング。

        Returns:
            ファイルの内容。

        Raises:
            FileNotFoundError: ファイルが見つからない場合。
            OSError: ファイル読み込みに失敗した場合。
        """
        ...

    def write_file(
        self, path: Path, content: str, encoding: str = 'utf-8', create_dirs: bool = True
    ) -> None:
        """ファイルに書き込む。

        Args:
            path: ファイルパス。
            content: 書き込む内容。
            encoding: エンコーディング。
            create_dirs: 親ディレクトリを作成するかどうか。

        Raises:
            OSError: ファイル書き込みに失敗した場合。
        """
        ...

    def list_files(self, path: Path, pattern: str = '*') -> list[Path]:
        """ディレクトリ内のファイルを再帰的に取得する。

        Args:
            path: ディレクトリパス。
            pattern: ファイルパターン (例: '*.py', '*.txt')。

        Returns:
            ファイルパスのリスト。
        """
        ...

    def exists(self, path: Path) -> bool:
        """パスが存在するかチェックする。

        Args:
            path: パス。

        Returns:
            存在する場合True。
        """
        ...

    def is_dir(self, path: Path) -> bool:
        """パスがディレクトリかチェックする。

        Args:
            path: パス。

        Returns:
            ディレクトリの場合True。
        """
        ...

    def is_file(self, path: Path) -> bool:
        """パスがファイルかチェックする。

        Args:
            path: パス。

        Returns:
            ファイルの場合True。
        """
        ...


class RealFileSystem:
    """実際のファイルシステム操作を行う実装クラス。"""

    def read_file(self, path: Path, encoding: str = 'utf-8') -> str:
        """ファイルを読み込む。

        Args:
            path: ファイルパス。
            encoding: エンコーディング。

        Returns:
            ファイルの内容。

        Raises:
            FileNotFoundError: ファイルが見つからない場合。
            OSError: ファイル読み込みに失敗した場合。
        """
        with open(path, encoding=encoding) as f:
            return f.read()

    def write_file(
        self, path: Path, content: str, encoding: str = 'utf-8', create_dirs: bool = True
    ) -> None:
        """ファイルに書き込む。

        Args:
            path: ファイルパス。
            content: 書き込む内容。
            encoding: エンコーディング。
            create_dirs: 親ディレクトリを作成するかどうか。

        Raises:
            OSError: ファイル書き込みに失敗した場合。
        """
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)

    def list_files(self, path: Path, pattern: str = '*') -> list[Path]:
        """ディレクトリ内のファイルを再帰的に取得する。

        Args:
            path: ディレクトリパス。
            pattern: ファイルパターン (例: '*.py', '*.txt')。

        Returns:
            ファイルパスのリスト。
        """
        if not path.exists() or not path.is_dir():
            return []

        return [f for f in path.rglob(pattern) if f.is_file()]

    def exists(self, path: Path) -> bool:
        """パスが存在するかチェックする。

        Args:
            path: パス。

        Returns:
            存在する場合True。
        """
        return path.exists()

    def is_dir(self, path: Path) -> bool:
        """パスがディレクトリかチェックする。

        Args:
            path: パス。

        Returns:
            ディレクトリの場合True。
        """
        return path.is_dir()

    def is_file(self, path: Path) -> bool:
        """パスがファイルかチェックする。

        Args:
            path: パス。

        Returns:
            ファイルの場合True。
        """
        return path.is_file()
