"""AIツール管理ページのUIモジュール。"""

import json
import traceback
from typing import Any, cast
from uuid import UUID

import streamlit as st

from app.config import config
from app.models import AIToolID
from app.models.ai_tool import AITool
from app.services.ai_tool_service import AIToolService


def render_ai_tool_management_page(ai_tool_service: AIToolService) -> None:
    """AIツール管理ページを描画する。

    Args:
        ai_tool_service: AIツールサービス。
    """
    try:
        _setup_session_state(ai_tool_service)
        _render_page_header()
        _render_create_button()
        _render_modals()
        _render_tool_list(ai_tool_service)
    except Exception as e:
        st.error(f'AIツール管理ページの描画中にエラーが発生しました: {e}')
        # デバッグ情報を出力
        if st.session_state.get('APP_ENV') == 'test':
            st.write(f'Debug: エラー詳細: {e}')
            st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _setup_session_state(ai_tool_service: AIToolService) -> None:
    """セッション状態を設定する。

    Args:
        ai_tool_service: AIツールサービス。
    """
    try:
        _init_service_state(ai_tool_service)
        _init_modal_states()
        _init_app_env_state()
    except Exception as e:
        st.error(f'セッション状態の設定中にエラーが発生しました: {e}')
        # デバッグ情報を出力
        if st.session_state.get('APP_ENV') == 'test':
            st.write(f'Debug: エラー詳細: {e}')
            st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _init_service_state(ai_tool_service: AIToolService) -> None:
    """サービス状態を初期化する。

    Args:
        ai_tool_service: AIツールサービス。
    """
    if 'ai_tool_service' not in st.session_state:
        st.session_state['ai_tool_service'] = ai_tool_service


def _init_modal_states() -> None:
    """モーダル状態を初期化する。"""
    if 'show_create_modal' not in st.session_state:
        st.session_state['show_create_modal'] = False
    if 'show_edit_modal' not in st.session_state:
        st.session_state['show_edit_modal'] = False


def _init_app_env_state() -> None:
    """アプリ環境状態を初期化する。"""
    if 'APP_ENV' not in st.session_state:
        st.session_state['APP_ENV'] = config.APP_ENV


def _render_page_header() -> None:
    """ページヘッダーを描画する。"""
    try:
        st.title('AIツール管理')
    except Exception as e:
        st.error(f'ページヘッダーの描画中にエラーが発生しました: {e}')
        # デバッグ情報を出力
        if st.session_state.get('APP_ENV') == 'test':
            st.write(f'Debug: エラー詳細: {e}')
            st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _render_create_button() -> None:
    """新規作成ボタンを描画する。"""
    try:
        if st.button('新規AIツール登録'):
            st.session_state['show_create_modal'] = True
            st.rerun()
    except Exception as e:
        st.error(f'新規作成ボタンの描画中にエラーが発生しました: {e}')
        # デバッグ情報を出力
        if st.session_state.get('APP_ENV') == 'test':
            st.write(f'Debug: エラー詳細: {e}')
            st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _render_modals() -> None:
    """モーダルを描画する。"""
    try:
        _render_create_modal_if_needed()
        _render_edit_modal_if_needed()
    except Exception as e:
        _handle_modal_render_error(e)


def _render_create_modal_if_needed() -> None:
    """作成モーダルが必要な場合に描画します。"""
    if st.session_state.get('show_create_modal'):
        _render_creation_modal()


def _render_edit_modal_if_needed() -> None:
    """編集モーダルが必要な場合に描画します。"""
    if st.session_state.get('show_edit_modal'):
        editing_tool = st.session_state.get('editing_tool')
        if editing_tool:
            _render_edit_modal(editing_tool)


