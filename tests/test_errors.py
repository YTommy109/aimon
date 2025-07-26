"""エラークラスのテスト。"""

from uuid import UUID

from app.errors import (
    APIConfigurationError,
    BaseError,
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


class TestBaseError:
    """BaseErrorのテストクラス。"""

    def test_BaseErrorがExceptionを継承している(self) -> None:
        """BaseErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(BaseError, Exception)


class TestFormValidationError:
    """FormValidationErrorのテストクラス。"""

    def test_FormValidationErrorがBaseErrorを継承している(self) -> None:
        """FormValidationErrorがBaseErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(FormValidationError, BaseError)


class TestRequiredFieldsEmptyError:
    """RequiredFieldsEmptyErrorのテストクラス。"""

    def test_RequiredFieldsEmptyErrorがFormValidationErrorを継承している(self) -> None:
        """RequiredFieldsEmptyErrorがFormValidationErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(RequiredFieldsEmptyError, FormValidationError)

    def test_RequiredFieldsEmptyErrorのメッセージが正しい(self) -> None:
        """RequiredFieldsEmptyErrorのメッセージが正しいことをテスト。"""
        # Act
        error = RequiredFieldsEmptyError()

        # Assert
        assert str(error) == 'すべてのフィールドを入力してください。'


class TestWorkerError:
    """WorkerErrorのテストクラス。"""

    def test_WorkerErrorがExceptionを継承している(self) -> None:
        """WorkerErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(WorkerError, Exception)


class TestProjectAlreadyRunningError:
    """ProjectAlreadyRunningErrorのテストクラス。"""

    def test_ProjectAlreadyRunningErrorがWorkerErrorを継承している(self) -> None:
        """ProjectAlreadyRunningErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(ProjectAlreadyRunningError, WorkerError)

    def test_文字列IDでProjectAlreadyRunningErrorが作成される(self) -> None:
        """文字列IDでProjectAlreadyRunningErrorが作成されることをテスト。"""
        # Act
        error = ProjectAlreadyRunningError('test-project-1')

        # Assert
        assert str(error) == 'プロジェクト test-project-1 は既に実行中です'

    def test_UUIDでProjectAlreadyRunningErrorが作成される(self) -> None:
        """UUIDでProjectAlreadyRunningErrorが作成されることをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        error = ProjectAlreadyRunningError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} は既に実行中です'


class TestProjectProcessingError:
    """ProjectProcessingErrorのテストクラス。"""

    def test_ProjectProcessingErrorがWorkerErrorを継承している(self) -> None:
        """ProjectProcessingErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(ProjectProcessingError, WorkerError)

    def test_文字列IDでProjectProcessingErrorが作成される(self) -> None:
        """文字列IDでProjectProcessingErrorが作成されることをテスト。"""
        # Act
        error = ProjectProcessingError('test-project-1')

        # Assert
        assert str(error) == 'プロジェクト test-project-1 の処理中にエラーが発生しました'

    def test_UUIDでProjectProcessingErrorが作成される(self) -> None:
        """UUIDでProjectProcessingErrorが作成されることをテスト。"""
        # Arrange
        project_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        error = ProjectProcessingError(project_id)

        # Assert
        assert str(error) == f'プロジェクト {project_id} の処理中にエラーが発生しました'


class TestAPIConfigurationError:
    """APIConfigurationErrorのテストクラス。"""

    def test_APIConfigurationErrorがWorkerErrorを継承している(self) -> None:
        """APIConfigurationErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(APIConfigurationError, WorkerError)

    def test_APIConfigurationErrorのメッセージが正しい(self) -> None:
        """APIConfigurationErrorのメッセージが正しいことをテスト。"""
        # Act
        error = APIConfigurationError('API key is missing')

        # Assert
        assert str(error) == 'APIの設定が不正です: API key is missing'


