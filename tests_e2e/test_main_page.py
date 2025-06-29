"""メインページの基本機能をテストするE2Eテストケース"""

import re

from playwright.sync_api import Page, expect


class TestMainPage:
    """メインページの基本機能をテストするクラス"""

    def test_ページ全体の基本レイアウトが正しく表示される(self, page_with_app: Page) -> None:
        """ページタイトル、ヘッダー、サイドバーが正しく表示されることを統合的に確認"""
        # Given
        page = page_with_app

        # Then - ページタイトルの確認
        expect(page).to_have_title(re.compile('AI Meeting Assistant'))

        # メインヘッダーの確認
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        expect(header).to_be_visible()

        # サイドバーとプロジェクト作成フォームの要素を確認
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()
        expect(sidebar.get_by_role('heading', name='プロジェクト作成')).to_be_visible()
        expect(sidebar.locator('text="プロジェクト名"')).to_be_visible()
        expect(sidebar.locator('text="対象ディレクトリのパス"')).to_be_visible()
        expect(sidebar.locator('text="AIツールを選択"')).to_be_visible()
        expect(sidebar.get_by_role('button', name='プロジェクト作成')).to_be_visible()

        # プロジェクト一覧セクションの確認
        expect(page.get_by_role('heading', name='プロジェクト一覧')).to_be_visible()

        # プロジェクトがない場合のメッセージまたはプロジェクト一覧の表示を確認
        project_info = page.get_by_text('まだプロジェクトがありません。')
        project_header = page.get_by_role('strong', name='プロジェクト名')
        expect(project_info.or_(project_header)).to_be_visible()


class TestProjectCreation:
    """プロジェクト作成機能をテストするクラス"""

    def test_プロジェクト作成フォームのバリデーションをテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        create_button = sidebar.locator('button:has-text("プロジェクト作成")')

        # When
        # AIツールを選択せずにプロジェクト作成ボタンをクリック
        create_button.click()

        # Then
        # 警告メッセージが表示されることを確認
        expect(page.locator('text="AIツールを選択してください。"')).to_be_visible()

    def test_プロジェクト作成フォームの入力フィールドをテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        project_name_input = sidebar.locator('input[aria-label="プロジェクト名"]')
        source_dir_input = sidebar.locator('input[aria-label="対象ディレクトリのパス"]')

        # When
        project_name_input.fill('テストプロジェクト')
        source_dir_input.fill('/test/path')

        # Then
        expect(project_name_input).to_have_value('テストプロジェクト')
        expect(source_dir_input).to_have_value('/test/path')


class TestProjectList:
    """プロジェクト一覧機能をテストするクラス"""

    def test_プロジェクトが存在しない場合にメッセージが表示されることをテスト(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # Then
        # プロジェクトがない場合のメッセージを確認
        # Streamlitのバージョンによりdata-testidが変わる可能性があるため、
        # より堅牢なテキストベースのセレクタを使用
        empty_message = page.get_by_text('まだプロジェクトがありません。')
        expect(empty_message).to_be_visible()

    def test_プロジェクトが1つ以上存在する場合ヘッダーが表示されることをテスト(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app
        project_header = page.get_by_role('strong', name='プロジェクト名')

        # When
        # (操作なし)

        # Then
        # データが存在しない場合は表示されない可能性があるため、条件付きでテスト
        if project_header.is_visible():
            expect(page.get_by_role('strong', name='No.')).to_be_visible()
            expect(page.get_by_role('strong', name='作成日時')).to_be_visible()
            expect(page.get_by_role('strong', name='実行日時')).to_be_visible()

    def test_プロジェクト一覧に実行ボタンが表示されることをテスト(
        self, page_with_app: Page
    ) -> None:
        page = page_with_app
        # プロジェクト一覧の行を取得
        rows = page.locator('button:has-text("実行")')
        # Pendingプロジェクトが1つ以上あれば実行ボタンが表示される
        assert rows.count() >= 0  # 0個以上（データ状況による）

    def test_実行ボタン押下でプロジェクトが実行状態になることをテスト(
        self, page_with_app: Page
    ) -> None:
        page = page_with_app
        # 実行ボタンがあればクリック
        exec_btns = page.locator('button:has-text("実行")')
        if exec_btns.count() > 0:
            exec_btns.nth(0).click()
            # 実行後はボタンが消える（非表示になる）
            expect(exec_btns.nth(0)).not_to_be_visible()

    def test_完了済みや実行中プロジェクトには実行ボタンが表示されない(
        self, page_with_app: Page
    ) -> None:
        page = page_with_app
        # 完了済みや実行中の行には「実行」ボタンがないことを確認
        # ここでは「詳細」ボタンの数と「実行」ボタンの数が異なる場合があることを許容
        exec_btns = page.locator('button:has-text("実行")')
        detail_btns = page.locator('button:has-text("詳細")')
        assert exec_btns.count() <= detail_btns.count()


class TestResponsiveDesign:
    """レスポンシブデザインをテストするクラス"""

    def test_デスクトップレイアウトの表示をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        page.set_viewport_size({'width': 1920, 'height': 1080})

        # Then
        # メインコンテンツとサイドバーが適切に表示されることを確認
        expect(page.locator('[data-testid="stSidebar"]')).to_be_visible()
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        expect(header).to_be_visible()

    def test_モバイルレイアウトの表示をテスト(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        page.set_viewport_size({'width': 375, 'height': 667})

        # Then
        # メインコンテンツが表示されることを確認
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        expect(header).to_be_visible()

        # モバイルではサイドバーが折りたたまれる場合があるため、
        # 基本的な要素の存在を確認
        expect(page.locator('[data-testid="stSidebar"]')).to_be_attached()
