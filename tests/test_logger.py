"""ロガーモジュールのテスト。"""

import logging
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from app.logger import setup_logging


class TestSetupLogging:
    """`setup_logging`関数のテストクラス。"""

    @pytest.fixture(autouse=True)
    def clean_logger(self) -> None:
        """各テストの実行前に'aiman'ロガーのハンドラをすべて削除し、クリーンな状態にする。"""
        app_logger = logging.getLogger('aiman')
        if app_logger.hasHandlers():
            app_logger.handlers.clear()

    def test_ロガーが正しく設定される(self, mocker: MockerFixture) -> None:
        """setup_loggingを初めて呼び出したときに、ロガーが正しく設定されることを確認する。"""
        # Arrange
        mock_config = mocker.MagicMock()
        mock_config.LOG_LEVEL = 'INFO'
        mock_config.log_file_path = Path('/tmp/test.log')
        mocker.patch('app.config.get_config', return_value=mock_config)
        mocker.patch.dict('os.environ', {'LOG_LEVEL': 'INFO'}, clear=True)

        # Act
        setup_logging()

        # Assert
        app_logger = logging.getLogger('aiman')
        assert app_logger.name == 'aiman'
        assert app_logger.level == logging.INFO

    def test_ロガー設定の冪等性(self, mocker: MockerFixture) -> None:
        """setup_loggingを複数回呼び出しても、ハンドラが重複して追加されないことを確認する。"""
        # Arrange
        mock_config = mocker.MagicMock()
        mock_config.LOG_LEVEL = 'INFO'
        mock_config.log_file_path = Path('/tmp/test.log')
        mocker.patch('app.config.get_config', return_value=mock_config)
        mocker.patch.dict('os.environ', {'LOG_LEVEL': 'INFO'}, clear=True)

        # Act
        setup_logging()
        setup_logging()

        # Assert
        app_logger = logging.getLogger('aiman')
        assert app_logger.name == 'aiman'
        assert app_logger.level == logging.INFO
