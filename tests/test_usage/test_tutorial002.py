import pytest
from asgi_lifespan import LifespanManager
from httpx2 import ASGITransport, AsyncClient

from docs_src.usage.tutorial002 import app


@pytest.mark.asyncio
async def test_app() -> None:
    async with (
        LifespanManager(app),
        AsyncClient(transport=ASGITransport(app), base_url="https://testserver") as client,
    ):
        response = await client.get("/")
        assert response.status_code == 200
