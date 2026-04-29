"""Health and metadata routes."""

from fastapi import APIRouter, Depends, Request

from fastapi_langchain_sample.routers.dependencies import get_rag_service
from fastapi_langchain_sample.schemas.chat import HealthResponse
from fastapi_langchain_sample.services.rag_service import RagService

router = APIRouter(prefix="/api/v1", tags=["모니터링"])


@router.get("/info", summary="API 정보", tags=["정보"])
async def info() -> dict[str, str]:
    """Return basic API metadata."""
    return {
        "name": "FastAPI + LangChain RAG 샘플",
        "version": "0.2.0",
        "description": "소득세법 문서를 검색해 답변하는 RAG API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="헬스체크",
)
async def health_check(
    request: Request,
    service: RagService = Depends(get_rag_service),
) -> HealthResponse:
    """Return server and vector index status."""
    settings = request.app.state.settings
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        environment=settings.app_env,
        indexed_documents=service.indexed_document_count(),
    )
