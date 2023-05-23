import time
import typing


class PerfMsTracker:
    """Measure time between enter and exit and records it in state."""

    def __init__(self, scope: typing.MutableMapping[str, typing.Any], key: str) -> None:
        self.start_ns = 0.0
        if "state" not in scope:
            scope["state"] = {}
        if "asgi_matomo" not in scope["state"]:
            scope["state"]["asgi_matomo"] = {}
        self.scope = scope
        self.key = key

    def __enter__(self):
        self.start_ns = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._record_time(self.key, time.perf_counter_ns())

    async def __aenter__(self):
        self.start_ns = time.perf_counter_ns()

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        self._record_time(self.key, time.perf_counter_ns())

    def _record_time(self, key: str, end_ns: float) -> None:
        elapsed_time_ms = (end_ns - self.start_ns) / 1000.0
        self.scope["state"]["asgi_matomo"][key] = elapsed_time_ms
