"""Example showing how to measure time spent computing or fetching data."""

import asyncio

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker


async def fetch_data() -> dict[str, int]:
    """Pretend this computes data or calls an external api."""
    await asyncio.sleep(0.2)
    return {"data": 4000}


async def homepage(request: Request) -> JSONResponse:
    """Show case how to track time when calling/computing data."""
    async with PerfMsTracker(scope=request.scope, key="pf_srv"):
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
        )
    ],
)
