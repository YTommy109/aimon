"""メインページのUIを管理するモジュール。"""

import logging

import streamlit as st
from streamlit_modal import Modal

from app.config import get_config
from app.logger import setup_logging
from app.repositories.project_repository import JsonProjectRepository
from app.services.project_service import ProjectService
from app.ui.project_creation_form import render_project_creation_form
from app.ui.project_detail_modal import render_project_detail_modal
from app.ui.project_list import render_project_list

# ログ設定の初期化（ここでは二重初期化を避けるため呼ばない）


def render_main_page() -> None:
    """メインページをレンダリングする。"""
    config = get_config()

    st.title('AI Project Manager')

    # データディレクトリの表示
    # ログ初期化
    setup_logging()
    logger = logging.getLogger('aiman')
    logger.info(f'Data directory: {config.data_dir_path}')

    # リポジトリとサービスの初期化
    project_repo = JsonProjectRepository(config.data_dir_path)
    project_service = ProjectService(project_repo)

    # プロジェクト作成フォームを表示
    render_project_creation_form(project_service)

    # プロジェクト一覧を表示
    modal = Modal('プロジェクト詳細', key='project_detail_modal')

    # プロジェクトリポジトリからプロジェクトを取得
    projects = project_repo.find_all()
    render_project_list(projects, modal, project_service)

    # プロジェクト詳細モーダルを表示
    render_project_detail_modal(modal)

    # ボタンハンドラーを設定
    # ボタンハンドラーの設定は各UIコンポーネント内で行う


if __name__ == '__main__':
    render_main_page()

__all__ = ['render_main_page', 'st']
