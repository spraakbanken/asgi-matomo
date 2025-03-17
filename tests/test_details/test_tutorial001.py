from starlette.testclient import TestClient

from docs_src.details.tutorial001 import app


def test_app() -> None:
    client = TestClient(app)
    response = client.get("/foo")
    assert response.status_code == 200

    assert response.json() == {"name": "foo"}
