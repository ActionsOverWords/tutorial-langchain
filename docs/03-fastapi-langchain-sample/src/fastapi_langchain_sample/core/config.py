"""Application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
STATIC_DIR = PACKAGE_ROOT / "static"
TEMPLATES_DIR = PACKAGE_ROOT / "templates"


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env files."""

    openai_api_key: SecretStr
    app_env: str = "development"
    log_level: str = "INFO"

    llm_model: str = "gpt-5.4-mini"
    embedding_model: str = "text-embedding-3-large"
    temperature: float = 0.2

    rag_document_path: Path = Field(
        default=REPOSITORY_ROOT / "Ch02-RAG" / "tax_with_markdown.docx"
    )
    chroma_persist_directory: Path = Field(default=SAMPLE_ROOT / "chroma")
    chroma_collection_name: str = "tax-markdown"
    chunk_size: int = 1500
    chunk_overlap: int = 200
    retriever_k: int = 4

    model_config = SettingsConfigDict(
        env_file=(REPOSITORY_ROOT / ".env", SAMPLE_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()  # type: ignore[call-arg]
