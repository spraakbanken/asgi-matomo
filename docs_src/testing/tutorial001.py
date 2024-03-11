import contextlib
import time
from dataclasses import dataclass
from typing import AsyncGenerator
from unittest import mock
from urllib.parse import parse_qs, urlsplit

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker
from httpx import AsyncClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.testclient import TestClient


@dataclass
class MockResponse:
    status_code: int
    text: str = "response"


def create_matomo_client():
    matomo_client = mock.AsyncMock(AsyncClient)
    matomo_client.post = mock.AsyncMock(return_value=MockResponse(status_code=204))
    return matomo_client


def create_app(matomo_client) -> Starlette:
    app = Starlette()

    app.add_middleware(
        MatomoMiddleware,
        client=matomo_client,
        matomo_url="http://trackingserver",
        idsite=12345,
    )

    async def foo(request):
        return PlainTextResponse("foo")

    app.add_route("/foo", foo)
    return app


matomo_client = create_matomo_client()
app = create_app(matomo_client)


def test_app():
    client = TestClient(app)
    response = client.get("/foo")
    assert response.status_code == 200  # noqa: S101

    matomo_client.post.assert_awaited()
