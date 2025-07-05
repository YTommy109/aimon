"""AIツール管理ページ。"""

import streamlit as st

from app.config import config
from app.infrastructure.factories import create_data_manager
from app.view.ai_tool_management import render_ai_tool_management_page


def main() -> None:
    """AIツール管理ページのメイン処理。"""
    st.set_page_config(
        page_title='AIツール管理',
        page_icon='🛠️',
        layout='wide',
        initial_sidebar_state='expanded',
    )

    # データマネージャーの設定
    data_manager = create_data_manager(config.data_dir_path)

    # AIツール管理ページの描画
    render_ai_tool_management_page(data_manager)


if __name__ == '__main__':
    main()
