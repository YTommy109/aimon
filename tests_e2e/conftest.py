"""E2Eテスト用のPytest設定とフィクスチャを定義します。"""

import os
import shutil

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def clean_test_data_before_each_test() -> None:
    """各テストの前にテスト用データディレクトリを削除して、クリーンな状態でテストを開始します。"""
    # 環境変数 `DATA_DIR_TEST` からテスト用ディレクトリのパスを取得。
    # 未設定の場合はデフォルト値 '.data_test' を使用。
    test_data_dir = os.environ.get('DATA_DIR_TEST', '.data_test')

    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

    # テスト用データディレクトリを作成
    os.makedirs(test_data_dir, exist_ok=True)

    # 環境変数を明示的に設定
    os.environ['DATA_DIR_TEST'] = test_data_dir
    os.environ['APP_ENV'] = 'test'


@pytest.fixture
def page_with_app(page: Page, base_url: str) -> Page:
    """アプリケーションにアクセス済みのPageオブジェクトを返します"""
    page.goto(base_url)
    # ファイル削除などを反映させるため、一度リロードを挟んで状態を確実にする
    page.reload()
    # Streamlitアプリが完全に読み込まれるまで待つ
    expect(page.get_by_role('heading', name='AI Meeting Assistant 🤖')).to_be_visible(timeout=10000)

    return page


@pytest.fixture
def page_with_ai_tool_management(page: Page, base_url: str) -> Page:
    """AIツール管理ページにアクセス済みのPageオブジェクトを返します"""
    page.goto(f'{base_url}/AI_Tool_Management')
    # ファイル削除などを反映させるため、一度リロードを挟んで状態を確実にする
    page.reload()
    # AIツール管理ページが完全に読み込まれるまで待つ
    expect(page.get_by_role('heading', name='AIツール管理')).to_be_visible(timeout=10000)

    return page


@pytest.fixture
def page_with_ai_tool_test_data(page: Page, base_url: str) -> Page:
    """AIツールのテストデータが作成済みのPageオブジェクトを返します"""
    page.goto(f'{base_url}/AI_Tool_Management')
    page.reload()
    expect(page.get_by_role('heading', name='AIツール管理')).to_be_visible(timeout=10000)

    # テスト用のAIツールを作成
    page.get_by_role('button', name='新規AIツール登録').click()
    page.get_by_label('ツール名').fill('テスト用AIツール')
    page.get_by_label('説明').fill('E2Eテスト用のAIツール')
    page.get_by_label('エンドポイントURL').fill('https://test.example.com/api')
    page.get_by_role('button', name='登録').first.click()

    # 登録完了を待機（固定時間待機）
    page.wait_for_timeout(3000)

    # ページをリロードしてからリスト表示を確認
    page.reload()
    page.wait_for_timeout(2000)

    # 作成されたツールが表示されるまで動的に待機
    # より長いタイムアウトとリトライロジックを追加
    max_retries = 5
    for attempt in range(max_retries):
        try:
            expect(page.get_by_text('テスト用AIツール')).to_be_visible(timeout=10000)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                # 最後の試行で失敗した場合はエラーを発生させる
                raise e
            # ページを再読み込みして再試行
            page.reload()
            page.wait_for_timeout(2000)

    return page
