import contextlib
import time
import typing
from collections.abc import AsyncGenerator, MutableMapping
from dataclasses import dataclass
from unittest import mock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.types import ASGIApp
from syrupy import matchers

from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker


@dataclass
class MockResponse:
    status_code: int
    text: str = "bad response"


def test_it_works() -> None:
    assert MatomoMiddleware is not None


@pytest.fixture(name="matomo_client")
def fixture_matomo_client() -> mock.AsyncMock:
    client = mock.AsyncMock(AsyncClient)
    client.post = mock.AsyncMock(return_value=MockResponse(status_code=204))
    return client


@pytest.fixture(name="settings", scope="session")
def fixture_settings() -> dict[str, typing.Any]:
    return {"idsite": 1, "base_url": "https://testserver"}


def create_app(
    matomo_client: AsyncClient,
    settings: dict[str, typing.Any],
    token: typing.Optional[str] = None,
) -> Starlette:
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

    def foo(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("foo")

    def health(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("ok")

    def old(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("old")

    def custom_var(request: Request) -> PlainTextResponse:
        if "state" not in request.scope:
            request.scope["state"] = {}
        request.scope["state"]["asgi_matomo"] = {
            "e_a": "Playing",
            "cvar": {"anything": "goes"},
        }
        with PerfMsTracker(scope=request.scope, key="pf_srv"):
            time.sleep(0.1)
        return PlainTextResponse("custom_var")

    def bar(_request: Request) -> PlainTextResponse:
        raise HTTPException(status_code=400, detail="bar")

    async def baz(request: Request) -> JSONResponse:
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
def fixture_app(matomo_client: AsyncClient, settings: dict[str, typing.Any]) -> Starlette:
    return create_app(matomo_client, settings)


@pytest.fixture(name="app_w_token")
def fixture_app_w_token(matomo_client: AsyncClient, settings: dict[str, typing.Any]) -> Starlette:
    return create_app(matomo_client, settings, token="FAKE-TOKEN")


@pytest_asyncio.fixture(name="client")
async def fixture_client(app: Starlette) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):  # noqa: SIM117
        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            yield client


@pytest_asyncio.fixture(name="client_w_token")
async def fixture_client_w_token(
    app_w_token: Starlette,
) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app_w_token):  # noqa: SIM117
        async with AsyncClient(transport=ASGITransport(app_w_token), base_url="http://testserver") as client:
            yield client


def make_matcher(**kwargs):  # noqa: ANN003, ANN201
    path_types = {"gt_ms": (float,), "rand": (int,)}
    if kwargs:
        path_types.update(kwargs)
    return matchers.path_type(path_types)


@pytest.mark.asyncio
async def test_middleware_w_token_tracks_cip(
    client_w_token: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    response = await client_w_token.get("/foo")
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_middleware_w_token_respects_x_forwarded_for(
    client_w_token: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    response = await client_w_token.get("/foo", headers={"x-forwarded-for": "127.0.0.2"})
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_middleware_tracks_urlref(client: AsyncClient, matomo_client: mock.AsyncMock, snapshot_json) -> None:  # noqa: ANN001
    response = await client.get("/foo", headers={"referer": "https://example.com"})
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_foo(
    client: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    response = await client.get("/foo")
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_bar(
    client: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    with contextlib.suppress(ValueError):
        _response = await client.get("/bar")
    # assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_get_custom_var(
    client: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    response = await client.get("/set/custom/var")
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher(pf_srv=(float,)))


@pytest.mark.asyncio
async def test_matomo_client_doesnt_gets_called_on_get_health(
    client: AsyncClient,
    matomo_client: mock.AsyncMock,
) -> None:
    response = await client.get("/health")
    assert response.status_code == 200

    matomo_client.post.assert_not_awaited()


@pytest.mark.parametrize("path", ["/some/old/path", "/old/path", "/really/old"])
@pytest.mark.asyncio
async def test_matomo_client_doesnt_gets_called_on_get_old(
    client: AsyncClient, matomo_client: mock.AsyncMock, path: str
) -> None:
    response = await client.get(path)
    assert response.status_code == 200

    matomo_client.post.assert_not_awaited()


@pytest.mark.asyncio
async def test_matomo_client_gets_called_on_post_baz(
    client: AsyncClient,
    matomo_client: mock.AsyncMock,
    snapshot_json,  # noqa: ANN001
) -> None:
    response = await client.post("/baz", json={"data": "content"})
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher(pf_srv=(float,)))


@pytest.mark.asyncio
async def test_real_async_client_is_created(settings: dict[str, typing.Any]) -> None:
    app = create_app(None, settings)
    async with LifespanManager(app):  # noqa: SIM117
        async with AsyncClient(transport=ASGITransport(app), base_url="http://testserver") as client:
            response = await client.get("/health")
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_foo2_has_custom_action_name(client: AsyncClient, matomo_client: mock.AsyncMock, snapshot_json) -> None:  # noqa: ANN001
    response = await client.get("/foo2")
    assert response.status_code == 200

    matomo_client.post.assert_awaited()

    assert matomo_client.post.await_args.kwargs["data"] == snapshot_json(matcher=make_matcher())


@pytest.mark.asyncio
async def test_middleware_handles_lifespan_startups_errors() -> None:
    # sourcery skip: remove-unreachable-code
    @contextlib.asynccontextmanager
    async def custom_lifespan(_app: ASGIApp):  # noqa: ANN202, RUF029
        raise RuntimeError("startup failure")
        yield

    async def homepage(_request: Request):  # noqa: ANN202, RUF029
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

    async def receive() -> dict[str, str]:  # noqa: RUF029
        return {"type": "lifespan.startup"}

    async def send(message: MutableMapping[str, typing.Any]) -> None:  # noqa: RUF029
        assert message["type"] in {
            "lifespan.startup.complete",
            "lifespan.startup.failed",
            "lifespan.shutdown.complete",
            "lifespan.shutdown.failed",
        }

    with pytest.raises(RuntimeError, match="startup failure"):
        await app(lifespan_scope, receive, send)


@pytest.mark.asyncio
async def test_middleware_handles_lifespan_shutdown_errors() -> None:
    @contextlib.asynccontextmanager
    async def custom_lifespan(_app: ASGIApp):  # noqa: ANN202, RUF029
        yield
        raise RuntimeError("shutdown failure")

    async def homepage(_request: Request) -> JSONResponse:  # noqa: RUF029
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

    async def receive() -> dict[str, typing.Any]:  # noqa: RUF029
        return {"type": "lifespan.shutdown"}

    async def send(message: MutableMapping[str, typing.Any]) -> None:  # noqa: RUF029
        assert message["type"] in {
            "lifespan.startup.complete",
            "lifespan.startup.failed",
            "lifespan.shutdown.complete",
            "lifespan.shutdown.failed",
        }

    with pytest.raises(RuntimeError, match="shutdown failure"):
        await app(lifespan_scope, receive, send)
