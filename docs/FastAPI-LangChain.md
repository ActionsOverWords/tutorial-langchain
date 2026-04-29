# FastAPI + LangChain 연동 가이드

## 프레임워크 비교

```
Spring 생태계          Python 생태계
─────────────────     ─────────────────
Spring MVC        ↔   FastAPI
Spring AI         ↔   LangChain
Spring Boot       ↔   uvicorn + FastAPI
```

**핵심 차이점**: Spring AI는 Spring과 강하게 결합되어 있지만, LangChain은 그냥 **Python 라이브러리**입니다.
FastAPI에서 `import`만 하면 됩니다. 별도의 스타터나 자동설정 같은 게 필요 없습니다.

---

## 연동 방법

### 1. 기본 구조

```python
# main.py
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# LangChain 체인을 FastAPI 앱 레벨에서 초기화 (싱글톤)
llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_template("Tell me about {topic}")
chain = prompt | llm | StrOutputParser()

@app.post("/chat")
async def chat(topic: str):
    result = await chain.ainvoke({"topic": topic})  # async 호출
    return {"response": result}
```

---

### 2. Request/Response 모델 (Pydantic)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

# 요청/응답 모델 정의
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    tokens_used: int

llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{message}")
])
chain = prompt | llm

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await chain.ainvoke({"message": request.message})
    return ChatResponse(
        answer=response.content,
        tokens_used=response.usage_metadata["total_tokens"]
    )
```

---

### 3. Streaming 응답 (핵심 패턴)

LangChain의 `astream()` + FastAPI의 `StreamingResponse` 조합입니다.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()
llm = ChatOpenAI(model="gpt-4o", streaming=True)
prompt = ChatPromptTemplate.from_template("{question}")
chain = prompt | llm

async def token_generator(question: str):
    async for chunk in chain.astream({"question": question}):
        yield chunk.content  # 토큰 단위로 스트리밍

@app.get("/stream")
async def stream_chat(question: str):
    return StreamingResponse(
        token_generator(question),
        media_type="text/event-stream"
    )
```

---

### 4. 대화 메모리 (세션 관리)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

app = FastAPI()

# 세션별 메모리 저장소
session_store: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# 대화 기록을 포함하는 프롬프트
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),  # 대화 기록 삽입
    ("human", "{message}"),
])

chain = prompt | ChatOpenAI(model="gpt-4o")

# 메모리가 붙은 체인
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="message",
    history_messages_key="history",
)

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await chain_with_history.ainvoke(
        {"message": request.message},
        config={"configurable": {"session_id": request.session_id}}
    )
    return {"response": response.content}
```

---

### 5. 의존성 주입 (FastAPI Depends)

Spring의 `@Autowired`에 대응하는 패턴입니다.

```python
from fastapi import FastAPI, Depends
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from functools import lru_cache

app = FastAPI()

# 싱글톤으로 관리할 리소스들
@lru_cache()
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model="gpt-4o", temperature=0)

@lru_cache()
def get_vector_store() -> VectorStore:
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=OpenAIEmbeddings()
    )

# RAG 엔드포인트
@app.post("/rag")
async def rag_query(
    question: str,
    llm: ChatOpenAI = Depends(get_llm),
    vector_store: VectorStore = Depends(get_vector_store),
):
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = await retriever.ainvoke(question)
    context = "\n".join([doc.page_content for doc in docs])

    response = await llm.ainvoke(
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    return {"answer": response.content}
```

---

### 6. LangServe — 가장 빠른 방법

LangChain이 공식 제공하는 FastAPI 자동 라우터입니다. 체인을 REST API로 **자동 노출**합니다.

```python
# pip install langserve
from fastapi import FastAPI
from langserve import add_routes
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

chain = (
    ChatPromptTemplate.from_template("Tell me about {topic}")
    | ChatOpenAI(model="gpt-4o")
)

# 체인을 /chat 경로로 자동 노출
add_routes(app, chain, path="/chat")

# 자동으로 생성되는 엔드포인트:
# POST /chat/invoke       → 단일 호출
# POST /chat/batch        → 배치 호출
# POST /chat/stream       → 스트리밍
# GET  /chat/playground   → 웹 UI 플레이그라운드
```

---

## 전체 프로젝트 구조 (권장)

```
my-project/
├── main.py                # FastAPI 앱 진입점
├── api/
│   ├── chat.py            # 채팅 라우터
│   └── rag.py             # RAG 라우터
├── chains/
│   ├── chat_chain.py      # LangChain 체인 정의
│   └── rag_chain.py       # RAG 체인 정의
├── dependencies.py        # FastAPI Depends 공통 의존성
└── config.py              # 환경 설정
```

```python
# main.py
from fastapi import FastAPI
from api import chat, rag

app = FastAPI(title="LangChain API")
app.include_router(chat.router, prefix="/chat")
app.include_router(rag.router, prefix="/rag")
```

---

## 핵심 포인트 요약

| 역할 | 담당 |
|------|------|
| HTTP 라우팅, 요청/응답 처리 | **FastAPI** |
| LLM 호출, 프롬프트, 체인 | **LangChain** |
| 데이터 유효성 검사 (공통) | **Pydantic** (둘 다 사용) |
| 스트리밍 | FastAPI `StreamingResponse` + LangChain `astream()` |
| 세션/메모리 관리 | LangChain `RunnableWithMessageHistory` |
| 빠른 API 노출 | **LangServe** `add_routes()` |

---

## Spring과의 대응 관계

| Spring | FastAPI + LangChain |
|--------|---------------------|
| `@RestController` | `@app.post("/path")` |
| `@Autowired` | `Depends()` |
| `@Service` (싱글톤 빈) | `@lru_cache()` |
| `@Bean` | 모듈 레벨 초기화 |
| Spring AI `ChatClient` | LangChain `chain.ainvoke()` |
| Spring AI Advisors | LangChain `RunnableWithMessageHistory` |
| Spring AI Streaming (`Flux`) | FastAPI `StreamingResponse` + `astream()` |
