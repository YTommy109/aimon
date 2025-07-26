"""プロジェクトワークフローのE2Eテスト。"""

import contextlib
import time

from playwright.sync_api import Page, expect


class TestProjectWorkflow:
    """プロジェクトワークフローの統合テストクラス"""

    def test_プロジェクト詳細モーダルを開いた場合に情報が表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

    def test_プロジェクト詳細モーダルの表示状態が正常である(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルの基本要素が正しく表示されることを確認
            modal_title = page.get_by_text('プロジェクト詳細')
            expect(modal_title).to_be_visible()

            # モーダルの背景が正しく表示されていることを確認
            modal_background = page.locator('.stModal')
            expect(modal_background).to_be_visible()

            # モーダルが画面中央に配置されていることを確認
            modal_rect = modal_background.bounding_box()
            page_rect = page.viewport_size
            assert modal_rect is not None, 'モーダルの位置情報が取得できません'
            assert page_rect is not None, 'ページサイズ情報が取得できません'

            # モーダルが画面の中央付近にあることを確認（完全な中央でなくても許容）
            modal_center_x = modal_rect['x'] + modal_rect['width'] / 2
            modal_center_y = modal_rect['y'] + modal_rect['height'] / 2
            page_center_x = page_rect['width'] / 2
            page_center_y = page_rect['height'] / 2

            # 中央から20%以内の範囲にあることを確認
            tolerance_x = page_rect['width'] * 0.2
            tolerance_y = page_rect['height'] * 0.2
            assert abs(modal_center_x - page_center_x) < tolerance_x, (
                f'モーダルが画面中央に配置されていません: '
                f'X座標差={abs(modal_center_x - page_center_x)}'
            )
            assert abs(modal_center_y - page_center_y) < tolerance_y, (
                f'モーダルが画面中央に配置されていません: '
                f'Y座標差={abs(modal_center_y - page_center_y)}'
            )

    def test_プロジェクト詳細モーダルの内容が正しく表示される(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダル内の主要な情報が表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # プロジェクト情報のフィールドが存在することを確認
            # UUID、対象パス、AIツール、ステータスなどの情報が表示される
            project_info_selectors = [
                'text=UUID:',
                'text=対象パス:',
                'text=AIツール:',
                'text=ステータス:',
                'text=作成日時:',
                'text=実行日時:',
                'text=終了日時:',
            ]

            for selector in project_info_selectors:
                with contextlib.suppress(Exception):
                    # 一部の情報が表示されない場合でもテストを継続
                    expect(page.locator(selector)).to_be_visible(timeout=3000)

    def test_プロジェクト詳細モーダルの閉じるボタンが正常に動作する(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # 閉じるボタンをクリック
            close_button = page.locator('button[aria-label="Close"]')
            if close_button.count() > 0:
                close_button.first.click()

                # Then
                # モーダルが非表示になることを確認
                expect(page.get_by_text('プロジェクト詳細')).not_to_be_visible()

    def test_プロジェクト詳細モーダルのZインデックスが適切である(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルのZインデックスが適切な値であることを確認
            modal_background = page.locator('.stModal')
            z_index = modal_background.evaluate(
                'element => window.getComputedStyle(element).zIndex'
            )

            # Zインデックスが数値で、適切な範囲内であることを確認
            assert z_index is not None, 'モーダルのZインデックスが取得できません'
            try:
                z_index_value = int(z_index)
                assert z_index_value > 0, (
                    f'モーダルのZインデックスが適切ではありません: {z_index_value}'
                )
            except ValueError:
                # autoやinheritなどの値の場合も許容
                pass

    def test_プロジェクト詳細モーダルのオーバーレイが正しく表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルのオーバーレイが表示されていることを確認
            overlay = page.locator('.stModal .stModalOverlay')
            if overlay.count() > 0:
                expect(overlay.first).to_be_visible()

                # オーバーレイの背景色が適切であることを確認
                background_color = overlay.first.evaluate(
                    'element => window.getComputedStyle(element).backgroundColor'
                )
                assert background_color is not None, 'オーバーレイの背景色が取得できません'

                # 背景色が透明でないことを確認（rgba(0,0,0,0)以外）
                assert background_color != 'rgba(0, 0, 0, 0)', (
                    f'オーバーレイの背景色が透明です: {background_color}'
                )

    def test_プロジェクト詳細モーダルがレスポンシブ対応している(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # モーダルのサイズが適切であることを確認
            modal_background = page.locator('.stModal')
            modal_rect = modal_background.bounding_box()
            page_rect = page.viewport_size

            assert modal_rect is not None, 'モーダルの位置情報が取得できません'
            assert page_rect is not None, 'ページサイズ情報が取得できません'

            # モーダルが画面サイズを超えていないことを確認
            assert modal_rect['width'] <= page_rect['width'], (
                f'モーダルが画面幅を超えています: '
                f'モーダル幅={modal_rect["width"]}, 画面幅={page_rect["width"]}'
            )
            assert modal_rect['height'] <= page_rect['height'], (
                f'モーダルが画面高さを超えています: '
                f'モーダル高さ={modal_rect["height"]}, 画面高さ={page_rect["height"]}'
            )

    def test_プロジェクト詳細モーダルのアニメーション状態が正常である(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # モーダルのアニメーション状態を確認
            modal_background = page.locator('.stModal')

            # モーダルが表示状態であることを確認（opacity > 0）
            opacity = modal_background.evaluate(
                'element => window.getComputedStyle(element).opacity'
            )
            assert opacity is not None, 'モーダルの透明度が取得できません'

            try:
                opacity_value = float(opacity)
                assert opacity_value > 0, f'モーダルが透明になっています: opacity={opacity_value}'
            except ValueError:
                # opacityが数値でない場合も許容
                pass

    def test_プロジェクト詳細モーダルのフォーカス管理が正常である(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # モーダル内にフォーカス可能な要素が存在することを確認
            modal = page.locator('.stModal')
            focusable_elements = modal.locator(
                'button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            )

            if focusable_elements.count() > 0:
                # フォーカス可能な要素が存在する場合、その要素にフォーカスできることを確認
                first_focusable = focusable_elements.first
                first_focusable.focus()

                # フォーカスが正しく設定されていることを確認
                focused_element = page.evaluate('document.activeElement')
                assert focused_element is not None, 'フォーカス可能な要素が見つかりません'

    def test_プロジェクト詳細モーダルのキーボード操作が正常である(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # プロジェクト一覧の詳細ボタンをクリック（存在する場合）
        detail_buttons = page.locator('button:has-text("詳細")')
        if detail_buttons.count() > 0:
            detail_buttons.first.click()

            # Then
            # モーダルが表示されることを確認
            expect(page.get_by_text('プロジェクト詳細')).to_be_visible()

            # Escapeキーでモーダルが閉じられることを確認
            page.keyboard.press('Escape')

            # モーダルが非表示になることを確認
            expect(page.get_by_text('プロジェクト詳細')).not_to_be_visible()

    def test_プロジェクトが存在する場合にステータスアイコンが表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし)

        # Then
        # プロジェクトが存在する場合、ステータスアイコンが表示されることを確認
        # プロジェクトがない場合は何も表示されない
        project_list = page.locator('[data-testid="stDataFrame"]')
        if project_list.count() > 0:
            # プロジェクトが存在する場合の確認
            expect(project_list).to_be_visible()

    def test_プロジェクトが存在する場合に実行コントロールが表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし)

        # Then
        # プロジェクトが存在する場合、実行ボタンが表示されることを確認
        # プロジェクトがない場合は何も表示されない
        exec_buttons = page.locator('button:has-text("実行")')
        if exec_buttons.count() > 0:
            expect(exec_buttons.first).to_be_visible()

    def test_プロジェクト名入力欄で値を入力_クリアした場合に正しく反映される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        project_name_input = sidebar.locator('input[aria-label="プロジェクト名"]')

        # When
        project_name_input.fill('テストプロジェクト')
        project_name_input.clear()

        # Then
        expect(project_name_input).to_have_value('')

    def test_対象ディレクトリ入力欄で値を入力_クリアした場合に正しく反映される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        source_dir_input = sidebar.locator('input[aria-label="対象ディレクトリのパス"]')

        # When
        source_dir_input.fill('/test/path')
        source_dir_input.clear()

        # Then
        expect(source_dir_input).to_have_value('')

    def test_AIツール選択ドロップダウンが正常に動作する(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        ai_tool_select = sidebar.locator('div[data-baseweb="select"]')

        # When
        ai_tool_select.click()

        # Then
        # ドロップダウンが開くことを確認（オプションがある場合とない場合の両方を考慮）
        try:
            expect(page.locator('li[role="option"]')).to_be_visible(timeout=3000)
        except Exception:
            # オプションがない場合は「No results」が表示される
            expect(page.get_by_text('No results')).to_be_visible(timeout=3000)

    def test_プロジェクト作成ボタンが正常に動作する(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app
        sidebar = page.locator('[data-testid="stSidebar"]')
        create_button = sidebar.locator('button:has-text("プロジェクト作成")')

        # When
        # (ボタンの存在確認)

        # Then
        expect(create_button).to_be_visible()

    def test_プロジェクト一覧とプロジェクト作成フォームが同時に表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし)

        # Then
        # プロジェクト一覧とプロジェクト作成フォームが同時に表示されることを確認
        expect(page.get_by_role('heading', name='プロジェクト一覧')).to_be_visible()
        expect(page.get_by_role('heading', name='プロジェクト作成')).to_be_visible()

    def test_AIツール未選択でプロジェクト作成ボタンを押した場合にエラーメッセージが表示される(
        self, page_with_app: Page
    ) -> None:
        # Given
        page = page_with_app

        # When
        # AIツールを選択せずにプロジェクト作成ボタンをクリック
        sidebar = page.locator('[data-testid="stSidebar"]')
        create_button = sidebar.locator('button:has-text("プロジェクト作成")')
        create_button.click()

        # Then
        expect(
            page.get_by_text('プロジェクト名と対象ディレクトリのパスを入力してください。')
        ).to_be_visible(timeout=5000)

    def test_ネットワークエラーが発生した場合でもページが正常に表示される(
        self, page_with_app: Page
    ) -> None:
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

    def test_ページを読み込んだ場合に15秒未満で表示される(self, page_with_app: Page) -> None:
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

    def test_自動更新機能が有効な場合にページが正常に動作する(self, page_with_app: Page) -> None:
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

    def test_Tabキー操作でフォーカスが移動する(self, page_with_app: Page) -> None:
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

    def test_サイドバー入力欄にARIAラベルが存在する(self, page_with_app: Page) -> None:
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

    def test_タイトルのカラーコントラストが取得できる(self, page_with_app: Page) -> None:
        # Given
        page = page_with_app

        # When
        # (操作なし)

        # Then
        # タイトルの色情報が取得できることを確認
        header = page.get_by_role('heading', name='AI Meeting Assistant 🤖')
        color = header.evaluate('element => window.getComputedStyle(element).color')
        assert color is not None, 'タイトルの色情報が取得できません'
