"""設定モジュールのテスト。"""

import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from app.config import Config


def test_デフォルト値が正しく設定される(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.APP_ENV == 'development'
    assert Path('.data') == config.DATA_DIR
    assert Path('.data_test') == config.DATA_DIR_TEST
    assert config.DEFAULT_PROJECTS_FILE == 'projects.json'
    assert config.DEFAULT_AI_TOOLS_FILE == 'ai_tools.json'
    assert Path('log') == config.DEFAULT_LOG_DIR
    assert config.DEFAULT_LOG_FILE == 'app.log'
    assert config.LOG_ROTATION_DAYS == 7
    assert config.GEMINI_MODEL_NAME == 'gemini-1.5-flash'
    assert config.API_RATE_LIMIT_DELAY == 1.0
    assert config.GEMINI_API_KEY is None
    assert config.AUTO_REFRESH_INTERVAL == 1000


def test_環境変数から設定値を読み込める(mocker: MockerFixture) -> None:
    # Arrange
    env_values = {
        'APP_ENV': 'test',
        'DATA_DIR': 'custom_data',
        'DATA_DIR_TEST': 'custom_test_data',
        'DEFAULT_PROJECTS_FILE': 'custom_projects.json',
        'GEMINI_API_KEY': 'test_api_key',
    }
    mocker.patch.dict(os.environ, env_values, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.APP_ENV == 'test'
    assert config.GEMINI_API_KEY == 'test_api_key'
    assert config.data_dir_path == Path('custom_test_data')
    assert config.data_file_path == Path('custom_test_data') / 'custom_projects.json'


@pytest.mark.parametrize(
    ('env_vars', 'expected_path'),
    [
        ({}, Path('.data')),
        ({'DATA_DIR': 'custom_data'}, Path('custom_data')),
    ],
)
def test_development環境でのデータディレクトリパス(
    mocker: MockerFixture,
    env_vars: dict[str, str],
    expected_path: Path,
) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {'APP_ENV': 'development', **env_vars}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.data_dir_path == expected_path


@pytest.mark.parametrize(
    ('env_vars', 'expected_path'),
    [
        ({}, Path('.data_test')),
        ({'DATA_DIR_TEST': 'custom_test_data'}, Path('custom_test_data')),
    ],
)
def test_test環境でのデータディレクトリパス(
    mocker: MockerFixture,
    env_vars: dict[str, str],
    expected_path: Path,
) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {'APP_ENV': 'test', **env_vars}, clear=True)
    # Act
    config = Config()

    # Assert
    assert config.data_dir_path == expected_path


def test_データファイルパス(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {}, clear=True)
    config = Config()
    # Assert
    assert config.data_file_path == Path('.data') / 'projects.json'

    # Arrange
    mocker.patch.dict(os.environ, {'APP_ENV': 'test'}, clear=True)
    config = Config()
    # Assert
    assert config.data_file_path == Path('.data_test') / 'projects.json'


def test_ログファイルパス(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.log_file_path == Path('log') / 'app.log'
