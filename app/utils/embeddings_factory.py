"""Embeddingsモデルのファクトリー。"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.config import config
from app.types import LLMProviderName


def get_embeddings_model(
    provider: LLMProviderName,
) -> OpenAIEmbeddings | GoogleGenerativeAIEmbeddings:
    """プロバイダに応じた埋め込みモデルを返す。

    Args:
        provider: 埋め込みプロバイダ。

    Returns:
        埋め込みモデル。

    Raises:
        ValueError: サポートされていないプロバイダの場合。
    """
    match provider:
        case LLMProviderName.OPENAI:
            return OpenAIEmbeddings(
                model=config.openai_embedding_model,
                api_key=SecretStr(config.openai_api_key) if config.openai_api_key else None,
                base_url=config.openai_api_base or None,
            )
        case LLMProviderName.GEMINI:
            return GoogleGenerativeAIEmbeddings(
                model=config.gemini_embedding_model,
                google_api_key=SecretStr(config.gemini_api_key) if config.gemini_api_key else None,
            )
        case _:
            raise ValueError(f'Unsupported embedding provider: {provider}')
