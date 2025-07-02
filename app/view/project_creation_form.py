from collections.abc import Callable

import streamlit as st

from app.model import DataManager
from app.service.project import handle_project_creation


def render_project_creation_form(get_data_manager: Callable[[], DataManager]) -> None:
    """プロジェクト作成フォームを描画します。"""
    with st.sidebar:
        st.header('プロジェクト作成')
        project_name = st.text_input('プロジェクト名')
        source_dir = st.text_input('対象ディレクトリのパス')
        # 入力値の前後空白を除去
        source_dir = source_dir.strip()
        ai_tools = get_data_manager().get_ai_tools()
        ai_tool_options = {tool.id: f'{tool.name_ja} ({tool.description})' for tool in ai_tools}
        selected_ai_tool_id = st.selectbox(
            'AIツールを選択',
            options=list(ai_tool_options.keys()),
            format_func=lambda x: ai_tool_options.get(x, '不明なツール'),
            index=None,
            placeholder='選択...',
        )
        if st.button('プロジェクト作成'):
            if selected_ai_tool_id:
                project, message = handle_project_creation(
                    project_name,
                    source_dir,
                    selected_ai_tool_id,
                    get_data_manager(),
                )
                if project:
                    st.success(message)
                else:
                    st.warning(message)
            else:
                st.warning('AIツールを選択してください。')
