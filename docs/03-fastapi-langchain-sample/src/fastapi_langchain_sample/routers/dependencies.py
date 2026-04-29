"""Shared FastAPI route dependencies."""

from fastapi import Request

from fastapi_langchain_sample.services.rag_service import RagService


def get_rag_service(request: Request) -> RagService:
    """Return the RAG service initialized during application startup."""
    service = request.app.state.rag_service
    if not isinstance(service, RagService):
        raise RuntimeError("RAG service is not configured")
    return service
