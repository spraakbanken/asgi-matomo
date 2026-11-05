# Getting started

## Installation

To use `asgi-matomo` in your project, use your package manager (here using [`uv`](https://docs.astral.sh/uv)):

```bash
uv add asgi-matomo
# or, if you want to run asgi-matomo in the background
uv add "asgi-matomo[background]"
```

To install `asgi-matomo`:

```bash
pip install asgi-matomo
# or, if you want to run asgi-matomo in the background
pip install "asgi-matomo[background]"
```

## Usage

To use the `MatomoMiddleware` with, for instance [Starlette](https://starlette.io), simply:

```python
{!../../../docs_src/usage/tutorial001.py!}
```

This will track all requests made to your service.

!!! warning
If you are running your ASGI app with `gunicorn`, you need to use [the `background` feature](<#make-tracking-calls-in background>).

### Make tracking calls in background

To use the `background` feature, first ensure that you added `asgi-matomo[background]` to your project.

Then add both `asgi_matomo.MatomoMiddleware` and `asgi_matomo.background.BackgroundTaskMiddleware`:

```python
{!../../../docs_src/usage/tutorial002.py!}
```

This will track all requests made to your service and all tracking calls will be
made in the background.

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
