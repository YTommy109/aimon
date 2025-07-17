import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from PIL import Image

from app.application.project_processor import ProjectProcessor
from app.domain.ai_tool_executor import AIToolExecutor
from app.domain.entities import AITool, Project
from app.errors import (
    APIConfigurationError,
    FileWritingError,
    ProjectProcessingError,
)


class DummyExecutor(AIToolExecutor):
    def execute(self, content: str, images: list[Image.Image]) -> str:
        return 'summary'


def make_project() -> Project:
    return Project(name='テスト', source='/tmp', ai_tool='tool1')


def make_processor() -> tuple[ProjectProcessor, MagicMock, MagicMock, MagicMock]:
    repo = MagicMock()
    file_proc = MagicMock()
    ai_repo = MagicMock()
    return ProjectProcessor(repo, file_proc, ai_repo), repo, file_proc, ai_repo


def test_handle_project_processing_not_found() -> None:
    processor, repo, _, _ = make_processor()
    repo.find_by_id.return_value = None
    with pytest.raises(ProjectProcessingError), processor._handle_project_processing(uuid4()):
        pass


def test_handle_project_processing_success() -> None:
    processor, repo, _, _ = make_processor()
    project = make_project()
    repo.find_by_id.return_value = project
    with processor._handle_project_processing(uuid4()) as p:
        assert p == project
    repo.save.assert_called()


def test_handle_project_error_file_processing() -> None:
    processor, repo, _, _ = make_processor()
    project = make_project()
    e = FileWritingError('file.txt')
    processor._handle_project_error(project, e)
    repo.save.assert_called()
    assert project.result is not None
    assert project.result['error'].startswith('ファイル処理エラー:')


def test_handle_project_error_api_config() -> None:
    processor, repo, _, _ = make_processor()
    project = make_project()
    e = APIConfigurationError('err')
    processor._handle_project_error(project, e)
    repo.save.assert_called()
    assert project.result is not None
    assert project.result['error'].startswith('API設定エラー:')


def test_get_ai_tool_entity_found() -> None:
    processor, _, _, ai_repo = make_processor()
    ai_tool = AITool(id='tool1', name_ja='t', endpoint_url='http://x')
    ai_repo.find_by_id.return_value = ai_tool
    assert processor._get_ai_tool_entity('tool1') == ai_tool


def test_get_ai_tool_entity_not_found() -> None:
    processor, _, _, ai_repo = make_processor()
    ai_repo.find_by_id.return_value = None
    with pytest.raises(RuntimeError):
        processor._get_ai_tool_entity('notfound')


def test_create_ai_executor_calls_factory() -> None:
    processor, _, _, _ = make_processor()
    ai_tool = AITool(id='tool1', name_ja='t', endpoint_url='http://x')
    with patch('app.application.project_processor.AIExecutorFactory.create_executor') as f:
        f.return_value = DummyExecutor()
        ex = processor._create_ai_executor(ai_tool)
        assert isinstance(ex, DummyExecutor)
        f.assert_called_once_with(ai_tool)


def test_process_files_with_executor() -> None:
    processor, _, _, _ = make_processor()
    ai_executor = DummyExecutor()
    files = [Path('a.txt'), Path('b.txt')]
    with patch.object(processor, '_process_single_file_with_ai_tool', side_effect=[True, False]):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                result = processor._process_files_with_executor(files, f_out, ai_executor)
            assert result == ['a.txt']
        finally:
            os.unlink(filename)


def test_process_single_file_with_ai_tool_success() -> None:
    processor, _, _, _ = make_processor()
    ai_executor = DummyExecutor()
    with patch.object(processor, '_try_process_file_with_ai_tool', return_value=True):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                assert processor._process_single_file_with_ai_tool(
                    Path('a.txt'), f_out, ai_executor
                )
        finally:
            os.unlink(filename)


def test_process_single_file_with_ai_tool_error() -> None:
    processor, _, _, _ = make_processor()
    ai_executor = DummyExecutor()
    with (
        patch.object(
            processor, '_try_process_file_with_ai_tool', side_effect=FileWritingError('file.txt')
        ),
        patch.object(processor, '_handle_processing_error', return_value=False) as mock_handle,
    ):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                assert not processor._process_single_file_with_ai_tool(
                    Path('a.txt'), f_out, ai_executor
                )
            mock_handle.assert_called()
        finally:
            os.unlink(filename)


def test_try_process_file_with_ai_tool_empty() -> None:
    processor, _, file_proc, _ = make_processor()
    ai_executor = DummyExecutor()
    file_proc.read_file_content.return_value = ('   ', [])
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
    try:
        with open(filename, 'w+', encoding='utf-8') as f_out:
            assert not processor._try_process_file_with_ai_tool(Path('a.txt'), f_out, ai_executor)
    finally:
        os.unlink(filename)


def test_try_process_file_with_ai_tool_success() -> None:
    processor, _, file_proc, _ = make_processor()
    ai_executor = DummyExecutor()
    file_proc.read_file_content.return_value = ('content', ['img'])
    with patch.object(
        processor, '_process_file_content_with_ai_tool', return_value=True
    ) as mock_proc:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                assert processor._try_process_file_with_ai_tool(Path('a.txt'), f_out, ai_executor)
            mock_proc.assert_called()
        finally:
            os.unlink(filename)


def test_process_file_content_with_ai_tool() -> None:
    processor, _, file_proc, _ = make_processor()
    ai_executor = DummyExecutor()
    file_proc.create_prompt_json = MagicMock()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
    try:
        with open(filename, 'w+', encoding='utf-8') as f_out:
            result = processor._process_file_content_with_ai_tool(
                Path('a.txt'), 'content', ['img'], f_out, ai_executor
            )
        with open(filename, encoding='utf-8') as f:
            content = f.read()
        assert result is True
        assert '要約結果' in content
    finally:
        os.unlink(filename)


def test_handle_file_processing_error() -> None:
    processor, _, _, _ = make_processor()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
    try:
        with open(filename, 'w+', encoding='utf-8') as f_out:
            result = processor._handle_file_processing_error(
                Path('a.txt'), f_out, FileWritingError('file.txt')
            )
        with open(filename, encoding='utf-8') as f:
            content = f.read()
        assert not result
        assert 'エラー' in content
    finally:
        os.unlink(filename)


def test_handle_api_error() -> None:
    processor, _, _, _ = make_processor()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
    try:
        with open(filename, 'w+', encoding='utf-8') as f_out:
            result = processor._handle_api_error(Path('a.txt'), f_out, APIConfigurationError('err'))
        with open(filename, encoding='utf-8') as f:
            content = f.read()
        assert not result
        assert 'API呼び出し中にエラー' in content
    finally:
        os.unlink(filename)


def test_handle_processing_error_file() -> None:
    processor, _, _, _ = make_processor()
    with patch.object(processor, '_handle_file_processing_error', return_value=False) as mock_proc:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                result = processor._handle_processing_error(
                    Path('a.txt'), f_out, FileWritingError('file.txt')
                )
            mock_proc.assert_called()
            assert result is False
        finally:
            os.unlink(filename)


def test_handle_processing_error_api() -> None:
    processor, _, _, _ = make_processor()
    with patch.object(processor, '_handle_api_error', return_value=False) as mock_proc:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            filename = tmp.name
        try:
            with open(filename, 'w+', encoding='utf-8') as f_out:
                result = processor._handle_processing_error(
                    Path('a.txt'), f_out, APIConfigurationError('err')
                )
            mock_proc.assert_called()
            assert result is False
        finally:
            os.unlink(filename)
