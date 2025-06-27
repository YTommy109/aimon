import logging
from logging.handlers import TimedRotatingFileHandler

import pytest

from app.logger import setup_logger


@pytest.fixture(autouse=True)
def clean_logger() -> None:
    """
    各テストの実行前に'aiman'ロガーのハンドラをすべて削除し、クリーンな状態にする。
    """
    app_logger = logging.getLogger('aiman')
    if app_logger.hasHandlers():
        for handler in app_logger.handlers[:]:
            app_logger.removeHandler(handler)


def test_ロガーが正しく設定される() -> None:
    """setup_loggerを初めて呼び出したときに、ロガーが正しく設定されることを確認する。"""
    # Act
    logger = setup_logger()

    # Assert
    assert logger.name == 'aiman'
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(isinstance(h, TimedRotatingFileHandler) for h in logger.handlers)


def test_ロガー設定の冪等性() -> None:
    """setup_loggerを複数回呼び出しても、ハンドラが重複して追加されないことを確認する。"""
    # Act
    logger1 = setup_logger()
    logger2 = setup_logger()

    # Assert
    assert logger1 is logger2
    assert len(logger1.handlers) == 2
