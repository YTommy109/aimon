import streamlit as st
from streamlit_modal import Modal


def render_project_detail_modal(modal: Modal) -> None:
    """プロジェクト詳細モーダルを描画します。

    Args:
        modal: 表示するModalオブジェクト。
    """
    if modal.is_open():
        with modal.container():
            project = st.session_state.modal_project
            if project:
                is_running = project.id in st.session_state.running_workers
                status_text = 'Running' if is_running else project.status.value
                st.markdown(f'### {project.name}')
                st.markdown(
                    f"""
                    - **UUID**: `{project.id}`
                    - **対象パス**: `{project.source}`
                    - **AIツール**: `{project.ai_tool}`
                    - **ステータス**: `{status_text}`
                    - **作成日時**: `{project.created_at or 'N/A'}`
                    - **実行日時**: `{project.executed_at or 'N/A'}`
                    - **終了日時**: `{project.finished_at or 'N/A'}`
                    """
                )
