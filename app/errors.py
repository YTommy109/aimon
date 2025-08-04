"""アプリケーション全体で利用するカスタム例外クラスを定義します。"""

from abc import ABC, abstractmethod

from app.models import AIToolID, ProjectID


class AppError(Exception):
    """すべての例外の基底クラス。"""


class CommandExecutionError(AppError):
    """Exception raised for errors in the command execution process."""

    def __init__(self, command: str, message: str = 'Command execution failed'):
        self.command = command
        self.message = message
        super().__init__(f'{message}: {command}')


class CommandSecurityError(AppError):
    """Exception raised for security errors related to command execution."""

    def __init__(self, command: str, message: str = 'Security violation detected'):
        self.command = command
        self.message = message
        super().__init__(f'{message}: {command}')


class FormValidationError(AppError):
    """フォーム入力の検証に関連する基底例外クラス。"""


class RequiredFieldsEmptyError(FormValidationError):
    """必須フィールドが入力されていない場合の例外クラス。"""

    def __init__(self) -> None:
        """例外を初期化します。"""
        super().__init__('すべてのフィールドを入力してください。')


class WorkerError(Exception):
    """ワーカー処理に関連する基底例外クラス。"""


class ProjectAlreadyRunningError(WorkerError):
    """プロジェクトが既に実行中の場合の例外クラス。"""

    def __init__(self, project_id: str | ProjectID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__(f'プロジェクト {project_id} は既に実行中です')


class ProjectProcessingError(WorkerError):
    """プロジェクト処理中に発生したエラーを表す例外クラス。"""

    def __init__(self, project_id: str | ProjectID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__(f'プロジェクト {project_id} の処理中にエラーが発生しました')


class APIConfigurationError(WorkerError):
    """API設定に関連するエラーを表す例外クラス。"""

    def __init__(self, message: str) -> None:
        """
        例外を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(f'APIの設定が不正です: {message}')


class FileProcessingError(WorkerError, ABC):
    """ファイル操作に関連する基底例外クラス。"""

    @abstractmethod
    def __init__(self, message: str) -> None:
        """
        例外を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(message)


class FileReadingError(FileProcessingError):
    """ファイルの読み込みに失敗した場合の例外クラス。"""

    def __init__(self, file_path: str) -> None:
        """
        例外を初期化します。

        Args:
            file_path: 読み込みに失敗したファイルパス。
        """
        super().__init__(f'ファイル {file_path} の読み込みに失敗しました')


class FileWritingError(FileProcessingError):
    """ファイルの書き込みに失敗した場合の例外クラス。"""

    def __init__(self, file_path: str) -> None:
        """
        例外を初期化します。

        Args:
            file_path: 書き込みに失敗したファイルパス。
        """
        super().__init__(f'ファイル {file_path} の書き込みに失敗しました')


class PathIsDirectoryError(FileProcessingError):
    """パスがディレクトリである場合の例外クラス。"""

    def __init__(self, path: str) -> None:
        """
        例外を初期化します。

        Args:
            path: ディレクトリとして存在するパス。
        """
        super().__init__(f'パス {path} はディレクトリです')


class FileDeletingError(FileProcessingError):
    """ファイルの削除に失敗した場合の例外クラス。"""

    def __init__(self, file_path: str) -> None:
        """
        例外を初期化します。

        Args:
            file_path: 削除に失敗したファイルパス。
        """
        super().__init__(f'ファイル {file_path} の削除に失敗しました')


class DataManagerError(WorkerError):
    """データ管理に関連するエラーを表す例外クラス。"""

    def __init__(self, message: str) -> None:
        """
        例外を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(f'データ管理エラー: {message}')


class ResourceNotFoundError(WorkerError):
    """リソースが見つからない場合の例外クラス。"""

    def __init__(self, resource_type: str, resource_id: str | ProjectID | AIToolID) -> None:
        """
        例外を初期化します。

        Args:
            resource_type: リソースの種類。
            resource_id: リソースID。
        """
        super().__init__(f'{resource_type} {resource_id} が見つかりません')
