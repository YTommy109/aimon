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
    assert Path('log') == config.DEFAULT_LOG_DIR
    assert config.DEFAULT_LOG_FILE == 'app.log'
    assert config.LOG_ROTATION_DAYS == 7


def test_環境変数から設定値を読み込める(mocker: MockerFixture) -> None:
    # Arrange
    env_values = {
        'APP_ENV': 'test',
        'DATA_DIR': 'custom_data',
        'DATA_DIR_TEST': 'custom_test_data',
        'GEMINI_API_KEY': 'test_api_key',
    }
    mocker.patch.dict(os.environ, env_values, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.APP_ENV == 'test'
    assert config.data_dir_path == Path('custom_test_data')


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


def test_ログファイルパス(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.log_file_path == Path('log') / 'app.log'


def test_Unixコマンド実行設定のデフォルト値(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.COMMAND_TIMEOUT == 300
    assert config.MAX_COMMAND_LENGTH == 1000
    assert 'python' in config.ALLOWED_COMMAND_PREFIXES
    assert 'node' in config.ALLOWED_COMMAND_PREFIXES
    assert 'npm' in config.ALLOWED_COMMAND_PREFIXES
    assert 'git' in config.ALLOWED_COMMAND_PREFIXES
    assert 'rm -rf' in config.BLOCKED_COMMANDS
    assert 'sudo' in config.BLOCKED_COMMANDS
    assert 'passwd' in config.BLOCKED_COMMANDS


def test_環境変数からUnixコマンド設定を読み込める(mocker: MockerFixture) -> None:
    # Arrange
    env_values = {
        'COMMAND_TIMEOUT': '600',
        'MAX_COMMAND_LENGTH': '2000',
    }
    mocker.patch.dict(os.environ, env_values, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.COMMAND_TIMEOUT == 600
    assert config.MAX_COMMAND_LENGTH == 2000
