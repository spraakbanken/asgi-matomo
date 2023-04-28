# asgi-matomo
[![Packaging status](https://img.shields.io/pypi/v/asgi-matomo?color=%2334D058&label=pypi%20package)](https://pypi.org/project/asgi-matomo)
[![CI](https://github.com/spraakbanken/asgi-matomo/workflows/CI/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions?query=workflow%3ACI)
[![Coverage](https://github.com/spraakbanken/asgi-matomo/workflows/Coverage/badge.svg)](https://github.com/spraakbanken/asgi-matomo/actions?query=workflow%3ACoverage)

Tracking requests with Matomo from ASGI apps.

`MatomoMiddleware` adds tracking of all requests to Matomo to ASGI applications (Starlette, FastAPI, Quart, etc.).

**Installation**

```bash
pip install asgi-matomo
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
  minimum_size=400,
)
```

**Parameters**:

- **(Required)** `matomo_url`: The URL to make your tracking calls to.
- **(Required)** `idsite`: The tracking id for your service.
- _(Optional)_ `access_token`: Access token for Matomo. If this is set `cip` is also tracked. Required for tracking some data.
- _(Optional)_ `assume_https`: If `True`, set tracked url scheme to `https`, useful when running behind a proxy. Defaults to `True`.


**Notes**:

- Currently only some parts [Matomo Tracking HTTP API](https://developer.matomo.org/api-reference/tracking-api) is supported.

## Ideas for further work:
- _filtering tracked of urls_
- _custom extraction of tracked data_


