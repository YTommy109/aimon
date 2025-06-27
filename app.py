from app.logger import setup_logger
from app.main_page import main_page


def main() -> None:
    """アプリケーションのエントリーポイント。

    ロガーをセットアップし、メインページ関数を呼び出します。
    """
    setup_logger()
    main_page()


if __name__ == '__main__':
    main()
