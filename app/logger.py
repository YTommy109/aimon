import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
from typing import Any

from app.config import config


def _create_console_handler() -> logging.StreamHandler[Any]:
    """コンソールハンドラーを作成する。"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    console_handler.setFormatter(console_formatter)
    return console_handler


def _create_file_handler() -> TimedRotatingFileHandler:
    """ファイルハンドラーを作成する。"""
    log_dir = config.log_file_path.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        config.log_file_path,
        when='D',
        interval=1,
        backupCount=config.LOG_ROTATION_DAYS,
        encoding='utf-8',
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    return file_handler


def setup_logger() -> logging.Logger:
    """アプリケーションロガーをセットアップする。

    'aiman'という名前のロガーを取得し、コンソールとファイルへの出力を設定します。
    ロガーが既に設定済みの場合は、既存のインスタンスを返します。
    ログファイルは日付ベースでローテーションされます。
    """
    logger = logging.getLogger('aiman')

    # 既に設定済みでも、テスト等でハンドラが除去された場合を考慮し再設定
    if not logger.handlers:
        logger.addHandler(_create_console_handler())
        logger.addHandler(_create_file_handler())

    if logger.level == logging.NOTSET:
        logger.setLevel(getattr(logging, config.LOG_LEVEL))

    return logger
