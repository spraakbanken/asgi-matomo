# Getting started

## Installation

To install `asgi-matomo`:

```bash
pip install asgi-matomo
```

## Usage

To use the `MatomoMiddleware` with, for instance [Starlette](https://starlette.io), simply:

```python
{!../../../docs_src/usage/tutorial001.py!}
```

This will track all requests made to your service.

## What is tracked?

Currently `asgi-matomo` tracks the following variables:

- `action_name` that defaults to the path
- `url` of the request
- `ua`: user-agent of the client
- `gt_ms`: measured as the time before and after this middleware call next in the asgi stack.
- `cvar` with at least `http_status_code` and `http_method` set.
- `lang`: if the header `accept-lang` is set
- `cip`: client ip, this is only tracked if `access_token` is given
- `sendimage=0` for performance issues

Please refer to [Matomo Tracking HTTP API](https://developer.matomo.org/api-reference/tracking-api) for available variables.
