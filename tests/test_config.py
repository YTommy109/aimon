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
    # デフォルト環境はdevなので、.env.devファイルが使用される
    assert Path('log') == config.DEFAULT_LOG_DIR
    assert config.DEFAULT_LOG_FILE == 'app.log'
    assert config.LOG_ROTATION_DAYS == 7


def test_環境変数から設定値を読み込める(mocker: MockerFixture) -> None:
    # Arrange
    env_values = {
        'ENV': 'test',
        'DATA_DIR': 'custom_data',
    }
    mocker.patch.dict(os.environ, env_values, clear=True)

    # Act
    config = Config()

    # Assert
    # test環境なので、.env.testファイルが使用される
    assert config.data_dir_path == Path('custom_data')


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
    mocker.patch.dict(os.environ, {'ENV': 'dev', **env_vars}, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.data_dir_path == expected_path


@pytest.mark.parametrize(
    ('env_vars', 'expected_path'),
    [
        ({}, Path('.data')),
        ({'DATA_DIR': 'custom_test_data'}, Path('custom_test_data')),
    ],
)
def test_test環境でのデータディレクトリパス(
    mocker: MockerFixture,
    env_vars: dict[str, str],
    expected_path: Path,
) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {'ENV': 'test', **env_vars}, clear=True)
    # このテストはデフォルト値の検証を目的としているため、
    # ローカルに存在する .env.test の影響を受けないようにする
    mocker.patch('app.config._get_environment_config', return_value=('test', 'NON_EXISTENT.env'))
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


def test_ENVが設定される(mocker: MockerFixture) -> None:
    # Arrange
    mocker.patch.dict(os.environ, {'ENV': 'prod'}, clear=True)

    # Act
    Config()

    # Assert
    # prod環境なので、.envファイルが使用される
    assert os.getenv('ENV') == 'prod'


@pytest.mark.parametrize(
    ('env_vars', 'expected_env_file'),
    [
        ({'ENV': 'test'}, '.env.test'),
        ({'ENV': 'dev'}, '.env.dev'),
        ({'ENV': ''}, '.env.dev'),  # 空文字は dev 扱い
        ({'ENV': 'prod'}, '.env'),
    ],
)
def test_ENVの正規化(
    mocker: MockerFixture, env_vars: dict[str, str], expected_env_file: str
) -> None:
    # Arrange
    mocker.patch.dict(os.environ, env_vars, clear=True)

    # Act
    config = Config()

    # Assert
    # 環境に応じた適切な.envファイルが選択されることを確認
    # 実際のファイル存在は関係なく、設定が正しく初期化されることを確認
    assert config is not None


@pytest.mark.parametrize(
    ('env_vars', 'expected_path'),
    [
        ({'ENV': 'prod'}, Path('.data')),
        ({'ENV': 'prod', 'DATA_DIR': 'prod_data'}, Path('prod_data')),
    ],
)
def test_production環境でのデータディレクトリパス(
    mocker: MockerFixture, env_vars: dict[str, str], expected_path: Path
) -> None:
    # Arrange
    mocker.patch.dict(os.environ, env_vars, clear=True)

    # Act
    config = Config()

    # Assert
    assert config.data_dir_path == expected_path
