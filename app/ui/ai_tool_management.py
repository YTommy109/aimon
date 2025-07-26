"""AIツール管理画面のビュー層モジュール。"""

from typing import Any

import streamlit as st

from app.models.ai_tool import AITool
from app.services.ai_tool_service import AIToolService


def render_ai_tool_management_page(ai_tool_service: AIToolService) -> None:
    """AIツール管理ページを描画。

    Args:
        ai_tool_service: AIツールサービス。
    """
    _setup_session_state(ai_tool_service)
    _render_page_header()
    _render_tool_list(ai_tool_service)
    _render_create_button()
    _render_modals()


def _setup_session_state(ai_tool_service: AIToolService) -> None:
    """セッション状態の初期化。

    Args:
        ai_tool_service: AIツールサービス。
    """
    if 'ai_tool_service' not in st.session_state:
        st.session_state['ai_tool_service'] = ai_tool_service


def _render_page_header() -> None:
    """ページヘッダーの描画。"""
    st.title('AIツール管理')


def _render_create_button() -> None:
    """新規作成ボタンの描画。"""
    if st.button('新規AIツール登録'):
        st.session_state['show_create_modal'] = True


def _render_modals() -> None:
    """モーダルの描画制御。"""
    # 新規作成モーダル
    if st.session_state.get('show_create_modal', False):
        _render_creation_modal()

    # 編集モーダルの表示
    if st.session_state.get('show_edit_modal', False) and st.session_state.get('editing_tool'):
        _render_edit_modal(st.session_state['editing_tool'])


def _render_tool_list(ai_tool_service: AIToolService) -> None:
    """AIツール一覧の描画。

    Args:
        ai_tool_service: AIツールサービス。
    """
    tools = ai_tool_service.get_all_ai_tools()

    if not tools:
        st.info('💡 AIツールがまだ登録されていません。')
        return

    _render_table_header()
    st.divider()

    # 各ツールの行
    for tool in tools:
        _render_tool_row(tool, ai_tool_service)


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


def _render_tool_row(tool: AITool, ai_tool_service: AIToolService) -> None:
    """AIツール行の描画。

    Args:
        tool: AIツールオブジェクト。
        ai_tool_service: AIツールサービス。
    """
    cols = st.columns([2, 2, 3, 2, 2, 1, 2])
    _render_tool_info_columns(tool, cols)
    with cols[6]:
        _render_tool_actions(tool, ai_tool_service)


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
        st.write(tool.created_at.strftime('%Y/%m/%d %H:%M'))
    with cols[4]:
        st.write(tool.updated_at.strftime('%Y/%m/%d %H:%M'))
    with cols[5]:
        status = '無効' if tool.disabled_at else '有効'
        st.write(status)


def _render_tool_actions(tool: AITool, ai_tool_service: AIToolService) -> None:
    """ツール操作ボタンの描画。

    Args:
        tool: AIツールオブジェクト。
        ai_tool_service: AIツールサービス。
    """
    col1, col2 = st.columns(2)

    with col1:
        _render_edit_button(tool)

    with col2:
        _render_enable_disable_button(tool, ai_tool_service)


def _render_edit_button(tool: AITool) -> None:
    """編集ボタンを描画する。"""
    if st.button('編集', key=f'edit_{tool.id}'):
        st.session_state['editing_tool'] = tool
        st.session_state['show_edit_modal'] = True
        st.rerun()


def _render_enable_disable_button(tool: AITool, ai_tool_service: AIToolService) -> None:
    """有効化/無効化ボタンを描画する。"""
    if tool.disabled_at:
        if st.button('有効化', key=f'enable_{tool.id}'):
            _handle_enable_tool(tool.id, ai_tool_service)
    elif st.button('無効化', key=f'disable_{tool.id}'):
        _handle_disable_tool(tool.id, ai_tool_service)


def _render_creation_modal() -> None:
    """新規作成モーダルの描画。"""
    with st.expander('新規AIツール登録', expanded=True):
        _render_creation_form()


