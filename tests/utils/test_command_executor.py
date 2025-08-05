"""Command Executor のテストモジュール。"""

import subprocess
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from pytest_mock import MockerFixture

from app.errors import CommandExecutionError, CommandSecurityError
from app.utils.executors.command_executor import CommandExecutor


class TestCommandExecutor:
    """CommandExecutorのテストクラス。"""

    def test_エグゼキューターが正常に初期化される(self) -> None:
        """エグゼキューターが正常に初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python -c "print("test")"'

        # Act
        executor = CommandExecutor(ai_tool_id, command)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.command == command

    def test_異なるAIツールIDでエグゼキューターが初期化される(self) -> None:
        """異なるAIツールIDでエグゼキューターが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('87654321-4321-8765-4321-876543210987')
        command = 'git status'

        # Act
        executor = CommandExecutor(ai_tool_id, command)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.command == command

    def test_空のAIツールIDでエグゼキューターが初期化される(self) -> None:
        """空のAIツールIDでエグゼキューターが初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('00000000-0000-0000-0000-000000000000')
        command = 'python -c "import os; print(os.getcwd())"'

        # Act
        executor = CommandExecutor(ai_tool_id, command)

        # Assert
        assert executor.ai_tool_id == ai_tool_id
        assert executor.command == command

    def test_正常なコマンドが実行される(self, mocker: MockerFixture) -> None:
        """正常なコマンドが実行されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python -c "print("Hello, World!")"'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # モックレスポンスの設定
        mock_completed_process = Mock()
        mock_completed_process.stdout = 'Hello, World!\n'
        mock_subprocess_run.return_value = mock_completed_process

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['ai_tool_id'] == str(ai_tool_id)
        assert result['project_id'] == project_id
        assert result['source_path'] == source_path
        assert result['output'] == 'Hello, World!\n'

        # コマンドが正しく実行されたことを確認（タイムアウト付き）
        mock_subprocess_run.assert_called_once_with(
            command, shell=True, check=True, capture_output=True, text=True, timeout=300
        )

    def test_コマンド実行エラーが適切に処理される(self, mocker: MockerFixture) -> None:
        """コマンド実行エラーが適切に処理されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python -c "import nonexistent_module"'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # エラーレスポンスの設定
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, command, stderr='command not found'
        )

        # Act & Assert
        with pytest.raises(CommandExecutionError):
            executor.execute(project_id, source_path)

    def test_複雑なコマンドが正しく処理される(self, mocker: MockerFixture) -> None:
        """複雑なコマンドが正しく処理されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = (
            'python -c "import os; '
            '[print(f) for f in os.listdir("/path/to/source") if f.endswith(".py")][:5]"'
        )
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # モックレスポンスの設定
        expected_output = '/path/to/source/main.py\n/path/to/source/utils.py\n'
        mock_completed_process = Mock()
        mock_completed_process.stdout = expected_output
        mock_subprocess_run.return_value = mock_completed_process

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['output'] == expected_output
        mock_subprocess_run.assert_called_once_with(
            command, shell=True, check=True, capture_output=True, text=True, timeout=300
        )

    def test_空の出力が正しく処理される(self, mocker: MockerFixture) -> None:
        """空の出力が正しく処理されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python -c "pass"'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # モックレスポンスの設定（空の出力）
        mock_completed_process = Mock()
        mock_completed_process.stdout = ''
        mock_subprocess_run.return_value = mock_completed_process

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['output'] == ''
        assert result['ai_tool_id'] == str(ai_tool_id)
        assert result['project_id'] == project_id
        assert result['source_path'] == source_path

    def test_長い出力が正しく処理される(self, mocker: MockerFixture) -> None:
        """長い出力が正しく処理されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python -c "print("Line 1\\\\n" * 1000, end="")"'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # 長い出力のモック
        long_output = 'Line 1\n' * 1000
        mock_completed_process = Mock()
        mock_completed_process.stdout = long_output
        mock_subprocess_run.return_value = mock_completed_process

        # Act
        result = executor.execute(project_id, source_path)

        # Assert
        assert result['output'] == long_output
        assert len(result['output'].split('\n')) == 1001  # 1000行 + 空行

    # セキュリティ検証のテスト
    def test_長すぎるコマンドがセキュリティエラーを発生させる(self) -> None:
        """長すぎるコマンドがセキュリティエラーを発生させることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        # 1000文字を超える長いコマンド
        command = 'echo "' + 'x' * 1000 + '"'

        # Act & Assert
        with pytest.raises(CommandSecurityError, match='コマンドが最大長'):
            CommandExecutor(ai_tool_id, command)

    def test_ブロックされたコマンドがセキュリティエラーを発生させる(self) -> None:
        """ブロックされたコマンドがセキュリティエラーを発生させることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        blocked_commands = ['rm -rf /', 'sudo rm -rf /', 'passwd root']

        for command in blocked_commands:
            # Act & Assert
            with pytest.raises(
                CommandSecurityError, match='ブロックされたパターンが含まれています'
            ):
                CommandExecutor(ai_tool_id, command)

    @patch('app.config.config.ALLOWED_COMMAND_PREFIXES', ['python', 'node'])
    def test_許可されていないコマンドプレフィックスがセキュリティエラーを発生させる(self) -> None:
        """許可されていないコマンドプレフィックスがセキュリティエラーを発生させることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'curl http://example.com'  # curl は許可されていない

        # Act & Assert
        with pytest.raises(
            CommandSecurityError, match='許可されたプレフィックスで始まる必要があります'
        ):
            CommandExecutor(ai_tool_id, command)

    @patch('app.config.config.ALLOWED_COMMAND_PREFIXES', ['python', 'node'])
    def test_許可されたコマンドプレフィックスで正常に初期化される(self) -> None:
        """許可されたコマンドプレフィックスで正常に初期化されることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        commands = ['python script.py', 'node app.js']

        for command in commands:
            # Act (例外が発生しないことを確認)
            executor = CommandExecutor(ai_tool_id, command)

            # Assert
            assert executor.command == command

    def test_pushd_popdコマンドが許可されている(self) -> None:
        """pushdとpopdコマンドが許可されていることをテスト。"""
        # Arrange
        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        commands = [
            'pushd ait && python -m ait.main OVERVIEW -d {source_path} && popd',
            'pushd /tmp && ls && popd',
        ]

        for command in commands:
            # Act (例外が発生しないことを確認)
            executor = CommandExecutor(ai_tool_id, command)

            # Assert
            assert executor.command == command

    # タイムアウトと新しいエラーハンドリングのテスト
    @patch('app.config.config.COMMAND_TIMEOUT', 30)
    def test_コマンド実行でタイムアウトが設定される(self, mocker: MockerFixture) -> None:
        """コマンド実行でタイムアウトが設定されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python script.py'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # モックレスポンスの設定
        mock_completed_process = Mock()
        mock_completed_process.stdout = 'Success'
        mock_subprocess_run.return_value = mock_completed_process

        # Act
        executor.execute(project_id, source_path)

        # Assert
        mock_subprocess_run.assert_called_once_with(
            command, shell=True, check=True, capture_output=True, text=True, timeout=30
        )

    def test_タイムアウトエラーが適切に処理される(self, mocker: MockerFixture) -> None:
        """タイムアウトエラーが適切に処理されることをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python long_running_script.py'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # タイムアウトエラーのモック
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(command, 300)

        # Act & Assert
        with pytest.raises(CommandExecutionError, match='コマンドが.*秒でタイムアウトしました'):
            executor.execute(project_id, source_path)

    def test_新しいCommandExecutionErrorが発生する(self, mocker: MockerFixture) -> None:
        """新しいCommandExecutionErrorが発生することをテスト。"""
        # Arrange
        mock_subprocess_run = mocker.patch('subprocess.run')

        ai_tool_id = UUID('12345678-1234-5678-1234-567812345678')
        command = 'python failing_script.py'
        executor = CommandExecutor(ai_tool_id, command)
        project_id = 'test-project'
        source_path = '/path/to/source'

        # CalledProcessErrorのモック
        error = subprocess.CalledProcessError(1, command, stderr='Script failed')
        mock_subprocess_run.side_effect = error

        # Act & Assert
        with pytest.raises(CommandExecutionError) as exc_info:
            executor.execute(project_id, source_path)

        assert exc_info.value.command == command
        assert 'Script failed' in str(exc_info.value)
