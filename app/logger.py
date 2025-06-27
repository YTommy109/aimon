import logging
import logging.handlers
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from app.config import Config


def setup_logger() -> logging.Logger:
    """アプリケーション全体のロガーを設定します。

    'aiman'という名前のロガーを取得し、ログレベル、フォーマット、
    およびログファイルをローテーションするハンドラを設定します。
    """
    log_dir = Config.DEFAULT_LOG_DIR
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 'aiman'という名前のアプリケーション固有ロガーを取得
    logger = logging.getLogger('aiman')
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    # 親ロガー(root)に伝播させない
    logger.propagate = False

    # 標準出力へのハンドラ
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    # ファイルへのハンドラ（日付ベースでローテーション）
    file_handler = TimedRotatingFileHandler(
        Config.get_log_file_path(),
        when='D',
        interval=1,
        backupCount=Config.LOG_ROTATION_DAYS,
        encoding='utf-8',
    )
    file_handler.setLevel(logging.INFO)

    # フォーマッタの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # ハンドラをロガーに追加
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger
