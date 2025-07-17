from collections.abc import Callable
from typing import Any

import streamlit as st

from app.application.data_manager import DataManager
from app.application.services.project_service import handle_project_creation


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


def _handle_project_creation_button(
    project_name: str,
    source_dir: str,
    selected_ai_tool_id: str | None,
    get_data_manager: Callable[[], DataManager],
) -> None:
    """プロジェクト作成ボタンがクリックされた際の処理。"""
    if selected_ai_tool_id and selected_ai_tool_id != '---':
        project, message = handle_project_creation(
            project_name,
            source_dir,
            selected_ai_tool_id,
            get_data_manager(),
        )
        if project:
            st.success(message)
        else:
            st.warning(message)
    else:
        st.warning('AIツールを選択してください。')


def render_project_creation_form(get_data_manager: Callable[[], DataManager]) -> None:
    """プロジェクト作成フォームを描画します。"""
    with st.sidebar:
        st.header('プロジェクト作成')
        project_name = st.text_input('プロジェクト名')
        source_dir = st.text_input('対象ディレクトリのパス')
        # 入力値の前後空白を除去
        source_dir = source_dir.strip()
        ai_tools = get_data_manager().get_ai_tools()
        all_options, ai_tool_options = _create_ai_tool_options(ai_tools)

        selected_ai_tool_id = st.selectbox(
            'AIツールを選択',
            options=all_options,
            format_func=lambda tool_id: _format_ai_tool(tool_id, ai_tool_options),
            index=None,
            placeholder='選択...',
        )
        if st.button('プロジェクト作成'):
            _handle_project_creation_button(
                project_name, source_dir, selected_ai_tool_id, get_data_manager
            )
