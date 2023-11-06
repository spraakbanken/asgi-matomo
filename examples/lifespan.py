import asyncio
import contextlib
import dataclasses
from unittest import mock

from httpx import AsyncClient
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker


@dataclasses.dataclass
class MockResponse:
    status_code: int
    text: str = "response"


def create_matomo_client():
    matomo_client = mock.AsyncMock(AsyncClient)
    matomo_client.get = mock.AsyncMock(return_value=MockResponse(status_code=204))
    return matomo_client


matomo_client = create_matomo_client()


@contextlib.asynccontextmanager
async def custom_lifespan(app):
    print("startup")
    # raise RuntimeError("startup")
    yield
    print("shutdown")
    raise RuntimeError("shutdown")


async def fetch_data():
    await asyncio.sleep(0.2)
    return {"data": 4000}


async def homepage(request):
    with PerfMsTracker(scope=request.scope, key="pf_srv"):
        # fetch/compute data
        data = await fetch_data()
    return JSONResponse(data)


app = Starlette(
    routes=[Route("/", homepage)],
    middleware=[
        Middleware(
            MatomoMiddleware,
            matomo_url="YOUR MATOMO TRACKING URL",
            idsite=12345,  # your service tracking id
            client=create_matomo_client(),
        )
    ],
    lifespan=custom_lifespan,
)
