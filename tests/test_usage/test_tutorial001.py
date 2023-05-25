from starlette.testclient import TestClient

from docs_src.usage.tutorial001 import app


def test_app():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
