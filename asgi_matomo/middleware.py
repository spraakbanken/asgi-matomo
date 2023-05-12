import json
import logging
import random
import re
import time
import traceback
import typing
import urllib.parse
from typing import Any

import httpx
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPScope,
)

logger = logging.getLogger(__name__)


_T = typing.TypeVar("_T")


class _DefaultLifespan:
    def __init__(self, app: "MatomoMiddleware"):
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
        exclude_paths: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> None:
        self.app = app
        self.matomo_url = matomo_url
        self.idsite = idsite
        self.assume_https = assume_https
        self.access_token = access_token
        self.lifespan_context = _DefaultLifespan(self)
        self.client = client
        self.exclude_paths = set(exclude_paths or [])
        self.compiled_patterns = [
            re.compile(pattern) for pattern in (exclude_patterns or [])
        ]

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
                    scope["state"].update(maybe_state)  # type: ignore
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
                server = value.decode("utf-8")
            elif header == b"user-agent":
                user_agent = value
            elif header == b"accept_lang":
                accept_lang = value

        if server is None:
            if scope["server"] is None:
                logger.error("'server' is not set in scope, skip tracking...")
                await self.app(scope, receive, send)
                return
            host, port = scope["server"]
            logger.debug(
                "setting server from scope", extra={"host": host, "port": port}
            )
            server = f"{host}:{port}" if port else host

        if ", " in server:
            servers = server.split(", ")
            logger.debug(
                "splitting server addresses, using first",
                extra={"server-orig": server, "servers": servers},
            )
            server = servers[0]

        path = scope["path"]
        dont_track_this = False
        if path in self.exclude_paths:
            logger.debug("excluding path='%s'", path, extra={"path": path})
            dont_track_this = True
        elif any(pattern.match(path) for pattern in self.compiled_patterns):
            logger.debug("excluding path='%s'", path, extra={"path": path})
            dont_track_this = True
        if root_path := scope.get("root_path"):
            logger.debug("using root_path", extra={"root_path": root_path})
            path = f"{root_path}{path}"

        logger.debug(
            "building url",
            extra={
                "server": server,
                "path": path,
                "user_agent": user_agent,
                "accept_lang": accept_lang,
            },
        )
        url = urllib.parse.urlunsplit(
            (
                "https" if self.assume_https else str(scope["scheme"]),
                server,
                path,
                "",
                str(scope["query_string"]) if scope.get("query_string") else None,
            )
        )

        cip = scope["client"][0] if scope["client"] else None

        start_time_ns = time.perf_counter_ns()

        try:
            await self.app(scope, receive, send)
        except Exception:
            raise
        finally:
            end_time_ns = time.perf_counter_ns()

            params_that_require_token = {}

            if self.access_token:
                if cip is None:
                    logger.error("'client' is not set in scope")
                else:
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
                "gt_ms": (end_time_ns - start_time_ns) / 1000,
                "send_image": 0,
                # "lang": accept_lang,
                **params_that_require_token,
            }
            if "state" in scope and "asgi_matomo" in scope["state"]:
                for field, value in scope["state"]["asgi_matomo"].items():
                    tracking_dict[field] = (
                        json.dumps(value) if isinstance(value, dict) else value
                    )
            if accept_lang:
                tracking_dict["lang"] = accept_lang

            tracking_params = urllib.parse.urlencode(tracking_dict)
            tracking_url = f"{self.matomo_url}?{tracking_params}"
            if dont_track_this:
                logger.debug("NOT tracking call", extra={"url": tracking_url})
            else:
                logger.debug("Making tracking call", extra={"url": tracking_url})
                try:
                    if self.client is None:
                        logger.error("self.client is not set, can't track request")
                    else:
                        tracking_response = await self.client.get(tracking_url)
                        logger.debug(
                            "tracking response",
                            extra={
                                "status": tracking_response.status_code,
                                "content": tracking_response.text,
                            },
                        )
                except httpx.HTTPError:
                    logger.exception("Error tracking view")
