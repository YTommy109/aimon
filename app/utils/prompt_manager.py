"""プロンプト管理クラス。"""

from abc import ABC, abstractmethod


class PromptTemplate(ABC):
    """プロンプトテンプレートの抽象基底クラス。"""

    @abstractmethod
    def generate_prompt(self, **kwargs: str | list[str] | dict[str, str]) -> str:
        """プロンプトを生成する。

        Args:
            **kwargs: プロンプト生成に必要なパラメータ。

        Returns:
            生成されたプロンプト。
        """


class OverviewPromptTemplate(PromptTemplate):
    """OVERVIEWツール用プロンプトテンプレート。"""

    def generate_prompt(self, **kwargs: str | list[str] | dict[str, str]) -> str:
        """OVERVIEWツール用プロンプトを生成する。

        Args:
            **kwargs: プロンプト生成に必要なパラメータ。
                - directory_path: 対象ディレクトリパス
                - file_list: ファイル一覧
                - file_contents: ファイル内容(オプション)

        Returns:
            生成されたプロンプト。
        """
        directory_path = kwargs.get('directory_path', '')
        file_list = kwargs.get('file_list', [])
        file_contents = kwargs.get('file_contents', {})

        # 型チェックとキャスト
        if not isinstance(directory_path, str):
            directory_path = ''
        if not isinstance(file_list, list):
            file_list = []
        if not isinstance(file_contents, dict):
            file_contents = {}

        prompt = self._build_base_prompt(directory_path, file_list)
        prompt += self._build_file_contents_section(file_contents)
        prompt += self._build_instruction_section()

        return prompt

    def _build_base_prompt(self, directory_path: str, file_list: list[str]) -> str:
        """基本プロンプトを構築する。"""
        return f"""以下のディレクトリの内容を分析し、概要を生成してください。

対象ディレクトリ: {directory_path}

ファイル一覧:
{self._format_file_list(file_list)}

"""

    def _build_file_contents_section(self, file_contents: dict[str, str]) -> str:
        """ファイル内容セクションを構築する。"""
        if not file_contents:
            return ''

        section = 'ファイル内容:\n'
        for file_path, content in file_contents.items():
            section += f'\n--- {file_path} ---\n{content[:1000]}...\n'
        return section

    def _build_instruction_section(self) -> str:
        """指示セクションを構築する。"""
        return """

以下の形式で回答してください:

## 概要
[ディレクトリの全体像を簡潔に説明]

## 主要な内容
[重要なファイルやディレクトリの説明]

## 主要な論点
[分析から得られた主要な論点や特徴]

## アクション項目
[今後の作業や検討が必要な項目]

## 技術的な特徴
[使用されている技術やフレームワーク等]

日本語で回答してください。"""

    def _format_file_list(self, file_list: list[str]) -> str:
        """ファイル一覧をフォーマットする。

        Args:
            file_list: ファイルパスのリスト。

        Returns:
            フォーマットされたファイル一覧。
        """
        if not file_list:
            return 'ファイルが見つかりませんでした。'

        formatted_list = []
        for file_path in file_list:
            formatted_list.append(f'- {file_path}')

        return '\n'.join(formatted_list)


class ReviewPromptTemplate(PromptTemplate):
    """REVIEWツール用プロンプトテンプレート。"""

    def generate_prompt(self, **kwargs: str | list[str] | dict[str, str]) -> str:
        """REVIEWツール用プロンプトを生成する。

        Args:
            **kwargs: プロンプト生成に必要なパラメータ。
                - file_path: 対象ファイルパス
                - file_content: ファイル内容
                - review_focus: レビューの焦点(オプション)

        Returns:
            生成されたプロンプト。
        """
        file_path = kwargs.get('file_path', '')
        file_content = kwargs.get('file_content', '')
        review_focus = kwargs.get('review_focus', '全般的な品質')

        # 型チェックとキャスト
        if not isinstance(file_path, str):
            file_path = ''
        if not isinstance(file_content, str):
            file_content = ''
        if not isinstance(review_focus, str):
            review_focus = '全般的な品質'

        return f"""以下のファイルのコードレビューを実行してください。

対象ファイル: {file_path}

レビューの焦点: {review_focus}

ファイル内容:
```
{file_content}
```

以下の観点でレビューを実行し、改善提案を提示してください:

## コード品質
- 可読性
- 保守性
- パフォーマンス
- セキュリティ

## 設計・アーキテクチャ
- クラス設計
- 関数設計
- 依存関係
- 設計パターンの適用

## コーディング規約
- 命名規則
- コメント
- エラーハンドリング
- テスト可能性

## 改善提案
- 具体的な改善点
- リファクタリングの提案
- ベストプラクティスの適用

## 指摘事項
- バグの可能性
- セキュリティ上の問題
- パフォーマンスの問題

## 整合性チェック
- 他のファイルとの整合性
- ドキュメントとの整合性
- 要件との整合性

日本語で回答してください。"""


class PromptManager:
    """プロンプト管理クラス。"""

    def __init__(self) -> None:
        """プロンプトマネージャーを初期化する。"""
        self._templates = {
            'overview': OverviewPromptTemplate(),
            'review': ReviewPromptTemplate(),
        }

    def generate_prompt(self, tool_type: str, **kwargs: str | list[str] | dict[str, str]) -> str:
        """指定されたツールタイプのプロンプトを生成する。

        Args:
            tool_type: ツールタイプ('overview' または 'review')。
            **kwargs: プロンプト生成に必要なパラメータ。

        Returns:
            生成されたプロンプト。

        Raises:
            ValueError: サポートされていないツールタイプが指定された場合。
        """
        if tool_type not in self._templates:
            raise ValueError(f'Unsupported tool type: {tool_type}')

        template = self._templates[tool_type]
        return template.generate_prompt(**kwargs)
