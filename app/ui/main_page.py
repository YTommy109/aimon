"""メインページのUIを定義するモジュール。"""

import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st
from streamlit_modal import Modal

from app.config import config
from app.logger import setup_logger
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.services.project_service import ProjectService
from app.ui.project_creation_form import render_project_creation_form
from app.ui.project_detail_modal import render_project_detail_modal
from app.ui.project_list import render_project_list

# --- 初期設定 ---
setup_logger()
logger = logging.getLogger('aiman')


def get_services() -> ProjectService:
    """サービス層のインスタンスを取得。"""
    # 環境変数の設定を確認
    env = os.getenv('ENV', 'dev')
    logger.info(f'Creating services for environment: {env}')
    logger.info(f'Data directory: {config.data_dir_path}')

    project_repo = JsonProjectRepository(config.data_dir_path)
    return ProjectService(project_repo)


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

    # サービスの取得
    project_service = get_services()

    # プロジェクト作成フォーム
    render_project_creation_form(project_service)

    # プロジェクト詳細モーダル
    modal = Modal(title='プロジェクト詳細', key='project_detail_modal')
    render_project_detail_modal(modal)

    # プロジェクト一覧
    projects = project_service.get_all_projects()
    jst = ZoneInfo('Asia/Tokyo')
    projects.sort(key=lambda p: _get_sort_key(p, jst), reverse=True)
    render_project_list(projects, modal, project_service)


if __name__ == '__main__':
    render_main_page()

__all__ = ['render_main_page', 'st']
