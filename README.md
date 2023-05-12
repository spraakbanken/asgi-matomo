# asgi-matomo
[![Packaging status](https://img.shields.io/pypi/v/asgi-matomo?color=%2334D058&label=pypi%20package)](https://pypi.org/project/asgi-matomo)
[![CI](https://github.com/spraakbanken/asgi-matomo/workflows/CI/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions?query=workflow%3ACI)
[![Coverage](https://github.com/spraakbanken/asgi-matomo/workflows/Coverage/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions?query=workflow%3ACoverage)
[![codecov](https://codecov.io/gh/spraakbanken/asgi-matomo/branch/main/graph/badge.svg?token=MRJZVCJQF5)](https://codecov.io/gh/spraakbanken/asgi-matomo)

Tracking requests with Matomo from ASGI apps.

`MatomoMiddleware` adds tracking of all requests to Matomo to ASGI applications (Starlette, FastAPI, Quart, etc.). The intended usage is for api tracking (backends).

**Note** If you serve HTML (directly or by templates), it is suggested to track those parts through Matomo's javascript tracking.

**Installation**

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
  BrotliMiddleware,
  matomo_url="YOUR MATOMO TRACKING URL",
  idsite=12345, # your service tracking id
)

@app.get("/")
def home() -> dict:
    return {"data": "a" * 4000}
```

## API Reference

**Overview**

```python
app.add_middleware(
  MatomoMiddleware,
  matomo_url="YOUR MATOMO TRACKING URL",
  idsite=12345, # your service tracking id
  access_token="SECRETTOKEN",
  assume_https=True,
  exclude_paths=["/health"],
  exclude_patterns=[".*/old.*"],
)
```

**Parameters**:

- **(Required)** `matomo_url`: The URL to make your tracking calls to.
- **(Required)** `idsite`: The tracking id for your service.
- _(Optional)_ `access_token`: Access token for Matomo. If this is set `cip` is also tracked. Required for tracking some data.
- _(Optional)_ `assume_https`: If `True`, set tracked url scheme to `https`, useful when running behind a proxy. Defaults to `True`.
- _(Optional)_ `exclude_paths`: A list of paths to exclude, only excludes path that is equal to a path in this list. These are tried before `exclude_patterns`.
- _(Optional)_ `exclude_patterns`: A list of regex patterns that are compiled, and then exclude a path from tracking if any pattern match.
These are tried after `exclude_paths`.


**Notes**:

- Currently only some parts [Matomo Tracking HTTP API](https://developer.matomo.org/api-reference/tracking-api) is supported.

## Ideas for further work:
- [x] _filtering tracked of urls_
- [x] _custom extraction of tracked data_


This project keeps a [changelog](./CHANGELOG.md).

