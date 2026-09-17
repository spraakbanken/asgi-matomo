"""Re-export from `asgi-beckground`."""

try:
    from asgi_background import BackgroundTaskMiddleware
except ImportError as err:
    raise RuntimeError("Please install `asgi-matomo[background]`") from err

__all__ = ["BackgroundTaskMiddleware"]
