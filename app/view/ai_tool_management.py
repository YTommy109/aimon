"""AIツール管理画面のビュー層モジュール。"""

from typing import Any

import streamlit as st

from app.application.data_manager import DataManager
from app.application.services.ai_tool_service import (
    get_ai_tools,
    handle_ai_tool_creation,
    handle_ai_tool_disable,
    handle_ai_tool_enable,
    handle_ai_tool_update,
)
from app.domain.entities import AITool


def render_ai_tool_management_page(data_manager: DataManager) -> None:
    """AIツール管理ページを描画。

    Args:
        data_manager: データマネージャー。
    """
    if 'data_manager' not in st.session_state:
        st.session_state['data_manager'] = data_manager

    st.title('AIツール管理')

    _render_tool_list(data_manager)

    # 新規作成ボタン
    if st.button('新規AIツール登録'):
        st.session_state['show_create_modal'] = True

    # 新規作成モーダル
    if st.session_state.get('show_create_modal', False):
        _render_creation_modal()


def _render_tool_list(data_manager: DataManager) -> None:
    """AIツール一覧の描画。

    Args:
        data_manager: データマネージャー。
    """
    tools = get_ai_tools(data_manager)

    if not tools:
        st.info('💡 AIツールがまだ登録されていません。')
        return

    _render_table_header()
    st.divider()

    # 各ツールの行
    for tool in tools:
        _render_tool_row(tool, data_manager)


def _render_table_header() -> None:
    """テーブルヘッダーの描画。"""
    headers = [
        '**ID**',
        '**ツール名**',
        '**説明**',
        '**登録日時**',
        '**更新日時**',
        '**状態**',
        '**操作**',
    ]
    cols = st.columns([2, 2, 3, 2, 2, 1, 2])
    for col, header in zip(cols, headers, strict=False):
        with col:
            st.write(header)


def _render_tool_row(tool: AITool, data_manager: DataManager) -> None:
    """AIツール行の描画。

    Args:
        tool: AIツールオブジェクト。
        data_manager: データマネージャー。
    """
    cols = st.columns([2, 2, 3, 2, 2, 1, 2])
    _render_tool_info_columns(tool, cols)
    with cols[6]:
        _render_tool_actions(tool, data_manager)


def _render_tool_info_columns(tool: AITool, cols: list[Any]) -> None:
    """ツール情報カラムの描画。

    Args:
        tool: AIツールオブジェクト。
        cols: Streamlitカラムリスト。
    """
    with cols[0]:
        st.write(tool.id)
    with cols[1]:
        st.write(tool.name_ja)
    with cols[2]:
        st.write(tool.description or '')
    with cols[3]:
        st.write(tool.created_at.strftime('%Y-%m-%d %H:%M'))
    with cols[4]:
        st.write(tool.updated_at.strftime('%Y-%m-%d %H:%M'))
    with cols[5]:
        st.write('有効' if tool.disabled_at is None else '無効')


def _render_tool_actions(tool: AITool, data_manager: DataManager) -> None:
    """AIツール操作ボタンの描画。

    Args:
        tool: AIツールオブジェクト。
        data_manager: データマネージャー。
    """
    cols = st.columns(2)
    with cols[0]:
        if st.button('編集', key=f'edit_{tool.id}'):
            st.session_state['edit_tool'] = tool
            st.session_state['show_edit_modal'] = True
    with cols[1]:
        if tool.disabled_at is None:
            if st.button('無効化', key=f'disable_{tool.id}'):
                _handle_disable_tool(tool.id, data_manager)
        elif st.button('有効化', key=f'enable_{tool.id}'):
            _handle_enable_tool(tool.id, data_manager)

    # 編集モーダル
    if (
        st.session_state.get('show_edit_modal', False)
        and st.session_state.get('edit_tool', {}).id == tool.id
    ):
        _render_edit_modal(tool)


def _render_creation_modal() -> None:
    """新規作成モーダルの描画。

    Args:
        data_manager: データマネージャー。
    """
    st.subheader('新規AIツール登録')
    with st.form(key='create_tool_form', clear_on_submit=True):
        _render_creation_form()


