"""Shared pytest fixtures."""

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from fastapi_langchain_sample.core.config import Settings, get_settings
from fastapi_langchain_sample.schemas.chat import SourceDocument
from fastapi_langchain_sample.services.rag_service import RagAnswer, RagService


class FakeRagService(RagService):
    """Small test double that avoids OpenAI and Chroma."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.initialized = False
        self.should_fail = False
        self.last_message: str | None = None

    @property
    def model_name(self) -> str:
        return self.settings.llm_model

    def indexed_document_count(self) -> int:
        return 12

    async def initialize(self) -> None:
        self.initialized = True

    async def answer(self, message: str) -> RagAnswer:
        self.last_message = message
        if self.should_fail:
            raise RuntimeError("forced failure")
        return RagAnswer(
            answer="연봉 5천만원은 과세표준 산정 후 소득세율표를 적용해야 합니다.",
            sources=[
                SourceDocument(
                    source="tax_with_markdown.docx",
                    page_content="제55조(세율) 종합소득 과세표준...",
                )
            ],
        )


@pytest.fixture
def mock_settings(tmp_path) -> Settings:  # type: ignore[no-untyped-def]
    """Return settings that do not depend on a real .env file."""
    return Settings(
        openai_api_key=SecretStr("sk-test-dummy-key-for-testing"),
        app_env="test",
        log_level="DEBUG",
        llm_model="gpt-test",
        rag_document_path=tmp_path / "tax_with_markdown.docx",
        chroma_persist_directory=tmp_path / "chroma",
    )


@pytest.fixture
def fake_rag_service(mock_settings: Settings) -> FakeRagService:
    """Return the service double used by the app lifespan."""
    return FakeRagService(mock_settings)


@pytest.fixture
def client(
    mock_settings: Settings,
    fake_rag_service: FakeRagService,
) -> Iterator[TestClient]:
    """Return a FastAPI TestClient with external services mocked."""
    get_settings.cache_clear()
    with (
        patch("fastapi_langchain_sample.main.get_settings", return_value=mock_settings),
        patch("fastapi_langchain_sample.main.RagService", return_value=fake_rag_service),
    ):
        from fastapi_langchain_sample.main import app

        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client

    get_settings.cache_clear()
