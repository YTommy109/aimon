"""Excelファイルを解析し、テキストと画像を抽出するユーティリティ。"""

import base64
import io
import json
import logging
from pathlib import Path
from typing import Any

import openpyxl
from PIL import Image

from app.errors import FileProcessingError, FileReadingError


class ExcelParser:
    """Excelファイルからテキストと画像を抽出するパーサークラス。"""

    def __init__(self) -> None:
        self.logger = logging.getLogger('aiman')
        self._text_content: str = ''
        self._images: list[Image.Image] = []
        self._parsed_data: dict[str, Any] = {}

    def parse(self, file_path: Path) -> None:
        """
        Excelファイルを解析してテキストと画像を抽出します。

        Args:
            file_path: 処理対象のExcelファイルのパス。

        Raises:
            FileProcessingError: ファイルの処理に失敗した場合。
            FileReadingError: ファイルの読み込みに失敗した場合。
        """
        try:
            workbook = openpyxl.load_workbook(file_path)
        except Exception as e:
            raise FileReadingError(f'Excelファイルの読み込みに失敗しました: {e}') from e

        full_text: list[str] = []
        images: list[Image.Image] = []
        image_count = 1
        sheets_data: dict[str, Any] = {}

        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            full_text.append(f'---シート: {sheet_name}---\n')

            # 画像の位置を特定し、マーカーを挿入するための辞書
            image_markers: dict[tuple[int, int], str] = {}
            sheet_images: list[dict[str, Any]] = []

            if sheet._images:  # type: ignore
                for img in sheet._images:  # type: ignore
                    # openpyxlの画像オブジェクトからPillowの画像オブジェクトに変換
                    try:
                        img_bytes = io.BytesIO(img._data())  # type: ignore
                        img_pil = Image.open(img_bytes)
                        images.append(img_pil)

                        # 画像のアンカーから位置を取得
                        row = img.anchor._from.row + 1  # type: ignore
                        col = img.anchor._from.col + 1  # type: ignore
                        marker = f'[図:{image_count}]'
                        image_markers[(row, col)] = marker

                        # 画像情報を保存
                        sheet_images.append(
                            {'figure_number': image_count, 'row': row, 'col': col, 'marker': marker}
                        )
                        image_count += 1
                    except Exception as e:
                        self.logger.warning(f'{file_path}の画像処理に失敗しました: {e}')

            # セルの内容を読み込み、画像マーカーを挿入
            cell_values: dict[tuple[int, int], str] = {}
            for row_data in sheet.iter_rows():
                for cell in row_data:
                    if cell.value is not None:
                        cell_values[(cell.row, cell.column)] = str(cell.value)

            # マーカーの位置にマーカーを追加
            for (row, col), marker in image_markers.items():
                if (row, col) in cell_values:
                    cell_values[(row, col)] = marker + ' ' + cell_values[(row, col)]
                else:
                    cell_values[(row, col)] = marker

            # シートのテキストを再構築
            sheet_text_lines: list[str] = []
            if cell_values:
                max_row = max(key[0] for key in cell_values.keys())
                max_col = max(key[1] for key in cell_values.keys())
                for r in range(1, max_row + 1):
                    row_text = []
                    for c in range(1, max_col + 1):
                        row_text.append(cell_values.get((r, c), ''))
                    sheet_text_lines.append('\t'.join(row_text))

            full_text.extend(sheet_text_lines)

            # シートデータを保存（cell_valuesのキーを文字列に変換）
            serializable_cell_values = {
                f'{row},{col}': value for (row, col), value in cell_values.items()
            }
            sheets_data[sheet_name] = {
                'text_lines': sheet_text_lines,
                'images': sheet_images,
                'cell_values': serializable_cell_values,
            }

        self._text_content = '\n'.join(full_text)
        self._images = images
        self._parsed_data = {
            'file_path': str(file_path),
            'total_images': len(images),
            'sheets': sheets_data,
        }

    def get_text(self) -> str:
        """
        解析されたテキスト内容を取得します。

        Returns:
            抽出されたテキスト内容。
        """
        return self._text_content

    def get_images(self) -> list[Image.Image]:
        """
        解析された画像リストを取得します。

        Returns:
            抽出された画像のリスト。
        """
        return self._images.copy()

    def to_json(self) -> dict[str, Any]:
        """
        解析結果をJSON形式で取得します。

        Returns:
            解析結果の辞書。画像はbase64エンコードされます。
        """
        result = self._parsed_data.copy()

        # 画像をbase64エンコードして追加
        encoded_images = []
        for idx, img in enumerate(self._images):
            buffered = io.BytesIO()
            img.save(buffered, format='PNG')
            img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            encoded_images.append({'figure_number': idx + 1, 'format': 'PNG', 'data': img_b64})

        result['images'] = encoded_images
        result['text_content'] = self._text_content

        return result

    def export_json(self, output_path: Path) -> None:
        """
        解析結果をJSONファイルとして出力します。

        Args:
            output_path: 出力するJSONファイルのパス。

        Raises:
            FileProcessingError: ファイルの書き込みに失敗した場合。
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise FileProcessingError(f'JSONファイルの書き込みに失敗しました: {e}') from e
