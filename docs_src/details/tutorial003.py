import asyncio

from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route


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
        )
    ],
)
