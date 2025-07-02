"""ロガーモジュールのテスト。"""

import logging
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from app.config import Config
from app.logger import setup_logger


class TestSetupLogger:
    """`setup_logger`関数のテストクラス。"""

    @pytest.fixture(autouse=True)
    def clean_logger(self) -> None:
        """各テストの実行前に'aiman'ロガーのハンドラをすべて削除し、クリーンな状態にする。"""
        app_logger = logging.getLogger('aiman')
        if app_logger.hasHandlers():
            app_logger.handlers.clear()

    def test_ロガーが正しく設定される(self, mocker: MockerFixture) -> None:
        """setup_loggerを初めて呼び出したときに、ロガーが正しく設定されることを確認する。"""
        # Arrange
        mock_path = Path('/tmp/test.log')
        mocker.patch.object(
            Config,
            'log_file_path',
            new_callable=mocker.PropertyMock,
            return_value=mock_path,
        )

        # Act
        logger = setup_logger()

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'aiman'
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 2  # Console and File handlers

    def test_ロガー設定の冪等性(self, mocker: MockerFixture) -> None:
        """setup_loggerを複数回呼び出しても、ハンドラが重複して追加されないことを確認する。"""
        # Arrange
        mock_path = Path('/tmp/test.log')
        mocker.patch.object(
            Config,
            'log_file_path',
            new_callable=mocker.PropertyMock,
            return_value=mock_path,
        )

        # Act
        logger1 = setup_logger()
        logger2 = setup_logger()

        # Assert
        assert logger1 is logger2
        assert len(logger1.handlers) == 2
