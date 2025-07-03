"""メインページのUIを定義するモジュール。"""

import logging
from collections.abc import Callable

import streamlit as st
from streamlit_modal import Modal

from app.config import config
from app.logger import setup_logger
from app.model import DataManager
from app.view.project_creation_form import render_project_creation_form
from app.view.project_detail_modal import render_project_detail_modal
from app.view.project_list import render_project_list

# --- 初期設定 ---
setup_logger()
logger = logging.getLogger('aiman')


@st.cache_resource
def get_data_manager(
    config_provider: Callable[[], DataManager] = lambda: DataManager(config.data_dir_path),
) -> DataManager:
    """セッションごとに一意のDataManagerインスタンスを取得します。

    Args:
        config_provider: DataManagerインスタンスを提供する関数。
            テスト時などに依存性を注入するために使用します。

    Returns:
        DataManagerインスタンス。
    """
    return config_provider()


def render_main_page() -> None:
    """メインページを描画します。"""
    st.set_page_config(
        page_title='AI Meeting Assistant',
        page_icon='🤖',
        layout='wide',
    )

    # セッション状態の初期化
    if 'running_workers' not in st.session_state:
        st.session_state.running_workers = {}

    if 'modal_project' not in st.session_state:
        st.session_state.modal_project = None

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
    # 作成日時の降順でソート
    projects.sort(key=lambda p: p.created_at, reverse=True)
    render_project_list(projects, modal, data_manager)


if __name__ == '__main__':
    render_main_page()
