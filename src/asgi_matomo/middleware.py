"""Matomo middleware for ASGI apps."""

import json
import logging
import random
import re
import time
import traceback
import typing
import urllib.parse
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, Literal

import httpx
import matomo_core.constants
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGIReceiveEvent,
    ASGISendCallable,
    ASGISendEvent,
    HTTPScope,
)

logger = logging.getLogger(__name__)


_T = typing.TypeVar("_T")


class _DefaultLifespan:
    def __init__(self, app: "MatomoMiddleware") -> None:
        self._app = app

    async def __aenter__(self) -> None:
        await self._app.startup()

    async def __aexit__(self, *exc_info: object) -> None:
        await self._app.shutdown()

    def __call__(self: _T, app: object) -> _T:  # noqa: ARG002
        return self


class MatomoMiddleware:
    """Matomo middleware."""

    def __init__(
        self,
        app: ASGI3Application,
        *,
        matomo_url: str,
        idsite: int,
        access_token: str | None = None,
        assume_https: bool = True,
        client: httpx.AsyncClient | None = None,
        http_timeout: int | None = 5,
        exclude_paths: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        route_details: dict[str, dict[str, str]] | None = None,
        allowed_methods: list[str] | Literal["all-methods"] = "all-methods",
        ignored_methods: list[str] | None = None,
    ) -> None:
        """Initialize the Matomo middleware.

        Args:
            app: Asgi app to use this middleware for
            matomo_url: url to call
            idsite: id of the site that should be tracked on Matomo
            access_token: token that can be found in the area API in the settings of Matomo
            assume_https: use https when building the tracked url. Default: True.
            client: http-client to use for tracking the requests.
                Must use the same api as `httpx.AsyncClient`.
                Default: creates `httpx.AsyncClient`
            http_timeout: the timeout to use for requests. Ignored if a custom client is provided.
            exclude_paths: exclude these paths
            exclude_patterns: exclude paths based on these regex patterns
            route_details: mapping of details for each path
            allowed_methods: list of methods to track or "all-methods". Default: "all-methods".
            ignored_methods: list of methods to ignore, takes precedence over allowed methods. Default: None.
        """
        self.app = app
        self.matomo_url = matomo_url
        self.idsite = idsite
        self.assume_https = assume_https
        self.access_token = access_token
        self.lifespan_context = _DefaultLifespan(self)
        self.client = client or httpx.AsyncClient(timeout=http_timeout)
        self.exclude_paths = set(exclude_paths or [])
        self.compiled_patterns = [re.compile(pattern) for pattern in (exclude_patterns or [])]
        self.route_details = route_details or {}
        self.allowed_methods: set[str] = set()
        if allowed_methods == "all-methods":
            self.allowed_methods = matomo_core.constants.HTTP_METHODS
        elif allowed_methods:
            self.allowed_methods.update(method.upper() for method in allowed_methods)
        self.ignored_methods: set[str] = {method.upper() for method in ignored_methods} if ignored_methods else set()

    async def startup(self) -> None:
        """Prepare this middleware for use."""

    async def shutdown(self) -> None:
        """Shut down http client properly."""
        await self.client.aclose()

    async def lifespan(self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        """Handle ASGI lifespan messages.

        This allows us to manage application startup and shutdown events.

        Code borrowed from: https://github.com/adriangb/asgi-lifespan
        """
        rcv_events: dict[str, bool] = {}
        send_events: dict[str, bool] = {}

        async def wrapped_rcv() -> ASGIReceiveEvent:
            message = await receive()
            rcv_events[message["type"]] = True
            return message

        async def wrapped_send(message: ASGISendEvent) -> None:
            send_events[message["type"]] = True
            if message["type"] == "lifespan.shutdown.complete":
                # we want to send this one ourselves
                # once we are done
                return
            await send(message)

        @asynccontextmanager
        async def cleanup() -> "AsyncIterator[None]":
            try:
                yield
            except BaseException:
                exc_text = traceback.format_exc()
                if "lifespan.startup.complete" in send_events:
                    await send({"type": "lifespan.shutdown.failed", "message": exc_text})
                else:
                    await send({"type": "lifespan.startup.failed", "message": exc_text})
                raise
            else:
                await send({"type": "lifespan.shutdown.complete"})

        lifespan_cm = self.lifespan_context(self.app)

        async with AsyncExitStack() as stack:
            await stack.enter_async_context(cleanup())
            await stack.enter_async_context(lifespan_cm)
            try:
                # one of 4 things will happen when we call the app:
                # 1. it supports lifespans. it will block until the server
                #    sends the shutdown signal, at which point we get control
                #    back and can run our own teardown
                # 2. it does nothing and returns. in this case we do the
                #    back and forth with the ASGI server ourselves
                # 3. it raises an exception.
                #    a. before raising the exception it sent a
                #       "lifespan.startup.failed" message
                #       this means it supports lifespans, but it's lifespan
                #       errored out. we'll re-raise to trigger our teardown
                #    b. it did not send a "lifespan.startup.failed" message
                #       this app doesn't support lifespans, the spec says
                #       to just swallow the exception and proceed
                # 4. it supports lifespan events and it's lifespan fails
                #    (it sends a "lifespan.startup.failed" message)
                #    in this case we'll run our teardown and then return
                await self.app(scope, wrapped_rcv, wrapped_send)
            except BaseException:
                if "lifespan.startup.failed" in send_events or "lifespan.shutdown.failed" in send_events:
                    # the app tried to start and failed
                    # this app re-raises the exceptions (Starlette does this)
                    # re-raise so that our teardown is triggered
                    raise
                # the app doesn't support lifespans
                # the spec says to ignore these errors and just don't send
                # more lifespan events
            if "lifespan.startup.failed" in send_events:
                # the app supports lifespan events
                # but it failed to start
                # this app does not re-raise exceptions
                # so all we can do is run our teardown and exit
                return
            if "lifespan.startup.complete" not in send_events:
                # the app doesn't support lifespans at all
                # so we'll have to talk to the ASGI server ourselves
                await receive()
                await send({"type": "lifespan.startup.complete"})
                # we'll block here until the ASGI server shuts us down
                await receive()
        # even if the app sent this, we intercepted it and discarded it until we were done
        # await send({"type": "lifespan.shutdown.complete"})

    async def __call__(self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> Any:
        """Handle request."""
        # locals inside the app function (send_wrapper) can't be assigned to,
        # as the interpreter detects the assignment and thus creates a new
        # local variable within that function, with that name.
        instance = {"http_status_code": 500}

        def send_wrapper(response: ASGISendEvent) -> Any:
            if response["type"] == "http.response.start":
                instance["http_status_code"] = response["status"]
            return send(response)

        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
            return

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # ensure 'asgi_matomo' is set in state
        if "state" not in scope:
            scope["state"] = {}  # type: ignore

        if "asgi_matomo" not in scope["state"]:  # type: ignore
            scope["state"]["asgi_matomo"] = {"tracking_data": {}}  # type: ignore
        elif "tracking_data" not in scope["state"]["asgi_matomo"]:
            scope["state"]["asgi_matomo"]["tracking_data"] = {}
        path = scope["path"]

        dont_track_this = False
        if (
            path in self.exclude_paths
            or scope["method"] in self.ignored_methods
            or scope["method"] not in self.allowed_methods
            or any(pattern.match(path) for pattern in self.compiled_patterns)
        ):
            logger.debug("excluding path='%s'", path, extra={"path": path})
            dont_track_this = True

        # Early exit if we don't track this path
        if dont_track_this:
            await self.app(scope, receive, send)
            return

        start_time_ns = time.perf_counter_ns()

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            raise
        finally:
            end_time_ns = time.perf_counter_ns()

            tracking_data = self._build_tracking_state(scope)
            tracking_data.update(
                {
                    "gt_ms": (end_time_ns - start_time_ns) / 1000,
                    "cvar": {
                        "http_status_code": instance["http_status_code"],
                        "http_method": scope["method"],
                    },
                }
            )

            tracking_state = scope.get("state", {}).get("asgi_matomo", {})  # type: ignore
            for field, value in tracking_state.get("tracking_data", {}).items():  # type: ignore
                if field in tracking_data and isinstance(tracking_data[field], dict) and isinstance(value, dict):
                    tracking_data[field].update(value)  # type: ignore
                else:
                    tracking_data[field] = value
            for key, value in tracking_state.get("custom_tracking_data", {}).items():
                if key == "cvar" and "cvar" in tracking_data:
                    tracking_data["cvar"].update(value)
                else:
                    tracking_data[key] = value
            # if exc:
            #     tracking_data["ca"] = 1
            #     tracking_data["cra"] = str(exc)
            tracking_data["cvar"] = json.dumps(tracking_data["cvar"])

            logger.debug(
                "Making tracking call to '%s'",
                self.matomo_url,
                extra={"tracking_data": tracking_data},
            )
            try:
                if self.client is None:
                    logger.error("self.client is not set, can't track request")
                else:
                    tracking_response = await self.client.post(self.matomo_url, data=tracking_data)
                    logger.debug(
                        "tracking response",
                        extra={
                            "status": tracking_response.status_code,
                            "content": tracking_response.text,
                        },
                    )
                    if tracking_response.status_code >= 300:  # noqa: PLR2004
                        logger.error(
                            "Tracking call failed (status_code=%d)",
                            tracking_response.status_code,
                            extra={
                                "status_code": tracking_response.status_code,
                                "text": tracking_response.text,
                            },
                        )
            except httpx.HTTPError:
                logger.exception("Error tracking view")

    def _build_tracking_state(self, scope: HTTPScope) -> dict[str, Any]:
        server = None
        user_agent = None
        accept_lang = None
        cip = None
        path = scope["path"]
        urlref = None

        for header, value in scope["headers"]:
            if header == b"accept_lang":
                accept_lang = value
            elif header == b"user-agent":
                user_agent = value
            elif header == b"x-forwarded-server":
                server = value.decode("utf-8")
            elif header == b"x-forwarded-for":
                cip = value.decode("utf-8")
            elif header == b"referer":
                urlref = value
        if server is None:
            if scope["server"] is None:
                logger.error("'server' is not set in scope, skip tracking...")
                raise RuntimeError("'server' is not set in scope")
            host, port = scope["server"]
            logger.debug("setting server from scope", extra={"host": host, "port": port})
            server = f"{host}:{port}" if port else host

        if ", " in server:
            servers = server.split(", ")
            logger.debug(
                "splitting server addresses, using first",
                extra={"server-orig": server, "servers": servers},
            )
            server = servers[0]

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

        if not cip:
            cip = scope["client"][0] if scope["client"] else None

        tracking_state = {
            "idsite": self.idsite,
            "action_name": scope["path"],
            "url": url,
            "rec": 1,
            "rand": random.getrandbits(32),
            "apiv": 1,
            "ua": user_agent,
            "send_image": 0,
        }

        if scope["path"] in self.route_details:
            tracking_state |= self.route_details[scope["path"]]
        if self.access_token and cip:
            tracking_state["token_auth"] = self.access_token
            tracking_state["cip"] = cip
        if accept_lang:
            tracking_state["lang"] = accept_lang
        if urlref:
            tracking_state["urlref"] = urlref
        return tracking_state
