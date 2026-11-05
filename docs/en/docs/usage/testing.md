# Testing

You can provide your own client to test what `MatomoMiddleware` tracks.

```python
{!../../../docs_src/testing/tutorial001.py!}
```

## Test tracking calls in background

When using the `background` feature, you need to use `asgi_lifespan.LifespanManager` to setup the `BackgroundTaskMiddleware` properly.

```python
{!../../../docs_src/testing/tutorial002.py!}
```
