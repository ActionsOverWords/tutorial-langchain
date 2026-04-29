# Spring AI 1.1.4 vs LangChain 상세 비교

## 전체 개요

| 항목 | Spring AI 1.1.4 | LangChain (Python) |
|------|----------------|-------------------|
| 언어 | Java / Kotlin | Python (JS/TS도 존재) |
| 설계 철학 | Spring 생태계 통합 우선 | LLM 네이티브, 모듈식 |
| 타깃 | 기존 Spring Boot 앱에 AI 추가 | AI 퍼스트 애플리케이션 |

---

## Spring AI가 지원하는 주요 기능

### 모델 지원
- **Chat**: OpenAI, Anthropic, Azure OpenAI, Gemini, Bedrock, Ollama, Mistral, Groq, DeepSeek 등
- **Embedding / Image Generation / Audio (TTS/STT) / Moderation** 지원

### 핵심 컴포넌트

| 컴포넌트 | 설명 |
|---------|------|
| **ChatClient** | Fluent API (동기 + Flux 스트리밍) |
| **Structured Output** | `@BeanOutputConverter`, JSON Schema 자동 변환 |
| **Tool Calling** | `@Tool` / `@ToolParam` 어노테이션 기반 |
| **Advisors API** | 미들웨어/인터셉터 시스템 (Spring AI 고유) |
| **MCP** | Model Context Protocol 네이티브 지원 (STDIO, HTTP/SSE) |
| **RAG ETL Pipeline** | 7종 DocumentReader + TokenTextSplitter + 20개 VectorStore |
| **Chat Memory** | InMemory, JDBC, Cassandra, Neo4j |
| **Observability** | Micrometer + Spring Boot Actuator 기반 |

### 내장 Advisors

| Advisor | 기능 |
|---------|------|
| `MessageChatMemoryAdvisor` | 대화 메모리를 메시지 컬렉션으로 프롬프트 삽입 |
| `PromptChatMemoryAdvisor` | 대화 메모리를 System 텍스트에 통합 |
| `VectorStoreChatMemoryAdvisor` | VectorStore에서 관련 메모리 검색 후 삽입 |
| `QuestionAnswerAdvisor` | 벡터 스토어 기반 Naive RAG |
| `RetrievalAugmentationAdvisor` | 모듈식 고급 RAG 아키텍처 |
| `SafeGuardAdvisor` | 유해 콘텐츠 생성 방지 |
| `SimpleLoggerAdvisor` | 요청/응답 로깅 |

### 지원 VectorStore (20개)
Apache Cassandra, Azure AI Search, Azure Cosmos DB, Chroma, Couchbase, Elasticsearch, GemFire, MariaDB, Milvus, MongoDB Atlas, Neo4j, OpenSearch, Oracle, PGvector, Pinecone, Qdrant, Redis, SAP HANA, Typesense, Weaviate, SimpleVectorStore(인메모리)

### 지원 DocumentReader (7개)
`JsonReader`, `TextReader`, `JsoupDocumentReader`, `MarkdownDocumentReader`, `PagePdfDocumentReader`, `ParagraphPdfDocumentReader`, `TikaDocumentReader`

---

## LangChain이 지원하지만 Spring AI가 미지원인 기능

### 1. LangGraph — 가장 큰 격차

| 기능 | LangGraph | Spring AI |
|------|-----------|---------|
| 상태 머신 기반 워크플로우 | 지원 | 미지원 |
| Human-in-the-Loop | 네이티브 지원 | 미지원 |
| 체크포인팅 / 영구 상태 | 네이티브 지원 | 미지원 |
| 에이전트 실행 일시 중지/재개 | 지원 | 미지원 |
| 그래프 노드 조건부 엣지 | 지원 | 미지원 |
| 시각적 그래프 디버깅 | LangSmith 연동 | 미지원 |

> Java 생태계에서는 `LangGraph4j`로 일부 대체 가능하나, Spring AI 자체 기능이 아님

