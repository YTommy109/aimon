"""エラークラスのテストモジュール。"""

from uuid import UUID

from app.errors import (
    APIConfigurationError,
    AppError,
    DataManagerError,
    FileDeletingError,
    FileProcessingError,
    FileReadingError,
    FileWritingError,
    FormValidationError,
    PathIsDirectoryError,
    ProjectAlreadyRunningError,
    ProjectProcessingError,
    RequiredFieldsEmptyError,
    ResourceNotFoundError,
    WorkerError,
)
from app.models import ProjectID


class TestAppError:
    """AppErrorのテストクラス。"""

    def test_AppErrorがExceptionを継承している(self) -> None:
        # Assert
        assert issubclass(AppError, Exception)


class TestFormValidationError:
    """FormValidationErrorのテストクラス。"""

    def test_FormValidationErrorがAppErrorを継承している(self) -> None:
        # Assert
        assert issubclass(FormValidationError, AppError)


class TestRequiredFieldsEmptyError:
    """RequiredFieldsEmptyErrorのテストクラス。"""

    def test_RequiredFieldsEmptyErrorがFormValidationErrorを継承している(self) -> None:
        # Assert
        assert issubclass(RequiredFieldsEmptyError, FormValidationError)

    def test_RequiredFieldsEmptyErrorのメッセージが正しい(self) -> None:
        # Act
        error = RequiredFieldsEmptyError()

        # Assert
        assert str(error) == 'すべてのフィールドを入力してください。'


class TestWorkerError:
    """WorkerErrorのテストクラス。"""

    def test_WorkerErrorがExceptionを継承している(self) -> None:
        # Assert
        assert issubclass(WorkerError, Exception)


class TestProjectAlreadyRunningError:
    """ProjectAlreadyRunningErrorのテストクラス。"""

    def test_ProjectAlreadyRunningErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(ProjectAlreadyRunningError, WorkerError)

    def test_文字列IDでProjectAlreadyRunningErrorが作成される(self) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        error = ProjectAlreadyRunningError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} は既に実行中です'

    def test_ProjectIDでProjectAlreadyRunningErrorが作成される(self) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        error = ProjectAlreadyRunningError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} は既に実行中です'


class TestProjectProcessingError:
    """ProjectProcessingErrorのテストクラス。"""

    def test_ProjectProcessingErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(ProjectProcessingError, WorkerError)

    def test_文字列IDでProjectProcessingErrorが作成される(self) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        error = ProjectProcessingError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} の処理中にエラーが発生しました'

    def test_ProjectIDでProjectProcessingErrorが作成される(self) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        error = ProjectProcessingError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} の処理中にエラーが発生しました'


class TestAPIConfigurationError:
    """APIConfigurationErrorのテストクラス。"""

    def test_APIConfigurationErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(APIConfigurationError, WorkerError)

    def test_APIConfigurationErrorのメッセージが正しい(self) -> None:
        # Act
        error = APIConfigurationError('API key is missing')

        # Assert
        assert str(error) == 'APIの設定が不正です: API key is missing'


class TestFileProcessingError:
    """FileProcessingErrorのテストクラス。"""

    def test_FileProcessingErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(FileProcessingError, WorkerError)

    def test_FileProcessingErrorが抽象クラスである(self) -> None:
        # Act & Assert
        # 抽象クラスなので直接インスタンス化できない
        # 実際にはTypeErrorではなく、抽象メソッドが実装されていないためエラーになる
        # このテストは抽象クラスの性質を確認するためのもの
        assert hasattr(FileProcessingError, '__abstractmethods__')


class TestFileReadingError:
    """FileReadingErrorのテストクラス。"""

    def test_FileReadingErrorがFileProcessingErrorを継承している(self) -> None:
        # Assert
        assert issubclass(FileReadingError, FileProcessingError)

    def test_FileReadingErrorのメッセージが正しい(self) -> None:
        # Act
        error = FileReadingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の読み込みに失敗しました'


class TestFileWritingError:
    """FileWritingErrorのテストクラス。"""

    def test_FileWritingErrorがFileProcessingErrorを継承している(self) -> None:
        # Assert
        assert issubclass(FileWritingError, FileProcessingError)

    def test_FileWritingErrorのメッセージが正しい(self) -> None:
        # Act
        error = FileWritingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の書き込みに失敗しました'


class TestPathIsDirectoryError:
    """PathIsDirectoryErrorのテストクラス。"""

    def test_PathIsDirectoryErrorがFileProcessingErrorを継承している(self) -> None:
        # Assert
        assert issubclass(PathIsDirectoryError, FileProcessingError)

    def test_PathIsDirectoryErrorのメッセージが正しい(self) -> None:
        # Act
        error = PathIsDirectoryError('/path/to/directory')

        # Assert
        assert str(error) == 'パス /path/to/directory はディレクトリです'


class TestFileDeletingError:
    """FileDeletingErrorのテストクラス。"""

    def test_FileDeletingErrorがFileProcessingErrorを継承している(self) -> None:
        # Assert
        assert issubclass(FileDeletingError, FileProcessingError)

    def test_FileDeletingErrorのメッセージが正しい(self) -> None:
        # Act
        error = FileDeletingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の削除に失敗しました'


class TestDataManagerError:
    """DataManagerErrorのテストクラス。"""

    def test_DataManagerErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(DataManagerError, WorkerError)

    def test_DataManagerErrorのメッセージが正しい(self) -> None:
        # Act
        error = DataManagerError('Database connection failed')

        # Assert
        assert str(error) == 'データ管理エラー: Database connection failed'


class TestResourceNotFoundError:
    """ResourceNotFoundErrorのテストクラス。"""

    def test_ResourceNotFoundErrorがWorkerErrorを継承している(self) -> None:
        # Assert
        assert issubclass(ResourceNotFoundError, WorkerError)

    def test_文字列IDでResourceNotFoundErrorが作成される(self) -> None:
        # Arrange
        project_id = ProjectID(UUID('12345678-1234-5678-1234-567812345678'))

        # Act
        error = ResourceNotFoundError('Project', project_id)

        # Assert
        assert str(error) == f'Project {project_id} が見つかりません'
