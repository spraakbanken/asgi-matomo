"""Example showing how to specify details to a route."""

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_matomo import MatomoMiddleware


async def foo(_request: Request) -> JSONResponse:  # noqa: RUF029
    """Pretend this route return something useful."""
    return JSONResponse({"name": "foo"})


app = Starlette(
    routes=[Route("/foo", foo)],
    middleware=[
        Middleware(
            MatomoMiddleware,
            matomo_url="YOUR MATOMO TRACKING URL",
            idsite=12345,  # your service tracking id
            route_details={"/foo": {"action_name": "Foo/foo", "e_c": "Foo", "e_a": "Playing"}},
        )
    ],
)
