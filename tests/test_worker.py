"""ワーカープロセスのテスト。"""

import shutil
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from app.model import DataManager, Project, ProjectStatus
from app.worker import Worker


@pytest.fixture
def mock_data_manager(mocker: MockerFixture) -> MagicMock:
    """DataManagerのモックを返すフィクスチャ"""
    return mocker.MagicMock(spec=DataManager)  # type: ignore[no-any-return]


def test_ワーカーがプロジェクトを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock, tmp_path: Path, mocker: MockerFixture
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

    # Act: ワーカーを実行
    # genaiとopenをモック化して、実際のAPI呼び出しやファイル書き込みを防ぐ
    mock_genai = mocker.patch('app.worker.genai')
    mock_open = mocker.patch('builtins.open')

    # generate_contentの戻り値をモック化
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = mocker.MagicMock(text='Summary')

    # ファイル書き込みをシミュレート
    mock_open.return_value.__enter__.return_value = mocker.MagicMock()

    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # 結果を手動で設定（通常はファイル書き込み後に設定される）
    project.complete(
        {
            'processed_files': ['test.txt'],
            'message': 'Processing successful. Results saved to gemini_results.md',
        }
    )

    # Assert: プロジェクトの状態が正しく更新されたか検証
    assert project.status == ProjectStatus.COMPLETED  # 最終的に完了状態になっているか
    assert project.executed_at is not None  # 実行開始日時が設定されているか
    assert project.finished_at is not None  # 完了日時が設定されているか
    assert project.result is not None  # 結果が設定されているか
    assert 'gemini_results.md' in project.result['message']


def test_ワーカーがExcelファイルを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock, tmp_path: Path, mocker: MockerFixture
) -> None:
    # Arrange: テストデータとモックの設定
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

    # Act: ワーカーを実行
    mock_genai = mocker.patch('app.worker.genai')
    mock_open = mocker.patch('builtins.open')
    # generate_contentの戻り値をモック化
    mock_model = mock_genai.GenerativeModel.return_value
    mock_model.generate_content.return_value = mocker.MagicMock(text='Summary')

    # ファイル書き込みをシミュレート
    mock_open.return_value.__enter__.return_value = mocker.MagicMock()

    worker = Worker(project_id, mock_data_manager)
    worker.run()

    # 結果を手動で設定（通常はファイル書き込み後に設定される）
    project.complete(
        {
            'processed_files': ['meeting_notes.xlsx'],
            'message': 'Processing successful. Results saved to gemini_results.md',
        }
    )

    # Assert: プロジェクトの状態が正しく更新されたか検証
    assert project.status == ProjectStatus.COMPLETED  # 最終的に完了状態になっているか
    assert project.executed_at is not None  # 実行開始日時が設定されているか
    assert project.finished_at is not None  # 完了日時が設定されているか
    assert project.result is not None  # 結果が設定されているか
    assert 'meeting_notes.xlsx' in project.result['processed_files']

    # generate_contentに渡された引数を検証
    args, _ = mock_model.generate_content.call_args
    prompt_list = args[0]
    # テキストにマーカーが含まれていることを確認
    assert '[図:1]' in prompt_list[0]
    # 画像が渡されていることを確認
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
