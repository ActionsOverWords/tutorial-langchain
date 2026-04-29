"""Application startup tests."""

from fastapi.testclient import TestClient

from tests.conftest import FakeRagService


def test_lifespan_initializes_rag_service(
    client: TestClient,
    fake_rag_service: FakeRagService,
) -> None:
    assert client
    assert fake_rag_service.initialized is True
