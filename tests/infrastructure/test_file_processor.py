"""FileProcessorクラスのテスト。"""

import builtins
from pathlib import Path

import pytest
from PIL import Image
from pytest_mock import MockerFixture

import app.infrastructure.file_processor as file_processor_module
from app.errors import FileReadingError, FileWritingError
from app.infrastructure.file_processor import FileProcessor


class TestFileProcessor:
    """FileProcessorクラスのテスト。"""

    @pytest.fixture
    def file_processor(self) -> FileProcessor:
        """FileProcessorのインスタンス。"""
        return FileProcessor()

    def test_FileProcessorが正しく初期化される(self) -> None:
        """FileProcessorが正しく初期化される。"""
        # Act
        processor = FileProcessor()

        # Assert
        assert isinstance(processor, FileProcessor)

    def test_処理対象のファイルが正しく収集される(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """処理対象のファイルが正しく収集される。"""
        # Arrange
        # テスト用ファイルを作成
        txt_file = tmp_path / 'test.txt'
        xlsx_file = tmp_path / 'test.xlsx'
        other_file = tmp_path / 'test.pdf'
        txt_file.touch()
        xlsx_file.touch()
        other_file.touch()

        # Act
        files = file_processor.collect_files_to_process(tmp_path)

        # Assert
        assert len(files) == 2
        assert txt_file in files
        assert xlsx_file in files
        assert other_file not in files

    def test_空のディレクトリで処理対象ファイルが空リストになる(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """空のディレクトリで処理対象ファイルが空リストになる。"""
        # Act
        files = file_processor.collect_files_to_process(tmp_path)

        # Assert
        assert files == []

    def test_txtファイルが正常に読み取られる(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """txtファイルが正常に読み取られる。"""
        # Arrange
        txt_file = tmp_path / 'test.txt'
        test_content = 'これはテストコンテンツです。'
        txt_file.write_text(test_content, encoding='utf-8')

        # Act
        content, images = file_processor.read_file_content(txt_file)

        # Assert
        assert content == test_content
        assert images == []

    def test_txtファイル読み取りエラー時にFileReadingErrorが発生する(
        self, file_processor: FileProcessor
    ) -> None:
        """txtファイル読み取りエラー時にFileReadingErrorが発生する。"""
        # Arrange
        non_existent_file = Path('/non/existent/file.txt')

        # Act & Assert
        with pytest.raises(FileReadingError):
            file_processor.read_file_content(non_existent_file)

    def test_xlsxファイルが正常に処理される(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """xlsxファイルが正常に処理される。"""
        # Arrange
        xlsx_file = tmp_path / 'test.xlsx'
        xlsx_file.touch()

        mock_excel_parser_class = mocker.patch.object(file_processor_module, 'ExcelParser')
        mock_parser = mocker.MagicMock()
        mock_parser.get_text.return_value = 'Excel内容'
        mock_parser.get_images.return_value = [mocker.MagicMock(spec=Image.Image)]
        mock_excel_parser_class.return_value = mock_parser

        # Act
        content, images = file_processor.read_file_content(xlsx_file)

        # Assert
        assert content == 'Excel内容'
        assert len(images) == 1
        mock_excel_parser_class.assert_called_once()
        mock_parser.parse.assert_called_once_with(xlsx_file)

    def test_サポートされていないファイル形式の場合に空の結果が返される(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """サポートされていないファイル形式の場合に空の結果が返される。"""
        # Arrange
        pdf_file = tmp_path / 'test.pdf'
        pdf_file.touch()

        # Act
        content, images = file_processor.read_file_content(pdf_file)

        # Assert
        assert content == ''
        assert images == []

    def test_プロンプトJSONが正常に作成される(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """プロンプトJSONが正常に作成される。"""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.touch()
        prompt: list[str | Image.Image] = ['テストプロンプト']

        # Act
        mock_file = mocker.patch.object(builtins, 'open', mocker.mock_open())
        file_processor.create_prompt_json(prompt, test_file)

        # Assert
        mock_file.assert_called_once_with(tmp_path / 'prompt.json', 'w', encoding='utf-8')

    def test_画像を含むプロンプトJSONが正常に作成される(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """画像を含むプロンプトJSONが正常に作成される。"""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.touch()
        mock_image = mocker.MagicMock(spec=Image.Image)
        prompt: list[str | Image.Image] = ['テストプロンプト', mock_image]

        # Act
        mock_file = mocker.patch.object(builtins, 'open', mocker.mock_open())
        file_processor.create_prompt_json(prompt, test_file)

        # Assert
        mock_file.assert_called_once()
        # 画像の保存が呼ばれることを確認
        mock_image.save.assert_called_once()

    def test_プロンプトJSON書き込みエラー時にFileWritingErrorが発生する(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """プロンプトJSON書き込みエラー時にFileWritingErrorが発生する。"""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.touch()
        prompt: list[str | Image.Image] = ['テストプロンプト']

        # Act & Assert
        mocker.patch.object(builtins, 'open', side_effect=OSError('書き込み失敗'))
        with pytest.raises(FileWritingError):
            file_processor.create_prompt_json(prompt, test_file)

    def test_出力ファイルが正常に準備される(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """出力ファイルが正常に準備される。"""
        # Arrange
        project_name = 'テストプロジェクト'

        # Act
        output_file = file_processor.prepare_output_file(tmp_path, project_name)

        # Assert
        assert output_file == tmp_path / 'gemini_results.md'
        assert not output_file.exists()  # ファイルは作成されない

    def test_既存の出力ファイルが削除される(
        self, file_processor: FileProcessor, tmp_path: Path
    ) -> None:
        """既存の出力ファイルが削除される。"""
        # Arrange
        project_name = 'テストプロジェクト'
        existing_file = tmp_path / 'gemini_results.md'
        existing_file.write_text('既存の内容')

        # Act
        output_file = file_processor.prepare_output_file(tmp_path, project_name)

        # Assert
        assert output_file == existing_file
        assert not output_file.exists()  # 既存ファイルが削除される

    def test_出力ファイル削除エラー時にFileWritingErrorが発生する(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """出力ファイル削除エラー時にFileWritingErrorが発生する。"""
        # Arrange
        project_name = 'テストプロジェクト'
        existing_file = tmp_path / 'gemini_results.md'
        existing_file.write_text('既存の内容')

        # Act & Assert
        mocker.patch.object(Path, 'unlink', side_effect=OSError('削除失敗'))
        with pytest.raises(FileWritingError):
            file_processor.prepare_output_file(tmp_path, project_name)

    def test_テキストのプロンプトJSONへの追加が正常に動作する(
        self, file_processor: FileProcessor
    ) -> None:
        """テキストのプロンプトJSONへの追加が正常に動作する。"""
        # Arrange
        prompt: list[str | Image.Image] = ['テキスト1', 'テキスト2']
        prompt_for_json: list[dict[str, str]] = []

        # Act
        file_processor._add_text_to_prompt_json(prompt, prompt_for_json)

        # Assert
        assert len(prompt_for_json) == 2
        assert prompt_for_json[0] == {'type': 'text', 'data': 'テキスト1'}
        assert prompt_for_json[1] == {'type': 'text', 'data': 'テキスト2'}

    def test_画像のプロンプトJSONへの追加が正常に動作する(
        self, file_processor: FileProcessor, mocker: MockerFixture
    ) -> None:
        """画像のプロンプトJSONへの追加が正常に動作する。"""
        # Arrange
        mock_image1 = mocker.MagicMock(spec=Image.Image)
        mock_image2 = mocker.MagicMock(spec=Image.Image)
        prompt: list[str | Image.Image] = [mock_image1, 'テキスト', mock_image2]
        prompt_for_json: list[dict[str, str]] = []

        # Act
        file_processor._add_images_to_prompt_json(prompt, prompt_for_json)

        # Assert
        assert len(prompt_for_json) == 2
        assert prompt_for_json[0]['type'] == 'image'
        assert prompt_for_json[0]['figure'] == '0'
        assert prompt_for_json[1]['type'] == 'image'
        assert prompt_for_json[1]['figure'] == '2'

    def test_混合プロンプトが正常に処理される(
        self, file_processor: FileProcessor, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """テキストと画像が混在するプロンプトが正常に処理される。"""
        # Arrange
        test_file = tmp_path / 'test.txt'
        test_file.touch()
        mock_image = mocker.MagicMock(spec=Image.Image)
        prompt: list[str | Image.Image] = ['テキスト部分', mock_image, 'もう一つのテキスト']

        # Mock the image encoding
        mock_b64encode = mocker.patch('base64.b64encode')
        mock_b64encode.return_value = b'base64data'
        mock_file = mocker.patch('builtins.open', mocker.mock_open())
        # Act
        file_processor.create_prompt_json(prompt, test_file)

        # Assert - ファイルが正しく呼ばれることを確認
        mock_file.assert_called_once_with(tmp_path / 'prompt.json', 'w', encoding='utf-8')
        mock_image.save.assert_called_once()
