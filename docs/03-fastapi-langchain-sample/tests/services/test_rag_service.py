"""Unit tests for RAG service helpers."""

from pathlib import Path
from typing import Any, cast

import pytest
from langchain_core.documents import Document
from pydantic import SecretStr

from fastapi_langchain_sample.core.config import Settings
from fastapi_langchain_sample.services.rag_service import RagService


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        openai_api_key=SecretStr("sk-test-dummy-key-for-testing"),
        app_env="test",
        rag_document_path=tmp_path / "tax_with_markdown.docx",
        chroma_persist_directory=tmp_path / "chroma",
    )


def test_model_name_uses_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        RagService,
        "__init__",
        lambda self, settings: setattr(self, "_settings", settings),
    )
    service = RagService(make_settings(tmp_path))

    assert service.model_name == "gpt-5.4-mini"


def test_to_source_documents(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        RagService,
        "__init__",
        lambda self, settings: setattr(self, "_settings", settings),
    )
    service = RagService(make_settings(tmp_path))
    documents = [
        Document(
            page_content="가" * 700,
            metadata={"source": "/tmp/tax_with_markdown.docx"},
        )
    ]

    sources = service._to_source_documents(documents)  # noqa: SLF001

    assert sources[0].source == "tax_with_markdown.docx"
    assert len(sources[0].page_content) == 600


@pytest.mark.asyncio
async def test_answer_requires_initialization(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_init(self: RagService, settings: Settings) -> None:
        self._settings = settings
        self._chain = None

    monkeypatch.setattr(RagService, "__init__", fake_init)
    service = RagService(make_settings(tmp_path))

    with pytest.raises(RuntimeError, match="not initialized"):
        await service.answer("질문")


@pytest.mark.asyncio
async def test_answer_maps_chain_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeChain:
        async def ainvoke(self, payload: dict[str, str]) -> dict[str, Any]:
            assert payload == {"input": "질문"}
            return {
                "answer": "답변",
                "context": [Document(page_content="근거", metadata={"source": "tax.docx"})],
            }

    def fake_init(self: RagService, settings: Settings) -> None:
        self._settings = settings
        self._chain = cast(Any, FakeChain())

    monkeypatch.setattr(RagService, "__init__", fake_init)
    service = RagService(make_settings(tmp_path))

    result = await service.answer("질문")

    assert result.answer == "답변"
    assert result.sources[0].source == "tax.docx"
