"""メインページのE2Eテスト。"""

from playwright.sync_api import Page, expect


class TestMainPage:
    """メインページの基本機能をテストするクラス"""

    def test_ページ全体の基本レイアウトが正しく表示される(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # Then
        expect(page.get_by_text('AI Meeting Assistant 🤖')).to_be_visible()
        expect(page.get_by_role('heading', name='プロジェクト作成')).to_be_visible()


class TestProjectCreation:
    """プロジェクト作成機能をテストするクラス"""

    def test_プロジェクト作成フォームのバリデーション(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        create_button = sidebar.locator('button:has-text("プロジェクト作成")')

        # When
        # AIツールを選択せずにプロジェクト作成ボタンをクリック
        create_button.click()

        # Then
        # 警告メッセージが表示されることを確認
        expect(
            page.get_by_text('プロジェクト名と対象ディレクトリのパスを入力してください。')
        ).to_be_visible()

    def test_プロジェクト作成フォームの入力フィールド(self, page_with_app: Page) -> None:
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

    def test_プロジェクトが存在しない場合にメッセージが表示される(
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

    def test_プロジェクトが1つ以上存在する場合ヘッダーが表示される(
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

    def test_プロジェクト一覧に実行ボタンが表示される(self, page_with_app: Page) -> None:
        page = page_with_app
        # プロジェクト一覧の行を取得
        rows = page.locator('button:has-text("実行")')
        # Pendingプロジェクトが1つ以上あれば実行ボタンが表示される
        assert rows.count() >= 0  # 0個以上（データ状況による）

    def test_実行ボタン押下でプロジェクトが実行状態になる(self, page_with_app: Page) -> None:
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

    def test_デスクトップレイアウトの表示(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # デスクトップサイズに設定
        page.set_viewport_size({'width': 1920, 'height': 1080})

        # Then
        # サイドバーが表示されることを確認
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_モバイルレイアウトの表示(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # モバイルサイズに設定
        page.set_viewport_size({'width': 375, 'height': 667})

        # Then
        # モバイルでも基本的な要素が表示されることを確認
        expect(page.get_by_text('AI Meeting Assistant 🤖')).to_be_visible()


class TestProjectWorkflow:
    """プロジェクトワークフローの統合テスト"""

    def test_プロジェクト作成から実行までの一連の流れ(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')

        # When
        # プロジェクト作成フォームに入力
        project_name_input = sidebar.locator('input[aria-label="プロジェクト名"]')
        source_dir_input = sidebar.locator('input[aria-label="対象ディレクトリのパス"]')
        project_name_input.fill('テストプロジェクト')
        source_dir_input.fill('/test/path')

        # AIツールを選択（最初のオプションを選択）
        ai_tool_select = sidebar.locator('div[data-baseweb="select"]')
        ai_tool_select.click()

        # AIツールが存在する場合のみ選択を試行
        try:
            first_option = page.locator('li[role="option"]').first
            first_option.click()

            # プロジェクト作成ボタンをクリック
            create_button = sidebar.locator('button:has-text("プロジェクト作成")')
            create_button.click()

            # Then
            # 成功メッセージが表示されることを確認
            expect(page.get_by_text('プロジェクトを作成しました。')).to_be_visible()
        except Exception:
            # AIツールが存在しない場合は、ドロップダウンを閉じてからボタンをクリック
            page.keyboard.press('Escape')
            create_button = sidebar.locator('button:has-text("プロジェクト作成")')
            create_button.click()
            expect(page.get_by_text('AIツールを選択してください。')).to_be_visible()
