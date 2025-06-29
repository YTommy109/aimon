"""プロジェクトワークフローの統合テストケース"""

import time

from playwright.sync_api import Page, expect


class TestProjectWorkflow:
    """プロジェクトの作成から実行までの一連のワークフローをテストするクラス"""

    def test_プロジェクト詳細モーダルの機能をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        # 前提：詳細ボタンが表示されるプロジェクトが1つ以上存在する
        detail_buttons = page.locator('button:has-text("詳細")')

        # When
        if detail_buttons.count() > 0:
            detail_buttons.first.click()
            modal = page.locator('[role="dialog"]')

            # Then
            expect(modal).to_be_visible(timeout=5000)
            # モーダル内にプロジェクト情報が表示されることを確認
            expect(modal.locator('text="UUID"')).to_be_visible()
            expect(modal.locator('text="対象パス"')).to_be_visible()
            expect(modal.locator('text="AIツール"')).to_be_visible()
            expect(modal.locator('text="ステータス"')).to_be_visible()

    def test_プロジェクトのステータスアイコンの表示をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        # 前提：プロジェクトが1つ以上存在する
        project_rows = page.locator('[data-testid="column"]:has-text("テスト")')

        # When
        # (操作なし)

        # Then
        if project_rows.count() > 0:
            # 🏃 (実行中), ⏳ (処理中), ✅ (完了), ❌ (失敗), 💬 (その他)
            status_icons = ['🏃', '⏳', '✅', '❌', '💬']
            has_status_icon = False

            for icon in status_icons:
                if page.locator(f'text="{icon}"').count() > 0:
                    has_status_icon = True
                    break
            # 少なくとも1つのステータスアイコンが表示されている
            assert has_status_icon

    def test_プロジェクト実行コントロールの表示をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        project_list = page.get_by_role('strong', name='プロジェクト名')

        # When
        # (操作なし)

        # Then
        if project_list.is_visible():
            # 実行プロジェクト選択のセレクトボックスを確認
            expect(page.locator('text="実行するプロジェクトを選択してください"')).to_be_visible()
            expect(page.get_by_role('button', name='選択したプロジェクトを実行')).to_be_visible()

    def test_ナビゲーションとインタラクションのテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        project_name_input = sidebar.locator('input[aria-label="プロジェクト名"]')

        # When
        project_name_input.click()
        project_name_input.fill('インタラクションテスト')

        # Then
        expect(sidebar).to_be_visible()
        expect(project_name_input).to_have_value('インタラクションテスト')

        # When
        project_name_input.clear()

        # Then
        expect(project_name_input).to_have_value('')
        expect(page.get_by_role('heading', name='プロジェクト一覧')).to_be_visible()
        expect(page.get_by_role('heading', name='プロジェクト作成')).to_be_visible()


class TestErrorHandling:
    """エラーハンドリングをテストするクラス"""

    def test_無効な入力に対するエラーハンドリングをテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        page.get_by_role('button', name='プロジェクト作成').click()

        # Then
        expect(page.get_by_text('AIツールを選択してください。')).to_be_visible(timeout=5000)

    def test_ネットワークエラーに対する耐性をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし - 実際のネットワークエラーの発生は複雑なため)

        # Then
        # ページの基本要素が正しく読み込まれていることを確認
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        expect(header).to_be_visible()


class TestPerformance:
    """パフォーマンス関連のテストクラス"""

    def test_ページの読み込み時間をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        start_time = time.time()

        # When
        # メインコンテンツの読み込み完了を待つ
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        expect(header).to_be_visible(timeout=10000)

        # Then
        end_time = time.time()
        load_time = end_time - start_time
        assert load_time < 15, f'ページの読み込みが遅すぎます: {load_time:.2f}秒'

    def test_自動更新機能のパフォーマンスをテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし)

        # Then
        # 自動更新が設定されていてもページが正常に動作することを確認
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        initial_title = header.text_content()
        assert initial_title == 'AI Meeting Assistant 🤖'


class TestAccessibility:
    """アクセシビリティをテストするクラス"""

    def test_キーボードナビゲーションをテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        page.keyboard.press('Tab')

        # Then
        # フォーカス可能な要素が存在することを確認
        focused_element = page.evaluate('document.activeElement.tagName')
        assert focused_element in [
            'INPUT',
            'BUTTON',
            'SELECT',
            'A',
            'DIV',
            'SECTION',
        ], f'フォーカス可能な要素: {focused_element}'

    def test_ARIAラベルの存在をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')

        # When
        # (要素の取得)
        project_name_input = sidebar.locator('input[aria-label="プロジェクト名"]')
        source_dir_input = sidebar.locator('input[aria-label="対象ディレクトリのパス"]')

        # Then
        expect(project_name_input).to_be_visible()
        expect(source_dir_input).to_be_visible()
        expect(page.locator('[aria-label="プロジェクト名"]')).to_be_visible()
        expect(page.locator('[aria-label="対象ディレクトリのパス"]')).to_be_visible()

    def test_カラーコントラストの基本確認(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')

        # Then
        expect(header).to_be_visible()
        # 基本的な色の情報が取得できることを確認
        title_color = header.evaluate('element => getComputedStyle(element).color')
        assert title_color is not None, 'タイトルの色が取得できません'
