"""設定モジュールのテスト。"""

from pathlib import Path

from app.config import config


class TestConfig:
    """設定クラスのテストクラス。

    Note:
        テストは .env.test で動作することを前提としている。
        環境変数の切り替えテストは不要な複雑さを生むため削除した。
    """

    def test_デフォルト値が正しく設定される(self) -> None:
        # Act & Assert
        assert Path('log') == config.DEFAULT_LOG_DIR
        assert config.DEFAULT_LOG_FILE == 'app.log'
        assert config.LOG_ROTATION_DAYS == 7

    def test_データディレクトリパスが取得できる(self) -> None:
        # Act
        data_dir = config.data_dir_path

        # Assert
        assert isinstance(data_dir, Path)
        # .env.test の DATA_DIR 設定値が返される
        assert data_dir is not None

    def test_ログファイルパスが取得できる(self) -> None:
        # Act
        log_path = config.log_file_path

        # Assert
        assert log_path == Path('log') / 'app.log'

    def test_LLM設定が取得できる(self) -> None:
        # Act & Assert
        assert config.llm_provider is not None
        assert config.openai_model is not None
        assert config.gemini_model is not None

    def test_埋め込みモデル設定が取得できる(self) -> None:
        # Act & Assert
        assert config.openai_embedding_model is not None
        assert config.gemini_embedding_model is not None
