"""非同期処理のヘルパーユーティリティ。"""

import asyncio
from collections.abc import Coroutine


def run_async[T](coroutine: Coroutine[None, None, T]) -> T:  # noqa: PLR0911
    """イベントループの状態に応じて非同期処理を実行する。

    Args:
        coroutine: 実行するコルーチン。

    Returns:
        コルーチンの実行結果。
    """
    try:
        # 既存のループが実行中かチェック
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # 既存のループが実行中の場合は、新しいループを作成
            return asyncio.run(coroutine)
        # ループが存在するが実行中でない場合
        return loop.run_until_complete(coroutine)
    except RuntimeError:
        # ループが存在しない場合は新しく作成
        return asyncio.run(coroutine)
