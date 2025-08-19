"""プロジェクト作成フォームのUIモジュール。"""

from dataclasses import dataclass

import streamlit as st

from app.models import ToolType
from app.models.project import Project
from app.services.project_service import ProjectService


@dataclass
class ProjectFormInputs:
    project_name: str | None
    source_dir: str | None
    selected_tool_type: ToolType | None = None


def _validate_project_inputs(
    project_name: str | None,
    source_dir: str | None,
    selected_tool_type: ToolType | None = None,
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
    elif selected_tool_type is None:
        error_message = '内蔵ツールを選択してください。'

    if error_message:
        return False, error_message

    return True, ''


def _create_project_with_validation(
    project: Project,
    project_service: ProjectService,
) -> tuple[bool, str]:
    """プロジェクト作成を検証付きで実行する。

    Args:
        project: 作成するプロジェクトオブジェクト
        project_service: プロジェクトサービス

    Returns:
        (成功フラグ, メッセージ)
    """
    try:
        created_project = project_service.create_project(project.name, project.source, project.tool)
        if created_project is None:
            message = 'プロジェクトの作成に失敗しました。'
        else:
            message = 'プロジェクトを作成しました。'
        return created_project is not None, message
    except Exception:
        return False, 'プロジェクトの作成に失敗しました。'


def _display_result_message(*, success: bool, message: str) -> None:
    """結果メッセージを表示する。"""
    if success:
        st.success(message)
    else:
        st.error(message)


def _handle_project_creation_button(
    project: Project | None,
    project_service: ProjectService,
) -> None:
    """プロジェクト作成ボタンの処理。

    Args:
        project: 作成するプロジェクトオブジェクト
        project_service: プロジェクトサービス
    """
    if project is not None:
        _handle_form_submission(project, project_service)


def _handle_form_submission(
    project: Project,
    project_service: ProjectService,
) -> None:
    """フォーム送信の処理。

    Args:
        project: 作成するプロジェクトオブジェクト
        project_service: プロジェクトサービス
    """
    success, message = _create_project_with_validation(project, project_service)
    _display_result_message(success=success, message=message)


def _render_form_inputs() -> tuple[str | None, str | None, ToolType | None]:
    """フォームの入力フィールドを描画する。

    Returns:
        (プロジェクト名, ソースディレクトリ, 選択された内蔵ツールタイプ)
    """
    project_name: str | None = st.text_input('プロジェクト名')
    source_dir: str | None = st.text_input('対象ディレクトリのパス')
    # 入力値の前後空白を除去
    source_dir = source_dir.strip() if source_dir else None
    # 内蔵ツール（固定2択）
    internal_tool_options: list[ToolType | None] = [None, ToolType.OVERVIEW, ToolType.REVIEW]
    selected_tool_type: ToolType | None = st.selectbox(
        '内蔵ツールを選択',
        options=internal_tool_options,
        format_func=lambda t: '選択...' if t is None else str(t),
        index=0,
    )

    return project_name, source_dir, selected_tool_type


def _handle_form_submission_logic(
    inputs: ProjectFormInputs,
    project_service: ProjectService,
) -> None:
    """フォーム送信ロジックの処理。

    Args:
        inputs: フォーム入力値
        project_service: プロジェクトサービス
    """
    # 入力値の検証
    is_valid, error_message = _validate_project_inputs(
        inputs.project_name, inputs.source_dir, inputs.selected_tool_type
    )

    if not is_valid:
        st.warning(error_message)
        return

    # プロジェクトオブジェクトの作成
    assert inputs.project_name is not None
    assert inputs.source_dir is not None
    assert inputs.selected_tool_type is not None
    project = Project(
        name=inputs.project_name,
        source=inputs.source_dir,
        tool=inputs.selected_tool_type,
    )

    # プロジェクト作成の実行
    _handle_project_creation_button(project, project_service)


def render_project_creation_form(project_service: ProjectService) -> None:
    """プロジェクト作成フォームを描画する。

    Args:
        project_service: プロジェクトサービス。
    """
    st.header('プロジェクト作成')

    # フォーム入力の取得
    project_name, source_dir, selected_tool_type = _render_form_inputs()

    # フォーム入力オブジェクトの作成
    inputs = ProjectFormInputs(
        project_name=project_name,
        source_dir=source_dir,
        selected_tool_type=selected_tool_type,
    )

    # 作成ボタンの処理
    if st.button('プロジェクト作成'):
        _handle_form_submission_logic(inputs, project_service)


__all__ = ['render_project_creation_form', 'st']
