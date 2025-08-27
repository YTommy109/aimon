"""ログ設定を管理するモジュール。"""

import logging
import logging.handlers
from typing import TYPE_CHECKING, TextIO

from app.config import get_config

if TYPE_CHECKING:
    from app.config import Config


def _setup_console_handler(config: 'Config') -> logging.StreamHandler[TextIO]:
    """コンソールハンドラーを設定する。"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    return console_handler


def _setup_file_handler(config: 'Config') -> logging.handlers.TimedRotatingFileHandler:
    """ファイルハンドラーを設定する。"""
    log_dir = config.log_file_path.parent
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        config.log_file_path,
        when='midnight',
        interval=1,
        backupCount=config.LOG_ROTATION_DAYS,
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    return file_handler


def _setup_litellm_debug(config: 'Config') -> None:
    """litellm の debug 設定を行う。"""
    if config.LOG_LEVEL == 'DEBUG':
        try:
            import litellm

            litellm._turn_on_debug()  # type: ignore[attr-defined]
            logging.getLogger('aiman').info('litellm debug mode enabled')
        except ImportError:
            # litellm がインストールされていない場合は無視
            pass


# ログレベルの設定
def setup_logging() -> None:
    """ログ設定を初期化する。"""
    config = get_config()

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # ハンドラーの設定
    root_logger.addHandler(_setup_console_handler(config))
    root_logger.addHandler(_setup_file_handler(config))

    # アプリケーション固有のロガーの設定
    app_logger = logging.getLogger('aiman')
    app_logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # 外部ライブラリのログレベルを制御
    # fseventsの大量のDEBUGログを抑制
    logging.getLogger('fsevents').setLevel(logging.WARNING)

    # watchdogのログレベルを制御（inotify_buffer等のDEBUGログを抑制）
    logging.getLogger('watchdog').setLevel(logging.WARNING)

    # その他の外部ライブラリも必要に応じて制御
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    # litellm の debug 設定
    _setup_litellm_debug(config)
