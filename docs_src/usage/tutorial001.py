"""Example showing minimal usage."""

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_matomo import MatomoMiddleware


async def homepage(_request: Request) -> JSONResponse:  # noqa: D103, RUF029
    return JSONResponse({"data": 4000})


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
