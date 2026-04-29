"""Chat API routes."""

import time

from fastapi import APIRouter, Depends, HTTPException

from fastapi_langchain_sample.routers.dependencies import get_rag_service
from fastapi_langchain_sample.schemas.chat import ChatRequest, ChatResponse
from fastapi_langchain_sample.services.rag_service import RagService

router = APIRouter(prefix="/api/v1", tags=["채팅"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="소득세 RAG 질문",
)
async def chat(
    body: ChatRequest,
    service: RagService = Depends(get_rag_service),
) -> ChatResponse:
    """Answer a question using the persisted tax-law Chroma index."""
    start_time = time.perf_counter()

    try:
        result = await service.answer(body.message)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="AI/RAG 서비스 호출 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from exc

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return ChatResponse(
        answer=result.answer,
        model=service.model_name,
        processing_time_ms=round(elapsed_ms, 2),
        sources=result.sources,
    )
