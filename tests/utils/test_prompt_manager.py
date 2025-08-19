"""PromptManagerクラスのテスト。"""

import pytest

from app.utils.prompt_manager import (
    OverviewPromptTemplate,
    PromptManager,
    PromptTemplate,
    ReviewPromptTemplate,
)


class TestPromptTemplate:
    """PromptTemplate抽象クラスのテスト。"""

    def test_prompt_template_is_abstract(self) -> None:
        """PromptTemplateが抽象クラスであることを確認する。"""
        with pytest.raises(TypeError):
            PromptTemplate()  # type: ignore[abstract]


class TestOverviewPromptTemplate:
    """OverviewPromptTemplateクラスのテスト。"""

    def test_overview_prompt_template_initialization(self) -> None:
        """OverviewPromptTemplateの初期化をテストする。"""
        # Act
        template = OverviewPromptTemplate()

        # Assert
        assert template is not None

    def test_generate_prompt_with_basic_params(self) -> None:
        """基本的なパラメータでのプロンプト生成をテストする。"""
        # Arrange
        template = OverviewPromptTemplate()
        directory_path = '/path/to/test'
        file_list: list[str] = ['file1.txt', 'file2.py', 'dir1/subfile.py']

        # Act
        prompt = template.generate_prompt(directory_path=directory_path, file_list=file_list)

        # Assert
        assert directory_path in prompt
        assert 'file1.txt' in prompt
        assert 'file2.py' in prompt
        assert 'dir1/subfile.py' in prompt
        assert '## 概要' in prompt
        assert '## 主要な内容' in prompt
        assert '## 主要な論点' in prompt
        assert '## アクション項目' in prompt
        assert '## 技術的な特徴' in prompt

    def test_generate_prompt_with_file_contents(self) -> None:
        """ファイル内容を含むプロンプト生成をテストする。"""
        # Arrange
        template = OverviewPromptTemplate()
        directory_path = '/path/to/test'
        file_list: list[str] = ['file1.txt', 'file2.py']
        file_contents = {
            'file1.txt': 'This is test content for file1',
            'file2.py': 'def test_function():\n    pass',
        }

        # Act
        prompt = template.generate_prompt(
            directory_path=directory_path,
            file_list=file_list,
            file_contents=file_contents,
        )

        # Assert
        assert 'ファイル内容:' in prompt
        assert 'This is test content for file1' in prompt
        assert 'def test_function():' in prompt

    def test_generate_prompt_with_empty_file_list(self) -> None:
        """空のファイルリストでのプロンプト生成をテストする。"""
        # Arrange
        template = OverviewPromptTemplate()
        directory_path = '/path/to/test'
        file_list: list[str] = []

        # Act
        prompt = template.generate_prompt(directory_path=directory_path, file_list=file_list)

        # Assert
        assert 'ファイルが見つかりませんでした。' in prompt

    def test_format_file_list(self) -> None:
        """ファイルリストのフォーマットをテストする。"""
        # Arrange
        template = OverviewPromptTemplate()
        file_list: list[str] = ['file1.txt', 'file2.py']

        # Act
        formatted = template._format_file_list(file_list)

        # Assert
        assert '- file1.txt' in formatted
        assert '- file2.py' in formatted

    def test_format_file_list_empty(self) -> None:
        """空のファイルリストのフォーマットをテストする。"""
        # Arrange
        template = OverviewPromptTemplate()
        file_list: list[str] = []

        # Act
        formatted = template._format_file_list(file_list)

        # Assert
        assert formatted == 'ファイルが見つかりませんでした。'


class TestReviewPromptTemplate:
    """ReviewPromptTemplateクラスのテスト。"""

    def test_review_prompt_template_initialization(self) -> None:
        """ReviewPromptTemplateの初期化をテストする。"""
        # Act
        template = ReviewPromptTemplate()

        # Assert
        assert template is not None

    def test_generate_prompt_with_basic_params(self) -> None:
        """基本的なパラメータでのプロンプト生成をテストする。"""
        # Arrange
        template = ReviewPromptTemplate()
        file_path = '/path/to/test.py'
        file_content = 'def test_function():\n    pass'

        # Act
        prompt = template.generate_prompt(file_path=file_path, file_content=file_content)

        # Assert
        assert file_path in prompt
        assert file_content in prompt
        assert '## コード品質' in prompt
        assert '## 設計・アーキテクチャ' in prompt
        assert '## コーディング規約' in prompt
        assert '## 改善提案' in prompt
        assert '## 指摘事項' in prompt
        assert '## 整合性チェック' in prompt

    def test_generate_prompt_with_custom_focus(self) -> None:
        """カスタム焦点でのプロンプト生成をテストする。"""
        # Arrange
        template = ReviewPromptTemplate()
        file_path = '/path/to/test.py'
        file_content = 'def test_function():\n    pass'
        review_focus = 'セキュリティ'

        # Act
        prompt = template.generate_prompt(
            file_path=file_path,
            file_content=file_content,
            review_focus=review_focus,
        )

        # Assert
        assert review_focus in prompt

    def test_generate_prompt_with_default_focus(self) -> None:
        """デフォルト焦点でのプロンプト生成をテストする。"""
        # Arrange
        template = ReviewPromptTemplate()
        file_path = '/path/to/test.py'
        file_content = 'def test_function():\n    pass'

        # Act
        prompt = template.generate_prompt(file_path=file_path, file_content=file_content)

        # Assert
        assert '全般的な品質' in prompt


class TestPromptManager:
    """PromptManagerクラスのテスト。"""

    def test_prompt_manager_initialization(self) -> None:
        """PromptManagerの初期化をテストする。"""
        # Act
        manager = PromptManager()

        # Assert
        assert manager is not None

    def test_generate_prompt_overview(self) -> None:
        """OVERVIEWツール用プロンプトの生成をテストする。"""
        # Arrange
        manager = PromptManager()
        directory_path = '/path/to/test'
        file_list: list[str] = ['file1.txt', 'file2.py']

        # Act
        prompt = manager.generate_prompt(
            'overview',
            directory_path=directory_path,
            file_list=file_list,
        )

        # Assert
        assert directory_path in prompt
        assert '## 概要' in prompt
        assert '## 主要な内容' in prompt

    def test_generate_prompt_review(self) -> None:
        """REVIEWツール用プロンプトの生成をテストする。"""
        # Arrange
        manager = PromptManager()
        file_path = '/path/to/test.py'
        file_content = 'def test_function():\n    pass'

        # Act
        prompt = manager.generate_prompt(
            'review',
            file_path=file_path,
            file_content=file_content,
        )

        # Assert
        assert file_path in prompt
        assert file_content in prompt
        assert '## コード品質' in prompt

    def test_generate_prompt_unsupported_tool_type(self) -> None:
        """サポートされていないツールタイプでのエラーをテストする。"""
        # Arrange
        manager = PromptManager()

        # Act & Assert
        with pytest.raises(ValueError, match='Unsupported tool type: invalid'):
            manager.generate_prompt('invalid')
