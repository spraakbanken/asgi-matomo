from asgi_matomo import MatomoMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route


async def foo(request):
    return JSONResponse({"name": "foo"})


app = Starlette(
    routes=[Route("/foo", foo)],
    middleware=[
        Middleware(
            MatomoMiddleware,
            matomo_url="YOUR MATOMO TRACKING URL",
            idsite=12345,  # your service tracking id
            route_details={
                "/foo": {"action_name": "Foo/foo", "e_c": "Foo", "e_a": "Playing"}
            },
        )
    ],
)
