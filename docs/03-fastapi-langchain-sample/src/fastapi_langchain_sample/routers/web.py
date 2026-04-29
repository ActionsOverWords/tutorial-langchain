"""Web page routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi_langchain_sample.core.config import TEMPLATES_DIR

router = APIRouter(tags=["웹"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse, summary="웹 채팅 화면")
async def index(request: Request) -> HTMLResponse:
    """Render the browser chat UI."""
    return templates.TemplateResponse(request, "index.html")
