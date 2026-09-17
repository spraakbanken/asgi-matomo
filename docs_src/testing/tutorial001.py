"""Example showing testing of MatomoMiddleware."""

from dataclasses import dataclass
from unittest import mock

from httpx2 import AsyncClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from asgi_matomo import MatomoMiddleware


@dataclass
class MockResponse:  # ruff: ignore[undocumented-public-class]
    status_code: int
    text: str = "response"

    @property
    def is_success(self) -> bool:
        return self.status_code < 300

def create_matomo_client() -> mock.AsyncMock:  # ruff: ignore[undocumented-public-function]
    matomo_client = mock.AsyncMock(AsyncClient)
    matomo_client.post = mock.AsyncMock(return_value=MockResponse(status_code=204))
    return matomo_client


def create_app(matomo_client: AsyncClient) -> Starlette:
    """Craeates the app."""
    app = Starlette()

    app.add_middleware(
        MatomoMiddleware,
        client=matomo_client,
        matomo_url="http://trackingserver",
        idsite=12345,
    )

    def foo(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("foo")

    app.add_route("/foo", foo)
    return app


matomo_client = create_matomo_client()
app = create_app(matomo_client)


def test_app() -> None:
    """Test that the matomo_client is called."""
    client = TestClient(app)
    response = client.get("/foo")
    assert response.status_code == 200  # ruff: ignore[magic-value-comparison]

    matomo_client.post.assert_awaited()