---

### 2. LCEL (LangChain Expression Language)

```python
# LangChain: 파이프 연산자로 선언적 체인 구성
chain = prompt | llm | output_parser
result = chain.invoke({"topic": "AI"})
```

Spring AI의 Advisors API가 일부 유사하나, **임의 컴포넌트를 파이프로 조합하는 범용 선언적 언어는 없음**

---

### 3. Document Loader 생태계 규모

| 항목 | LangChain | Spring AI |
|------|-----------|---------|
| 지원 개수 | 115개 이상 | 7개 |
| Slack, Notion, Google Drive | 지원 | 미지원 |
| GitHub / Confluence | 지원 | 미지원 |
| YouTube Transcript | 지원 | 미지원 |
| AWS S3 / Dropbox / OneDrive | 지원 | 미지원 |
| Gmail / Outlook | 지원 | 미지원 |
| Pandas DataFrame / Jupyter | 지원 | 미지원 |
| 웹 스크레이핑 (Selenium 등 다양) | 지원 | Jsoup만 지원 |

---

### 4. Vector Store 생태계 규모

| 항목 | LangChain | Spring AI |
|------|-----------|---------|
| 지원 개수 | 100개 이상 | 20개 |
| FAISS (로컬 고성능) | 지원 | 미지원 |
| LanceDB / DuckDB | 지원 | 미지원 |
| Snowflake / Databricks | 지원 | 미지원 |
| Supabase / Vectara / Zep | 지원 | 미지원 |

---

### 5. 고급 Retriever 전략

| Retriever 전략 | LangChain | Spring AI |
|---------------|-----------|---------|
| MultiQueryRetriever (쿼리 재작성 후 다중 검색) | 지원 | 미지원 |
| EnsembleRetriever (BM25 + 벡터 하이브리드) | 지원 | 미지원 |
| ParentDocumentRetriever (부모 문서 검색) | 지원 | 미지원 |
| SelfQueryRetriever (자연어 → 필터 자동 변환) | 지원 | 미지원 |
| ContextualCompressionRetriever | 지원 | 미지원 |
| BM25Retriever (키워드 검색) | 지원 | 미지원 |
| TimeWeightedVectorStoreRetriever | 지원 | 미지원 |
| WebSearchRetriever | 지원 | 미지원 |

---

### 6. Text Splitter 다양성

| 분할기 | LangChain | Spring AI |
|--------|-----------|---------|
| RecursiveCharacterTextSplitter | 지원 | 미지원 |
| CharacterTextSplitter | 지원 | 미지원 |
| MarkdownHeaderTextSplitter | 지원 | 미지원 |
| HTMLHeaderTextSplitter | 지원 | 미지원 |
| PythonCodeTextSplitter | 지원 | 미지원 |
| LatexTextSplitter | 지원 | 미지원 |
| TokenTextSplitter | 지원 | **지원** |

---

### 7. 고급 메모리 전략

| 메모리 타입 | LangChain | Spring AI |
|-----------|-----------|---------|
| ConversationBufferMemory | 지원 | `MessageChatMemoryAdvisor`로 대응 |
| ConversationSummaryMemory (자동 요약) | 지원 | 미지원 |
| ConversationBufferWindowMemory (N턴 유지) | 지원 | 미지원 |
| VectorStoreRetrieverMemory | 지원 | `VectorStoreChatMemoryAdvisor`로 대응 |
| ConversationKGMemory (지식 그래프) | 지원 | 미지원 |
| EntityMemory (엔티티 추출) | 지원 | 미지원 |
| CombinedMemory | 지원 | 미지원 |

---

### 8. 에이전트 타입 다양성

