import logging
from uuid import UUID

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_modal import Modal

from app.config import Config
from app.data_manager import DataManager, Project
from app.logger import setup_logger
from app.page_logic import handle_project_creation, handle_project_execution

# --- 初期設定 ---
setup_logger()
logger = logging.getLogger('aiman')


@st.cache_resource
def get_data_manager() -> DataManager:
    """セッションごとに一意のDataManagerインスタンスを取得します。"""
    return DataManager(Config.get_data_file_path())


def refresh_running_workers() -> None:
    """実行中のワーカープロセスをチェックし、終了したものをセッションから削除する"""
    finished_workers = []
    for project_id, worker in st.session_state.get('running_workers', {}).items():
        if not worker.is_alive():
            logger.info(f'Worker for project {project_id} has finished.')
            finished_workers.append(project_id)

    for project_id in finished_workers:
        del st.session_state.running_workers[project_id]


def _initialize_session_state() -> None:
    """セッション状態を初期化します。"""
    if 'running_workers' not in st.session_state:
        st.session_state['running_workers'] = {}
    if 'modal_project' not in st.session_state:
        st.session_state['modal_project'] = None


def _render_project_detail_modal(modal: Modal) -> None:
    """プロジェクト詳細モーダルを描画します。

    Args:
        modal: 表示するModalオブジェクト。
    """
    if modal.is_open():
        with modal.container():
            project = st.session_state.modal_project
            if project:
                is_running = project.id in st.session_state.running_workers
                st.markdown(f'### {project.name}')
                st.markdown(
                    f"""
                    - **UUID**: `{project.id}`
                    - **対象パス**: `{project.source}`
                    - **AIツール**: `{project.ai_tool}`
                    - **ステータス**: `{'Running' if is_running else project.status}`
                    - **作成日時**: `{project.created_at or 'N/A'}`
                    - **実行日時**: `{project.executed_at or 'N/A'}`
                    - **終了日時**: `{project.finished_at or 'N/A'}`
                    """
                )


def _render_project_creation_form() -> None:
    """プロジェクト作成フォームを描画します。"""
    with st.sidebar:
        st.header('プロジェクト作成')
        project_name = st.text_input('プロジェクト名')
        source_dir = st.text_input('対象ディレクトリのパス')
        ai_tools = get_data_manager().get_ai_tools()
        ai_tool_options = {
            tool.id: f'{tool.name_ja} ({tool.description})' for tool in ai_tools
        }
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
                    project_name, source_dir, selected_ai_tool_id, get_data_manager()
                )
                if project:
                    st.success(message)
                else:
                    st.warning(message)
            else:
                st.warning('AIツールを選択してください。')


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
    elif project.status == 'Processing':
        return '⏳'
    elif project.status == 'Completed':
        return '✅'
    elif project.status == 'Failed':
        return '❌'
    else:
        return '💬'


def _render_project_list(projects: list[Project], modal: Modal) -> None:
    """プロジェクト一覧を描画します。

    Args:
        projects: プロジェクトのリスト。
        modal: 詳細表示用のModalオブジェクト。
    """
    st.header('プロジェクト一覧')

    if not projects:
        st.info('まだプロジェクトがありません。')
        return

    header_cols = st.columns((1, 4, 2, 2, 1))
    header_cols[0].write('**No.**')
    header_cols[1].write('**プロジェクト名**')
    header_cols[2].write('**作成日時**')
    header_cols[3].write('**実行日時**')
    st.divider()

    for i, p in enumerate(projects):
        is_running = p.id in st.session_state.running_workers
        status_icon = _get_status_icon(p, is_running)

        row_cols = st.columns((1, 4, 2, 2, 1))
        row_cols[0].write(str(i + 1))
        row_cols[1].write(f'{status_icon} {p.name}')
        row_cols[2].write(
            p.created_at.strftime('%Y/%m/%d %H:%M') if p.created_at else ''
        )
        row_cols[3].write(
            p.executed_at.strftime('%Y/%m/%d %H:%M') if p.executed_at else ''
        )
        if row_cols[4].button('詳細', key=f'detail_{p.id}'):
            st.session_state.modal_project = p
            modal.open()


def _render_project_execution_controls(projects: list[Project]) -> None:
    """プロジェクト実行コントロールを描画します。

    Args:
        projects: プロジェクトのリスト。
    """
    st.divider()

    # --- 実行ボタン ---
    pending_projects = [p for p in projects if p.status == 'Pending']

    def get_project_display_name(project_id: UUID) -> str:
        for i, p in enumerate(projects):
            if p.id == project_id:
                return f'No.{i + 1}: {p.name}'
        return '不明なプロジェクト'

    selected_project_id_str = st.selectbox(
        '実行するプロジェクトを選択してください',
        options=[p.id for p in pending_projects],
        format_func=get_project_display_name,
        index=None,
        placeholder='選択...',
    )
    if st.button('選択したプロジェクトを実行'):
        worker, message = handle_project_execution(
            selected_project_id_str,
            get_data_manager(),
            st.session_state.running_workers,
        )
        if worker:
            st.session_state.running_workers[worker.project_id] = worker
            st.info(message)
            st.rerun()
        else:
            st.warning(message)


def main_page() -> None:
    """アプリケーションのメインページを描画します。

    サイドバー、プロジェクト一覧、詳細モーダルなど、UI全体のレイアウトと
    インタラクションを管理します。
    """
    _initialize_session_state()

    st.set_page_config(page_title='AI-MAN', layout='wide')
    st.title('AI-MAN: AI Multi-Agent Network')

    st_autorefresh(interval=Config.AUTO_REFRESH_INTERVAL, key='main_autorefresh')
    refresh_running_workers()

    # --- モーダル定義 ---
    modal = Modal('プロジェクト詳細', key='details-modal')
    _render_project_detail_modal(modal)

    # --- プロジェクト作成フォーム ---
    _render_project_creation_form()

    # --- プロジェクト一覧と実行コントロール ---
    projects = sorted(
        get_data_manager().get_projects(), key=lambda p: p.created_at, reverse=True
    )

    _render_project_list(projects, modal)

    if projects:  # プロジェクトが存在する場合のみ実行コントロールを表示
        _render_project_execution_controls(projects)


if __name__ == '__main__':
    main_page()
