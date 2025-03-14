from starlette.testclient import TestClient

from docs_src.details.tutorial003 import app


def test_app() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200

    assert response.json() == {"data": 4000}
