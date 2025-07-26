"""プロジェクト一覧ページのコンポーネント。"""

import logging

import streamlit as st
from streamlit_modal import Modal

from app.models.project import Project, ProjectStatus
from app.services.project_service import ProjectService


def _get_status_icon(project: Project, is_running: bool) -> str:
    status_icon_map = {
        ProjectStatus.PROCESSING: '⏳',
        ProjectStatus.COMPLETED: '✅',
        ProjectStatus.FAILED: '❌',
    }
    return '🏃' if is_running else status_icon_map.get(project.status, '💬')


def _render_header_columns() -> None:
    """プロジェクト一覧のヘッダーを描画します。"""
    header_cols = st.columns((1, 4, 2, 2, 1, 1))
    header_cols[0].write('**No.**')
    header_cols[1].write('**プロジェクト名**')
    header_cols[2].write('**作成日時**')
    header_cols[3].write('**実行日時**')
    header_cols[4].write('**詳細**')
    header_cols[5].write('**実行**')
    st.divider()


def render_project_list(
    projects: list[Project], modal: Modal, project_service: ProjectService
) -> None:
    """プロジェクト一覧を描画します。

    Args:
        projects: プロジェクトのリスト。
        modal: 詳細表示用のModalオブジェクト。
        project_service: プロジェクトサービス。
    """
    # running_workersの初期化
    if 'running_workers' not in st.session_state:
        st.session_state.running_workers = {}

    st.header('プロジェクト一覧')

    if not projects:
        st.info('まだプロジェクトがありません。')
        return

    _render_header_columns()

    for i, p in enumerate(projects):
        _render_project_row(i, p, modal, project_service)


def _render_project_row(
    index: int,
    project: Project,
    modal: Modal,
    project_service: ProjectService,
) -> None:
    """プロジェクトの各行を描画します。"""
    is_running = project.id in st.session_state.running_workers
    status_icon = _get_status_icon(project, is_running)

    row_cols = st.columns((1, 4, 1, 1, 1, 1))
    row_cols[0].write(str(index + 1))
    row_cols[1].write(f'{status_icon} {project.name}')
    row_cols[2].write(project.created_at.strftime('%Y/%m/%d %H:%M'))
    row_cols[3].write(
        project.executed_at.strftime('%Y/%m/%d %H:%M') if project.executed_at is not None else '',
    )
    detail_btn = row_cols[4].button('詳細', key=f'detail_{project.id}')
    exec_btn = project.executed_at is None and row_cols[5].button('実行', key=f'run_{project.id}')

    _handle_project_buttons(
        {'detail_btn': detail_btn, 'exec_btn': exec_btn},
        project,
        modal,
        project_service,
    )


def _handle_project_buttons(
    button_state: dict[str, bool],
    project: Project,
    modal: Modal,
    project_service: ProjectService,
) -> None:
    """詳細および実行ボタンのアクションを処理"""
    if button_state['detail_btn']:
        st.session_state.modal_project = project
        modal.open()
    if button_state['exec_btn']:
        logger = logging.getLogger('aiman')
        logger.info(
            f'[Streamlit] 実行ボタン押下: project_id={project.id}, ai_tool={project.ai_tool}'
        )
        updated_project, message = project_service.execute_project(str(project.id))
        if updated_project:
            st.info(message)
            st.rerun()
        else:
            st.error(message)