| 에이전트 타입 | LangChain | Spring AI |
|-------------|-----------|---------|
| ReAct Agent | 지원 | 패턴으로 구현 가능 |
| OpenAI Functions/Tools Agent | 지원 | Tool Calling으로 지원 |
| XML Agent (Anthropic 최적화) | 지원 | 미지원 |
| Self-Ask with Search | 지원 | 미지원 |
| Structured Chat Agent | 지원 | 미지원 |
| AgentExecutor | 지원 | 미지원 (Agentic 패턴으로 대체) |
| MultiAgentExecutor | 지원 | A2A Protocol로 부분 지원 |

---

### 9. LangSmith — 개발/평가 플랫폼

| 기능 | LangSmith | Spring AI |
|------|-----------|---------|
| 체인 단계별 시각적 추적 | 지원 | Micrometer로 부분 지원 |
| 프롬프트 플레이그라운드 | 지원 | 미지원 |
| A/B 프롬프트 테스팅 | 지원 | 미지원 |
| 데이터셋 생성 및 평가 | 지원 | 제한적 지원 |
| 협업 디버깅 UI | 지원 | 미지원 |
| 비용 추적 (토큰/비용 대시보드) | 지원 | 토큰 메트릭만 지원 |

---

### 10. 콜백 시스템

LangChain은 모든 체인/에이전트/LLM 호출의 각 단계에 후킹 가능:

```python
class MyCallbackHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs): ...
    def on_llm_end(self, response, **kwargs): ...
    def on_tool_start(self, serialized, input_str, **kwargs): ...
    def on_chain_start(self, serialized, inputs, **kwargs): ...
    def on_agent_action(self, action, **kwargs): ...
```

Spring AI의 Advisors API는 요청/응답 인터셉션을 제공하나, **체인의 각 하위 단계별 세밀한 이벤트 후킹은 불가**

---

## 핵심 격차 3가지 요약

```
1. LangGraph 수준의 상태 기반 워크플로우 오케스트레이션
   → Human-in-the-Loop, 체크포인팅, 에이전트 일시 중지/재개

2. SaaS 데이터 소스 통합 생태계 규모
   → 115개 Document Loader (Slack, Notion, GDrive 등)

3. 고급 RAG 검색 전략
   → BM25 하이브리드, MultiQuery, ParentDocument, SelfQuery 등
```

---

## 아키텍처적 한계

- **Spring 의존성 강제**: Spring Boot Context 없이는 동작 불가. 서버리스 함수, Quarkus/Micronaut 환경에서 부적합
- **LLM 네이티브 워크플로우 부재**: LCEL과 같은 선언적 체인 언어 없음
- **LangGraph 수준의 상태 관리 부재**: 에이전트 실행의 체크포인팅, 일시 중지/재개, Human-in-the-Loop 미지원
- **긴 대화 자동 컨텍스트 압축 없음**: Summary Memory 등 고급 메모리 전략 미지원

---

## 용도별 선택 가이드

| 상황 | 추천 |
|------|------|
| 기존 Spring Boot 앱에 AI 추가 | **Spring AI** |
| 엔터프라이즈 운영 환경 (보안, 배포, 모니터링) | **Spring AI** |
| OpenAI/Claude/Gemini 주요 3사 모델만 사용 | **Spring AI** |
| 복잡한 멀티 에이전트 워크플로우 | **LangChain + LangGraph** |
| Human-in-the-Loop 필수 워크플로우 | **LangGraph** |
| 다양한 SaaS 데이터 소스 수집 | **LangChain** |
| 고급 RAG 전략 (Hybrid, MultiQuery 등) | **LangChain** |
| Python AI/ML 생태계 활용 | **LangChain** |
| 경량 서버리스/Native Image 배포 | **LangChain4j (Java)** |
| 빠른 프로토타이핑 및 실험 | **LangChain** |

---

## 참고 자료

- [Spring AI Reference Documentation](https://docs.spring.io/spring-ai/reference/index.html)
- [Spring AI GitHub Releases](https://github.com/spring-projects/spring-ai/releases)
- [LangChain Documentation](https://python.langchain.com/docs/introduction/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangGraph4j (Java)](https://github.com/langgraph4j/langgraph4j)
