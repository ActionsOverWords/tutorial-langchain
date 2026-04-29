"""Web route tests."""

from fastapi.testclient import TestClient


def test_index_returns_chat_ui(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "소득세 RAG 챗봇" in response.text
    assert "/static/styles.css" in response.text
    assert "/static/app.js" in response.text
