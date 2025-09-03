import argparse
import logging
import os
from typing import cast

# Streamlitはスクリプトを再実行する可能性があるため、引数の解釈と
# グローバルな状態の設定を、他のアプリケーションモジュールをインポートする前に行う。
# これにより、モジュールレベルでの初期化が正しい環境設定で行われることを保証する。


def _parse_env() -> str:
    """起動引数からアプリケーション環境を取得する。"""
    parser = argparse.ArgumentParser(description='Streamlit app with selectable environment.')
    parser.add_argument(
        '--app-env',
        type=str,
        default='dev',
        choices=['dev', 'test', 'prod'],
        help='Application environment (dev, test, or prod)',
    )
    args = parser.parse_args()
    return cast(str, args.app_env)


def _apply_environment(env: str) -> None:
    """環境変数へ反映。"""
    os.environ['ENV'] = env


def _initialize_config() -> None:
    """設定を初期化する。"""
    # 設定を初期化して、環境変数が正しく読み込まれることを確認
    from app.config import config
    from app.logger import setup_logging

    # ログ設定を初期化
    setup_logging()

    # ログ設定完了を記録
    logger = logging.getLogger('aiman')
    logger.info(f'Logging initialized with level: {config.LOG_LEVEL}')


def main() -> None:
    """アプリケーションのエントリポイント。"""
    env = _parse_env()
    _apply_environment(env)

    # 設定を初期化
    _initialize_config()

    from app.ui.main_page import render_main_page

    render_main_page()


if __name__ == '__main__':
    main()
