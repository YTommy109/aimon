"""E2Eテストの設定とユーティリティ"""

from typing import Any

# ブラウザ固有の設定
BROWSER_CONFIGS: dict[str, dict[str, Any]] = {
    'chromium': {
        'timeout': 30000,
        'action_timeout': 5000,
        'navigation_timeout': 10000,
        'args': ['--disable-web-security'],  # CORS対応
    },
    'firefox': {
        'timeout': 35000,
        'action_timeout': 6000,
        'navigation_timeout': 12000,
        'args': [],
    },
    'webkit': {
        'timeout': 40000,  # WebKitは少し遅い傾向
        'action_timeout': 7000,
        'navigation_timeout': 15000,
        'args': [],
    },
}

# 共通設定
COMMON_CONFIG = {
    'expect_timeout': 5000,
    'screenshot_mode': 'only-on-failure',
    'video_mode': 'retain-on-failure',
    'trace_mode': 'retain-on-failure',
}

# テスト分類
TEST_CATEGORIES = {
    'smoke': [
        'test_ページ全体の基本レイアウトが正しく表示される',
    ],
    'core': [
        'test_プロジェクト作成フォームのバリデーションをテスト',
        'test_プロジェクト作成フォームの入力フィールドをテスト',
        'test_プロジェクト詳細モーダルの機能をテスト',
    ],
    'ui': [
        'test_デスクトップレイアウトの表示をテスト',
        'test_モバイルレイアウトの表示をテスト',
    ],
    'performance': [
        'test_ページの読み込み時間をテスト',
        'test_自動更新機能のパフォーマンスをテスト',
    ],
    'accessibility': [
        'test_キーボードナビゲーションをテスト',
        'test_ARIAラベルの存在をテスト',
        'test_カラーコントラストの基本確認',
    ],
}
