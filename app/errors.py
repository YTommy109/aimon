"""アプリケーション全体で利用するカスタム例外クラスを定義します。"""

from abc import ABC, abstractmethod

from app.types import LLMProviderName, ProjectID

__all__ = [
    'APIConfigurationError',
    'AppError',
    'DataManagerError',
    'FileDeletingError',
    'FileProcessingError',
    'FileReadingError',
    'FileWritingError',
    'FormValidationError',
    'LLMAPICallError',
    'LLMError',
    'LLMUnexpectedResponseError',
    'MissingConfigError',
    'PathIsDirectoryError',
    'ProjectAlreadyRunningError',
    'ProjectNotFoundError',
    'ProjectProcessingError',
    'ProviderInitializationError',
    'ProviderNotInitializedError',
    'RequiredFieldsEmptyError',
    'ResourceNotFoundError',
    'UnsupportedProviderError',
    'ValidationError',
    'WorkerError',
]


class AppError(Exception):
    """すべての例外の基底クラス。"""


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

    def __init__(self, project_id: ProjectID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__(f'プロジェクト {project_id} は既に実行中です')


class ProjectProcessingError(WorkerError):
    """プロジェクト処理中に発生したエラーを表す例外クラス。"""

    def __init__(self, project_id: ProjectID) -> None:
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


class LLMError(Exception):
    """LLM呼び出し時のエラーを表す例外クラス。"""

    def __init__(
        self,
        message: str,
        provider: LLMProviderName,
        model: str,
        original_error: Exception | None = None,
    ) -> None:
        """LLMエラーを初期化します。

        Args:
            message: エラーメッセージ。
            provider: プロバイダ名。
            model: モデル名。
            original_error: 元の例外。
        """
        self.message = message
        self.provider: LLMProviderName = provider
        self.model = model
        self.original_error = original_error
        super().__init__(self.message)


class ProviderInitializationError(RuntimeError):
    """LLMプロバイダ初期化に失敗した場合の例外。"""

    def __init__(self) -> None:
        super().__init__('プロバイダの初期化に失敗しました')


class ProviderNotInitializedError(RuntimeError):
    """LLMプロバイダが未初期化の場合の例外。"""

    def __init__(self) -> None:
        super().__init__('プロバイダが初期化されていません')


class UnsupportedProviderError(AppError):
    """未サポートのプロバイダが指定された場合の例外。"""

    def __init__(self) -> None:
        super().__init__('サポートされていないプロバイダです')


class MissingConfigError(AppError):
    """必須設定が不足している場合の例外。"""

    def __init__(self, config_key: str) -> None:
        self.config_key = config_key
        super().__init__('必須設定が不足しています')


class LLMAPICallError(LLMError):
    """LLM API 呼び出しエラー (プロバイダ共通)。"""

    def __init__(
        self, provider: LLMProviderName, model: str, original_error: Exception | None = None
    ) -> None:
        message = f'{provider} API呼び出しエラー'
        super().__init__(message, provider, model, original_error)


class LLMUnexpectedResponseError(LLMError):
    """LLMレスポンス形式が不正な場合の例外。"""

    def __init__(self, provider: LLMProviderName, model: str) -> None:
        # 既存テスト互換のため英語メッセージで固定
        super().__init__(f'Unexpected response format from {provider.value}', provider, model)


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

    def __init__(self, resource_type: str, resource_id: ProjectID) -> None:
        """
        例外を初期化します。

        Args:
            resource_type: リソースの種類。
            resource_id: リソースID。
        """
        super().__init__(f'{resource_type} {resource_id} が見つかりません')


class ProjectNotFoundError(ResourceNotFoundError):
    """プロジェクトが見つからない場合の例外クラス。"""

    def __init__(self, project_id: ProjectID) -> None:
        """
        例外を初期化します。

        Args:
            project_id: プロジェクトID。
        """
        super().__init__('Project', project_id)


class ValidationError(AppError):
    """バリデーションエラーを表す例外クラス。"""

    def __init__(self, message: str) -> None:
        """
        例外を初期化します。

        Args:
            message: エラーメッセージ。
        """
        super().__init__(message)