def _render_creation_form() -> None:
    """新規作成フォームの描画。"""
    tool_info = {
        'tool_id': st.text_input('ツールID', key='create_tool_id'),
        'name': st.text_input('ツール名', key='create_name'),
        'description': st.text_area('説明', key='create_description'),
        'endpoint_url': st.text_input('エンドポイントURL', key='create_endpoint_url'),
    }
    _render_creation_form_buttons(tool_info)


def _render_creation_form_buttons(tool_info: dict[str, str]) -> None:
    """新規作成フォームのボタン描画。

    Args:
        tool_info: ツール情報。
    """
    col1, col2 = st.columns(2)
    with col1:
        if st.button('登録'):
            _handle_create_tool(tool_info)
    with col2:
        if st.button('キャンセル'):
            st.session_state['show_create_modal'] = False
            st.rerun()


def _render_edit_modal(tool: AITool) -> None:
    """編集モーダルの描画。

    Args:
        tool: 編集対象のAIツール。
    """
    with st.expander(f'AIツール編集: {tool.name_ja}', expanded=True):
        _render_edit_form(tool)


def _render_edit_form(tool: AITool) -> None:
    """編集フォームの描画。

    Args:
        tool: 編集対象のAIツール。
    """
    tool_info = {
        'tool_id': tool.id,
        'name': st.text_input('ツール名', value=tool.name_ja, key='edit_name'),
        'description': st.text_area('説明', value=tool.description or '', key='edit_description'),
        'endpoint_url': st.text_input(
            'エンドポイントURL', value=tool.endpoint_url, key='edit_endpoint_url'
        ),
    }
    _render_edit_form_buttons(tool_info)


def _render_edit_form_buttons(tool_info: dict[str, str]) -> None:
    """編集フォームのボタン描画。

    Args:
        tool_info: ツール情報。
    """
    col1, col2 = st.columns(2)
    with col1:
        if st.button('更新'):
            _handle_update_tool(tool_info)
    with col2:
        if st.button('キャンセル'):
            st.session_state['show_edit_modal'] = False
            st.rerun()


def _handle_create_tool(tool_info: dict[str, str]) -> None:
    """ツール作成処理。

    Args:
        tool_info: ツール情報。
    """
    ai_tool_service = st.session_state.get('ai_tool_service')
    if not ai_tool_service:
        st.error('AIツールサービスが見つかりません。')
        return

    success = ai_tool_service.create_ai_tool(
        tool_info['tool_id'],
        tool_info['name'],
        tool_info['description'],
        tool_info['endpoint_url'],
    )
    if success:
        st.success('AIツールを作成しました。')
        st.session_state['show_create_modal'] = False
        st.rerun()
    else:
        st.error('AIツールの作成に失敗しました。')


def _handle_update_tool(tool_info: dict[str, str]) -> None:
    """ツール更新処理。

    Args:
        tool_info: ツール情報。
    """
    ai_tool_service = st.session_state.get('ai_tool_service')
    if not ai_tool_service:
        st.error('AIツールサービスが見つかりません。')
        return

    success = ai_tool_service.update_ai_tool(
        tool_info['tool_id'],
        tool_info['name'],
        tool_info['description'],
        tool_info['endpoint_url'],
    )
    if success:
        st.success('AIツールを更新しました。')
        st.session_state['show_edit_modal'] = False
        st.rerun()
    else:
        st.error('AIツールの更新に失敗しました。')


def _handle_disable_tool(tool_id: str, ai_tool_service: AIToolService) -> None:
    """ツール無効化処理。

    Args:
        tool_id: ツールID。
        ai_tool_service: AIツールサービス。
    """
    success = ai_tool_service.disable_ai_tool(tool_id)
    if success:
        st.success('AIツールを無効化しました。')
        st.rerun()
    else:
        st.error('AIツールの無効化に失敗しました。')


def _handle_enable_tool(tool_id: str, ai_tool_service: AIToolService) -> None:
    """ツール有効化処理。

    Args:
        tool_id: ツールID。
        ai_tool_service: AIツールサービス。
    """
    success = ai_tool_service.enable_ai_tool(tool_id)
    if success:
        st.success('AIツールを有効化しました。')
        st.rerun()
    else:
        st.error('AIツールの有効化に失敗しました。')
