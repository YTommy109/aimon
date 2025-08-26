"""エラークラスのテスト。"""

from uuid import uuid4

from app.errors import (
    APIConfigurationError,
    LLMAPICallError,
    LLMError,
    LLMUnexpectedResponseError,
    MissingConfigError,
    PathIsDirectoryError,
    ProjectNotFoundError,
    ProviderInitializationError,
    ResourceNotFoundError,
    ValidationError,
)
from app.types import ProjectID


class TestErrorClasses:
    """エラークラスのテストクラス。"""

    def test_APIConfigurationErrorがExceptionを継承している(self) -> None:
        """APIConfigurationErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(APIConfigurationError, Exception)

    def test_APIConfigurationErrorのメッセージが正しい(self) -> None:
        """APIConfigurationErrorのメッセージが正しいことをテスト。"""
        # Arrange
        message = 'API設定エラー'

        # Act
        error = APIConfigurationError(message)

        # Assert
        assert 'APIの設定が不正です' in str(error)
        assert message in str(error)

    def test_PathIsDirectoryErrorがExceptionを継承している(self) -> None:
        """PathIsDirectoryErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(PathIsDirectoryError, Exception)

    def test_PathIsDirectoryErrorのメッセージが正しい(self) -> None:
        """PathIsDirectoryErrorのメッセージが正しいことをテスト。"""
        # Arrange
        path = '/path/to/directory'

        # Act
        error = PathIsDirectoryError(path)

        # Assert
        assert 'パス' in str(error)
        assert path in str(error)
        assert 'ディレクトリ' in str(error)

    def test_ResourceNotFoundErrorがExceptionを継承している(self) -> None:
        """ResourceNotFoundErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(ResourceNotFoundError, Exception)

    def test_文字列IDでResourceNotFoundErrorが作成される(self) -> None:
        """文字列IDでResourceNotFoundErrorが作成されることをテスト。"""
        # Arrange
        resource_type = 'Project'
        resource_id = ProjectID(uuid4())

        # Act
        error = ResourceNotFoundError(resource_type, resource_id)

        # Assert
        assert resource_type in str(error)
        assert str(resource_id) in str(error)
        assert '見つかりません' in str(error)

    def test_ProjectIDでResourceNotFoundErrorが作成される(self) -> None:
        """ProjectIDでResourceNotFoundErrorが作成されることをテスト。"""
        # Arrange
        resource_type = 'Project'
        project_id = ProjectID(uuid4())

        # Act
        error = ResourceNotFoundError(resource_type, project_id)

        # Assert
        assert resource_type in str(error)
        assert str(project_id) in str(error)
        assert '見つかりません' in str(error)

    def test_ProjectNotFoundErrorがResourceNotFoundErrorを継承している(self) -> None:
        """ProjectNotFoundErrorがResourceNotFoundErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(ProjectNotFoundError, ResourceNotFoundError)

    def test_ProjectNotFoundErrorのメッセージが正しい(self) -> None:
        """ProjectNotFoundErrorのメッセージが正しいことをテスト。"""
        # Arrange
        project_id = ProjectID(uuid4())

        # Act
        error = ProjectNotFoundError(project_id)

        # Assert
        assert 'Project' in str(error)
        assert str(project_id) in str(error)
        assert '見つかりません' in str(error)

    def test_ValidationErrorがExceptionを継承している(self) -> None:
        """ValidationErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(ValidationError, Exception)

    def test_ValidationErrorのメッセージが正しい(self) -> None:
        """ValidationErrorのメッセージが正しいことをテスト。"""
        # Arrange
        message = 'バリデーションエラー'

        # Act
        error = ValidationError(message)

        # Assert
        assert str(error) == message

    def test_MissingConfigErrorがExceptionを継承している(self) -> None:
        """MissingConfigErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(MissingConfigError, Exception)

    def test_MissingConfigErrorのメッセージが正しい(self) -> None:
        """MissingConfigErrorのメッセージが正しいことをテスト。"""
        # Arrange
        config_key = 'API_KEY'

        # Act
        error = MissingConfigError(config_key)

        # Assert
        assert '必須設定が不足しています' in str(error)

    def test_LLMErrorがExceptionを継承している(self) -> None:
        """LLMErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(LLMError, Exception)

    def test_LLMErrorのメッセージが正しい(self) -> None:
        """LLMErrorのメッセージが正しいことをテスト。"""
        # Arrange
        message = 'LLMエラー'
        provider = 'openai'
        model = 'gpt-3.5-turbo'

        # Act
        error = LLMError(message, provider, model)

        # Assert
        assert str(error) == message

    def test_LLMAPICallErrorがLLMErrorを継承している(self) -> None:
        """LLMAPICallErrorがLLMErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(LLMAPICallError, LLMError)

    def test_LLMAPICallErrorのメッセージが正しい(self) -> None:
        """LLMAPICallErrorのメッセージが正しいことをテスト。"""
        # Arrange
        provider = 'openai'
        model = 'gpt-3.5-turbo'

        # Act
        error = LLMAPICallError(provider, model)

        # Assert
        assert 'OpenAI API呼び出しエラー' in str(error)

    def test_LLMUnexpectedResponseErrorがLLMErrorを継承している(self) -> None:
        """LLMUnexpectedResponseErrorがLLMErrorを継承していることをテスト。"""
        # Assert
        assert issubclass(LLMUnexpectedResponseError, LLMError)

    def test_LLMUnexpectedResponseErrorのメッセージが正しい(self) -> None:
        """LLMUnexpectedResponseErrorのメッセージが正しいことをテスト。"""
        # Arrange
        provider = 'openai'
        model = 'gpt-3.5-turbo'

        # Act
        error = LLMUnexpectedResponseError(provider, model)

        # Assert
        assert 'Unexpected response format' in str(error)
        assert provider in str(error)

    def test_ProviderInitializationErrorがExceptionを継承している(self) -> None:
        """ProviderInitializationErrorがExceptionを継承していることをテスト。"""
        # Assert
        assert issubclass(ProviderInitializationError, Exception)

    def test_ProviderInitializationErrorのメッセージが正しい(self) -> None:
        """ProviderInitializationErrorのメッセージが正しいことをテスト。"""
        # Act
        error = ProviderInitializationError()

        # Assert
        assert 'プロバイダの初期化に失敗しました' in str(error)
