from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from asgi_matomo import MatomoMiddleware


async def foo(request: Request):
    if "state" not in request.scope:
        request.scope["state"] = {}
    request.scope["state"]["asgi_matomo"] = {
        "action_name": "Foo/foo",
        "e_c": "Foo",
        "e_a": "Playing",
        "cvar": {"anything": "goes"},
    }
    return JSONResponse({"name": "foo"})


app = Starlette(
    routes=[Route("/foo", foo)],
    middleware=[
        Middleware(
            MatomoMiddleware,
            matomo_url="YOUR MATOMO TRACKING URL",
            idsite=12345,  # your service tracking id
        )
    ],
)
