import contextlib
import time
import typing
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
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route


@dataclass
class MockResponse:
    status_code: int
    text: str = "bad response"


def test_it_works() -> None:
    assert MatomoMiddleware is not None


@pytest.fixture(name="matomo_client")
def fixture_matomo_client():
    client = mock.AsyncMock(AsyncClient)
    client.get = mock.AsyncMock(return_value=MockResponse(status_code=204))
    return client


@pytest.fixture(name="settings", scope="session")
def fixture_settings() -> dict:
    return {"idsite": 1, "base_url": "https://testserver"}


def create_app(matomo_client, settings: dict, token: typing.Optional[str] = None) -> Starlette:
    app = Starlette()

    app.add_middleware(
        MatomoMiddleware,
        client=matomo_client,
        matomo_url="http://trackingserver",
        idsite=settings["idsite"],
        access_token=token,
        exclude_paths=["/health"],
        exclude_patterns=[".*/old.*"],
        route_details={"/foo2": {"action_name": "The real foo", "e_a": "fooing"}},
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
            "cvar": {"anything": "goes"},
        }
        with PerfMsTracker(scope=request.scope, key="pf_srv"):
            time.sleep(0.1)
        return PlainTextResponse("custom_var")

    async def bar(request):
        raise HTTPException(status_code=400, detail="bar")

    async def baz(request):
        async with PerfMsTracker(scope=request.scope, key="pf_srv"):
            data = await request.json()
        return JSONResponse({"data": data})

    app.add_route("/foo", foo)
    app.add_route("/foo2", foo)
    app.add_route("/bar", bar)
    app.add_route("/health", health)
    app.add_route("/some/old/path", old)
    app.add_route("/old/path", old)
    app.add_route("/really/old", old)
    app.add_route("/set/custom/var", custom_var)
    app.add_route("/baz", baz, methods=["POST"])
    return app


@pytest.fixture(name="app")
def fixture_app(matomo_client, settings: dict) -> Starlette:
    return create_app(matomo_client, settings)


@pytest.fixture(name="app_w_token")
def fixture_app_w_token(matomo_client, settings: dict) -> Starlette:
    return create_app(matomo_client, settings, token="FAKE-TOKEN")  # noqa: S106


@pytest.fixture(name="expected_q")
def fixture_expected_q(settings: dict) -> dict:
    return {
        "idsite": [str(settings["idsite"])],
        "url": [settings["base_url"]],
        "apiv": ["1"],
        # "lang": ["None"]
        "rec": ["1"],
        "send_image": ["0"],
        "cvar": ['{"http_status_code": 200, "http_method": "GET"}'],
    }


@pytest_asyncio.fixture(name="client")
async def fixture_client(app: Starlette) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client


@pytest_asyncio.fixture(name="client_w_token")
async def fixture_client_w_token(
    app_w_token: Starlette,
) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app_w_token):
        async with AsyncClient(app=app_w_token, base_url="http://testserver") as client:
            yield client


