"""Trackers to measure time."""

import typing

import matomo_core.trackers


def PerfMsTracker(scope: typing.MutableMapping[str, typing.Any], key: str) -> matomo_core.trackers.PerfMsTracker:  # noqa: N802
    """Measure time between enter and exit and records it in state.

    Args:
        scope: mapping of tracked data
        key: the key to use to store this measurement.
    """
    # if "state" not in scope:
    #     scope["state"] = {}
    # if "asgi_matomo" not in scope["state"]:
    #     scope["state"]["asgi_matomo"] = {}
    return matomo_core.trackers.PerfMsTracker(scope=scope["state"]["asgi_matomo"], key=key)
