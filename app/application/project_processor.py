"""プロジェクト処理のオーケストレータークラス。"""

import io
import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

from app.domain.ai_tool_executor import AIToolExecutor
from app.domain.entities import AITool, Project
from app.domain.repositories import AIToolRepository, ProjectRepository
from app.errors import (
    APIConfigurationError,
    FileProcessingError,
    FileWritingError,
    ProjectProcessingError,
)
from app.infrastructure.ai_executors import AIExecutorFactory
from app.infrastructure.file_processor import FileProcessor


class ProjectProcessor:
    """プロジェクト処理のオーケストレータークラス。"""

    def __init__(
        self,
        project_repository: ProjectRepository,
        file_processor: FileProcessor,
        ai_tool_repository: AIToolRepository,
    ) -> None:
        """プロジェクトプロセッサーを初期化します。

        Args:
            project_repository: プロジェクトリポジトリ。
            file_processor: ファイルプロセッサー。
        """
        self.project_repository = project_repository
        self.file_processor = file_processor
        self.ai_tool_repository = ai_tool_repository
        self.logger = logging.getLogger('aiman')

    def process_project(self, project_id: UUID) -> None:
        """プロジェクトを処理します。

        Args:
            project_id: 処理対象のプロジェクトID。

        Raises:
            ProjectProcessingError: プロジェクトの処理中にエラーが発生した場合。
        """
        try:
            with self._handle_project_processing(project_id) as project:
                self._execute_ai_tool_processing(project)
        except Exception as e:
            self.logger.error(f'Worker error: {e}')
            raise

    @contextmanager
    def _handle_project_processing(self, project_id: UUID) -> Generator[Project, None, None]:
        """プロジェクト処理のコンテキストマネージャー。

        Args:
            project_id: 処理対象のプロジェクトID。

        Yields:
            処理対象のProjectオブジェクト。

        Raises:
            ProjectProcessingError: プロジェクトが見つからない場合。
        """
        project = None
        try:
            project = self.project_repository.find_by_id(project_id)
            if not project:
                raise ProjectProcessingError(project_id)

            project.start_processing()
            self.project_repository.save(project)
            self.logger.info(f'Started processing project: {project.name}')
            yield project

        except Exception as e:
            self._handle_project_error(project, e)
            raise

    def _handle_project_error(self, project: Project | None, e: Exception) -> None:
        """プロジェクト処理エラーをハンドリングします。

        Args:
            project: エラーが発生したプロジェクト。
            e: 発生した例外。
        """
        self.logger.error(f'Error processing project: {e}')
        if project:
            error_message = str(e)
            if isinstance(e, FileProcessingError):
                error_message = f'ファイル処理エラー: {e}'
            elif isinstance(e, APIConfigurationError):
                error_message = f'API設定エラー: {e}'
            project.fail({'error': error_message})
            self.project_repository.save(project)

    def _get_ai_tool_entity(self, ai_tool_id: str) -> AITool:
        ai_tool_entity = self.ai_tool_repository.find_by_id(ai_tool_id)
        logger = logging.getLogger('aiman')
        logger.info(
            f'[ProjectProcessor] ai_tool_entity type: {type(ai_tool_entity)}, '
            f'value: {ai_tool_entity!r}'
        )
        if ai_tool_entity is None:
            raise RuntimeError(f'AIツールが見つかりません: {ai_tool_id}')
        return ai_tool_entity

    def _create_ai_executor(self, ai_tool: AITool) -> AIToolExecutor:
        logger = logging.getLogger('aiman')
        logger.info(
            f'[ProjectProcessor] create_executor: ai_tool.id={ai_tool.id}, '
            f'endpoint_url={ai_tool.endpoint_url}'
        )
        return AIExecutorFactory.create_executor(ai_tool)

    def _process_files_with_executor(
        self, files_to_process: list[Path], f_out: io.TextIOWrapper, ai_executor: AIToolExecutor
    ) -> list[str]:
        processed_files = []
        for file_path in files_to_process:
            if self._process_single_file_with_ai_tool(file_path, f_out, ai_executor):
                processed_files.append(file_path.name)
        return processed_files

    def _execute_ai_tool_processing(self, project: Project) -> None:
        source_path = Path(project.source)
        output_file = self.file_processor.prepare_output_file(source_path, project.name)

        ai_tool_entity = self._get_ai_tool_entity(project.ai_tool)
        ai_executor = self._create_ai_executor(ai_tool_entity)

        try:
            with open(output_file, 'w', encoding='utf-8') as f_out:
                f_out.write(f'# {project.ai_tool} 処理結果: {project.name}\n\n')
                files_to_process = self.file_processor.collect_files_to_process(source_path)
                processed_files = self._process_files_with_executor(
                    files_to_process, f_out, ai_executor
                )
        except Exception as e:
            raise FileWritingError(str(output_file)) from e

        result = {
            'processed_files': processed_files,
            'message': f'Processing successful. Results saved to {output_file.name}',
        }
        self.project_repository.update_result(project.id, result)

    # 古い_execute_gemini_summarizeメソッドを削除しました。
    # 新しいシステムでは_execute_ai_tool_processingを使用してください。

    def _process_single_file_with_ai_tool(
        self, file_path: Path, f_out: io.TextIOWrapper, ai_executor: AIToolExecutor
    ) -> bool:
        """選択されたAIツールで単一のファイルを処理します。

        Args:
            file_path: 処理対象のファイルパス。
            f_out: 出力ファイルのハンドル。
            ai_executor: AIツールエグゼキューター。

        Returns:
            処理が成功したかどうか。
        """
        self.logger.info(f'Processing file: {file_path.name}')
        try:
            return self._try_process_file_with_ai_tool(file_path, f_out, ai_executor)
        except (FileProcessingError, APIConfigurationError) as e:
            return self._handle_processing_error(file_path, f_out, e)

    def _try_process_file_with_ai_tool(
        self, file_path: Path, f_out: io.TextIOWrapper, ai_executor: AIToolExecutor
    ) -> bool:
        """選択されたAIツールでファイル処理を試行します。

        Args:
            file_path: 処理対象のファイルパス。
            f_out: 出力ファイルのハンドル。
            ai_executor: AIツールエグゼキューター。

        Returns:
            処理が成功したかどうか。
        """
        content, images = self.file_processor.read_file_content(file_path)

        if not content.strip():
            self.logger.warning(f'File {file_path.name} is empty. Skipping.')
            return False

        return self._process_file_content_with_ai_tool(
            file_path, content, images, f_out, ai_executor
        )

    def _process_file_content_with_ai_tool(  # noqa: PLR0913
        self,
        file_path: Path,
        content: str,
        images: list[Any],
        f_out: io.TextIOWrapper,
        ai_executor: AIToolExecutor,
    ) -> bool:
        """選択されたAIツールでファイルコンテンツを処理します。

        Args:
            file_path: 処理対象のファイルパス。
            content: ファイルの内容。
            images: 画像のリスト。
            f_out: 出力ファイルのハンドル。
            ai_executor: AIツールエグゼキューター。

        Returns:
            処理が成功したかどうか。
        """
        prompt: list[str | Any] = [
            f'以下の文章と図の内容を日本語で3行で要約し、各図の内容も簡単に解説してください。\\n\\n---\\n{content}',
        ]
        # 画像があればプロンプトに追加
        if images:
            prompt.extend(images)

        self.file_processor.create_prompt_json(prompt, file_path)

        # 選択されたAIツールで処理を実行
        summary = ai_executor.execute(content, images)

        f_out.write(f'## ファイル: {file_path.name}\\n\\n')
        f_out.write('### 要約結果\\n\\n')
        f_out.write(summary)
        f_out.write('\\n\\n---\\n\\n')

        return True

    # 古いメソッドを削除しました。
    # 新しいシステムでは_process_single_file_with_ai_toolを使用してください。

    def _handle_file_processing_error(
        self,
        file_path: Path,
        f_out: io.TextIOWrapper,
        e: FileProcessingError,
    ) -> bool:
        """ファイル処理エラーをハンドリングします。

        Args:
            file_path: エラーが発生したファイルパス。
            f_out: 出力ファイルのハンドル。
            e: 発生した例外。

        Returns:
            常にFalse。
        """
        self.logger.error(f'Failed to process {file_path.name}: {e}')
        f_out.write(f'## ファイル: {file_path.name}\\n\\n')
        f_out.write(f'**エラー:** ファイル処理中にエラーが発生しました: {e}\\n\\n')
        f_out.write('---\\n\\n')
        return False

    def _handle_api_error(
        self,
        file_path: Path,
        f_out: io.TextIOWrapper,
        e: APIConfigurationError,
    ) -> bool:
        """API設定エラーをハンドリングします。

        Args:
            file_path: エラーが発生したファイルパス。
            f_out: 出力ファイルのハンドル。
            e: 発生した例外。

        Returns:
            常にFalse。
        """
        self.logger.error(f'API error while processing {file_path.name}: {e}')
        f_out.write(f'## ファイル: {file_path.name}\\n\\n')
        f_out.write(f'**エラー:** API呼び出し中にエラーが発生しました: {e}\\n\\n')
        f_out.write('---\\n\\n')
        return False

    def _handle_processing_error(
        self,
        file_path: Path,
        f_out: io.TextIOWrapper,
        e: FileProcessingError | APIConfigurationError,
    ) -> bool:
        """処理エラーを統合してハンドリングします。

        Args:
            file_path: エラーが発生したファイルパス。
            f_out: 出力ファイルのハンドル。
            e: 発生した例外。

        Returns:
            常にFalse。
        """
        if isinstance(e, FileProcessingError):
            return self._handle_file_processing_error(file_path, f_out, e)
        return self._handle_api_error(file_path, f_out, e)
