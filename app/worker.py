import logging
import time
from contextlib import contextmanager
from multiprocessing import Process
from pathlib import Path
from typing import Generator
from uuid import UUID

import google.generativeai as genai

from .config import Config
from .data_manager import DataManager, Project, ProjectNotFoundError


class WorkerError(Exception):
    """Worker関連のベース例外クラス。"""

    pass


class Worker(Process):
    """
    プロジェクトをバックグラウンドで処理するワーカープロセス。
    """

    def __init__(self, project_id: UUID, data_manager: DataManager) -> None:
        """
        Workerを初期化します。

        Args:
            project_id: 処理対象のプロジェクトID。
            data_manager: プロジェクトデータを管理するDataManagerインスタンス。
        """
        super().__init__()
        self.project_id = project_id
        self.data_manager = data_manager
        self.logger = logging.getLogger('aiman')

    @contextmanager
    def _handle_project_processing(self) -> Generator[Project, None, None]:
        """プロジェクト処理のコンテキストマネージャー。

        プロジェクトの取得、ステータス更新、エラーハンドリングを一元管理します。

        Yields:
            処理対象のProjectオブジェクト。

        Raises:
            WorkerError: プロジェクトが見つからない場合。
        """
        try:
            project = self.data_manager.get_project(self.project_id)
            if not project:
                raise WorkerError(f'Project with id {self.project_id} not found.')

            self.data_manager.update_project_status(self.project_id, 'Processing')
            self.logger.info(f'Started processing project: {project.name}')
            yield project

            self.data_manager.update_project_status(self.project_id, 'Completed')
            self.logger.info(f'Successfully completed project: {project.name}')

        except Exception as e:
            self.logger.error(f'Error processing project {self.project_id}: {e}')
            self.data_manager.update_project_status(self.project_id, 'Failed')
            raise

    def run(self) -> None:
        """ワーカースレッドのメイン処理。プロジェクトの実行から完了までを担当します。"""
        self.logger.info(f'Worker started for project_id: {self.project_id}')

        try:
            with self._handle_project_processing() as project:
                api_key = Config.get_gemini_api_key()
                if not api_key:
                    raise WorkerError('GEMINI_API_KEY environment variable not set.')

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)

                self._execute_gemini_summarize(project, model)

        except (WorkerError, ProjectNotFoundError) as e:
            self.logger.error(f'Worker error: {e}')
        except Exception as e:
            self.logger.error(f'Unexpected error in worker: {e}')

    def _execute_gemini_summarize(
        self, project: Project, model: genai.GenerativeModel
    ) -> None:
        """指定されたディレクトリ内のテキストファイルを要約し、結果をファイルに書き出します。

        Args:
            project: 処理対象のプロジェクトオブジェクト。
            model: 要約に使用するGeminiモデルのインスタンス。
        """
        source_path = Path(project.source)
        output_file = source_path / 'gemini_results.md'
        processed_files = []

        if output_file.exists():
            output_file.unlink()

        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(f'# Gemini処理結果: {project.name}\n\n')

            for file_path in source_path.glob('*.txt'):
                self.logger.info(f'Processing file: {file_path.name}')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f_in:
                        content = f_in.read()

                    prompt = (
                        f'以下の文章を日本語で3行で要約してください。\n\n---\n{content}'
                    )
                    response = model.generate_content(prompt)

                    f_out.write(f'## ファイル: {file_path.name}\n\n')
                    f_out.write('### 要約結果\n\n')
                    f_out.write(response.text)
                    f_out.write('\n\n---\n\n')
                    processed_files.append(file_path.name)
                    time.sleep(Config.API_RATE_LIMIT_DELAY)  # APIのレート制限を考慮

                except Exception as e:
                    self.logger.error(f'Failed to process {file_path.name}: {e}')
                    f_out.write(f'## ファイル: {file_path.name}\n\n')
                    f_out.write(f'**エラー:** 処理中にエラーが発生しました: {e}\n\n')
                    f_out.write('---\n\n')

        result = {
            'processed_files': processed_files,
            'message': f'Processing successful. Results saved to {output_file.name}',
        }

        self.data_manager.update_project_result(self.project_id, result)
