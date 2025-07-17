"""プロジェクト関連のサービス関数群。"""

import logging

import streamlit as st

from app.application.container import ApplicationContainer
from app.application.data_manager import DataManager
from app.domain.entities import Project
from app.infrastructure.new_worker import NewWorker


def _validate_project_input(name: str, source: str, ai_tool: str) -> str | None:
    """プロジェクト入力値の検証を行います。

    Returns:
        エラーメッセージ、問題がない場合はNone。
    """
    if not name or not name.strip():
        return 'プロジェクト名を入力してください。'

    return (
        'ソースディレクトリパスを入力してください。'
        if not source or not source.strip()
        else ('AIツールを選択してください。' if not ai_tool or not ai_tool.strip() else None)
    )


def handle_project_creation(
    name: str,
    source: str,
    ai_tool: str,
    data_manager: DataManager,
) -> tuple[Project | None, str]:
    """プロジェクト作成処理を実行します。

    Args:
        name: プロジェクト名。
        source: ソースディレクトリパス。
        ai_tool: AIツールID。
        data_manager: データマネージャー。

    Returns:
        作成したプロジェクト(失敗時はNone)とメッセージのタプル。
    """
    # 入力値チェック
    validation_error = _validate_project_input(name, source, ai_tool)
    if validation_error:
        return None, validation_error

    # プロジェクト作成
    project = data_manager.create_project(name.strip(), source.strip(), ai_tool)

    return (
        (project, f'プロジェクト「{project.name}」を作成しました。')
        if project
        else (None, 'プロジェクトの作成に失敗しました。')
    )


def _start_project_worker(project: Project, logger: logging.Logger) -> None:
    """プロジェクト処理用のワーカーを起動します。

    Args:
        project: 実行するプロジェクト。
        logger: ロガー。
    """
    logger.info(f'[ProjectService] Starting NewWorker for project_id: {project.id}')

    # ApplicationContainerを使って必要な依存関係を取得
    container = ApplicationContainer()
    worker = NewWorker(
        project_id=project.id,
        project_repository=container.project_repository,
        ai_tool_repository=container.ai_tool_repository,
    )

    # ワーカープロセスを開始
    worker.start()

    # セッション状態にワーカーを追加
    if 'running_workers' not in st.session_state:
        st.session_state.running_workers = {}
    st.session_state.running_workers[project.id] = worker

    logger.info(f'[ProjectService] NewWorker started successfully for project_id: {project.id}')


def _execute_project_processing(
    project: Project, data_manager: DataManager, logger: logging.Logger
) -> tuple[Project | None, str]:
    """プロジェクトの処理を実行します。

    Args:
        project: 実行するプロジェクト。
        data_manager: データマネージャー。
        logger: ロガー。

    Returns:
        更新後のプロジェクト(失敗時はNone)とメッセージのタプル。
    """
    # プロジェクトの実行開始
    project.start_processing()

    # データベースに保存
    success = data_manager.update_project(project)
    if not success:
        return None, 'プロジェクトの実行開始に失敗しました。'

    # NewWorkerを起動してAIツール処理を実行
    _start_project_worker(project, logger)

    return project, f'プロジェクト「{project.name}」の実行を開始しました。'


def handle_project_execution(
    project: Project,
    data_manager: DataManager,
) -> tuple[Project | None, str]:
    """プロジェクト実行処理を実行します。

    Args:
        project: 実行するプロジェクト。
        data_manager: データマネージャー。

    Returns:
        更新後のプロジェクト(失敗時はNone)とメッセージのタプル。
    """
    logger = logging.getLogger('aiman')
    logger.info(f'[ProjectService] handle_project_execution called: project={project!r}')

    try:
        return _execute_project_processing(project, data_manager, logger)
    except Exception as e:
        logger.error(f'[ProjectService] Error starting project execution: {e}')
        return None, f'プロジェクトの実行開始中にエラーが発生しました: {e!s}'