def _handle_modal_render_error(e: Exception) -> None:
    """モーダル描画エラーを処理します。"""
    st.error(f'モーダルの描画中にエラーが発生しました: {e}')
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: エラー詳細: {e}')
        st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _render_tool_list(ai_tool_service: AIToolService) -> None:
    """AIツール一覧を描画する。

    Args:
        ai_tool_service: AIツールサービス。
    """
    try:
        tools = ai_tool_service.get_all_ai_tools()
        _render_debug_info(tools)

        if not tools:
            st.info('登録されているAIツールがありません。')
            return

        _reset_tool_counter()
        _render_table_header()
        _render_tool_rows(tools, ai_tool_service)
    except Exception as e:
        st.error(f'AIツール一覧の描画中にエラーが発生しました: {e}')
        # デバッグ情報を出力
        if st.session_state.get('APP_ENV') == 'test':
            st.write(f'Debug: エラー詳細: {e}')
            st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _render_debug_info(tools: list[AITool]) -> None:
    """デバッグ情報を描画する。

    Args:
        tools: AIツールリスト。
    """
    if st.session_state.get('APP_ENV') == 'test':
        _render_tools_debug_info(tools)
        _render_directory_debug_info()
        _render_file_debug_info()


def _render_tools_debug_info(tools: list[AITool]) -> None:
    """ツールのデバッグ情報を描画する。

    Args:
        tools: AIツールリスト。
    """
    st.write(f'Debug: 取得されたツール数: {len(tools)}')
    for i, tool in enumerate(tools):
        st.write(f'Debug: ツール{i + 1}: {tool.name_ja} (ID: {tool.id})')


def _render_directory_debug_info() -> None:
    """ディレクトリのデバッグ情報を描画する。"""
    st.write(f'Debug: データディレクトリ: {config.data_dir_path}')
    st.write(f'Debug: AIツールファイル: {config.data_dir_path / "ai_tools.json"}')


def _render_file_debug_info() -> None:
    """ファイルのデバッグ情報を描画する。"""
    ai_tools_file = config.data_dir_path / 'ai_tools.json'
    st.write(f'Debug: AIツールファイル存在: {ai_tools_file.exists()}')
    if ai_tools_file.exists():
        try:
            with open(ai_tools_file, encoding='utf-8') as f:
                data = json.load(f)
                st.write(f'Debug: ファイル内容: {data}')
        except Exception as e:
            st.write(f'Debug: ファイル読み込みエラー: {e}')


def _reset_tool_counter() -> None:
    """ツールカウンターをリセットする。"""
    st.session_state['tool_counter'] = 0


def _render_tool_rows(tools: list[AITool], ai_tool_service: AIToolService) -> None:
    """ツール行を描画する。

    Args:
        tools: AIツールリスト。
        ai_tool_service: AIツールサービス。
    """
    for tool in tools:
        _render_tool_row(tool, ai_tool_service)


def _render_table_header() -> None:
    """テーブルヘッダーを描画する。"""
    cols = st.columns(4)
    with cols[0]:
        st.write('**No.**')
    with cols[1]:
        st.write('**ツール名**')
    with cols[2]:
        st.write('**説明**')
    with cols[3]:
        st.write('**操作**')
    st.divider()


def _render_tool_row(tool: AITool, ai_tool_service: AIToolService) -> None:
    """AIツール行を描画する。

    Args:
        tool: AIツールオブジェクト。
        ai_tool_service: AIツールサービス。
    """
    cols = st.columns(4)
    _render_tool_info_and_actions(tool, ai_tool_service, cols)


def _render_tool_info_and_actions(
    tool: AITool, ai_tool_service: AIToolService, cols: list[Any]
) -> None:
    """ツール情報と操作ボタンを描画。

    Args:
        tool: AIツールオブジェクト。
        ai_tool_service: AIツールサービス。
        cols: Streamlitカラムリスト。
    """
    # 通番を取得（セッション状態から取得するか、インデックスを使用）
    if 'tool_counter' not in st.session_state:
        st.session_state['tool_counter'] = 0
    st.session_state['tool_counter'] += 1

    with cols[0]:
        st.write(str(st.session_state['tool_counter']))
    with cols[1]:
        st.write(tool.name_ja)
    with cols[2]:
        st.write(tool.description or '')
    with cols[3]:
        _render_tool_actions_inline(tool, ai_tool_service)


