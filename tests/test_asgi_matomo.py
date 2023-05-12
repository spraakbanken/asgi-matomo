import contextlib
from typing import AsyncGenerator
from unittest import mock
from urllib.parse import parse_qs, urlsplit

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from asgi_matomo import MatomoMiddleware


def test_it_works() -> None:
    assert MatomoMiddleware is not None


@pytest.fixture(name="matomo_client")
def fixture_matomo_client():
    return mock.AsyncMock(AsyncClient)


@pytest.fixture(name="settings", scope="session")
def fixture_settings() -> dict:
    return {"idsite": 1, "base_url": "https://testserver"}


@pytest.fixture(name="app")
def create_app(matomo_client, settings: dict) -> Starlette:
    app = Starlette()

    app.add_middleware(
        MatomoMiddleware,
        client=matomo_client,
        matomo_url="http://trackingserver",
        idsite=settings["idsite"],
        exclude_paths=["/health"],
        exclude_patterns=[".*/old.*"],
    )

    async def foo(request):
        return PlainTextResponse("foo")

    async def health(request):
        return PlainTextResponse("ok")

    async def old(request):
        return PlainTextResponse("old")

    async def custom_var(request: Request):
        if "state" not in request.scope:
            request.scope["state"] = {}
        request.scope["state"]["asgi_matomo"] = {
            "e_a": "Playing",
            "pf_srv": "123",
            "cvar": {"anything": "goes"},
        }
        return PlainTextResponse("custom_var")

    async def bar(request):
        raise HTTPException(status_code=400, detail="bar")

    async def baz(request):
        data = await request.json()
        return JSONResponse({"data": data})

    app.add_route("/foo", foo)
    app.add_route("/bar", bar)
    app.add_route("/health", health)
    app.add_route("/some/old/path", old)
    app.add_route("/old/path", old)
    app.add_route("/really/old", old)
    app.add_route("/set/custom/var", custom_var)
    app.add_route("/baz", baz, methods=["POST"])
    return app


@pytest.fixture(name="expected_q")
def fixture_expected_q(settings: dict) -> dict:
    return {
        "idsite": [str(settings["idsite"])],
        "url": [settings["base_url"]],
        "apiv": ["1"],
        # "lang": ["None"]
        "rec": ["1"],
        "ua": ["python-httpx/0.24.0"],
        "send_image": ["0"],
        "cvar": ['{"http_status_code": 200, "http_method": "GET"}'],
    }


@pytest_asyncio.fixture(name="client")
async def fixture_client(app: Starlette) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_foo(
    client: AsyncClient, matomo_client, expected_q: dict
):
    response = await client.get("/foo")
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/foo"
    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_bar(
    client: AsyncClient, matomo_client, expected_q: dict
):
    with contextlib.suppress(ValueError):
        _response = await client.get("/bar")
    # assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/bar"
    expected_q["cvar"][0] = expected_q["cvar"][0].replace("200", "400")

    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_custom_var(
    client: AsyncClient, matomo_client, expected_q: dict
):
    with contextlib.suppress(ValueError):
        _response = await client.get("/set/custom/var")
    # assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/set/custom/var"
    expected_q["e_a"] = ["Playing"]
    expected_q["pf_srv"] = ["123"]
    expected_q["cvar"] = [
        '{"http_status_code": 200, "http_method": "GET", "anything": "goes"}'
    ]

    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_matomo_client_doesnt_gets_called_on_get_health(
    client: AsyncClient,
    matomo_client,
):
    response = await client.get("/health")
    assert response.status_code == 200

    matomo_client.get.assert_not_awaited()


@pytest.mark.parametrize("path", ["/some/old/path", "/old/path", "/really/old"])
@pytest.mark.asyncio
async def test_matomo_client_doesnt_gets_called_on_get_old(
    client: AsyncClient, matomo_client, path: str
):
    response = await client.get(path)
    assert response.status_code == 200

    matomo_client.get.assert_not_awaited()


def assert_query_string(url: str, expected_q: dict) -> None:
    urlparts = urlsplit(url[6:-2])
    q = parse_qs(urlparts.query)
    assert q.pop("rand") is not None
    assert q.pop("gt_ms") is not None

    assert q == expected_q


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_post_baz(
    client: AsyncClient, matomo_client, expected_q: dict
):
    response = await client.post("/baz", json={"data": "content"})
    assert response.status_code == 200

    expected_q["url"][0] += "/baz"
    expected_q["cvar"][0] = expected_q["cvar"][0].replace("GET", "POST")
    matomo_client.get.assert_awaited()

    assert_query_string(str(matomo_client.get.await_args), expected_q)


# @pytest.mark.asyncio
# async def test_matomo_client_gets_called_on_get_bar(client: AsyncClient, matomo_client):
#     try:
#         response = await client.get("/bar")
#     except ValueError:
#         pass
#     # assert response.status_code == 200

#     matomo_client.get.assert_awaited_with("http://trackingserver?")
