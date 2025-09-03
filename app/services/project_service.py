"""プロジェクトのビジネスロジックを管理するサービス。"""

import asyncio
import logging
from collections.abc import Callable
from pathlib import Path

from app.config import config
from app.errors import (
    LLMError,
    ResourceNotFoundError,
)
from app.models.project import Project
from app.repositories.project_repository import JsonProjectRepository
from app.types import LLMProviderName, ProjectID, ToolType
from app.utils.llm_client import LLMClient
from app.utils.prompt_manager import PromptManager

logger = logging.getLogger('aiman')


class ProjectService:
    """プロジェクトのビジネスロジックを管理するサービス。"""

    def __init__(self, repository: JsonProjectRepository):
        """サービスを初期化します。

        Args:
            repository: プロジェクトリポジトリ。
        """
        self.repository = repository
        self.prompt_manager = PromptManager()

    def create_project(self, name: str, source: str, tool: ToolType) -> Project | None:
        """プロジェクトを作成する。

        Args:
            name: プロジェクト名。
            source: ソースディレクトリパス。
            tool: 内蔵ツールタイプ。

        Returns:
            作成したプロジェクト、失敗した場合はNone。
        """
        if not self._is_valid_input(name, source, tool):
            return None

        try:
            project = Project(name=name, source=source, tool=tool)
            self.repository.save(project)
            result = project
        except Exception as e:
            logger.error(f'[ERROR] プロジェクト作成エラー: {e}')
            result = None

        return result

    def execute_project(self, project_id: ProjectID) -> tuple[Project | None, str]:
        """プロジェクトを実行する。

        Args:
            project_id: プロジェクトID。

        Returns:
            (更新されたプロジェクト, メッセージ)
        """
        logger.debug(f'[DEBUG] execute_project開始: project_id={project_id}')
        project: Project | None = None

        try:
            # プロジェクト取得
            project = self.repository.find_by_id(project_id)

            # 内蔵ツールで実行
            self._execute_internal_tool(project)

            self._complete_project(project)
            return project, 'プロジェクトの実行が完了しました'
        except Exception as e:
            return self._handle_execution_error(project, e)

    def _complete_project(self, project: Project) -> None:
        """プロジェクトを完了状態にします。

        Args:
            project: プロジェクト。
        """
        project.complete({'message': 'プロジェクトの実行が完了しました。'})
        self.repository.save(project)

    def _execute_internal_tool(self, project: Project) -> None:
        """内蔵ツールで処理を実行する。"""
        project.start_processing()

        try:
            # プロンプト生成
            prompt = self._generate_prompt_for_tool(project)

            # LLM呼び出し
            response = self._call_llm(prompt)

            # 結果をファイルに保存
            self._save_tool_result(project, response)

            # 結果をプロジェクトに保存
            project.complete({'response': response})

        except LLMError as e:
            self._handle_llm_error(project, e)
            raise
        except Exception as e:
            logger.error(f'[ERROR] 内蔵ツール実行エラー: {e}')
            project.fail({'error': str(e)})
            raise

    def _handle_llm_error(self, project: Project, error: LLMError) -> None:
        """LLMエラーを処理する。

        Args:
            project: プロジェクト。
            error: LLMエラー。
        """
        # エラーメッセージから重複を除去
        clean_message = error.message.replace(
            'LLM呼び出しエラー: LLM呼び出しエラー:', 'LLM呼び出しエラー:'
        )

        error_msg = f'[ERROR] {clean_message} (プロバイダ: {error.provider}, モデル: {error.model})'
        logger.error(error_msg)

        if error.original_error:
            logger.error(f'[ERROR] 元のエラー: {error.original_error}')

        project.fail({'error': clean_message, 'provider': error.provider, 'model': error.model})

    def _call_llm(self, prompt: str) -> str:
        """LLMを呼び出してテキスト生成を実行する。

        Args:
            prompt: プロンプト。

        Returns:
            LLMからの応答。

        Raises:
            LLMError: LLM呼び出し時にエラーが発生した場合。
        """
        try:
            # テストでのモックを反映させるため、呼び出し毎にLLMClientを生成
            llm_client = LLMClient(LLMProviderName(config.llm_provider))
            return self._execute_async_llm_call(llm_client, prompt)

        except Exception as err:
            # LLMError以外のエラーをLLMErrorに変換（ただし、ファイルI/Oエラーは除く）
            if not isinstance(err, LLMError):
                # ファイルI/Oエラーの場合は元のエラーをそのまま再送出
                if isinstance(err, OSError | IOError):
                    raise
                # その他のエラーはLLMErrorに変換
                # 現在の設定からプロバイダ名を取得して付与
                current_provider = LLMProviderName(config.llm_provider)
                raise LLMError(
                    f'LLM呼び出しエラー: {err!s}', current_provider, 'unknown', err
                ) from err
            # LLMErrorの場合はそのまま再送出
            raise

    def _execute_async_llm_call(self, llm_client: LLMClient, prompt: str) -> str:
        """非同期LLM呼び出しを実行する。

        Args:
            llm_client: LLMクライアント。
            prompt: プロンプト。

        Returns:
            LLMからの応答。
        """
        # テスト環境では常にasyncio.runを使用し、本番環境では既存のループを使用
        try:
            # 既存のループが実行中かチェック
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # 既存のループが実行中の場合は、新しいループを作成
                response = asyncio.run(llm_client.generate_text(prompt))
            else:
                response = loop.run_until_complete(llm_client.generate_text(prompt))
            return response
        except RuntimeError:
            # ループが存在しない場合は新しく作成
            return asyncio.run(llm_client.generate_text(prompt))

    def _handle_execution_error(
        self, project: Project | None, error: Exception
    ) -> tuple[None, str]:
        """実行エラーを処理する。

        Args:
            project: プロジェクト(存在する場合)。
            error: 発生したエラー。

        Returns:
            (None, エラーメッセージ)
        """
        message = self._get_error_message(error)
        logger.error(f'[ERROR] {message}')

        if project and not isinstance(error, ValueError | ResourceNotFoundError):
            project.fail({'error': str(error)})
            self.repository.save(project)

        return None, message

    def _get_error_message(self, error: Exception) -> str:
        """エラーメッセージを取得する。

        Args:
            error: 発生したエラー。

        Returns:
            エラーメッセージ。
        """
        error_handlers: dict[type[Exception], Callable[[Exception], str]] = {
            # ValueError は元のエラーメッセージをそのまま返す（例: ファイル未検出など）
            ValueError: lambda e: str(e),
            ResourceNotFoundError: lambda e: str(e),
            LLMError: lambda e: getattr(e, 'message', str(e)),
        }

        for error_type, handler in error_handlers.items():
            if isinstance(error, error_type):
                return handler(error)

        return '予期しないエラーが発生しました'

    def _generate_prompt_for_tool(self, project: Project) -> str:
        """ツールタイプに応じたプロンプトを生成する。

        Args:
            project: プロジェクト。

        Returns:
            生成されたプロンプト。
        """
        if project.tool == ToolType.OVERVIEW:
            return self._generate_overview_prompt(project)
        if project.tool == ToolType.REVIEW:
            return self._generate_review_prompt(project)
        raise ValueError(f'Unsupported tool type: {project.tool}')

    def _generate_overview_prompt(self, project: Project) -> str:
        """OVERVIEWツール用プロンプトを生成する。

        Args:
            project: プロジェクト。

        Returns:
            生成されたプロンプト。
        """
        source_path = Path(project.source)
        file_list, file_contents = self._scan_directory_for_files(source_path)

        return self.prompt_manager.generate_prompt(
            'overview',
            directory_path=str(source_path),
            file_list=file_list,
            file_contents=file_contents,
        )

    def _scan_directory_for_files(self, source_path: Path) -> tuple[list[str], dict[str, str]]:
        """ディレクトリ内のファイルをスキャンする。

        Args:
            source_path: ソースディレクトリパス。

        Returns:
            (ファイルリスト, ファイル内容辞書)のタプル。
        """
        return self._scan_files_with_pattern(source_path, '*', include_content=True)

    def _scan_files_with_pattern(
        self, source_path: Path, pattern: str, include_content: bool = False
    ) -> tuple[list[str], dict[str, str]]:
        """パターンに一致するファイルをスキャンする。

        Args:
            source_path: ソースディレクトリパス。
            pattern: ファイルパターン(例: '*.py', '*')。
            include_content: ファイル内容を含めるかどうか。

        Returns:
            (ファイルリスト, ファイル内容辞書)のタプル。
        """
        if not self._is_valid_source_path(source_path):
            return [], {}

        file_list: list[str] = []
        file_contents: dict[str, str] = {}

        for file_path in source_path.rglob(pattern):
            if file_path.is_file():
                self._process_file(
                    file_path, source_path, (file_list, file_contents), include_content
                )

        return file_list, file_contents

    def _process_file(
        self,
        file_path: Path,
        source_path: Path,
        file_data: tuple[list[str], dict[str, str]],
        include_content: bool,
    ) -> None:
        """個別のファイルを処理する。

        Args:
            file_path: ファイルパス。
            source_path: ソースディレクトリパス。
            file_data: (ファイルリスト, ファイル内容辞書)のタプル。
            include_content: ファイル内容を含めるかどうか。
        """
        file_list, file_contents = file_data
        relative_path = str(file_path.relative_to(source_path))
        file_list.append(relative_path)

        if include_content:
            self._read_file_content_if_text(file_path, relative_path, file_contents)

    def _is_valid_source_path(self, source_path: Path) -> bool:
        """ソースパスが有効かチェックする。

        Args:
            source_path: ソースディレクトリパス。

        Returns:
            有効な場合はTrue。
        """
        return source_path.exists() and source_path.is_dir()

    def _read_file_content_if_text(
        self, file_path: Path, relative_path: str, file_contents: dict[str, str]
    ) -> None:
        """テキストファイルの内容を読み込む。

        Args:
            file_path: ファイルパス。
            relative_path: 相対パス。
            file_contents: ファイル内容辞書。
        """
        if file_path.suffix in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                    file_contents[relative_path] = content
            except Exception as e:
                logger.warning(f'[WARNING] ファイル読み込みエラー {file_path}: {e}')

    def _generate_review_prompt(self, project: Project) -> str:
        """REVIEWツール用プロンプトを生成する。

        Args:
            project: プロジェクト。

        Returns:
            生成されたプロンプト。
        """
        source_path = Path(project.source)
        target_file, file_content = self._find_first_review_target_file(source_path)

        if not target_file:
            raise ValueError('レビュー対象のファイルが見つかりません')

        return self.prompt_manager.generate_prompt(
            'review', file_path=str(target_file), file_content=file_content
        )

    def _find_first_review_target_file(self, source_path: Path) -> tuple[Path | None, str]:
        """REVIEW用に最初の対象ファイルを見つける (.md, .txt を優先、次に .py)。

        Args:
            source_path: ソースディレクトリパス。

        Returns:
            (ファイルパス, ファイル内容)のタプル。
        """
        # 優先順で探索: .md -> .txt -> .py
        for pattern in ('*.md', '*.txt', '*.py'):
            file_list, file_contents = self._scan_files_with_pattern(
                source_path, pattern, include_content=True
            )
            if file_list:
                first_file = file_list[0]
                file_content = file_contents.get(first_file, '')
                target_file = source_path / first_file
                return target_file, file_content

        return None, ''

    def _save_tool_result(self, project: Project, response: str) -> None:
        """ツール実行結果をファイルに保存する。

        Args:
            project: プロジェクト。
            response: LLMからの応答。
        """
        # 出力先は対象ディレクトリ配下の固定ファイル名
        output_filename = 'overview.txt' if project.tool == ToolType.OVERVIEW else 'review.txt'
        output_path = Path(project.source) / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = f'# {project.tool} result\n\n{response}\n'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _is_valid_input(self, name: str, source: str, tool: ToolType) -> bool:
        """入力値の妥当性チェック。"""
        return bool(name and name.strip()) and bool(source and source.strip()) and tool is not None
