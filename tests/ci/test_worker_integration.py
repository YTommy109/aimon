"""
Integration tests for the worker and data manager.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.data_manager import DataManager
from app.worker import Worker


@pytest.fixture
def data_manager(tmp_path: Path) -> DataManager:
    """テスト用のDataManagerインスタンスを作成する"""
    data_dir = tmp_path / '.data'
    data_dir.mkdir()
    data_file = data_dir / 'projects.json'
    (data_dir / 'ai_tools.json').touch()
    return DataManager(data_file)


@pytest.mark.ci
def test_プロジェクトの作成からワーカー処理を経てステータスと結果が正しく更新される(
    data_manager: DataManager, tmp_path: Path
) -> None:
    # Arrange: Create a project and mock source files
    source_dir = tmp_path / 'source_files'
    source_dir.mkdir()
    (source_dir / 'file1.txt').write_text('content1')
    (source_dir / 'file2.txt').write_text('content2')

    project = data_manager.create_project(
        name='Test Project Integration',
        source=str(source_dir),
        ai_tool='TestTool',
    )
    assert project.status == 'Pending'

    # Act: Run the worker process with a mocked genai
    mock_response = MagicMock()
    mock_response.text = 'Mocked summary'

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    mock_genai = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model

    with patch('app.worker.genai', mock_genai):
        worker = Worker(project.id, data_manager)
        worker.run()

    # Assert: Verify the project has been updated
    updated_project = data_manager.get_project(project.id)
    assert updated_project is not None
    assert updated_project.status == 'Completed'
    assert updated_project.result is not None
    assert 'processed_files' in updated_project.result
    assert len(updated_project.result['processed_files']) == 2
    assert 'file1.txt' in updated_project.result['processed_files']
    assert 'file2.txt' in updated_project.result['processed_files']

    # Assert: Check if the output file was created correctly
    output_file = source_dir / 'gemini_results.md'
    assert output_file.exists()
    content = output_file.read_text(encoding='utf-8')
    assert 'Mocked summary' in content
    assert 'file1.txt' in content
    assert 'file2.txt' in content
