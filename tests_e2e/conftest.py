"""E2Eテスト用のPytest設定とフィクスチャを定義します。"""

import os
import shutil

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(autouse=True)
def clean_test_data_before_each_test() -> None:
    """各テストの前にテスト用データディレクトリを削除して、クリーンな状態でテストを開始します。"""
    # テスト用データディレクトリのパスを取得
    test_data_dir = os.environ.get('DATA_DIR', '.data_test')

    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

    # テスト用データディレクトリを作成
    os.makedirs(test_data_dir, exist_ok=True)

    # 環境変数を明示的に設定
    os.environ['ENV'] = 'test'


@pytest.fixture
def page_with_app(page: Page, base_url: str) -> Page:
    """アプリケーションにアクセス済みのPageオブジェクトを返します"""
    page.goto(base_url)
    # ファイル削除などを反映させるため、一度リロードを挟んで状態を確実にする
    page.reload()
    # Streamlitアプリが完全に読み込まれるまで待つ
    expect(page.get_by_role('heading', name='AI Project Manager')).to_be_visible(timeout=10000)

    return page
