"""アプリケーション全体で利用するカスタム例外クラスを定義します。"""

from abc import abstractmethod
from uuid import UUID


class BaseError(Exception):
    """すべての例外の基底クラス。"""


class FormValidationError(BaseError):
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

    def __init__(self, project_id: str | UUID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__(f'プロジェクト {project_id} は既に実行中です')


class ProjectProcessingError(WorkerError):
    """プロジェクト処理中に発生したエラーを表す例外クラス。"""

    def __init__(self, project_id: str | UUID) -> None:
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


class APIKeyNotSetError(APIConfigurationError):
    """APIキーが設定されていない場合の例外クラス。"""

    def __init__(self) -> None:
        """例外を初期化します。"""
        super().__init__('GEMINI_API_KEY environment variable not set.')


class APIConfigurationFailedError(APIConfigurationError):
    """Gemini APIの設定に失敗した場合の例外クラス。"""

    def __init__(self, error: Exception) -> None:
        """
        例外を初期化します。

        Args:
            error: 元の例外オブジェクト。
        """
        super().__init__(f'Gemini APIの設定に失敗しました: {error}')


class APICallFailedError(APIConfigurationError):
    """Gemini APIの呼び出しに失敗した場合の例外クラス。"""

    def __init__(self, error: Exception) -> None:
        """
        例外を初期化します。

        Args:
            error: 元の例外オブジェクト。
        """
        super().__init__(f'Gemini APIの呼び出しに失敗しました: {error}')


class FileProcessingError(WorkerError):
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
    """データマネージャーに関連するエラーを表す例外クラス。"""

    def __init__(self, message: str) -> None:
        """
        例外を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(f'データマネージャーでエラーが発生しました: {message}')


class ProjectNotFoundError(WorkerError):
    """プロジェクトが見つからない場合の例外クラス。"""

    def __init__(self, project_id: str | UUID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__(f'プロジェクト {project_id} が見つかりません')
