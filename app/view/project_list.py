"""プロジェクト一覧を表示するコンポーネント。"""

import streamlit as st
from streamlit_modal import Modal

from ..model import DataManager, Project, ProjectStatus
from ..service.execution import handle_project_execution


def _get_status_icon(project: Project, is_running: bool) -> str:
    """プロジェクトのステータスに応じたアイコンを返します。

    Args:
        project: プロジェクトオブジェクト。
        is_running: 実行中かどうかのフラグ。

    Returns:
        ステータスを表すアイコン文字列。
    """
    if is_running:
        return '🏃'
    elif project.status == ProjectStatus.PROCESSING:
        return '⏳'
    elif project.status == ProjectStatus.COMPLETED:
        return '✅'
    elif project.status == ProjectStatus.FAILED:
        return '❌'
    else:
        return '💬'


def _render_header_columns() -> None:
    """プロジェクト一覧のヘッダーを描画します。"""
    header_cols = st.columns((1, 4, 2, 2, 1))
    header_cols[0].write('**No.**')
    header_cols[1].write('**プロジェクト名**')
    header_cols[2].write('**作成日時**')
    header_cols[3].write('**実行日時**')
    st.divider()


def render_project_list(projects: list[Project], modal: Modal, data_manager: DataManager) -> None:
    """プロジェクト一覧を描画します。

    Args:
        projects: プロジェクトのリスト。
        modal: 詳細表示用のModalオブジェクト。
        data_manager: データマネージャーのインスタンス。
    """
    st.header('プロジェクト一覧')

    if not projects:
        st.info('まだプロジェクトがありません。')
        return

    _render_header_columns()

    for i, p in enumerate(projects):
        _render_project_row(i, p, modal, data_manager)


def _render_project_row(
    index: int, project: Project, modal: Modal, data_manager: DataManager
) -> None:
    """プロジェクトの各行を描画します。"""
    is_running = project.id in st.session_state.running_workers
    status_icon = _get_status_icon(project, is_running)

    row_cols = st.columns((1, 4, 1, 1, 1, 1))
    row_cols[0].write(str(index + 1))
    row_cols[1].write(f'{status_icon} {project.name}')
    row_cols[2].write(project.created_at.strftime('%Y/%m/%d %H:%M') if project.created_at else '')
    row_cols[3].write(project.executed_at.strftime('%Y/%m/%d %H:%M') if project.executed_at else '')
    detail_btn = row_cols[4].button('詳細', key=f'detail_{project.id}')
    exec_btn = False
    if project.executed_at is None:
        exec_btn = row_cols[5].button('実行', key=f'run_{project.id}')
    if detail_btn:
        st.session_state.modal_project = project
        modal.open()
    if exec_btn:
        worker, message = handle_project_execution(
            project.id, data_manager, st.session_state.running_workers
        )
        if worker:
            st.info(message)
            st.rerun()
        else:
            st.warning(message)
