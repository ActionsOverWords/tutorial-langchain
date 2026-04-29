FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Layer 1: 시스템 패키지 (가장 드물게 변경)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: 의존성 설치 (src 코드와 분리 → 캐시 활용)
COPY docs/03-fastapi-langchain-sample/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Layer 3: 패키지 메타데이터 + 소스 코드 (자주 변경)
COPY docs/03-fastapi-langchain-sample/pyproject.toml ./
COPY docs/03-fastapi-langchain-sample/README.md ./
COPY docs/03-fastapi-langchain-sample/src ./src
RUN pip install --no-cache-dir -e . --no-deps

# Layer 4: 데이터 파일
COPY Ch02-RAG/tax_with_markdown.docx /data/tax_with_markdown.docx

ENV RAG_DOCUMENT_PATH=/data/tax_with_markdown.docx \
    CHROMA_PERSIST_DIRECTORY=/data/chroma \
    APP_ENV=production

EXPOSE 8000

CMD ["uvicorn", "fastapi_langchain_sample.main:app", "--host", "0.0.0.0", "--port", "8000"]