def _render_creation_form() -> None:
    tool_id = st.text_input('AIツールID')
    name = st.text_input('ツール名')
    description = st.text_input('説明')
    endpoint_url = st.text_input('エンドポイントURL')
    tool_info = {
        'tool_id': tool_id,
        'name': name,
        'description': description,
        'endpoint_url': endpoint_url,
    }
    _render_creation_form_buttons(tool_info)


def _render_creation_form_buttons(tool_info: dict[str, str]) -> None:
    cols = st.columns(2)
    with cols[0]:
        submit_button = st.form_submit_button('作成')
        if submit_button:
            _handle_create_tool(tool_info)
    with cols[1]:
        cancel_button = st.form_submit_button('キャンセル')
        if cancel_button:
            st.session_state['show_create_modal'] = False
            st.rerun()


def _render_edit_modal(tool: AITool) -> None:
    """編集モーダルの描画。

    Args:
        tool: 編集対象のAIツール。
        data_manager: データマネージャー。
    """
    st.subheader('AIツール編集')
    with st.form(key=f'edit_tool_form_{tool.id}', clear_on_submit=True):
        _render_edit_form(tool)


def _render_edit_form(tool: AITool) -> None:
    st.text_input('AIツールID', value=tool.id, disabled=True)
    name = st.text_input('ツール名', value=tool.name_ja)
    description = st.text_input('説明', value=tool.description or '')
    endpoint_url = st.text_input('エンドポイントURL', value=tool.endpoint_url or '')
    tool_info = {
        'tool_id': tool.id,
        'name': name,
        'description': description,
        'endpoint_url': endpoint_url,
    }
    _render_edit_form_buttons(tool_info)


def _render_edit_form_buttons(tool_info: dict[str, str]) -> None:
    cols = st.columns(2)
    with cols[0]:
        submit_button = st.form_submit_button('更新')
        if submit_button:
            _handle_update_tool(tool_info)
    with cols[1]:
        cancel_button = st.form_submit_button('キャンセル')
        if cancel_button:
            st.session_state['show_edit_modal'] = False
            st.session_state['edit_tool'] = None
            st.rerun()


def _handle_create_tool(tool_info: dict[str, str]) -> None:
    """AIツール作成処理。

    Args:
        tool_info: AIツール情報の辞書。
        data_manager: データマネージャー。
    """
    if handle_ai_tool_creation(
        st.session_state['data_manager'],
        tool_info,
    ):
        st.success(f'AIツール「{tool_info["name"]}」を作成しました。')
        st.session_state['show_create_modal'] = False
        st.rerun()
    else:
        st.error('AIツールの作成に失敗しました。入力内容を確認してください。')


def _handle_update_tool(tool_info: dict[str, str]) -> None:
    """AIツール更新処理。

    Args:
        tool_info: AIツール情報の辞書。
        data_manager: データマネージャー。
    """
    if handle_ai_tool_update(
        st.session_state['data_manager'],
        tool_info,
    ):
        st.success(f'AIツール「{tool_info["name"]}」を更新しました。')
        st.session_state['show_edit_modal'] = False
        st.session_state['edit_tool'] = None
        st.rerun()
    else:
        st.error('AIツールの更新に失敗しました。入力内容を確認してください。')


def _handle_disable_tool(tool_id: str, data_manager: DataManager) -> None:
    """AIツール無効化処理。

    Args:
        tool_id: ツールID。
        data_manager: データマネージャー。
    """
    if handle_ai_tool_disable(data_manager, tool_id):
        st.success(f'AIツール「{tool_id}」を無効化しました。')
        st.rerun()
    else:
        st.error('AIツールの無効化に失敗しました。')


def _handle_enable_tool(tool_id: str, data_manager: DataManager) -> None:
    """AIツール有効化処理。

    Args:
        tool_id: ツールID。
        data_manager: データマネージャー。
    """
    if handle_ai_tool_enable(data_manager, tool_id):
        st.success(f'AIツール「{tool_id}」を有効化しました。')
        st.rerun()
    else:
        st.error('AIツールの有効化に失敗しました。')
