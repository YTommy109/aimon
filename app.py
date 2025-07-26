import argparse
import os

# Streamlitはスクリプトを再実行する可能性があるため、引数の解釈と
# グローバルな状態の設定を、他のアプリケーションモジュールをインポートする前に行う。
# これにより、モジュールレベルでの初期化が正しい環境設定で行われることを保証する。


def main() -> None:
    """アプリケーションのエントリポイント。"""
    parser = argparse.ArgumentParser(description='Streamlit app with selectable environment.')
    parser.add_argument(
        '--app-env',
        type=str,
        default='development',
        choices=['development', 'test'],
        help='Application environment (development or test)',
    )
    args = parser.parse_args()

    # configインスタンス生成前に環境変数にセット
    os.environ['APP_ENV'] = args.app_env

    from app.ui.main_page import render_main_page

    render_main_page()


if __name__ == '__main__':
    main()
