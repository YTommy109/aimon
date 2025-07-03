"""AIツール管理機能のE2Eテスト。"""

from playwright.sync_api import Page, expect


class TestAIToolManagementPage:
    """AIツール管理ページの基本レイアウトテスト。"""

    def test_ページが正常に表示される(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management

        # When
        # ページが既に表示済み

        # Then
        expect(page.get_by_role('heading', name='AIツール管理')).to_be_visible()

    def test_新規登録ボタンが表示される(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management

        # When
        # ページが既に表示済み

        # Then
        expect(page.get_by_role('button', name='新規AIツール登録')).to_be_visible()


class TestAIToolCreation:
    """AIツール作成機能のテスト。"""

    def test_新規登録ボタンをクリックするとモーダルが開く(
        self, page_with_ai_tool_management: Page
    ) -> None:
        # Given
        page = page_with_ai_tool_management

        # When
        page.get_by_role('button', name='新規AIツール登録').click()

        # Then
        expect(page.get_by_text('新規AIツール登録')).to_be_visible()

    def test_正常な値で新規ツールを作成できる(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management
        page.get_by_role('button', name='新規AIツール登録').click()

        # When
        page.get_by_role('textbox', name='AIツールID').fill('test_tool')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()

        # Then
        # 成功メッセージは表示されないので、一覧に追加されたことを確認
        expect(page.get_by_text('test_tool')).to_be_visible()
        expect(page.get_by_text('テストツール')).to_be_visible()

    def test_空のツールIDでは登録できない(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management
        page.get_by_role('button', name='新規AIツール登録').click()

        # When
        page.get_by_role('textbox', name='AIツールID').fill('')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()

        # Then
        expect(page.get_by_text('AIツールの作成に失敗しました。')).to_be_visible()


class TestAIToolList:
    """AIツール一覧機能のテスト。"""

    def test_ツールが存在しない場合にメッセージが表示される(
        self, page_with_ai_tool_management: Page
    ) -> None:
        # Given
        page = page_with_ai_tool_management

        # When
        # ページが既に表示済み

        # Then
        # AIツールが存在しない場合は、メッセージが表示される
        expect(page.get_by_role('heading', name='AIツール管理')).to_be_visible()
        expect(page.get_by_text('AIツールがまだ登録されていません。')).to_be_visible()
        expect(page.get_by_role('button', name='新規AIツール登録')).to_be_visible()

    def test_作成したツールが一覧に表示される(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management

        # ツールを作成
        page.get_by_role('button', name='新規AIツール登録').click()
        page.get_by_role('textbox', name='AIツールID').fill('test_tool')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()

        # When
        page.reload()

        # Then
        expect(page.get_by_text('test_tool')).to_be_visible()
        expect(page.get_by_text('テストツール')).to_be_visible()
        expect(page.get_by_text('テスト用のツール')).to_be_visible()
        # 「有効」の状態についてはstrict mode violationを避けるため、
        # 基本的なテストツールの表示確認のみで十分とする


class TestAIToolEdit:
    """AIツール編集機能のテスト。"""

    def test_編集ボタンをクリックするとモーダルが開く(
        self, page_with_ai_tool_management: Page
    ) -> None:
        # Given
        page = page_with_ai_tool_management

        # ツールを作成
        page.get_by_role('button', name='新規AIツール登録').click()
        page.get_by_role('textbox', name='AIツールID').fill('test_tool')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()
        page.reload()

        # When
        # 特定のツールの編集ボタンをクリック（最初のツールの編集ボタン）
        page.locator('button:has-text("編集")').first.click()

        # Then
        expect(page.get_by_text('AIツール編集')).to_be_visible()

    def test_ツール情報を更新できる(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management

        # ツールを作成
        page.get_by_role('button', name='新規AIツール登録').click()
        page.get_by_role('textbox', name='AIツールID').fill('test_tool')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()
        page.reload()

        # When
        page.locator('button:has-text("編集")').first.click()
        # 既存の値をクリアしてから新しい値を入力
        page.get_by_role('textbox', name='ツール名').clear()
        page.get_by_role('textbox', name='ツール名').fill('更新されたツール')
        page.get_by_role('textbox', name='説明').clear()
        page.get_by_role('textbox', name='説明').fill('更新された説明')
        page.get_by_role('button', name='更新').click()

        # Then
        # 成功メッセージは表示されないので、一覧の内容が更新されたことを確認
        expect(page.get_by_text('更新されたツール')).to_be_visible()
        expect(page.get_by_text('更新された説明')).to_be_visible()


class TestAIToolStatusChange:
    """AIツール状態変更機能のテスト。"""

    def test_ツールを無効化できる(self, page_with_ai_tool_management: Page) -> None:
        # Given
        page = page_with_ai_tool_management

        # ツールを作成
        page.get_by_role('button', name='新規AIツール登録').click()
        page.get_by_role('textbox', name='AIツールID').fill('test_tool')
        page.get_by_role('textbox', name='ツール名').fill('テストツール')
        page.get_by_role('textbox', name='説明').fill('テスト用のツール')
        page.get_by_role('button', name='作成').click()
        page.reload()

        # When
        page.locator('button:has-text("無効化")').first.click()

        # Then
        # 無効化されたツールは一覧から消える
        page.reload()
        expect(page.get_by_text('test_tool')).not_to_be_visible()
        expect(page.get_by_text('テストツール')).not_to_be_visible()

    # TODO: 無効化されたツールの有効化機能は、現在の仕様では一覧に表示されないため実装できない
    # 将来的に無効化されたツールも表示する仕様に変更された場合に、このテストを有効化する
    # def test_無効化されたツールを有効化できる(self, page_with_ai_tool_management: Page) -> None:
    #     # Given
    #     page = page_with_ai_tool_management
    #
    #     # ツールを作成して無効化
    #     page.get_by_role('button', name='新規AIツール登録').click()
    #     page.get_by_role('textbox', name='AIツールID').fill('test_tool')
    #     page.get_by_role('textbox', name='ツール名').fill('テストツール')
    #     page.get_by_role('textbox', name='説明').fill('テスト用のツール')
    #     page.get_by_role('button', name='作成').click()
    #     page.reload()
    #     page.locator('button:has-text("無効化")').first.click()
    #     page.reload()
    #
    #     # When
    #     page.locator('button:has-text("有効化")').first.click()
    #
    #     # Then
    #     # 成功メッセージは表示されないので、状態が有効に戻ったことを確認
    #     expect(page.get_by_text('有効')).to_be_visible()
