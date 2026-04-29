"""Health route tests."""

from fastapi.testclient import TestClient


def test_info(client: TestClient) -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.2.0"
    assert data["health"] == "/api/v1/health"


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "healthy",
        "version": "0.2.0",
        "environment": "test",
        "indexed_documents": 12,
    }
