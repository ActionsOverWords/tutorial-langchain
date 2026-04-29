"""RAG service backed by Chroma and OpenAI models."""

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fastapi_langchain_sample.core.config import Settings
from fastapi_langchain_sample.schemas.chat import SourceDocument

logger = logging.getLogger(__name__)

USER_DICTIONARY = ["사람을 나타내는 표현 -> 거주자"]

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "아래 context를 참고해서 한국어로 답변하세요.\n"
            "context에 근거가 부족하면 부족하다고 말하고, 임의로 꾸며내지 마세요.\n"
            "세금 계산이 필요한 경우 관련 조문 또는 세율표를 근거로 계산 과정을 간단히 보여주세요.\n\n"
            "{context}",
        ),
        ("human", "{input}"),
    ]
)

DICTIONARY_PROMPT = ChatPromptTemplate.from_template(
    """
사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
만약 변경할 필요가 없다고 판단되면, 사용자의 질문을 그대로 응답합니다.

사전: {dictionary}
질문: {input}
""".strip()
)


@dataclass(frozen=True)
class RagAnswer:
    """Answer plus retrieved source documents."""

    answer: str
    sources: list[SourceDocument]


class RagService:
    """Load the tax document once, persist it in Chroma, and answer questions."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
        self._database = Chroma(
            embedding_function=self._embeddings,
            persist_directory=str(settings.chroma_persist_directory),
            collection_name=settings.chroma_collection_name,
        )
        self._chain: Runnable[dict[str, str], dict[str, Any]] | None = None

    @property
    def model_name(self) -> str:
        return self._settings.llm_model

    def indexed_document_count(self) -> int:
        """Return the number of vectors persisted in Chroma."""
        return int(self._database._collection.count())  # noqa: SLF001

    async def initialize(self) -> None:
        """Ensure the Chroma collection exists and build the retrieval chain."""
        indexed_count = self.indexed_document_count()
        if indexed_count > 0:
            logger.info("Chroma 인덱스가 이미 존재합니다. 적재를 스킵합니다: %s개", indexed_count)
        else:
            await self._index_source_document()

        self._chain = self._create_chain()

    async def answer(self, message: str) -> RagAnswer:
        """Answer a user question using the retrieval chain."""
        if self._chain is None:
            raise RuntimeError("RAG service is not initialized")

        result = await self._chain.ainvoke({"input": message})
        return RagAnswer(
            answer=str(result["answer"]),
            sources=self._to_source_documents(result.get("context", [])),
        )

    async def _index_source_document(self) -> None:
        document_path = self._settings.rag_document_path
        if not document_path.exists():
            raise FileNotFoundError(f"RAG source document not found: {document_path}")

        logger.info("문서를 읽어 Chroma에 저장합니다: %s", document_path)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )
        loader = Docx2txtLoader(str(document_path))
        documents = await loader.aload()
        chunks = splitter.split_documents(documents)

        if not chunks:
            raise RuntimeError(f"No document chunks were created from {document_path}")

        self._database.add_documents(chunks)
        logger.info("Chroma 저장 완료: %s개 문서 조각", len(chunks))

    def _create_chain(self) -> Runnable[dict[str, str], dict[str, Any]]:
        llm = ChatOpenAI(
            model=self._settings.llm_model,
            api_key=self._settings.openai_api_key,
            temperature=self._settings.temperature,
        )
        dictionary_chain = DICTIONARY_PROMPT.partial(dictionary=USER_DICTIONARY) | llm | StrOutputParser()
        retriever = self._database.as_retriever(
            search_kwargs={"k": self._settings.retriever_k}
        )
        combine_chain = create_stuff_documents_chain(llm, ANSWER_PROMPT)
        retrieval_chain = create_retrieval_chain(retriever, combine_chain)
        chain = {"input": dictionary_chain} | retrieval_chain
        return cast(Runnable[dict[str, str], dict[str, Any]], chain)

    def _to_source_documents(self, documents: Sequence[Document]) -> list[SourceDocument]:
        sources: list[SourceDocument] = []
        for document in documents:
            source = str(document.metadata.get("source", self._settings.rag_document_path))
            sources.append(
                SourceDocument(
                    source=Path(source).name,
                    page_content=document.page_content[:600],
                )
            )
        return sources
