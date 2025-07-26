"""AIツール管理ページ。"""

import streamlit as st

from app.config import config
from app.repositories.ai_tool_repository import JsonAIToolRepository
from app.services.ai_tool_service import AIToolService
from app.ui.ai_tool_management import render_ai_tool_management_page


def main() -> None:
    """AIツール管理ページのメイン処理。"""
    st.set_page_config(
        page_title='AIツール管理',
        page_icon='🛠️',
        layout='wide',
        initial_sidebar_state='expanded',
    )

    # AIツールサービスの設定
    ai_tool_repo = JsonAIToolRepository(config.data_dir_path)
    ai_tool_service = AIToolService(ai_tool_repo)

    # AIツール管理ページの描画
    render_ai_tool_management_page(ai_tool_service)


if __name__ == '__main__':
    main()
