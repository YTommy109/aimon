from dataclasses import dataclass
from typing import Any

import streamlit as st

from app.errors import ResourceNotFoundError
from app.models.project import Project
from app.services.ai_tool_service import AIToolService
from app.services.project_service import ProjectService


@dataclass
class ProjectFormInputs:
    project_name: str | None
    source_dir: str | None
    selected_ai_tool_id: str | None


def _create_ai_tool_options(ai_tools: list[Any]) -> tuple[list[str], dict[str, str]]:
    """プロジェクト作成フォーム用のAIツールオプションを作成します。"""
    ai_tool_options = {tool.id: f'{tool.name_ja} ({tool.description})' for tool in ai_tools}

    # セパレータを追加（JSONからツールが存在する場合のみ）
    all_options = list(ai_tool_options.keys())
    if all_options:
        all_options.append('---')

    return all_options, ai_tool_options


def _format_ai_tool(tool_id: str, ai_tool_options: dict[str, str]) -> str:
    """プロジェクト作成フォーム用のAIツールフォーマット関数。"""
    if tool_id == '---':
        return '--- 内蔵ツール ---'
    return ai_tool_options.get(tool_id, '不明なツール')


def _validate_project_inputs(
    project_name: str | None,
    source_dir: str | None,
    selected_ai_tool_id: str | None,
) -> tuple[bool, str]:
    """プロジェクト入力値の検証を行う。

    Returns:
        (検証成功フラグ, エラーメッセージ)
    """
    error_message = ''

    # 空白文字のチェックを追加
    if (
        not project_name
        or (project_name and not project_name.strip())
        or not source_dir
        or (source_dir and not source_dir.strip())
    ):
        error_message = 'プロジェクト名と対象ディレクトリのパスを入力してください。'
    elif not selected_ai_tool_id or selected_ai_tool_id == '---':
        error_message = 'AIツールを選択してください。'

    if error_message:
        return False, error_message

    return True, ''


def _validate_ai_tool_exists(ai_tool_id: str, ai_tool_service: AIToolService) -> bool:
    try:
        ai_tool_service.get_ai_tool_by_id(ai_tool_id)
        return True
    except ResourceNotFoundError:
        return False


def _create_project_with_validation(
    project: Project,
    project_service: ProjectService,
    ai_tool_service: AIToolService,
) -> tuple[bool, str]:
    """プロジェクト作成を検証付きで実行する。

    Args:
        project: 作成するプロジェクトオブジェクト
        project_service: プロジェクトサービス
        ai_tool_service: AIツールサービス

    Returns:
        (成功フラグ, メッセージ)
    """
    success = True
    message = 'プロジェクトを作成しました。'

    if not _validate_ai_tool_exists(project.ai_tool, ai_tool_service):
        success = False
        message = '選択されたAIツールが見つかりません。'
    else:
        created_project = project_service.create_project(
            project.name,
            project.source,
            project.ai_tool,
        )
        if not created_project:
            success = False
            message = 'プロジェクトの作成に失敗しました。'

    return success, message


def _display_result_message(*, success: bool, message: str) -> None:
    """結果メッセージを表示する。"""
    if success:
        st.success(message)
    else:
        st.warning(message)


def _handle_project_creation_button(
    project: Project | None,
    project_service: ProjectService,
    ai_tool_service: AIToolService,
) -> None:
    """プロジェクト作成ボタンがクリックされた際の処理。"""
    if project is None:
        st.warning('プロジェクトデータが不正です。')
        return

    # プロジェクト作成の実行
    success, message = _create_project_with_validation(project, project_service, ai_tool_service)

    _display_result_message(success=success, message=message)


def _handle_form_submission(
    project: Project,
    project_service: ProjectService,
    ai_tool_service: AIToolService,
) -> None:
    """フォーム送信時の処理。"""
    _handle_project_creation_button(project, project_service, ai_tool_service)


def _render_form_inputs(
    ai_tool_service: AIToolService,
) -> tuple[str | None, str | None, str | None]:
    """フォームの入力フィールドを描画する。

    Returns:
        (プロジェクト名, ソースディレクトリ, 選択されたAIツールID)
    """
    project_name: str | None = st.text_input('プロジェクト名')
    source_dir: str | None = st.text_input('対象ディレクトリのパス')
    # 入力値の前後空白を除去
    source_dir = source_dir.strip() if source_dir else None
    ai_tools = ai_tool_service.get_all_ai_tools()
    all_options, ai_tool_options = _create_ai_tool_options(ai_tools)

    selected_ai_tool_id: str | None = st.selectbox(
        'AIツールを選択',
        options=all_options,
        format_func=lambda tool_id: _format_ai_tool(tool_id, ai_tool_options),
        index=None,
        placeholder='選択...',
    )

    return project_name, source_dir, selected_ai_tool_id


def _handle_form_submission_logic(
    inputs: ProjectFormInputs,
    project_service: ProjectService,
    ai_tool_service: AIToolService,
) -> None:
    """フォーム送信時のロジックを処理する。"""
    # 入力値の検証
    is_valid, error_message = _validate_project_inputs(
        inputs.project_name, inputs.source_dir, inputs.selected_ai_tool_id
    )
    if not is_valid:
        st.warning(error_message)
        return

    # 型アサーション（検証済みなので None ではない）
    assert inputs.project_name is not None
    assert inputs.source_dir is not None
    assert inputs.selected_ai_tool_id is not None

    # Project オブジェクトを作成
    project = Project(
        name=inputs.project_name,
        source=inputs.source_dir,
        ai_tool=inputs.selected_ai_tool_id,
    )

    _handle_form_submission(project, project_service, ai_tool_service)


def render_project_creation_form(
    project_service: ProjectService, ai_tool_service: AIToolService
) -> None:
    """プロジェクト作成フォームを描画します。"""
    with st.sidebar:
        st.header('プロジェクト作成')
        project_name, source_dir, selected_ai_tool_id = _render_form_inputs(ai_tool_service)

        if st.button('プロジェクト作成'):
            inputs = ProjectFormInputs(
                project_name=project_name,
                source_dir=source_dir,
                selected_ai_tool_id=selected_ai_tool_id,
            )
            _handle_form_submission_logic(inputs, project_service, ai_tool_service)
