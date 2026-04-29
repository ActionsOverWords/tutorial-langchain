# FastAPI + LangChain RAG 샘플

`Ch02-RAG/tax_with_markdown.docx` 소득세법 문서를 Chroma에 저장하고, 웹 화면과 REST API에서 질문에 답변하는 FastAPI 샘플입니다.

## 구조

FastAPI의 큰 애플리케이션 구성에서 자주 쓰는 `routers`, `schemas`, `services`, `core` 방식으로 모듈을 나눴습니다.

```text
src/fastapi_langchain_sample/
├── routers/                   # APIRouter 단위의 HTTP route
│   ├── web.py                 # 웹 화면 route
│   ├── health.py              # 상태 확인, API 정보 route
│   ├── chat.py                # 질문 API route
│   └── dependencies.py        # route 공통 의존성
├── core/config.py             # 환경변수, 경로, 모델 설정
├── schemas/chat.py            # Pydantic request/response schema
├── services/rag_service.py    # 문서 적재, Chroma, LangChain RAG 로직
├── templates/index.html       # Jinja2 HTML 템플릿
├── static/styles.css          # 화면 스타일
├── static/app.js              # 브라우저 이벤트/API 호출
└── main.py                    # FastAPI 앱 생성, router 등록, startup 처리
```

테스트도 같은 축으로 나눴습니다.

```text
tests/
├── conftest.py                # 공통 fixture, 테스트용 RAG service
├── routers/                   # HTTP route 테스트
│   ├── test_web.py
│   ├── test_health.py
│   ├── test_chat.py
│   └── test_app_lifespan.py
└── services/
    └── test_rag_service.py    # RAG service 단위 테스트
```

## 동작 방식

1. FastAPI 시작 시 Chroma 컬렉션 `tax-markdown`을 확인합니다.
2. 저장된 벡터가 있으면 문서 적재를 스킵합니다.
3. 비어 있으면 `Ch02-RAG/tax_with_markdown.docx`를 읽고 `1500/200` 단위로 split한 뒤 Chroma에 저장합니다.
4. 질문은 노트북 `Ch02-RAG/2.1. rag-with-chroma.ipynb`와 같은 흐름으로 dictionary chain을 거친 뒤 retrieval chain이 답변합니다.

기본 모델은 비용 대비 성능을 고려해 `gpt-5.4-mini`로 설정했습니다. `gpt-4o`를 쓰려면 `.env`에서 `LLM_MODEL=gpt-4o`로 바꾸면 됩니다. 임베딩은 노트북과 동일하게 `text-embedding-3-large`입니다.

## 로컬 실행

처음 한 번은 샘플 디렉터리로 이동한 뒤 의존성을 설치합니다.

```bash
cd docs/03-fastapi-langchain-sample
uv pip install -e ".[dev]"
```

서버를 시작합니다.

```bash
uvicorn fastapi_langchain_sample.main:app --reload --port 8000
```

명령어 의미는 다음과 같습니다.

- `fastapi_langchain_sample.main:app`: `main.py` 안의 FastAPI 앱 객체를 실행합니다.
- `--reload`: 개발 중 파일이 바뀌면 서버를 자동 재시작합니다.
- `--port 8000`: 8000번 포트에서 서버를 엽니다.

환경변수는 저장소 루트의 `.env` 또는 이 샘플의 `.env`에서 읽습니다.

```dotenv
OPENAI_API_KEY=sk-...
APP_ENV=development
LOG_LEVEL=INFO
LLM_MODEL=gpt-5.4-mini
EMBEDDING_MODEL=text-embedding-3-large
```

브라우저 화면: http://127.0.0.1:8000/  
Swagger UI: http://127.0.0.1:8000/docs

### 실행 확인

서버가 정상 시작되면 터미널에 대략 아래 로그가 보입니다.

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

최초 실행 시에는 `tax_with_markdown.docx`를 읽고 Chroma에 저장합니다.

```text
문서를 읽어 Chroma에 저장합니다: .../Ch02-RAG/tax_with_markdown.docx
Chroma 저장 완료: 225개 문서 조각
```

이미 저장된 내역이 있으면 다음 실행부터는 적재를 스킵합니다.

```text
Chroma 인덱스가 이미 존재합니다. 적재를 스킵합니다: 225개
```

터미널에서 API만 확인하고 싶으면 다음 명령을 실행합니다.

```bash
curl http://127.0.0.1:8000/api/v1/health
```

질문 API를 직접 호출하려면 다음처럼 실행합니다.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "연봉 5천만원인 직장인 소득세는?"}'
```

### 서버 중지

`uvicorn`을 실행 중인 터미널에서 `Ctrl + C`를 누르면 서버가 중지됩니다.

```text
^C
Application shutdown complete.
```

백그라운드에서 실행했거나 8000번 포트가 이미 사용 중이라는 에러가 나면 실행 중인 프로세스를 확인합니다.

```bash
lsof -i :8000
```

출력의 `PID`를 확인한 뒤 종료합니다.

```bash
kill <PID>
```

예를 들어 PID가 `12345`라면 다음과 같습니다.

```bash
kill 12345
```

### 자주 쓰는 개발 명령어

```bash
# 샘플 디렉터리 이동
cd docs/03-fastapi-langchain-sample

# 의존성 설치 또는 갱신
uv pip install -e ".[dev]"

# 개발 서버 시작
uvicorn fastapi_langchain_sample.main:app --reload --port 8000

# 테스트 실행
pytest -v

# 타입 체크
mypy src/fastapi_langchain_sample tests
```

### 흔한 문제

`Address already in use`가 나오면 이미 8000번 포트를 쓰는 서버가 떠 있는 상태입니다. `Ctrl + C`로 기존 서버를 끄거나, 다른 포트로 실행합니다.

```bash
uvicorn fastapi_langchain_sample.main:app --reload --port 8001
```

`OPENAI_API_KEY` 관련 오류가 나오면 저장소 루트의 `.env` 또는 이 샘플 디렉터리의 `.env`에 키가 있는지 확인합니다.

```dotenv
OPENAI_API_KEY=sk-...
```

Chroma 인덱스를 처음부터 다시 만들고 싶으면 서버를 중지한 뒤 샘플 디렉터리의 `chroma/` 폴더를 삭제하고 서버를 다시 시작합니다. 이 폴더는 런타임 산출물이라 Git에 커밋하지 않습니다.

## 테스트

테스트는 OpenAI와 Chroma를 모킹합니다.

```bash
pytest -v
mypy src/fastapi_langchain_sample tests
```

`pytest`는 `--cov-fail-under=80`으로 80% 미만이면 실패하도록 설정되어 있습니다.

## Docker

Docker 빌드는 저장소 루트에서 실행합니다. 문서 파일을 이미지에 포함하기 위해 빌드 컨텍스트가 저장소 루트여야 합니다.

```bash
docker build -f docs/03-fastapi-langchain-sample/Dockerfile -t fastapi-langchain-rag .
docker run --rm -p 8000:8000 --env-file .env fastapi-langchain-rag
```

운영에서는 `/data/chroma`를 볼륨으로 마운트하면 재배포 후에도 Chroma 인덱스를 재사용할 수 있습니다.
