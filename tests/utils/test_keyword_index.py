"""BM25キーワードインデックス構築機能のテスト。"""

import pickle
import tempfile
from pathlib import Path

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.utils.keyword_index import KeywordIndexBuilder, build_keyword_index


class TestKeywordIndexBuilder:
    """KeywordIndexBuilderクラスのテスト。"""

    def test_初期化(self) -> None:
        """KeywordIndexBuilderが正しく初期化される。"""
        # Act
        builder = KeywordIndexBuilder()

        # Assert
        assert builder.target_exts == {'.md', '.txt', '.py'}
        assert builder.keyword_db_name == 'keyword_db'

    def test_無効なディレクトリの場合にインデックス生成をスキップする(self) -> None:
        """無効なディレクトリの場合、インデックス生成をスキップする。"""
        # Arrange
        builder = KeywordIndexBuilder()
        invalid_dir = Path('/nonexistent/directory')
        index_dir = Path('/tmp/test_index')

        # Act
        builder.build_index(invalid_dir, index_dir)

        # Assert
        # エラーが発生せず、処理が完了することを確認
        assert True

    def test_テキストファイルが存在しない場合にインデックス生成をスキップする(self) -> None:
        """対象ファイルが存在しない場合、インデックス生成をスキップする。"""
        # Arrange
        builder = KeywordIndexBuilder()
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # Act
            builder.build_index(source_dir, index_dir)

            # Assert
            # 空のディレクトリでも_ensure_clean_dirが呼ばれるため、ディレクトリは作成される
            # しかし、インデックスファイルは作成されない
            assert index_dir.exists()
            assert not (index_dir / 'bm25_index.pkl').exists()
            assert not (index_dir / 'metadata.pkl').exists()

    def test_ドキュメントの収集とインデックス作成(self) -> None:
        """有効なドキュメントが存在する場合、インデックスを作成する。"""
        # Arrange
        builder = KeywordIndexBuilder()
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # テストファイルを作成
            test_file = source_dir / 'test.txt'
            test_file.write_text('これはテストドキュメントです。BM25インデックスを作成します。')

            # Act
            builder.build_index(source_dir, index_dir)

            # Assert
            assert index_dir.exists()
            assert (index_dir / 'bm25_index.pkl').exists()
            assert (index_dir / 'metadata.pkl').exists()

    def test_複数ファイルのインデックス作成(self) -> None:
        """複数のファイルからインデックスを作成する。"""
        # Arrange
        builder = KeywordIndexBuilder()
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # 複数のテストファイルを作成
            (source_dir / 'file1.txt').write_text('最初のドキュメントです。')
            (source_dir / 'file2.md').write_text('2番目のドキュメントです。')
            (source_dir / 'file3.py').write_text('# Pythonファイルです。')

            # Act
            builder.build_index(source_dir, index_dir)

            # Assert
            assert index_dir.exists()

            # インデックスファイルを読み込み
            with open(index_dir / 'bm25_index.pkl', 'rb') as f:
                bm25_index = pickle.load(f)

            with open(index_dir / 'metadata.pkl', 'rb') as f:
                metadata = pickle.load(f)

            assert isinstance(bm25_index, BM25Okapi)
            assert len(metadata) > 0

    def test_テキストのトークン化(self) -> None:
        """テキストが正しくトークン化される。"""
        # Arrange
        builder = KeywordIndexBuilder()
        text = 'これはテストドキュメントです。BM25インデックスを作成します。'

        # Act
        tokens = builder._tokenize_text(text)

        # Assert
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(token, str) for token in tokens)

    def test_チャンク分割(self) -> None:
        """ドキュメントが適切にチャンクに分割される。"""
        # Arrange
        builder = KeywordIndexBuilder()

        docs = [Document(page_content='長いテキストです。' * 100, metadata={'path': 'test.txt'})]

        # Act
        chunks = builder._split_documents(docs)

        # Assert
        assert len(chunks) > 1  # 長いテキストは複数のチャンクに分割される
        assert all(chunk.page_content for chunk in chunks)

    def test_キーワードデータベースディレクトリの除外(self) -> None:
        """keyword_dbディレクトリ内のファイルは除外される。"""
        # Arrange
        builder = KeywordIndexBuilder()
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # keyword_dbディレクトリ内にファイルを作成
            keyword_db_dir = source_dir / 'keyword_db'
            keyword_db_dir.mkdir()
            (keyword_db_dir / 'ignored.txt').write_text('これは無視されるファイルです。')

            # 通常のファイルを作成
            (source_dir / 'normal.txt').write_text('これは処理されるファイルです。')

            # Act
            builder.build_index(source_dir, index_dir)

            # Assert
            with open(index_dir / 'metadata.pkl', 'rb') as f:
                metadata = pickle.load(f)

            # keyword_db内のファイルは除外され、通常のファイルのみが含まれる
            paths = [item['path'] for item in metadata]
            assert 'normal.txt' in paths
            assert 'keyword_db/ignored.txt' not in paths


class TestBuildKeywordIndex:
    """build_keyword_index関数のテスト。"""

    def test_関数が正常に動作する(self) -> None:
        """build_keyword_index関数が正常に動作する。"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # テストファイルを作成
            test_file = source_dir / 'test.txt'
            test_file.write_text('テストドキュメントです。')

            # Act
            build_keyword_index(source_dir, index_dir)

            # Assert
            assert index_dir.exists()
            assert (index_dir / 'bm25_index.pkl').exists()
            assert (index_dir / 'metadata.pkl').exists()

    def test_空のディレクトリでエラーが発生しない(self) -> None:
        """空のディレクトリでもエラーが発生しない。"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / 'source'
            source_dir.mkdir()
            index_dir = Path(temp_dir) / 'index'

            # Act & Assert
            # エラーが発生しないことを確認
            build_keyword_index(source_dir, index_dir)
            assert True
