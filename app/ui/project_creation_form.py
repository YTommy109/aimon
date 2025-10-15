"""プロジェクト作成フォームのUIコンポーネント。"""

from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from app.models.project import Project
from app.services.project_service import ProjectService
from app.types import ToolType


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


def _render_form_inputs(
    projects_root: Path | None,
) -> tuple[str | None, str | None, ToolType | None]:
    """フォームの入力フィールドを描画する。

    Returns:
        (プロジェクト名, ソースディレクトリ, 選択された内蔵ツールタイプ)
    """
    project_name: str | None = st.text_input('プロジェクト名')

    # projects 配下のサブディレクトリ一覧を取得し、選択式にする
    subdirs: list[str] = []
    if projects_root is not None and projects_root.exists():
        subdirs = [p.name for p in projects_root.iterdir() if p.is_dir()]
    source_choice_options: list[str | None] = [None, *subdirs]
    selected_subdir: str | None = st.selectbox(
        '対象ディレクトリ',
        options=source_choice_options,
        format_func=lambda s: '選択...' if s is None else s,
        index=0,
    )
    source_dir: str | None = selected_subdir
    # 内蔵ツール（固定2択）
    internal_tool_options: list[ToolType | None] = [None, ToolType.OVERVIEW, ToolType.REVIEW]
    selected_tool_type: ToolType | None = st.selectbox(
        '内蔵ツールを選択',
        options=internal_tool_options,
        format_func=lambda t: '選択...' if t is None else str(t),
        index=0,
    )

    return project_name, source_dir, selected_tool_type


def _handle_form_submission_logic(  # noqa: PLR0915
    inputs: ProjectFormInputs,
    project_service: ProjectService,
    projects_root: Path | None = None,
) -> None:
    """フォーム送信ロジックの処理。

    Args:
        inputs: フォーム入力値
        project_service: プロジェクトサービス
        projects_root: プロジェクトルートディレクトリ
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
    # プロジェクトのソースは $DATA_DIR/projects/{選択ディレクトリ} を保持
    if projects_root is not None:
        project_source: str = str((projects_root / inputs.source_dir).as_posix())
    else:
        project_source = f'projects/{inputs.source_dir}'
    project = Project(
        name=inputs.project_name,
        source=project_source,
        tool=inputs.selected_tool_type,
    )

    # プロジェクト作成の実行
    success, message = _create_project_with_validation(project, project_service)

    # 結果メッセージを表示
    if success:
        st.success(message)
    else:
        st.error(message)


def render_project_creation_form(
    project_service: ProjectService,
    projects_root: Path | None = None,
) -> None:
    """プロジェクト作成フォームを描画する。

    Args:
        project_service: プロジェクトサービス。
    """
    st.header('プロジェクト作成')

    # フォーム入力の取得
    project_name, source_dir, selected_tool_type = _render_form_inputs(projects_root)

    # フォーム入力オブジェクトの作成
    inputs = ProjectFormInputs(
        project_name=project_name,
        source_dir=source_dir,
        selected_tool_type=selected_tool_type,
    )

    # 作成ボタンの処理
    if st.button('プロジェクト作成'):
        _handle_form_submission_logic(inputs, project_service, projects_root)


__all__ = ['render_project_creation_form', 'st']