class TestFileProcessingError:
    """FileProcessingErrorのテストクラス。"""

    def test_FileProcessingErrorがWorkerErrorを継承している(self) -> None:
        """FileProcessingErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(FileProcessingError, WorkerError)

    def test_FileProcessingErrorが抽象クラスである(self) -> None:
        """FileProcessingErrorが抽象クラスであることをテスト。"""
        # Act & Assert
        # 抽象クラスなので直接インスタンス化できない
        # 実際にはTypeErrorではなく、抽象メソッドが実装されていないためエラーになる
        # このテストは抽象クラスの性質を確認するためのもの
        assert hasattr(FileProcessingError, '__abstractmethods__')


class TestFileReadingError:
    """FileReadingErrorのテストクラス。"""

    def test_FileReadingErrorがFileProcessingErrorを継承している(self) -> None:
        """FileReadingErrorがFileProcessingErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(FileReadingError, FileProcessingError)

    def test_FileReadingErrorのメッセージが正しい(self) -> None:
        """FileReadingErrorのメッセージが正しいことをテスト。"""
        # Act
        error = FileReadingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の読み込みに失敗しました'


class TestFileWritingError:
    """FileWritingErrorのテストクラス。"""

    def test_FileWritingErrorがFileProcessingErrorを継承している(self) -> None:
        """FileWritingErrorがFileProcessingErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(FileWritingError, FileProcessingError)

    def test_FileWritingErrorのメッセージが正しい(self) -> None:
        """FileWritingErrorのメッセージが正しいことをテスト。"""
        # Act
        error = FileWritingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の書き込みに失敗しました'


class TestPathIsDirectoryError:
    """PathIsDirectoryErrorのテストクラス。"""

    def test_PathIsDirectoryErrorがFileProcessingErrorを継承している(self) -> None:
        """PathIsDirectoryErrorがFileProcessingErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(PathIsDirectoryError, FileProcessingError)

    def test_PathIsDirectoryErrorのメッセージが正しい(self) -> None:
        """PathIsDirectoryErrorのメッセージが正しいことをテスト。"""
        # Act
        error = PathIsDirectoryError('/path/to/directory')

        # Assert
        assert (
            str(error) == 'パス /path/to/directory はディレクトリです。ファイルである必要があります'
        )


class TestFileDeletingError:
    """FileDeletingErrorのテストクラス。"""

    def test_FileDeletingErrorがFileProcessingErrorを継承している(self) -> None:
        """FileDeletingErrorがFileProcessingErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(FileDeletingError, FileProcessingError)

    def test_FileDeletingErrorのメッセージが正しい(self) -> None:
        """FileDeletingErrorのメッセージが正しいことをテスト。"""
        # Act
        error = FileDeletingError('/path/to/file.txt')

        # Assert
        assert str(error) == 'ファイル /path/to/file.txt の削除に失敗しました'


class TestDataManagerError:
    """DataManagerErrorのテストクラス。"""

    def test_DataManagerErrorがWorkerErrorを継承している(self) -> None:
        """DataManagerErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(DataManagerError, WorkerError)

    def test_DataManagerErrorのメッセージが正しい(self) -> None:
        """DataManagerErrorのメッセージが正しいことをテスト。"""
        # Act
        error = DataManagerError('Database connection failed')

        # Assert
        assert str(error) == 'データマネージャーでエラーが発生しました: Database connection failed'


class TestResourceNotFoundError:
    """ResourceNotFoundErrorのテストクラス。"""

    def test_ResourceNotFoundErrorがWorkerErrorを継承している(self) -> None:
        """ResourceNotFoundErrorがWorkerErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(ResourceNotFoundError, WorkerError)

    def test_文字列IDでResourceNotFoundErrorが作成される(self) -> None:
        """文字列IDでResourceNotFoundErrorが作成されることをテスト。"""
        # Act
        error = ResourceNotFoundError('Project', 'test-project-1')

        # Assert
        assert str(error) == 'Project test-project-1 が見つかりません'

    def test_UUIDでResourceNotFoundErrorが作成される(self) -> None:
        """UUIDでResourceNotFoundErrorが作成されることをテスト。"""
        # Arrange
        resource_id = UUID('12345678-1234-5678-1234-567812345678')

        # Act
        error = ResourceNotFoundError('AI Tool', resource_id)

        # Assert
        assert str(error) == f'AI Tool {resource_id} が見つかりません'
