import logging
import os

import streamlit as st


def _apply_environment_from_session() -> None:
    """セッションまたはクエリからENVを設定する。

    Streamlitのマルチページでは `app.py` が先に実行される想定だが、
    直接このページだけを開いた場合に備えて `ENV` をデフォルト `dev` に補正する。
    """
    env = os.environ.get('ENV') or 'dev'
    os.environ['ENV'] = env


def render_rag_chat() -> None:
    """RAGチャットページ本体。"""
    _apply_environment_from_session()

    from app.config import config  # noqa: PLC0415
    from app.logger import setup_logging  # noqa: PLC0415
    from app.repositories.project_repository import JsonProjectRepository  # noqa: PLC0415
    from app.services.project_service import ProjectService  # noqa: PLC0415
    from app.ui.rag_chat_page import render_rag_chat_page  # noqa: PLC0415

    # ログ初期化（多重初期化はsetup側で抑止されている想定）
    setup_logging()
    logger = logging.getLogger('aiman')
    logger.info(f'RAG page loaded. ENV={os.environ.get("ENV")} LOG_LEVEL={config.LOG_LEVEL}')

    # リポジトリとサービスの初期化
    project_repo = JsonProjectRepository(config.data_dir_path)
    project_service = ProjectService(project_repo)

    st.set_page_config(page_title='RAG チャット', page_icon='💬', layout='wide')
    render_rag_chat_page(project_service, project_repo)


render_rag_chat()
