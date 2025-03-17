# Configuring tracked details

Sometimes we want to change something that is tracked, it can either be about a route or about a specific request.

## Configuring a route

We can configure a route by giving the middleware a dict with details.

```python
{! ../../../docs_src/details/tutorial001.py!}
```

In this example, we are changing the details about the route `/foo` in the following ways:

1. We override the `action_name` with `Foo/foo`.
2. We add an event category `e_c` and an event `e_a` to this roure.

## Configuring a request

We can also configure what is tracked during a request by adding a dictionary with values as `asgi_matomo` in the request state.

```python
{!../../../docs_src/details/tutorial002.py!}
```

Here, in this example, we

1. override the `action_name`
2. add an event category `e_c` and an event `e_a`
3. We also add `cvar`, where custom variables can be tracked.

!!! note
    Notice that `cvar` can only be set during a request.


## Tracking time for different steps of a request

To help you track time spent on different tasks, you can use `PerfMsTracker`.

```python
{! ../../../docs_src/details/tutorial003.py!}
```

In this example the function `fetch_data` simulates fetching some data from somewhere else, and we want to track the time it takes to fetch the data in the variable `pf_srv`.

So we use `PerfMsTracker` as a context manager and the time is recorded between entering and exiting the context. The elapsed time (in milliseconds) is then stored in the request state under `asgi_matomo` with the given key (here = `pf_srv`).

!!! note
    `PerfMsTracker` can also be used as an async context manager if that is needed.

## Customize the client use to call Matomo

You can use a custom http client (must use the same API as `httpx.AsyncClient`). You can also set the timeout used with the default client by supplying `http_timeout` to the constructor.

## Customize tracking based on HTTP method

You can specify what HTTP methods to allow with `allowed_methods`, and what methods that should be ignored with `ignored_methods`. Ignored methods takes precedence over allowed methods.
