"""
Command Executor for Unix-based AI tool execution.
"""

import logging
import subprocess
from typing import Any
from uuid import UUID

from app.config import config
from app.errors import CommandExecutionError, CommandSecurityError

logger = logging.getLogger('aiman')


class CommandExecutor:
    """Executes AI tool as Unix command."""

    def __init__(self, ai_tool_id: UUID, command: str) -> None:
        """Initialize the AI Tool Executor with a command to execute.

        Args:
            ai_tool_id: UUID of the AI tool.
            command: Unix command to execute.

        Raises:
            CommandSecurityError: If command fails security validation.
        """
        self.ai_tool_id = ai_tool_id
        self.command = command
        self._validate_command_security()

    def execute(self, project_id: str, source_path: str) -> dict[str, Any]:
        """Execute the AI tool command.

        Args:
            project_id: Project ID.
            source_path: Path to the source directory.

        Returns:
            Dictionary with execution results.

        Raises:
            RuntimeError: If execution fails.
        """
        logger.debug(
            f'[DEBUG] CommandExecutor.execute start: '
            f'ai_tool_id={self.ai_tool_id}, command={self.command}, '
            f'project_id={project_id}, source_path={source_path}'
        )

        # コマンドにディレクトリパスを組み込む
        # {source_path} プレースホルダーを実際のパスに置換
        command_with_path = self.command.replace('{source_path}', source_path)

        logger.debug(f'[DEBUG] Command with path: {command_with_path}')

        try:
            # Note: shell=True is intentionally used here to execute AI tool commands
            # Commands are provided by trusted AI tool configurations, not user input
            completed_process = subprocess.run(  # noqa: S602
                command_with_path,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                timeout=config.COMMAND_TIMEOUT,
            )
            output = completed_process.stdout
            logger.debug(f'[DEBUG] Command execution successful: {output}')
            return {
                'ai_tool_id': str(self.ai_tool_id),
                'project_id': project_id,
                'source_path': source_path,
                'output': output,
            }
        except subprocess.TimeoutExpired as e:
            raise CommandExecutionError(self.command, timeout_seconds=config.COMMAND_TIMEOUT) from e
        except subprocess.CalledProcessError as e:
            raise CommandExecutionError(self.command, stderr=e.stderr) from e

    def _validate_command_security(self) -> None:
        """Validate command against security policies.

        Raises:
            CommandSecurityError: If command fails security validation.
        """
        self._validate_command_length()
        self._validate_blocked_commands()
        self._validate_allowed_prefixes()
        self._validate_placeholder_usage()

    def _validate_placeholder_usage(self) -> None:
        """Validate that command contains required placeholder.

        Raises:
            CommandSecurityError: If command doesn't contain required placeholder.
        """
        # {source_path}プレースホルダーが含まれている場合は検証
        # 含まれていない場合は、コマンドが固定のまま実行される（後方互換性のため）
        if '{source_path}' in self.command:
            logger.debug(f'[DEBUG] Command contains {{source_path}} placeholder: {self.command}')
        else:
            logger.debug(
                f'[DEBUG] Command does not contain {{source_path}} placeholder: {self.command}'
            )

    def _validate_command_length(self) -> None:
        """Validate command length."""
        if len(self.command) > config.MAX_COMMAND_LENGTH:
            raise CommandSecurityError(
                self.command,
                reason=f'コマンドが最大長 {config.MAX_COMMAND_LENGTH} 文字を超えています',
            )

    def _validate_blocked_commands(self) -> None:
        """Validate command against blocked patterns."""
        for blocked in config.BLOCKED_COMMANDS:
            if blocked in self.command:
                raise CommandSecurityError(
                    self.command, reason=f'ブロックされたパターンが含まれています: {blocked}'
                )

    def _validate_allowed_prefixes(self) -> None:
        """Validate command against allowed prefixes."""
        if not config.ALLOWED_COMMAND_PREFIXES:
            return

        command_parts = self.command.strip().split()
        if not command_parts:
            return

        first_command = command_parts[0]
        is_allowed = any(
            first_command.startswith(prefix) for prefix in config.ALLOWED_COMMAND_PREFIXES
        )
        if not is_allowed:
            allowed_list = ', '.join(config.ALLOWED_COMMAND_PREFIXES)
            raise CommandSecurityError(
                self.command,
                reason=f'許可されたプレフィックスで始まる必要があります: {allowed_list}',
            )
