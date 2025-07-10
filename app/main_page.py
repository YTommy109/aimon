"""メインページのUIを定義するモジュール。"""

import logging
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from streamlit_modal import Modal

from app.application.data_manager import DataManager
from app.config import config
from app.domain.entities import Project
from app.infrastructure.factories import create_data_manager
from app.logger import setup_logger
from app.view.project_creation_form import render_project_creation_form
from app.view.project_detail_modal import render_project_detail_modal
from app.view.project_list import render_project_list

# --- 初期設定 ---
setup_logger()
logger = logging.getLogger('aiman')


@st.cache_resource
def get_data_manager(
    config_provider: Callable[[], DataManager] = lambda: create_data_manager(config.data_dir_path),
) -> DataManager:
    """セッションごとに一意のDataManagerインスタンスを取得します。

    Args:
        config_provider: DataManagerインスタンスを提供する関数。
            テスト時などに依存性を注入するために使用します。

    Returns:
        DataManagerインスタンス。
    """
    return config_provider()


def _get_sort_key(project: Project, jst: ZoneInfo) -> datetime:
    """プロジェクトのソートキーを取得します。"""
    created_at = project.created_at
    # offset-naiveの場合はJST、既にtimezone情報がある場合はそのまま使用
    return created_at.replace(tzinfo=jst) if created_at.tzinfo is None else created_at


def _initialize_session_state() -> None:
    """セッション状態を初期化します。"""
    if 'running_workers' not in st.session_state:
        st.session_state.running_workers = {}
    if 'modal_project' not in st.session_state:
        st.session_state.modal_project = None


def render_main_page() -> None:
    """メインページを描画します。"""
    st.set_page_config(
        page_title='AI Meeting Assistant',
        page_icon='🤖',
        layout='wide',
    )

    _initialize_session_state()
    st.title('AI Meeting Assistant 🤖')

    # データマネージャーの取得
    data_manager = get_data_manager()

    # プロジェクト作成フォーム
    render_project_creation_form(get_data_manager)

    # プロジェクト詳細モーダル
    modal = Modal(title='プロジェクト詳細', key='project_detail_modal')
    render_project_detail_modal(modal)

    # プロジェクト一覧
    projects = data_manager.get_projects()
    jst = ZoneInfo('Asia/Tokyo')
    projects.sort(key=lambda p: _get_sort_key(p, jst), reverse=True)
    render_project_list(projects, modal, data_manager)


if __name__ == '__main__':
    render_main_page()
