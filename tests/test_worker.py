import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from PIL import Image

from app.data_manager import DataManager, Project
from app.worker import Worker


@pytest.fixture
def mock_data_manager() -> MagicMock:
    """DataManagerのモックを返すフィクスチャ"""
    return MagicMock(spec=DataManager)


def test_ワーカーがプロジェクトを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock, tmp_path: Path
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
    with patch('app.worker.genai'), patch('builtins.open'):
        worker = Worker(project_id, mock_data_manager)
        worker.run()

    # Assert: 期待されるメソッドが正しい引数で呼ばれたか検証
    mock_data_manager.update_project_status.assert_any_call(project_id, 'Processing')
    mock_data_manager.update_project_status.assert_any_call(project_id, 'Completed')
    mock_data_manager.update_project_result.assert_called_once()
    assert (
        'gemini_results.md'
        in mock_data_manager.update_project_result.call_args[0][1]['message']
    )


def test_ワーカーがExcelファイルを正常に処理しステータスと結果を更新する(
    mock_data_manager: MagicMock, tmp_path: Path
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
    with patch('app.worker.genai') as mock_genai, patch('builtins.open'):
        # generate_contentの戻り値をモック化
        mock_model = mock_genai.GenerativeModel.return_value
        mock_model.generate_content.return_value = MagicMock(text='Summary')

        worker = Worker(project_id, mock_data_manager)
        worker.run()

    # Assert: 期待されるメソッドが正しい引数で呼ばれたか検証
    mock_data_manager.update_project_status.assert_any_call(project_id, 'Processing')
    mock_data_manager.update_project_status.assert_any_call(project_id, 'Completed')
    mock_data_manager.update_project_result.assert_called_once()
    result = mock_data_manager.update_project_result.call_args[0][1]
    assert 'meeting_notes.xlsx' in result['processed_files']

    # generate_contentに渡された引数を検証
    args, _ = mock_model.generate_content.call_args
    prompt_list = args[0]
    # テキストにマーカーが含まれていることを確認
    assert '[図:1]' in prompt_list[0]
    # 画像が渡されていることを確認
    assert isinstance(prompt_list[1], Image.Image)


def test_process_xlsx_はExcelからテキストと画像を正しく抽出する() -> None:
    # Arrange
    worker = Worker(uuid4(), MagicMock())
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

    # Assert
    # ステータスが'Failed'で1回だけ更新されることを確認
    mock_data_manager.update_project_status.assert_called_once_with(
        project_id, 'Failed'
    )