def _render_tool_actions_inline(tool: AITool, ai_tool_service: AIToolService) -> None:
    """ツール操作ボタンをインラインで描画。

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
        'name': st.text_input('ツール名', key='create_name'),
        'description': st.text_area('説明', key='create_description'),
        'command': st.text_input('実行コマンド', key='create_command'),
    }
    _render_creation_form_buttons(tool_info)


def _render_creation_form_buttons(tool_info: dict[str, str]) -> None:
    """新規作成フォームのボタン描画。

    Args:
        tool_info: ツール情報。
    """
    col1, col2 = st.columns(2)
    with col1:
        if st.button('登録', key='create-tool-submit'):
            _handle_create_tool(tool_info)
            # 作成処理が完了したら即座にリターン
            return
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
        'command': st.text_input(
            '実行コマンド',
            value=tool.command or '',
            key='edit_command',
        ),
    }
    _render_edit_form_buttons(tool_info)


def _render_edit_form_buttons(tool_info: dict[str, Any]) -> None:
    """編集フォームのボタン描画。

    Args:
        tool_info: ツール情報。
    """
    col1, col2 = st.columns(2)
    with col1:
        if st.button('更新', key='edit-tool-submit'):
            _handle_update_tool(tool_info)
    with col2:
        if st.button('キャンセル'):
            st.session_state['show_edit_modal'] = False
            st.rerun()


def _validate_tool_info(tool_info: dict[str, str]) -> bool:
    """ツール情報のバリデーション。

    Args:
        tool_info: ツール情報。

    Returns:
        バリデーション結果。
    """
    if not tool_info['name'].strip():
        st.error('ツール名は必須です。')
        return False
    return True


def _get_ai_tool_service() -> AIToolService | None:
    """AIツールサービスを取得。

    Returns:
        AIツールサービス。見つからない場合はNone。
    """
    ai_tool_service = st.session_state.get('ai_tool_service')
    if not ai_tool_service:
        st.error('AIツールサービスが見つかりません。')
        return None
    return cast(AIToolService, ai_tool_service)


def _create_ai_tool(ai_tool_service: AIToolService, tool_info: dict[str, str]) -> bool:
    """AIツールを作成。

    Args:
        ai_tool_service: AIツールサービス。
        tool_info: ツール情報。

    Returns:
        作成成功時はTrue。
    """
    try:
        _log_create_ai_tool_start(tool_info)
        success = _perform_creation_process(ai_tool_service, tool_info)
        _log_create_ai_tool_completion(success)
        return success
    except Exception as e:
        _handle_create_ai_tool_error(e, tool_info)
        return False


def _log_create_ai_tool_start(tool_info: dict[str, str]) -> None:
    """AIツール作成開始をログに出力します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: _create_ai_tool開始: {tool_info}')


def _perform_creation_process(ai_tool_service: AIToolService, tool_info: dict[str, str]) -> bool:
    """作成処理を実行します。"""
    _log_creation_start(tool_info)
    success = _execute_creation(ai_tool_service, tool_info)
    _log_creation_result(success)
    _show_creation_result(success)
    return success


def _log_create_ai_tool_completion(success: bool) -> None:
    """AIツール作成完了をログに出力します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: _create_ai_tool完了: {success}')


def _handle_create_ai_tool_error(e: Exception, tool_info: dict[str, str]) -> None:
    """AIツール作成エラーを処理します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: _create_ai_toolエラー: {e}')
    _handle_creation_error(e, tool_info)


def _log_creation_start(tool_info: dict[str, str]) -> None:
    """作成開始をログに出力します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: ツール作成開始: {tool_info}')


def _execute_creation(ai_tool_service: AIToolService, tool_info: dict[str, str]) -> bool:
    """作成処理を実行します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: _execute_creation開始: {tool_info}')

    result = ai_tool_service.create_ai_tool(
        tool_info['name'],
        tool_info['description'],
        tool_info['command'],
    )

    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: _execute_creation完了: {result}')

    return result


