# asgi-matomo


[![PyPI version](https://img.shields.io/pypi/v/asgi-matomo.svg?style=flat-square&colorB=dfb317)](https://pypi.org/project/asgi-matomo/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/asgi-matomo)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/asgi-matomo)](https://pypi.org/project/asgi-matomo/)
 [![Docs](https://img.shields.io/badge/docs-here-red.svg?style=flat-square)](https://spraakbanken.github.io/asgi-matomo/)
![MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)

[![Maturity badge - level 3](https://img.shields.io/badge/Maturity-Level%203%20--%20Stable-green.svg)](https://github.com/spraakbanken/getting-started/blob/main/scorecard.md)
[![Stage](https://img.shields.io/pypi/status/asgi-matomo)](https://pypi.org/project/asgi-matomo/)

[![Code Coverage](https://codecov.io/gh/spraakbanken/asgi-matomo/branch/main/graph/badge.svg)](https://codecov.io/gh/spraakbanken/asgi-matomo/)

[![CI(check)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/check.yml/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/check.yml)
[![CI(release)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/release.yml/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/release.yml)
[![CI(scheduled)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/scheduled.yml/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/scheduled.yml)
[![CI(test)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/test.yml/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions/workflows/test.yml)


Tracking requests with Matomo from ASGI apps.

`MatomoMiddleware` adds tracking of all requests to Matomo to ASGI applications (Starlette, FastAPI, Quart, etc.). The intended usage is for api tracking (backends).

**Note** If you serve HTML (directly or by templates), it is suggested to track those parts through Matomo's javascript tracking.

## Installation

```bash
pip install asgi-matomo
```

## What is tracked

Currently this middleware tracks:

- `url`
- `ua`: user_agent
- `gt_ms`: mesaured as the time before and after this middleware call next in the asgi stack.
- `send_image=0` for performance issues
- `cvar` with at least `http_status_code` and `http_method` set.
- `lang` if `accept-lang` is set
- `cip` client ip, **requires** `access_token` to be given.
- `action_name` that defaults to path, but can be specified.

You can also pass variable to track by adding an `asgi_matomo`  dict in the `state` dict of the ASGI `scope`:

```python
scope = {
  "state": {
    "asgi_matomo": {
      "e_a": "Playing",
      "cvar": {
        "your": "custom",
        "data": "here",
      }
    }
  }
}
```

The keys of the `asgi_matomo` dict is expected to be valid parameter for the [Matomo HTTP Tracking API](https://developer.matomo.org/api-reference/tracking-api). `cvar` is serialized with the standard `json` lib.

You can also track time spent on different tasks with `trackers.PerfMsTracker`.

```python
import asyncio
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware

from asgi_matomo import MatomoMiddleware
from asgi_matomo.trackers import PerfMsTracker

async def homepage(request):
    async with PerfMsTracker(scope=request.scope, key="pf_srv"):
        # fetch/compute data
        await asyncio.sleep(1)
        data = {"data": "a"*4000}
    return JSONResponse(data)

app = Starlette(
  routes=[Route("/", homepage)],
  middleware=[
    Middleware(
      MatomoMiddleware,
      matomo_url="YOUR MATOMO TRACKING URL",
      idsite=12345, # your service tracking id
  )],
)
```

## Examples

### Starlette

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware

from asgi_matomo import MatomoMiddleware

async def homepage(request):
    return JSONResponse({"data": "a" * 4000})

app = Starlette(
  routes=[Route("/", homepage)],
  middleware=[
    Middleware(
      MatomoMiddleware,
      matomo_url="YOUR MATOMO TRACKING URL",
      idsite=12345, # your service tracking id
  )],
)
```

### FastAPI

```python
from fastapi import FastAPI
from asgi_matomo import MatomoMiddleware

app = FastAPI()
app.add_middleware(
  MatomoMiddleware,
  matomo_url="YOUR MATOMO TRACKING URL",
  idsite=12345, # your service tracking id
)

@app.get("/")
def home() -> dict:
    return {"data": "a" * 4000}
```

## API Reference

### Overview

```python
app.add_middleware(
  MatomoMiddleware,
  matomo_url="YOUR MATOMO TRACKING URL",
  idsite=12345, # your service tracking id
  access_token="SECRETTOKEN",
  assume_https=True,
  exclude_paths=["/health"],
  exclude_patterns=[".*/old.*"],
  route_details={
    "route": {
      "action_name": "Name",
    }
  }
  client=None,
  http_timeout=5,
  allowed_methods="all-methods",
  ignored_methods=None
)
```

**Parameters**:

- **(Required)** `matomo_url`: The URL to make your tracking calls to.
- **(Required)** `idsite`: The tracking id for your service.
- _(Optional)_ `access_token`: Access token for Matomo. If this is set `cip` is also tracked. Required for tracking some data.
- _(Optional)_ `assume_https`: If `True`, set tracked url scheme to `https`, useful when running behind a proxy. Defaults to `True`.
- _(Optional)_ `exclude_paths`: A list of paths to exclude, only excludes path that is equal to a path in this list. These are tried before `exclude_patterns`. Defaults to `None`.
- _(Optional)_ `exclude_patterns`: A list of regex patterns that are compiled, and then exclude a path from tracking if any pattern match. Defaults to `None`.
These are tried after `exclude_paths`.
- _(Optional)_ `route_details`: A dict with custom route-specific tracking data. Defaults to `None`.
- _(Optional)_ `client`: A custom http client to use (must use the same API as `httpx.Client`). Defaults to `None`, a client is created.
- _(Optional)_ `http_timeout`: Timeout to use for the client being created. Ignored if a custom client is provided. Defaults to `5`. 
- _(Optional)_ `allowed_methods`: List of HTTP methods that should be tracked. Defaults to `"all-methods"`.
- _(Optional)_ `ignored_methods`: List of HTTP methods to ignored. Ignored methods takes precedence over allowed methods. Defaults to `None`.

**Notes**:

- Currently only some parts [Matomo Tracking HTTP API](https://developer.matomo.org/api-reference/tracking-api) is supported.

## Ideas for further work

- [x] _filtering tracked of urls_
- [x] _custom extraction of tracked data_

This project keeps a [changelog](https://github.com/spraakbanken/asgi-matomo/CHANGELOG.md).

## Development

This project uses `uv` and `pre-commit`.
