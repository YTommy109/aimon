"""プロジェクト一覧のUIコンポーネント。"""

import streamlit as st
from streamlit_modal import Modal

from app.models.project import Project
from app.services.project_service import ProjectService
from app.types import ProjectStatus
from app.ui.button_handlers import ModalButtonConfig, handle_button_action, handle_modal_button


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
    # 詳細ボタンの処理
    modal_config = ModalButtonConfig(
        data=project,
        session_key='modal_project',
        open_func=modal.open,
    )
    handle_modal_button(
        button_clicked=button_state['detail_btn'],
        config=modal_config,
        log_context=f'project_id={project.id}',
    )

    # 実行ボタンの処理
    def execute_project_action() -> tuple[bool, str]:
        updated_project, message = project_service.execute_project(project.id)
        return updated_project is not None, message

    handle_button_action(
        button_clicked=button_state['exec_btn'],
        action=execute_project_action,
        log_context=f'project_id={project.id}, tool={project.tool}',
        auto_rerun=True,
    )


__all__ = ['render_project_list', 'st']
