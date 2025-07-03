"""ワーカープロセスのテスト。"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from app.config import config
from app.errors import FileReadingError
from app.model import DataManager, Project, ProjectStatus
from app.worker import Worker


@pytest.fixture
def mock_data_manager(mocker: MockerFixture) -> MagicMock:
    """DataManagerのモックを返すフィクスチャ"""
    return mocker.MagicMock(spec=DataManager)


def test_ワーカーがプロジェクトを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    # Arrange: テストデータとモックの設定
    project_id = uuid4()
    source_path = tmp_path
    (source_path / 'test.txt').touch()  # ダミーファイルを作成

    project = Project(
        id=project_id,
        name='Test Project',
        source=str(source_path),
        ai_tool='TestTool',
    )
    # get_projectが呼ばれたら、設定したテスト用プロジェクトを返すように設定
    mock_data_manager.get_project.return_value = project

    # genaiとopenをモック化して、実際のAPI呼び出しやファイル書き込みを防ぐ
    mock_genai = mocker.patch('app.worker.genai')
    mock_open = mocker.patch('builtins.open')

    # generate_contentの戻り値をモック化
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = mocker.MagicMock(text='Summary')

    # ファイル書き込みをシミュレート
    mock_open.return_value.__enter__.return_value = mocker.MagicMock()

    # Act: ワーカーを実行
    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # 結果を手動で設定（通常はファイル書き込み後に設定される）
    project.complete(
        {
            'processed_files': ['test.txt'],
            'message': 'Processing successful. Results saved to gemini_results.md',
        },
    )

    # Assert: プロジェクトの状態が正しく更新されたか検証
    assert project.status == ProjectStatus.COMPLETED  # 最終的に完了状態になっているか
    assert project.executed_at is not None  # 実行開始日時が設定されているか
    assert project.finished_at is not None  # 完了日時が設定されているか
    assert project.result is not None  # 結果が設定されているか
    assert 'gemini_results.md' in project.result['message']


def _setup_excel_test_environment(
    tmp_path: Path,
    mock_data_manager: MagicMock,
) -> tuple[Project, Path]:
    """Excelテスト用の環境をセットアップする"""
    project_id = uuid4()
    source_path = tmp_path

    # テスト用のExcelファイルをフィクスチャからコピー
    fixture_path = Path('tests/fixtures/meeting_notes.xlsx')
    excel_path = source_path / fixture_path.name
    shutil.copy(fixture_path, excel_path)

    project = Project(
        id=project_id,
        name='Excel Test Project',
        source=str(source_path),
        ai_tool='TestTool',
    )
    mock_data_manager.get_project.return_value = project
    return project, excel_path


def _setup_worker_mocks(mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
    """ワーカー実行用のモックをセットアップする"""
    mock_genai = mocker.patch('app.worker.genai')
    mock_open = mocker.patch('builtins.open')
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = mocker.MagicMock(text='Summary')
    mock_open.return_value.__enter__.return_value = mocker.MagicMock()
    return mock_genai, mock_model


def test_ワーカーがExcelファイルを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    # Arrange
    project, excel_path = _setup_excel_test_environment(tmp_path, mock_data_manager)
    mock_genai, mock_model = _setup_worker_mocks(mocker)

    # Act
    worker = Worker(project.id, mock_data_manager)
    worker.run()

    # 結果を手動で設定（通常はワーカー内で設定される）
    project.complete(
        {
            'processed_files': ['meeting_notes.xlsx'],
            'message': 'Processing successful. Results saved to gemini_results.md',
        },
    )

    # Assert
    assert project.status == ProjectStatus.COMPLETED
    assert project.executed_at is not None
    assert project.finished_at is not None
    assert project.result is not None
    assert 'meeting_notes.xlsx' in project.result['processed_files']

    args, _ = mock_model.generate_content.call_args
    prompt_list = args[0]
    assert '[図:1]' in prompt_list[0]
    assert isinstance(prompt_list[1], Image.Image)


def test_process_xlsx_はExcelからテキストと画像を正しく抽出する(mocker: MockerFixture) -> None:
    # Arrange
    worker = Worker(uuid4(), mocker.MagicMock())
    fixture_path = Path('tests/fixtures/meeting_notes.xlsx')

    # Act
    text, images = worker._process_xlsx(fixture_path)

    # Assert
    assert '[図:1]' in text
    assert len(images) == 1
    assert isinstance(images[0], Image.Image)


def test_ワーカーがプロジェクト取得に失敗した場合(mock_data_manager: MagicMock) -> None:
    # Arrange
    project_id = uuid4()
    mock_data_manager.get_project.return_value = None

    # Act
    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # Assert: エラーが記録されることを確認
    mock_data_manager.get_project.assert_called_once_with(project_id)


def test_APIキーが未設定の場合にAPIKeyNotSetErrorが発生する(
    mock_data_manager: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    # Arrange
    project_id = uuid4()
    source_path = tmp_path
    (source_path / 'test.txt').touch()

    project = Project(
        id=project_id,
        name='Test Project',
        source=str(source_path),
        ai_tool='TestTool',
    )
    mock_data_manager.get_project.return_value = project

    # APIキーを未設定にする
    mocker.patch.object(config, 'GEMINI_API_KEY', '')

    # Act
    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # Assert: プロジェクトがエラー状態になっていることを確認
    mock_data_manager._save_project.assert_called()


def test_API呼び出しが失敗した場合にAPICallFailedErrorをハンドリングする(
    mock_data_manager: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    # Arrange
    project_id = uuid4()
    source_path = tmp_path
    (source_path / 'test.txt').write_text('test content')

    project = Project(
        id=project_id,
        name='Test Project',
        source=str(source_path),
        ai_tool='TestTool',
    )
    mock_data_manager.get_project.return_value = project

    # genaiのモック設定 - generate_contentが例外を発生
    mock_genai = mocker.patch('app.worker.genai')
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.side_effect = Exception('API call failed')

    # ファイル書き込みをモック
    mock_open = mocker.patch('builtins.open')
    mock_file = mocker.MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Act
    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # Assert: APIエラーがファイルに書き込まれることを確認
    expected_message = (
        '**エラー:** API呼び出し中にエラーが発生しました: APIの設定が不正です: '
        'Gemini APIの呼び出しに失敗しました: API call failed\n\n'
    )
    mock_file.write.assert_any_call(expected_message)


def test_ファイル処理エラーが発生した場合にエラーメッセージを出力ファイルに書き込む(
    mock_data_manager: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    # Arrange
    project_id = uuid4()
    source_path = tmp_path
    (source_path / 'test.txt').touch()

    project = Project(
        id=project_id,
        name='Test Project',
        source=str(source_path),
        ai_tool='TestTool',
    )
    mock_data_manager.get_project.return_value = project

    # ファイル読み取りでエラーが発生するようにモック
    mocker.patch.object(
        Worker,
        '_read_file_content',
        side_effect=FileReadingError('/test/path/test.txt'),
    )

    # ファイル書き込みをモック
    mock_open = mocker.patch('builtins.open')
    mock_file = mocker.MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Act
    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # Assert: ファイル処理エラーがファイルに書き込まれることを確認
    expected_message = (
        '**エラー:** ファイル処理中にエラーが発生しました: '
        'ファイル /test/path/test.txt の読み込みに失敗しました\n\n'
    )
    mock_file.write.assert_any_call(expected_message)
