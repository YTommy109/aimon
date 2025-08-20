"""共通のボタンハンドラー関数。"""

import logging
from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st


@dataclass
class ModalButtonConfig:
    """モーダルボタンの設定。"""

    data: object
    session_key: str
    open_func: Callable[[], None]


def _log_button_action(log_context: str | None) -> None:
    """ボタンアクションのログを出力する。"""
    if log_context:
        logger = logging.getLogger('aiman')
        logger.info(f'[Streamlit] ボタン押下: {log_context}')


def _display_action_result(
    success: bool, message: str, success_message: str | None, error_message: str | None
) -> None:
    """アクション結果を表示する。"""
    if success:
        display_message = success_message or message
        st.success(display_message)
    else:
        display_message = error_message or message
        st.error(display_message)


def handle_button_action(
    button_clicked: bool,
    action: Callable[[], tuple[bool, str]],
    log_context: str | None = None,
    auto_rerun: bool = False,
) -> None:
    """ボタンアクションの共通処理を行う。

    Args:
        button_clicked: ボタンがクリックされたかどうか。
        action: 実行するアクション関数。
        log_context: ログ出力時のコンテキスト情報。
        auto_rerun: 成功時に自動的にページをリロードするかどうか。
    """
    if not button_clicked:
        return

    # ログ出力
    _log_button_action(log_context)

    # アクション実行
    try:
        success, message = action()

        # メッセージ表示
        _display_action_result(success, message, None, None)

        # 自動リロード
        if success and auto_rerun:
            st.rerun()
    except Exception as e:
        # 予期しないエラーの場合
        logger = logging.getLogger('aiman')
        logger.error(f'[Streamlit] ボタンアクション実行エラー: {e}')
        st.error('予期しないエラーが発生しました。')


def handle_modal_button(
    button_clicked: bool,
    config: ModalButtonConfig,
    log_context: str | None = None,
) -> None:
    """モーダル表示ボタンの共通処理を行う。

    Args:
        button_clicked: ボタンがクリックされたかどうか。
        config: モーダルボタンの設定。
        log_context: ログ出力時のコンテキスト情報。
    """
    if not button_clicked:
        return

    # ログ出力
    _log_button_action(log_context)

    # モーダルデータをセッション状態に保存
    st.session_state[config.session_key] = config.data

    # モーダルを開く
    config.open_func()
