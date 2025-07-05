"""ファイル処理専門クラス。"""

import base64
import io
import json
from pathlib import Path
from typing import Any

from PIL import Image

from app.errors import FileReadingError, FileWritingError
from app.utils import ExcelParser


class FileProcessor:
    """ファイル処理専門クラス。"""

    def collect_files_to_process(self, source_path: Path) -> list[Path]:
        """処理対象のファイルを収集します。

        Args:
            source_path: プロジェクトのソースパス。

        Returns:
            処理対象のファイルリスト。
        """
        files_to_process: list[Path] = []
        for ext in ['*.txt', '*.xlsx']:
            files_to_process.extend(source_path.glob(ext))
        return files_to_process

    def read_file_content(self, file_path: Path) -> tuple[str, list[Image.Image]]:
        """ファイルからコンテンツを読み取ります。

        Args:
            file_path: 読み取り対象のファイルパス。

        Returns:
            読み取ったテキストと画像のタプル。

        Raises:
            FileReadingError: ファイル読み取りに失敗した場合。
        """
        content: str = ''
        images: list[Image.Image] = []

        if file_path.suffix == '.txt':
            try:
                with open(file_path, encoding='utf-8') as f_in:
                    content = f_in.read()
            except Exception as e:
                raise FileReadingError(str(file_path)) from e
        elif file_path.suffix == '.xlsx':
            content, images = self._process_xlsx(file_path)

        return content, images

    def create_prompt_json(self, prompt: list[str | Image.Image], file_path: Path) -> None:
        """プロンプトをJSONファイルとして保存します。

        Args:
            prompt: プロンプトのリスト。
            file_path: 元ファイルのパス。

        Raises:
            FileWritingError: ファイル書き込みに失敗した場合。
        """
        prompt_json_path = file_path.parent / 'prompt.json'
        prompt_for_json: list[dict[str, Any]] = []

        self._add_text_to_prompt_json(prompt, prompt_for_json)
        self._add_images_to_prompt_json(prompt, prompt_for_json)

        try:
            with open(prompt_json_path, 'w', encoding='utf-8') as f_prompt:
                json.dump(prompt_for_json, f_prompt, ensure_ascii=False, indent=2)
        except Exception as e:
            raise FileWritingError(str(prompt_json_path)) from e

    def prepare_output_file(self, source_path: Path, _project_name: str) -> Path:
        """出力ファイルを準備します。

        Args:
            source_path: プロジェクトのソースパス。
            _project_name: プロジェクト名。

        Returns:
            準備された出力ファイルのパス。

        Raises:
            FileWritingError: 既存ファイルの削除に失敗した場合。
        """
        output_file = source_path / 'gemini_results.md'

        if output_file.exists():
            try:
                output_file.unlink()
            except Exception as e:
                raise FileWritingError(str(output_file)) from e

        return output_file

    def _process_xlsx(self, file_path: Path) -> tuple[str, list[Image.Image]]:
        """Excelファイルからテキストと画像を抽出します。

        Args:
            file_path: 処理対象のExcelファイルのパス。

        Returns:
            抽出されたテキストと画像のリストのタプル。

        Raises:
            FileProcessingError: ファイルの処理に失敗した場合。
        """
        parser = ExcelParser()
        parser.parse(file_path)
        return parser.get_text(), parser.get_images()

    def _add_text_to_prompt_json(
        self,
        prompt: list[str | Image.Image],
        prompt_for_json: list[dict[str, Any]],
    ) -> None:
        """テキスト部分をプロンプトJSONに追加します。"""
        for item in prompt:
            if isinstance(item, str):
                prompt_for_json.append({'type': 'text', 'data': item})

    def _add_images_to_prompt_json(
        self,
        prompt: list[str | Image.Image],
        prompt_for_json: list[dict[str, Any]],
    ) -> None:
        """画像部分をプロンプトJSONに追加します。"""
        for idx, item in enumerate(prompt):
            if isinstance(item, Image.Image):
                buffered = io.BytesIO()
                item.save(buffered, format='PNG')
                img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                prompt_for_json.append(
                    {
                        'type': 'image',
                        'figure': str(idx),
                        'data': img_b64,
                    },
                )
