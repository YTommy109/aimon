"""
Integration tests for the worker and data manager.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.model import DataManager, Project, ProjectStatus
from app.worker import Worker


@pytest.fixture
def data_manager(tmp_path: Path) -> DataManager:
    """テスト用のDataManagerインスタンスを作成する"""
    data_dir = tmp_path / '.data'
    data_dir.mkdir()
    (data_dir / 'ai_tools.json').touch()
    return DataManager(data_dir)


@pytest.mark.ci
class TestWorkerIntegration:
    """ワーカーとデータマネージャーの統合テスト"""

    def _setup_test_project_and_mocks(
        self,
        data_manager: DataManager,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> tuple[Project, Path]:
        """テスト用のプロジェクトとモックを設定します。"""
        source_dir = tmp_path / 'source_files'
        source_dir.mkdir()
        (source_dir / 'file1.txt').write_text('content1')
        (source_dir / 'file2.txt').write_text('content2')

        project = data_manager.create_project(
            name='Test Project Integration',
            source=str(source_dir),
            ai_tool='TestTool',
        )

        mock_response = MagicMock()
        mock_response.text = 'Mocked summary'
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mocker.patch('app.worker.genai', mock_genai)

        return project, source_dir

    def test_プロジェクトの作成からワーカー処理を経てステータスと結果が正しく更新される(
        self,
        data_manager: DataManager,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        # Arrange: プロジェクトを作成し、ソースファイルをモックする
        project, source_dir = self._setup_test_project_and_mocks(data_manager, tmp_path, mocker)
        assert project.status == ProjectStatus.PENDING

        # Act: モックされた genai でワーカープロセスを実行
        worker = Worker(project.id, data_manager)
        worker.run()

        # Assert: プロジェクトが正しく更新されていることを確認
        updated_project = data_manager.get_project(project.id)
        assert updated_project is not None
        assert updated_project.status == ProjectStatus.COMPLETED
        assert updated_project.result is not None
        assert 'processed_files' in updated_project.result
        assert len(updated_project.result['processed_files']) == 2
        assert 'file1.txt' in updated_project.result['processed_files']
        assert 'file2.txt' in updated_project.result['processed_files']

        # Assert: 出力ファイルが正しく作成されていることを確認
        output_file = source_dir / 'gemini_results.md'
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert 'Mocked summary' in content
        assert 'file1.txt' in content
        assert 'file2.txt' in content