def _log_creation_result(success: bool) -> None:
    """作成結果をログに出力します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: ツール作成結果: {success}')


def _show_creation_result(success: bool) -> None:
    """作成結果を表示します。"""
    if success:
        st.success('AIツールを作成しました。')
    else:
        st.error('AIツールの作成に失敗しました。')


def _handle_creation_error(e: Exception, tool_info: dict[str, str]) -> None:
    """作成エラーを処理します。"""
    st.error(f'AIツール作成中にエラーが発生しました: {e}')
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: エラー詳細: {e}')
        st.write(f'Debug: ツール情報: {tool_info}')


def _clear_creation_form() -> None:
    """作成フォームの値をクリアする。"""
    form_keys = ['create_name', 'create_description', 'create_command']
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]


def _reset_tool_counter_state() -> None:
    """ツールカウンター状態をリセットする。"""
    if 'tool_counter' in st.session_state:
        del st.session_state['tool_counter']


def _handle_successful_creation() -> None:
    """作成成功時の処理。"""
    st.session_state['show_create_modal'] = False
    _reset_tool_counter_state()
    _clear_creation_form()
    # 作成完了を確実にするため、少し待ってからリロード
    # time.sleep()はStreamlitでは適切に動作しないため、st.rerun()を直接呼ぶ
    st.rerun()


def _handle_create_tool(tool_info: dict[str, str]) -> None:
    """ツール作成処理。

    Args:
        tool_info: ツール情報。
    """
    try:
        _log_creation_process_start(tool_info)
        _execute_creation_process(tool_info)
    except Exception as e:
        _handle_creation_process_error(e, tool_info)


def _execute_creation_process(tool_info: dict[str, str]) -> None:
    """作成処理を実行します。"""
    _log_creation_process_start(tool_info)

    if not _validate_creation_input(tool_info):
        return

    ai_tool_service = _get_creation_service()
    if not ai_tool_service:
        return

    success = _perform_creation(tool_info, ai_tool_service)
    _handle_creation_result(success)


def _validate_creation_input(tool_info: dict[str, str]) -> bool:
    """作成入力の検証を行います。"""
    if not _validate_tool_info(tool_info):
        if st.session_state.get('APP_ENV') == 'test':
            st.write('Debug: バリデーション失敗')
        return False
    return True


def _get_creation_service() -> AIToolService | None:
    """作成用のサービスを取得します。"""
    ai_tool_service = _get_ai_tool_service()
    if not ai_tool_service:
        if st.session_state.get('APP_ENV') == 'test':
            st.write('Debug: AIツールサービスが見つかりません')
        return None
    return ai_tool_service


def _perform_creation(tool_info: dict[str, str], ai_tool_service: AIToolService) -> bool:
    """作成処理を実行します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write('Debug: AIツール作成を実行します')

    success = _create_ai_tool(ai_tool_service, tool_info)

    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: 作成結果: {success}')

    return success


def _handle_creation_result(success: bool) -> None:
    """作成結果を処理します。"""
    if success:
        _handle_successful_creation()


def _log_creation_process_start(tool_info: dict[str, str]) -> None:
    """作成処理開始をログに出力します。"""
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: ツール作成処理開始: {tool_info}')


def _handle_creation_process_error(e: Exception, tool_info: dict[str, str]) -> None:
    """作成処理エラーを処理します。"""
    st.error(f'AIツール作成中にエラーが発生しました: {e}')
    if st.session_state.get('APP_ENV') == 'test':
        st.write(f'Debug: エラー詳細: {e}')
        st.write(f'Debug: ツール情報: {tool_info}')
        st.write(f'Debug: スタックトレース: {traceback.format_exc()}')


def _handle_successful_update() -> None:
    """更新成功時の処理。"""
    st.success('AIツールを更新しました。')
    st.session_state['show_edit_modal'] = False
    _reset_tool_counter_state()
    st.rerun()


def _handle_update_tool(tool_info: dict[str, Any]) -> None:
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
        tool_info.get('command', ''),
    )
    if success:
        _handle_successful_update()
    else:
        st.error('AIツールの更新に失敗しました。')


def _handle_disable_tool(tool_id: UUID, ai_tool_service: AIToolService) -> None:
    """ツール無効化処理。

    Args:
        tool_id: ツールID。
        ai_tool_service: AIツールサービス。
    """
    success = ai_tool_service.disable_ai_tool(AIToolID(tool_id))
    if success:
        st.success('AIツールを無効化しました。')
        _reset_tool_counter_state()
        st.rerun()
    else:
        st.error('AIツールの無効化に失敗しました。')


def _handle_enable_tool(tool_id: UUID, ai_tool_service: AIToolService) -> None:
    """ツール有効化処理。

    Args:
        tool_id: ツールID。
        ai_tool_service: AIツールサービス。
    """
    success = ai_tool_service.enable_ai_tool(AIToolID(tool_id))
    if success:
        st.success('AIツールを有効化しました。')
        _reset_tool_counter_state()
        st.rerun()
    else:
        st.error('AIツールの有効化に失敗しました。')


__all__ = ['render_ai_tool_management_page', 'st']
