import logging
import random
import time
import typing
from typing import Any
import urllib.parse
import traceback

from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable
from asgiref.typing import HTTPScope

import httpx


logger = logging.getLogger(__name__)


_T = typing.TypeVar("_T")


class _DefaultLifespan:
    def __init__(self, app: "Router"):
        self._app = app

    async def __aenter__(self) -> None:
        await self._app.startup()

    async def __aexit__(self, *exc_info: object) -> None:
        await self._app.shutdown()

    def __call__(self: _T, app: object) -> _T:
        return self


class MatomoMiddleware:
    def __init__(
        self,
        app: ASGI3Application,
        *,
        matomo_url,
        idsite: int,
        access_token: str | None = None,
        assume_https: bool = True,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.app = app
        self.matomo_url = matomo_url
        self.idsite = idsite
        self.assume_https = assume_https
        self.access_token = access_token
        self.lifespan_context = _DefaultLifespan(self)
        self.client = client

    async def startup(self) -> None:
        if self.client is None:
            self.client = httpx.AsyncClient()

    async def shutdown(self) -> None:
        if self.client is not None:
            await self.client.aclose()

    async def lifespan(
        self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        """
        Handle ASGI lifespan messages, which allows us to manage application
        startup and shutdown events.
        """
        started = False
        app: typing.Any = scope.get("app")
        await receive()
        try:
            async with self.lifespan_context(app) as maybe_state:
                if maybe_state is not None:
                    if "state" not in scope:
                        raise RuntimeError(
                            'The server does not support "state" in the lifespan scope.'
                        )
                    scope["state"].update(maybe_state)
                await send({"type": "lifespan.startup.complete"})
                started = True
                await receive()
        except BaseException:
            exc_text = traceback.format_exc()
            if started:
                await send({"type": "lifespan.shutdown.failed", "message": exc_text})
            else:
                await send({"type": "lifespan.startup.failed", "message": exc_text})
            raise
        else:
            await send({"type": "lifespan.shutdown.complete"})

    async def __call__(
        self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> Any:
        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
            return

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        server = None
        user_agent = None
        accept_lang = None
        for header, value in scope["headers"]:
            if header == b"x-forwarded-server":
                server = value
            elif header == b"user-agent":
                user_agent = value
            elif header == b"accept_lang":
                accept_lang = value

        if server is None:
            host, port = scope["server"]
            server = f"{host}:{port}" if port else host

        path = scope["path"]
        if root_path := scope.get("root_path"):
            path = f"{root_path}{path}"

        url = urllib.parse.urlunsplit(
            (
                "https" if self.assume_https else str(scope["scheme"]),
                server,
                path,
                "",
                str(scope["query_string"]) if scope.get("query_string") else None,
            )
        )

        cip = scope["client"][0]

        start_time = time.perf_counter()

        try:
            await self.app(scope, receive, send)
        except Exception:
            raise
        finally:
            end_time = time.perf_counter()

            params_that_require_token = {}

            if self.access_token:
                params_that_require_token = {
                    "token_auth": self.access_token,
                    "cip": cip,
                }

            tracking_dict = {
                "idsite": self.idsite,
                "url": url,
                "rec": 1,
                "rand": random.getrandbits(32),
                "apiv": 1,
                "ua": user_agent,
                "gt_ms": end_time - start_time,
                # "lang": accept_lang,
                **params_that_require_token,
            }

            if accept_lang:
                tracking_dict["lang"] = accept_lang

            tracking_params = urllib.parse.urlencode(tracking_dict)
            tracking_url = f"{self.matomo_url}?{tracking_params}"
            logger.debug("Making tracking call", extra={"url": tracking_url})
            try:
                tracking_response = await self.client.get(tracking_url)
            except httpx.HTTPError:
                logger.exception("Error tracking view")
