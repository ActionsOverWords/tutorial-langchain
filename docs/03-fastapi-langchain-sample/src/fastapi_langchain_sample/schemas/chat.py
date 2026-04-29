"""Request and response schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """User question request."""

    message: str = Field(..., min_length=1, description="질문 메시지")
    stream: bool = Field(default=False, description="스트리밍 응답 여부 (현재 미지원)")


class SourceDocument(BaseModel):
    """A retrieved document snippet used by the RAG answer."""

    source: str = Field(..., description="원본 문서 경로")
    page_content: str = Field(..., description="검색된 문서 일부")


class ChatResponse(BaseModel):
    """RAG chat response."""

    answer: str = Field(..., description="AI 답변")
    model: str = Field(..., description="사용된 LLM 모델명")
    processing_time_ms: float = Field(..., description="처리 시간 (밀리초)")
    sources: list[SourceDocument] = Field(default_factory=list, description="참고 문서")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="서버 상태")
    version: str = Field(..., description="애플리케이션 버전")
    environment: str = Field(..., description="실행 환경")
    indexed_documents: int = Field(..., description="Chroma에 저장된 문서 조각 수")