@pytest.mark.asyncio
async def test_middleware_w_token_tracks_cip(
    client_w_token: AsyncClient, matomo_client, expected_q: dict
):
    response = await client_w_token.get("/foo")
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    expected_q["cip"] = ["127.0.0.1"]
    expected_q["token_auth"] = ["FAKE-TOKEN"]
    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_middleware_w_token_respects_x_forwarded_for(
    client_w_token: AsyncClient, matomo_client, expected_q: dict
):
    response = await client_w_token.get("/foo", headers={"x-forwarded-for": "127.0.0.2"})
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    expected_q["cip"] = ["127.0.0.2"]
    expected_q["token_auth"] = ["FAKE-TOKEN"]
    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_middleware_tracks_urlref(client: AsyncClient, matomo_client, expected_q: dict):
    response = await client.get("/foo", headers={"referer": "https://example.com"})
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    expected_q["urlref"] = ["https://example.com"]
    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_foo(
    client: AsyncClient, matomo_client, expected_q: dict
):
    response = await client.get("/foo")
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
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
    expected_q["action_name"] = ["/bar"]
    expected_q["cvar"][0] = expected_q["cvar"][0].replace("200", "400")

    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_custom_var(
    client: AsyncClient, matomo_client, expected_q: dict
):
    response = await client.get("/set/custom/var")
    assert response.status_code == 200

    matomo_client.get.assert_awaited()

    expected_q["url"][0] += "/set/custom/var"
    expected_q["e_a"] = ["Playing"]
    expected_q["pf_srv"] = 90000
    expected_q["action_name"] = ["/set/custom/var"]
    expected_q["cvar"] = ['{"http_status_code": 200, "http_method": "GET", "anything": "goes"}']

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
    assert q.pop("ua")[0].startswith("python-httpx")
    if expected_lower_limit := expected_q.pop("pf_srv", None):
        assert float(q.pop("pf_srv")[0]) >= expected_lower_limit

    assert q == expected_q


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_post_baz(
    client: AsyncClient, matomo_client, expected_q: dict
):
    response = await client.post("/baz", json={"data": "content"})
    assert response.status_code == 200

    expected_q["url"][0] += "/baz"
    expected_q["action_name"] = ["/baz"]
    expected_q["pf_srv"] = 25
    expected_q["cvar"][0] = expected_q["cvar"][0].replace("GET", "POST")
    matomo_client.get.assert_awaited()

    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_real_async_client_is_created(settings: dict) -> None:
    app = create_app(None, settings)
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            response = await client.get("/health")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_foo2_has_custom_action_name(
    client: AsyncClient, matomo_client, expected_q: dict
) -> None:
    respone = await client.get("/foo2")
    assert respone.status_code == 200

    expected_q["url"][0] += "/foo2"
    expected_q["action_name"] = ["The real foo"]
    expected_q["e_a"] = ["fooing"]

    matomo_client.get.assert_awaited()

    assert_query_string(str(matomo_client.get.await_args), expected_q)


@pytest.mark.asyncio
async def test_middleware_handles_lifespan_startups_errors():
    @contextlib.asynccontextmanager
    async def custom_lifespan(app):
        raise RuntimeError("startup failure")
        yield

    async def homepage(request):
        return JSONResponse({"a": "b"})

    app = Starlette(
        routes=[Route("/", homepage)],
        middleware=[
            Middleware(
                MatomoMiddleware,
                matomo_url="YOUR MATOMO TRACKING URL",
                idsite=12345,  # your service tracking id
            )
        ],
        lifespan=custom_lifespan,
    )

    lifespan_scope = {
        "type": "lifespan",
        "asgi": {
            "version": "3.0",
        },
        "state": {},
    }

    async def receive():
        return {"type": "lifespan.startup"}

    async def send(message) -> None:
        assert message["type"] in (
            "lifespan.startup.complete",
            "lifespan.startup.failed",
            "lifespan.shutdown.complete",
            "lifespan.shutdown.failed",
        )

    with pytest.raises(RuntimeError, match="startup failure"):
        await app(lifespan_scope, receive, send)


@pytest.mark.asyncio
async def test_middleware_handles_lifespan_shutdown_errors():
    @contextlib.asynccontextmanager
    async def custom_lifespan(app):
        yield
        raise RuntimeError("shutdown failure")

    async def homepage(request):
        return JSONResponse({"a": "b"})

    app = Starlette(
        routes=[Route("/", homepage)],
        middleware=[
            Middleware(
                MatomoMiddleware,
                matomo_url="YOUR MATOMO TRACKING URL",
                idsite=12345,  # your service tracking id
            )
        ],
        lifespan=custom_lifespan,
    )

    lifespan_scope = {
        "type": "lifespan",
        "asgi": {
            "version": "3.0",
        },
        "state": {},
    }

    async def receive():
        return {"type": "lifespan.shutdown"}

    async def send(message) -> None:
        assert message["type"] in (
            "lifespan.startup.complete",
            "lifespan.startup.failed",
            "lifespan.shutdown.complete",
            "lifespan.shutdown.failed",
        )

    with pytest.raises(RuntimeError, match="shutdown failure"):
        await app(lifespan_scope, receive, send)
