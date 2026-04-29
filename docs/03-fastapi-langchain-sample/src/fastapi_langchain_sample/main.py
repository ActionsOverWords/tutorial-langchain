"""FastAPI application factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastapi_langchain_sample.core.config import STATIC_DIR, get_settings
from fastapi_langchain_sample.routers import chat, health, web
from fastapi_langchain_sample.services.rag_service import RagService

logger = logging.getLogger(__name__)


def setup_logging(log_level: str) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and shut down application resources."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("애플리케이션 시작: env=%s", settings.app_env)

    rag_service = RagService(settings)
    await rag_service.initialize()
    app.state.settings = settings
    app.state.rag_service = rag_service

    yield

    logger.info("애플리케이션 종료")


def create_app() -> FastAPI:
    """Build the FastAPI app."""
    application = FastAPI(
        title="FastAPI + LangChain RAG 샘플",
        description="소득세법 문서를 검색해 한국어로 답변하는 RAG API",
        version="0.2.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    application.include_router(web.router)
    application.include_router(health.router)
    application.include_router(chat.router)
    return application


app = create_app()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert unhandled exceptions to a stable JSON response."""
    logger.error("처리되지 않은 예외 발생: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
    )
