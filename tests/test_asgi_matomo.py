from asgi_matomo import MatomoMiddleware


def test_it_works() -> None:
    assert MatomoMiddleware is not None
