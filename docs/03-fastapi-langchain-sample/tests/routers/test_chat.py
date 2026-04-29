"""Chat route tests."""

from fastapi.testclient import TestClient

from tests.conftest import FakeRagService


def test_chat_endpoint(
    client: TestClient,
    fake_rag_service: FakeRagService,
) -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "연봉 5천만원인 직장인 소득세는?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gpt-test"
    assert data["processing_time_ms"] >= 0
    assert "소득세율표" in data["answer"]
    assert data["sources"][0]["source"] == "tax_with_markdown.docx"
    assert fake_rag_service.last_message == "연봉 5천만원인 직장인 소득세는?"


def test_chat_with_stream_false(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={"message": "인적공제가 뭐야?", "stream": False},
    )

    assert response.status_code == 200


def test_chat_failure_returns_502(
    client: TestClient,
    fake_rag_service: FakeRagService,
) -> None:
    fake_rag_service.should_fail = True

    response = client.post("/api/v1/chat", json={"message": "실패 테스트"})

    assert response.status_code == 502
    assert "AI/RAG 서비스 호출" in response.json()["detail"]


def test_chat_empty_message(client: TestClient) -> None:
    response = client.post("/api/v1/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_missing_message(client: TestClient) -> None:
    response = client.post("/api/v1/chat", json={})

    assert response.status_code == 422


def test_chat_invalid_json(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        content="not-json",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 422
